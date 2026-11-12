"""Bridge projection must not reconstruct setup trading decisions."""
from datetime import timedelta
import importlib
from pathlib import Path
from types import SimpleNamespace as NS
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/"bridge"))
from test_bullish_setup_engine import Market, D


def test_setup_projection_has_exact_levels_and_actual_confirmation_provenance():
    bridge=importlib.import_module("trading_pipeline")
    assert hasattr(bridge,"serialize_setup_annotations"), "Setup projection is missing"
    m=Market();m.stopall(1,1,2,stop=7);m.behavior(3,5)
    market=NS(start_index=0,end_index=99)
    payload=bridge.serialize_setup_annotations(m.calculate(),market)
    setup,=payload["positionSetups"]
    assert setup["entryPrice"]=="110" and setup["stopPrice"]=="100"
    assert setup["targetPrice"]=="150" and setup["riskReward"]=="4"
    assert setup["entryIndex"]==5 and setup["behaviorSourceIndex"]==3
    assert setup["confirmationEventTime"]!=setup["behaviorSourceTime"]
    assert setup["closeEventTime"]-setup["entryTime"]==30
    assert setup["widthBars"]==50
    assert payload["stopAllAssessments"][0]["status"]=="F"
    assert payload["behaviorAssessments"][0]["status"]=="F"


def test_projection_clips_by_entry_without_restarting_history_or_changing_ids():
    bridge=importlib.import_module("trading_pipeline")
    assert hasattr(bridge,"serialize_setup_annotations"), "Setup projection is missing"
    m=Market();m.stopall(1,1,2,stop=7);m.behavior(3,5)
    result=m.calculate()
    full=bridge.serialize_setup_annotations(result,NS(start_index=0,end_index=99))
    narrow=bridge.serialize_setup_annotations(result,NS(start_index=5,end_index=99))
    assert narrow["positionSetups"]==full["positionSetups"]
    assert narrow["stopAllAssessments"]==[]
    assert bridge.serialize_setup_annotations(result,NS(start_index=6,end_index=99))["positionSetups"]==[]
    shifted=bridge.absolute_payload_indexes(narrow,100)
    assert shifted["positionSetups"][0]["entryIndex"]==105
    assert shifted["positionSetups"][0]["anchorSourceIndex"]==101
    assert shifted["positionSetups"][0]["id"]==full["positionSetups"][0]["id"]


def test_setup_fields_survive_independent_regime_merging():
    bridge=importlib.import_module("trading_pipeline")
    assert hasattr(bridge,"serialize_setup_annotations"), "Setup projection is missing"
    m=Market();m.stopall(1,1,2);m.behavior(3,4)
    first=bridge.serialize_setup_annotations(m.calculate(),NS(start_index=0,end_index=99))
    second={"positionSetups":[],"stopAllAssessments":[],"behaviorAssessments":[],"setupReferenceBreaks":[]}
    combined=bridge.merge_regime_outputs([("bullish",first),("bearish",{}),("bullish",second)])
    assert combined["bullish"]["positionSetups"]==first["positionSetups"]
    assert combined["bullish"]["calculationSegments"][0] is first


def test_setup_primary_cycle_identity_matches_absolute_regime_projection():
    bridge=importlib.import_module("trading_pipeline")
    m=Market();m.primary(1,1,2,cycle="bullish:cycle:7:9");m.behavior(3,4)
    payload=bridge.serialize_setup_annotations(m.calculate(),NS(start_index=0,end_index=99,index_offset=100))
    assert payload["positionSetups"][0]["cycleId"]=="bullish:cycle:107:109"


def test_secondary_bullish_dependency_context_does_not_publish_trend_setups(monkeypatch):
    _check_setup_owner(monkeypatch,"both",False)


def test_explicit_bullish_owner_publishes_setup_stage(monkeypatch):
    _check_setup_owner(monkeypatch,"bullish",True)


def _check_setup_owner(monkeypatch,direction,expected):
    bridge=importlib.import_module("trading_pipeline")
    setup=importlib.import_module("bullish_setup_engine")
    m=Market();m.stopall(1,1,2);m.behavior(3,4);result=m.calculate()
    calls=[]
    def calculate(*args,**kwargs):
        calls.append(args)
        return result
    monkeypatch.setattr(setup,"calculate_bullish_setups",calculate)
    monkeypatch.setattr(bridge,"calculate_direction_range_state",lambda *args:None)
    monkeypatch.setattr(bridge,"finalize_direction_visibility",lambda *args:NS(primary_groups={"S":[],"E":[],"StopAll":[]}))
    monkeypatch.setattr(bridge,"serialize_direction_payload",lambda *args:{"native":True})
    args=NS(direction=direction,lifecycle_engine=object(),s_zones="enabled")
    output=bridge.build_direction_output("bullish",args,NS(primary=None),
        NS(chronology=object(),start_index=0,end_index=99),NS(full_e_detectors={}),{})
    assert bool(calls)==expected
    assert ("positionSetups" in output)==expected
    assert output["native"] is True
