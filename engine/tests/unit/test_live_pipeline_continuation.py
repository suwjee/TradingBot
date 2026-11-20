import json
from pathlib import Path
import sys

import pytest

ENGINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ENGINE / "bridge"))
import trading_pipeline as pipeline


def setup(direction, destination, start, end, timeframe=30):
    flags = {
        "engine": "reaction_engine", "blue-engine": "blue_line_detector",
        "a-engine": "a_zone_detector", "s-engine": "s_zone_detector",
        "e-engine": "e_zone_detector", "stopall-engine": "lifecycle_engine",
    }
    args = []
    for flag, module in flags.items():
        args.extend((f"--{flag}", str(ENGINE / "pipeline" / (module + ".py"))))
    args.extend((
        "--data", str(destination), "--direction", direction, "--timeframe", str(timeframe),
        "--from-time", str(start), "--to-time", str(end), "--bridge-output",
    ))
    return pipeline.parse_arguments(args)


@pytest.mark.parametrize("direction", ("bullish", "bearish"))
@pytest.mark.parametrize("timeframe", (1, 30))
def test_live_pipeline_matches_manual_apply_at_each_horizon(direction, timeframe, tmp_path):
    from live_pipeline import LivePipelineContinuation

    source = tmp_path / "sample.json"
    first = 1_795_000_020
    rows = []
    for i in range(420):
        mid = 100 + (i * 13 % 41) - i // 17
        opening, closing = mid + (i % 3), mid - (i % 2)
        rows.append(dict(time=first + i * 5, open=opening, high=max(opening, closing) + i % 7,
                         low=min(opening, closing) - i % 5, close=closing))
    args = setup(direction, source, first, rows[239]["time"], timeframe)
    engines = pipeline.load_engines(args, {})
    live = LivePipelineContinuation(args, engines)
    previous = 0
    for count in (240, 241, 247, 301, 420):
        args.to_time = rows[count - 1]["time"]
        source.write_text(json.dumps(rows[:count]), encoding="utf-8")
        market = pipeline.prepare_market_context(args, engines, {})
        expected = pipeline.build_response_payload(
            args, engines, market, pipeline.prepare_pipeline_state(args, engines, market, {}), {}, 0,
        )
        actual = live.append(rows[previous:count])
        previous = count
        actual.pop("timings")
        expected.pop("timings")
        assert actual == expected


def test_failed_full_replay_leaves_the_raw_append_retryable(monkeypatch, tmp_path):
    from types import SimpleNamespace
    import live_pipeline

    args = setup("bullish", tmp_path / "raw.json", 100, 100)
    worker = live_pipeline.LivePipelineContinuation(args, SimpleNamespace(e_zone=True, primary=None))
    attempts = []

    def calculate(_args, _engines, buckets, **_options):
        times = [row["time"] for row in buckets.second_buckets]
        attempts.append(times)
        if len(attempts) == 2:
            raise ValueError("Calculation failed")
        return {"times": times}

    monkeypatch.setattr(live_pipeline, "calculate_live_from_buckets", calculate)
    first = dict(time=100, open=1, high=2, low=0, close=1)
    second = dict(first, time=105, high=3)
    assert worker.append([first]) == {"times": [100]}
    with pytest.raises(ValueError, match="Calculation failed"):
        worker.append([second])
    assert worker.append([second]) == {"times": [100, 105]}
    assert worker.append([]) == {"times": [100, 105]}
    assert attempts == [[100], [100, 105], [100, 105], [100, 105]]


def test_failed_publication_rebuilds_market_indexes_from_the_rolled_back_prefix(monkeypatch, tmp_path):
    import live_pipeline

    rows = [dict(time=180 + i * 5, open=10, high=12 + i % 7, low=8, close=11) for i in range(20)]
    args = setup("bearish", tmp_path / "raw.json", rows[0]["time"], rows[-1]["time"])
    engines = pipeline.load_engines(args, {})
    worker = live_pipeline.LivePipelineContinuation(args, engines)
    worker.append(rows[:12])
    accepted = worker._market_views
    original = live_pipeline.calculate_live_from_buckets

    def reject_after_calculating(*args, **options):
        original(*args, **options)
        raise ValueError("Rejected after calculation")

    with monkeypatch.context() as staged:
        staged.setattr(live_pipeline, "calculate_live_from_buckets", reject_after_calculating)
        with pytest.raises(ValueError, match="Rejected after calculation"):
            worker.append(rows[12:])
    assert worker._market_views is not accepted
    actual = worker.append(rows[12:])
    expected = pipeline.calculate_live_from_raw(args, engines, rows)
    actual.pop("timings")
    expected.pop("timings")
    assert actual == expected


