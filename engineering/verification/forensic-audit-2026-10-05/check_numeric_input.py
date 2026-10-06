"""Show Decimal-sensitive divergence at the accepted numeric JSON boundary."""
from pathlib import Path
from decimal import Decimal
import importlib.util, json, orjson, sys

OUT=Path(__file__).resolve().parent

def main():
    spec=importlib.util.spec_from_file_location('numeric_audit_bridge',OUT/'package/bridge/trading_pipeline.py')
    bridge=importlib.util.module_from_spec(spec); sys.modules[spec.name]=bridge; spec.loader.exec_module(bridge)
    engine=bridge.load_engine(OUT/'package/pipeline/reaction_engine.py')
    encoded=b'[{"time":1789000020,"open":100.0000000000000002,"high":100.0000000000000003,"low":100.0000000000000000,"close":100.0000000000000001}]'
    exact=json.loads(encoded,parse_float=Decimal)
    current=orjson.loads(encoded)
    exact_buckets=bridge.build_candle_buckets(exact,30)[1]
    actual_buckets=bridge.build_candle_buckets(current,30)[1]
    expected=bridge.build_candle_objects(engine,exact_buckets)[0]
    actual=bridge.build_candle_objects(engine,actual_buckets)[0]
    # Control: the accepted string price representation preserves the same prices.
    string_rows=[{k:(str(v) if k!='time' else v) for k,v in row.items()} for row in exact]
    string_candle=bridge.build_candle_objects(engine,bridge.build_candle_buckets(string_rows,30)[1])[0]
    result={'encodedNumericJSON':encoded.decode(),'inputValidity':'valid numeric JSON, internally consistent OHLC',
            'expected':{'open':str(expected.open),'close':str(expected.close),'tag':expected.tag},
            'actual':{'open':str(actual.open),'close':str(actual.close),'tag':actual.tag},
            'stringInputControl':{'open':str(string_candle.open),'close':str(string_candle.close),'tag':string_candle.tag},
            'firstDiff':'orjson.loads converts unequal exact prices into equal float100.0 before Decimal normalization',
            'marketRAWScope':'synthetic valid input; no price lexeme loss demonstrated in current market files'}
    assert expected.tag=='RED' and actual.tag=='GREEN' and string_candle.tag=='RED'
    (OUT/'numeric-input-results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
