"""Reproduce the frozen V8.2/V9 synthetic input; no real-market data."""
import argparse
import hashlib
import json
import random
from pathlib import Path


def price(value):
    return f'{value // 1000}.{value % 1000:03d}'


def generate(path, count):
    rng = random.Random(20261123)
    t, value = 1767225600, 3500000
    with path.open('x', encoding='ascii', newline='') as stream:
        stream.write('[')
        for i in range(count):
            if i and i % 60000 == 0:
                t += 21600
            if i and i % 80000 == 0:
                value += (-1 if i % 160000 else 1) * 1400
            drift = 2 if (i // 2200) % 4 == 0 else (-3 if (i // 2200) % 4 == 2 else 0)
            shock = rng.randrange(-26, 27) + rng.randrange(-19, 20) + drift
            if i % 2101 == 0:
                shock += rng.randrange(-170, 171)
            op, close = value, max(1, value + shock)
            high = max(op, close) + rng.randrange(0, 22)
            low = max(1, min(op, close) - rng.randrange(0, 22))
            if i:
                stream.write(',')
            stream.write(f'{{"time":{t},"open":{price(op)},"high":{price(high)},"low":{price(low)},"close":{price(close)}}}')
            t += 5
            value = close
        stream.write(']')
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return digest, t - 5


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bars', type=int, choices=(100000, 250000, 500000, 1000000), required=True)
    p.add_argument('--frozen', type=Path, required=True)
    p.add_argument('--raw', type=Path, required=True)
    p.add_argument('--case', type=Path, required=True)
    a = p.parse_args()
    frozen = json.loads(a.frozen.read_text())
    expected = frozen['scales'][str(a.bars)]
    digest, last = generate(a.raw, a.bars)
    if digest != expected['raw_sha256']:
        raise ValueError('Generated RAW differs from frozen historical input')
    case = {'name': f'SYNTHETIC_XAUUSD_5S_{a.bars}_seed20261123', 'records': a.bars,
            'first_time': 1767225600, 'last_time': last, 'source_sha256': frozen['source_sha256'],
            **expected}
    a.case.write_text(json.dumps(case, indent=2) + '\n')
    print(f'{a.bars} exact historical synthetic RAW records: SHA256 PASS {digest}')


if __name__ == '__main__':
    main()