def test_raw_lineage_catches_up_once_and_accepts_only_an_exact_append():
    from decimal import Decimal
    from live_pipeline import LiveRawChanged, LiveRawSource, _decode_raw

    original = b'\xef\xbb\xbf[{"time":10,"open":1.00},{"time":15,"open":2.0}]\n'
    source = _decode_raw(original)
    live = LiveRawSource(source[:1], original, source)

    class Engine:
        def append(self, rows):
            return rows

    engine = Engine()
    assert live.append(original, engine) == [source[1]]
    assert live.append(original, engine) == []
    extended = original[:original.rfind(b"]")] + b',{"time":20,"open":3.000}]\n'
    assert live.append(extended, engine) == [{"time": 20, "open": Decimal("3.000")}]
    with pytest.raises(LiveRawChanged, match="Existing RAW candles changed"):
        live.append(extended.replace(b"1.00", b"1.20"), engine)


def test_worker_rejects_a_path_supplied_over_stdin(tmp_path, monkeypatch, capsys):
    from io import BytesIO, TextIOWrapper
    from types import SimpleNamespace

    import live_pipeline

    source = tmp_path / "raw.json"
    source.write_bytes(b'[{"time":10}]')
    external = tmp_path / "other" / "external.json"
    external.parent.mkdir()
    external.write_bytes(b'[{"time":10},{"time":15}]')
    request = json.dumps({"data": str(external)}) + "\n"
    monkeypatch.setenv("TRADINGBOT_LIVE_RAW_SOURCE", str(source))
    monkeypatch.setattr(sys, "stdin", TextIOWrapper(BytesIO(request.encode())))
    monkeypatch.setattr(live_pipeline, "parse_arguments", lambda: SimpleNamespace(data=source))
    monkeypatch.setattr(live_pipeline, "load_engines", lambda *_: {})

    class Engine:
        def __init__(self, *_):
            pass

        def append(self, rows):
            return rows

    monkeypatch.setattr(live_pipeline, "LivePipelineContinuation", Engine)

    assert live_pipeline.main() == 1
    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [message["type"] for message in messages] == ["seed", "error"]
    assert messages[-1]["code"] == "LIVE_ENGINE_FAILED"


def test_raw_delta_requires_the_exact_base_and_final_bytes_and_can_return_to_a_full_snapshot():
    from hashlib import sha256
    from live_pipeline import LiveRawDeltaMismatch, LiveRawSource, _decode_raw

    original = b'\xef\xbb\xbf[{"time":10,"open":1.00},{"time":15,"open":2.0}]\r\n'
    rows = _decode_raw(original)
    source = LiveRawSource(rows[:1], original, rows)
    delta = b',{"time":20,"open":3.000},{"time":25,"open":4.00}'
    boundary = original.rfind(b"]")
    target = original[:boundary] + delta + original[boundary:]

    class Engine:
        calls = []

        def append(self, new_rows):
            self.calls.append(new_rows)
            return new_rows

    engine = Engine()
    fingerprint = lambda data: sha256(data).hexdigest()
    with pytest.raises(LiveRawDeltaMismatch):
        source.append_delta(delta, "0" * 64, fingerprint(target), engine)
    with pytest.raises(LiveRawDeltaMismatch):
        source.append_delta(delta.replace(b"3.000", b"3.100"), fingerprint(original), fingerprint(target), engine)
    assert not engine.calls
    assert source.append_delta(delta, fingerprint(original), fingerprint(target), engine) == _decode_raw(target)[1:]
    subsequent = target[:target.rfind(b"]")] + b',{"time":30,"open":5.0}]\r\n'
    assert source.append(subsequent, engine) == _decode_raw(subsequent)[-1:]
