"""Check serialized Order_B provenance against the selected immutable RAW file."""

from __future__ import annotations

import argparse
import json
from bisect import bisect_left, bisect_right
from decimal import Decimal
from pathlib import Path

import orjson


def verify(raw_path: Path, payload_path: Path, timeframe: int) -> dict[str, int]:
    raw = orjson.loads(raw_path.read_bytes())
    payload = json.loads(payload_path.read_bytes())
    lower: list[tuple[int, Decimal, Decimal]] = []
    main: list[tuple[int, Decimal, Decimal]] = []
    for row in raw:
        timestamp = int(row["time"])
        low = Decimal(str(row["low"]))
        high = Decimal(str(row["high"]))
        if lower and lower[-1][0] == timestamp:
            prior = lower[-1]
            lower[-1] = (timestamp, min(prior[1], low), max(prior[2], high))
        else:
            lower.append((timestamp, low, high))
        bucket = timestamp // timeframe * timeframe
        if main and main[-1][0] == bucket:
            prior = main[-1]
            main[-1] = (bucket, min(prior[1], low), max(prior[2], high))
        else:
            main.append((bucket, low, high))
    lower_times = [item[0] for item in lower]
    counts: dict[str, int] = {}
    for direction, result in payload["directions"].items():
        validated = 0
        reset_lookup = {
            (item["index"], item["fromFirstIndex"], item["brokenLevel"]): item
            for item in result["resets"]
        }
        for order in result["orderAudit"]:
            for cause in order["causes"]:
                if cause["kind"] != "reset-leg":
                    continue
                # Authoritative Order_B provenance (Reference 10.7 / production
                # register_order_b_reset_legs) records the geometric anchor and
                # reset Reaction identity. previousReaction* is optional legacy
                # evidence and is not part of the current serialized contract.
                current = cause["resetReactionIdentity"]
                first_index, break_index = cause["physicalOrderIdentity"]
                assert (first_index, break_index) == (
                    order["firstIndex"], order["breakIndex"]
                )
                assert cause["physicalOrderConfirmationTime"] >= order["breakTime"]
                # Reference 10.6: FirstTime equality with strictBreakTime is
                # valid; only the price break and confirmation remain strict.
                assert (
                    cause["postBehaviorStopTime"]
                    < cause["resetTime"]
                    < cause["strictBreakTime"]
                    <= order["firstTime"]
                    <= cause["physicalOrderConfirmationTime"]
                )
                if "previousReactionConfirmationTime" in cause:
                    assert (
                        cause["postBehaviorStopTime"]
                        < cause["previousReactionConfirmationTime"]
                        < cause["resetReactionConfirmationTime"]
                        < cause["resetTime"]
                    )
                assert main[current[1]][0] == cause["resetReactionBreakoutTime"]
                reset_key = (
                    cause["resetIndex"], current[0], cause["resetBrokenLevel"],
                )
                reset = reset_lookup[reset_key]
                if reset["secondTime"] is not None:
                    assert reset["secondTime"] == cause["resetTime"]
                else:
                    start = main[cause["resetIndex"]][0]
                    left_reset = bisect_left(lower_times, start)
                    right_reset = bisect_left(lower_times, start + timeframe)
                    broken_level = Decimal(reset["brokenLevel"])
                    first_reset = next((
                        item[0] for item in lower[left_reset:right_reset]
                        if (item[1] < broken_level if direction == "bullish"
                            else item[2] > broken_level)
                    ), None)
                    assert first_reset == cause["resetTime"]
                # Frozen LL/HH boundary is owned by the accepted anchor behavior
                # candle through the Reset Reaction First candle (Reference 10).
                source_start = cause["anchorBehaviorSourceIndex"]
                reset_first = current[0]
                assert source_start <= reset_first
                prices = [
                    main[index][1 if direction == "bullish" else 2]
                    for index in range(source_start, reset_first + 1)
                ]
                boundary = min(prices) if direction == "bullish" else max(prices)
                source_index = source_start + prices.index(boundary)
                assert Decimal(cause["legBoundary"]) == boundary
                assert cause["legBoundarySourceIndex"] == source_index
                assert cause["legBoundarySourceTime"] == main[source_index][0]
                left = bisect_right(lower_times, cause["resetTime"])
                first_cross = next((
                    item[0] for item in lower[left:]
                    if (item[1] < boundary if direction == "bullish"
                        else item[2] > boundary)
                ), None)
                assert first_cross == cause["strictBreakTime"]
                validated += 1
        counts[direction] = validated
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--timeframe", type=int, default=30)
    args = parser.parse_args()
    print(json.dumps(verify(args.raw, args.payload, args.timeframe), sort_keys=True))
