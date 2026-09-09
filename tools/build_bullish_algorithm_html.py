from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import orjson


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/algorithms/BULLISH_INDICATOR_ALGORITHM_FA.html"
PAYLOAD = ROOT / "tmp/full-bullish-dominant-stop-fix.json"
RAW = ROOT / "market-data/raw/RAW_FOREXCOM_XAUUSD_1S_FROM_2026_08_18_04_44_40_TO_2026_09_05_00.json"
TEHRAN = ZoneInfo("Asia/Tehran")


def esc(value: object) -> str:
    return html.escape("—" if value is None else str(value))


def local_time(epoch: int | None) -> str:
    if epoch is None:
        return "—"
    return datetime.fromtimestamp(epoch, TEHRAN).strftime("%Y-%m-%d %H:%M:%S")


def load() -> tuple[dict, list[dict], dict]:
    envelope = orjson.loads(PAYLOAD.read_bytes())
    payload = envelope["directions"]["bullish"]
    raw = orjson.loads(RAW.read_bytes())
    return payload, raw, envelope


def find(items: list[dict], **wanted: object) -> dict:
    for item in items:
        if all(item.get(key) == value for key, value in wanted.items()):
            return item
    raise RuntimeError(f"نمونه پیدا نشد: {wanted}")


def candle_inventory(raw: list[dict], times: set[int]) -> dict[int, dict]:
    exact = {t for t in times if t % 30}
    buckets = {t - (t % 30) for t in times}
    one_second: dict[int, dict] = {}
    grouped: dict[int, dict] = {}
    for candle in raw:
        timestamp = candle["time"]
        if timestamp in exact:
            one_second[timestamp] = candle
        bucket = timestamp - (timestamp % 30)
        if bucket not in buckets:
            continue
        current = grouped.get(bucket)
        if current is None:
            grouped[bucket] = dict(candle)
        else:
            current["high"] = max(current["high"], candle["high"])
            current["low"] = min(current["low"], candle["low"])
            current["close"] = candle["close"]
    return {**grouped, **one_second}


def role(label: str, timestamp: int | None, why: str) -> tuple[str, int | None, str]:
    return label, timestamp, why


def role_table(rows: list[tuple[str, int | None, str]], candles: dict[int, dict]) -> str:
    body = []
    for label, timestamp, why in rows:
        candle = candles.get(timestamp or -1)
        if candle is None:
            body.append(
                f"<tr><th>{esc(label)}</th><td>{esc(local_time(timestamp))}</td>"
                f"<td>—</td><td>—</td><td colspan='4'>—</td><td>{esc(why)}</td></tr>"
            )
            continue
        green = candle["open"] <= candle["close"]
        color = "سبز" if green else "قرمز"
        badge = "green" if green else "red"
        timeframe = "۱ ثانیه (رویداد دقیق)" if timestamp and timestamp % 30 else "۳۰ ثانیه"
        body.append(
            f"<tr><th>{esc(label)}</th><td dir='ltr'>{esc(local_time(timestamp))}</td>"
            f"<td>{timeframe}</td><td><span class='candle {badge}'>{color}</span></td>"
            f"<td>{esc(candle['open'])}</td><td>{esc(candle['high'])}</td>"
            f"<td>{esc(candle['low'])}</td><td>{esc(candle['close'])}</td><td>{esc(why)}</td></tr>"
        )
    return (
        "<div class='table-wrap' tabindex='0'><table><thead><tr>"
        "<th>نقش کندل</th><th>زمان تهران</th><th>TF</th><th>رنگ</th>"
        "<th>Open</th><th>High</th><th>Low</th><th>Close</th><th>چرا این کندل؟</th>"
        "</tr></thead><tbody>" + "".join(body) + "</tbody></table></div>"
    )


def example(title: str, note: str, rows: list[tuple[str, int | None, str]], candles: dict[int, dict], *, open_: bool = False, extra: str = "") -> str:
    opened = " open" if open_ else ""
    return f"<details{opened}><summary>{esc(title)}</summary><p>{esc(note)}</p>{role_table(rows, candles)}{extra}</details>"


def card(title: str, text: str, formula: str | None = None) -> str:
    formula_html = f"<div class='formula' dir='ltr'>{esc(formula)}</div>" if formula else ""
    return f"<article class='rule'><h3>{esc(title)}</h3><p>{esc(text)}</p>{formula_html}</article>"


READABLE_KIND = {
    "scale": "Scale", "reset": "Reset", "simple": "Simple",
    "advanced": "Advanced", "type3": "Type 3",
    "parent-stop": "Parent stop", "reset-leg": "Reset leg",
    "carried-live": "Carried live", "sequence-group-stop": "Sequence group stop",
    "stopall-stop": "StopAll stop", "Order_A": "Parent stop", "Order_B": "Reset leg",
}

FIELD_HELP = {
    "type": "نوع collection در /info", "direction": "جهت آبجکت", "timezone": "منطقه زمانی نمایش",
    "mode": "حالت Reaction؛ Leg start یعنی Mode A و Normal یعنی Mode B", "startedAt": "زمان کندل First",
    "structure": "ظرف هندسه Box", "boxTop": "سقف Box و کندل منبع آن", "boxBottom": "کف Box و کندل منبع آن",
    "price": "قیمت آبجکت یا سطح", "time": "زمان کندل منبع/رویداد", "confirmedAt": "زمان تأیید یا Break",
    "occurredAt": "زمان واقعی وقوع", "mainCandleAt": "شروع کندل اصلی حامل رویداد", "brokenLevel": "سطح strict شکسته‌شده",
    "reactionStartedAt": "First Reaction مالک Reset", "formation": "نوع تشکیل آبجکت", "formedAt": "کندل محل تشکیل/رسم",
    "line": "مشخصات خط Blue", "sourceExtreme": "extreme منبع و سطح stop محاسباتی Blue", "stop": "اطلاعات stop نمایش‌داده‌شده در /info",
    "blueLines": "دو Blue مالک A", "first": "Blue اول", "second": "Blue دوم", "stoppedAt": "زمان stop دقیق/اصلی والد",
    "stopLevel": "سطح strict stop", "continuation": "سطح continuation و کندل منبع", "triggeredAt": "زمان دقیق trigger",
    "reaction": "Reaction تأییدکننده A", "color": "خانواده lifecycle آبجکت S", "parentA": "A والد S",
    "reset": "Reset مالک Type 3", "order": "Order نزولی مصرف‌شده", "decisionAt": "زمان دقیق تصمیم نهایی",
    "family": "خانواده Blue/Red در E", "parent": "S/E/StopAll والد", "causes": "علت‌های مالکیتی یک Order فیزیکی",
    "causeEvidence": "زمان‌های اثبات علت Order", "parentStoppedAt": "stop والد که Order_A را مجاز کرده",
    "resetAt": "Reset آغازگر Order_B", "boundaryBrokenAt": "لحظه strict شکستن boundary leg",
    "gate": "شرط تبدیل E به StopAll", "stopped": "رفتار قبلی که gate را ساخته", "group": "کلید گروه lifecycle",
    "count": "تعداد اعضای گروه", "sourceE": "خانواده E زیرین StopAll", "level": "سطح stop Order Audit",
    "sourceAt": "کندل منبع سطح", "hitAt": "لحظه دقیق برخورد strict", "consumed": "آیا Order Reaction مصرف شده است",
    "stopHitAt": "لحظه stop شدن Order Reaction", "timeframeSeconds": "تایم‌فریم محاسبه به ثانیه",
    "range": "بازه واقعی محاسبه", "from": "ابتدای بازه", "to": "انتهای بازه", "source": "مشخصات منبع محاسبه",
    "kind": "نوع علت Order", "parentType": "نوع والد علت", "parentFamily": "خانواده والد علت",
    "parentFormedAt": "کندل تشکیل والد علت", "parentStoppedAt": "لحظه stop والد علت",
}


def clean(value: object) -> object | None:
    if value is None:
        return None
    if isinstance(value, list):
        items = [clean(item) for item in value]
        return [item for item in items if item is not None] or None
    if isinstance(value, dict):
        output = {key: cleaned for key, item in value.items() if (cleaned := clean(item)) is not None}
        return output or None
    return value


def time_value(value: int | None) -> dict | None:
    return {"time": value} if value is not None else None


def price_point(price: object, timestamp: int | None) -> dict:
    return {"time": timestamp, "price": price}


def cause_object(cause: object) -> object:
    if isinstance(cause, str):
        return READABLE_KIND.get(cause, cause)
    if not isinstance(cause, dict):
        return cause
    if cause.get("kind") == "parent-stop":
        return clean({"kind": "Parent stop", "parentType": cause.get("parentType"),
                      "parentFamily": cause.get("parentFamily"), "parentFormedAt": time_value(cause.get("parentSourceTime")),
                      "parentStoppedAt": time_value(cause.get("eventTime"))})
    if cause.get("kind") == "reset-leg":
        return clean({"kind": "Reset leg", "resetAt": time_value(cause.get("resetTime")),
                      "boundaryBrokenAt": time_value(cause.get("boundaryBreakTime"))})
    return {"kind": READABLE_KIND.get(cause.get("kind"), cause.get("kind"))}


def order_object(row: dict) -> dict | None:
    if row.get("orderFirstTime") is None and row.get("orderBreakTime") is None and row.get("orderStopLevel") is None:
        return None
    return clean({
        "direction": "Bullish" if row.get("orderDirection") == "bullish" else "Bearish",
        "mode": "Leg start" if row.get("orderMode") == "A" else "Normal" if row.get("orderMode") == "B" else row.get("orderMode"),
        "causes": [cause_object(cause) for cause in row.get("orderCauses", [])] or None,
        "startedAt": time_value(row.get("orderFirstTime")),
        "confirmedAt": time_value(row.get("orderConfirmationTime") or row.get("orderBreakTime")),
        "structure": {"boxTop": price_point(row.get("orderBoxTop"), row.get("orderBoxTopSourceTime")),
                      "boxBottom": price_point(row.get("orderBoxBottom"), row.get("orderBoxBottomSourceTime"))},
        "stop": price_point(row.get("orderStopLevel"), row.get("orderStopSourceTime")),
        "causeEvidence": {"parentStoppedAt": time_value(row.get("orderParentStopCauseTime")),
                          "resetAt": time_value(row.get("orderResetLegResetTime")),
                          "boundaryBrokenAt": time_value(row.get("orderResetLegBreakTime"))},
    })


def info_projection(group: str, row: dict, groups: dict) -> dict:
    base = {"type": {"reactions": "Reaction", "resets": "Reset", "blueLines": "Blue Line", "aZones": "A",
                     "sZones": "S", "eZones": "E", "stopAlls": "StopAll", "orderAudit": "Order audit"}[group],
            "direction": "Bullish", "timezone": "Asia/Tehran"}
    if group == "reactions":
        return clean({**base, "mode": "Leg start" if row["mode"] == "A" else "Normal",
                      "startedAt": time_value(row["firstTime"]),
                      "structure": {"boxTop": price_point(row["boxTop"], row["boxTopSourceTime"]),
                                    "boxBottom": price_point(row["boxBottom"], row["boxBottomSourceTime"])},
                      "confirmedAt": time_value(row["breakTime"])})
    if group == "resets":
        owner = next((item for item in groups["reactions"] if item["firstIndex"] == row["fromFirstIndex"]), None)
        return clean({**base, "occurredAt": time_value(row.get("secondTime") or row["time"]),
                      "mainCandleAt": time_value(row["time"]), "brokenLevel": row["brokenLevel"],
                      "reactionStartedAt": time_value(owner.get("firstTime") if owner else None)})
    if group == "blueLines":
        return clean({**base, "formation": READABLE_KIND[row["kind"]], "formedAt": time_value(row["sourceTime"]),
                      "line": {"price": row["linePrice"], "sourceExtreme": row["sourceExtreme"]},
                      "stop": price_point(row["sourceExtreme"], row["endTime"])})
    if group == "aZones":
        child = next((item for item in groups["sZones"] if item["aSourceTime"] == row["sourceTime"]), None)
        return clean({**base, "formedAt": time_value(row["sourceTime"]), "price": row["price"],
                      "blueLines": {"first": {"formedAt": time_value(row["blue1SourceTime"]), "stoppedAt": time_value(row["blue1StopTime"]), "stopLevel": row["blue1StopLevel"]},
                                    "second": {"formedAt": time_value(row["blue2SourceTime"]), "stoppedAt": time_value(row["blue2StopTime"]), "stopLevel": row["blue2StopLevel"]}},
                      "continuation": price_point(row["continuationLevel"], row["continuationSourceTime"]),
                      "triggeredAt": time_value(row.get("triggerEventTime") or row["triggerTime"]),
                      "reaction": {"startedAt": time_value(row["reactionFirstTime"]), "confirmedAt": time_value(row["reactionBreakTime"])},
                      "stop": price_point(row["price"], child.get("aStopEventTime") if child else None)})
    if group == "sZones":
        child = next((item for item in groups["eZones"] if item["parentSourceTime"] == row["sourceTime"]), None)
        return clean({**base, "color": row["color"].title(), "formation": READABLE_KIND[row["formationType"]],
                      "formedAt": time_value(row["sourceTime"]), "price": row["price"],
                      "parentA": {"formedAt": time_value(row["aSourceTime"]), "price": row["aPrice"],
                                  "stoppedAt": time_value(row.get("aStopEventTime") or row["aStopTime"])},
                      "reset": time_value(row.get("resetTime")) if row["formationType"] == "type3" else None,
                      "order": order_object(row), "decisionAt": time_value(row.get("decisionEventTime") or row["decisionTime"]),
                      "stop": price_point(row["price"], child.get("parentStopEventTime") if child else None)})
    if group == "eZones":
        # This intentionally mirrors /info: its current lookup uses family+number only.
        child = next((item for item in groups["stopAlls"] if item["underlyingEFamily"] == row["family"] and item["underlyingENumber"] == row["number"]), None)
        return clean({**base, "family": row["family"].title(), "formedAt": time_value(row["sourceTime"]), "price": row["price"],
                      "parent": {"type": row["parentType"], "formedAt": time_value(row["parentSourceTime"]),
                                 "price": row["parentPrice"], "stoppedAt": time_value(row.get("parentStopEventTime") or row["parentStopTime"])},
                      "order": order_object(row), "decisionAt": time_value(row.get("decisionEventTime") or row["decisionTime"]),
                      "stop": price_point(row["price"], child.get("gateEventTime") if child else None)})
    if group == "stopAlls":
        return clean({**base, "formedAt": time_value(row["sourceTime"]), "price": row["price"],
                      "gate": {"type": READABLE_KIND.get(row["gateType"], row["gateType"]), "time": time_value(row["gateEventTime"]),
                               "stopped": {"type": row["stoppedBehaviorType"], "group": row["stoppedBehaviorKey"], "count": row["stoppedBehaviorCount"]}},
                      "sourceE": {"family": row["underlyingEFamily"]}, "order": order_object(row),
                      "decisionAt": time_value(row.get("decisionEventTime") or row["decisionTime"]),
                      "stop": time_value(row.get("stopEventTime") or row.get("stopTime"))})
    if group == "orderAudit":
        return clean({**base, "mode": "Leg start" if row["reactionMode"] == "A" else "Normal",
                      "startedAt": time_value(row["firstTime"]), "confirmedAt": time_value(row["breakTime"]),
                      "stop": {"level": row["stopLevel"], "sourceAt": time_value(row["stopSourceTime"]),
                               "hitAt": time_value(row.get("stopHitEventTime") or row["stopHitTime"])},
                      "causes": [cause_object(cause) for cause in row.get("causes", [])]})
    raise ValueError(group)


def field_rows(value: object, candles: dict[int, dict], path: str = "") -> list[str]:
    rows: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            field_path = f"{path}.{key}" if path else key
            meaning = FIELD_HELP.get(key, "فیلد داخلی آبجکت /info")
            if isinstance(item, (dict, list)):
                kind = "object" if isinstance(item, dict) else "array"
                rows.append(f"<tr class='object-row'><th dir='ltr'>{esc(field_path)}</th><td>{kind}</td><td>—</td><td>{esc(meaning)}</td><td>ظرف داده؛ کندل مستقل ندارد</td></tr>")
                rows.extend(field_rows(item, candles, field_path))
            else:
                candle_html = "فیلد وضعیتی؛ کندل مستقل ندارد"
                shown = local_time(item) if key == "time" and isinstance(item, int) else item
                if key == "time" and isinstance(item, int) and item in candles:
                    candle = candles[item]
                    color = "سبز" if candle["open"] <= candle["close"] else "قرمز"
                    candle_html = f"{color} · O {esc(candle['open'])} · H {esc(candle['high'])} · L {esc(candle['low'])} · C {esc(candle['close'])}"
                rows.append(f"<tr><th dir='ltr'>{esc(field_path)}</th><td>field</td><td dir='ltr'>{esc(shown)}</td><td>{esc(meaning)}</td><td>{candle_html}</td></tr>")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(field_rows(item, candles, f"{path}[]") if isinstance(item, (dict, list)) else [
                f"<tr><th dir='ltr'>{esc(path)}[]</th><td>field</td><td>{esc(item)}</td><td>عضو آرایه شماره {index + 1}</td><td>فیلد وضعیتی؛ کندل مستقل ندارد</td></tr>"
            ])
    return rows


def info_panel(group: str, row: dict, groups: dict, candles: dict[int, dict]) -> str:
    projection = info_projection(group, row, groups)
    collection = {"reactions": "reactions", "resets": "resets", "blueLines": "blueLines",
                  "aZones": "aStructures", "sZones": "sStructures", "eZones": "eStructures",
                  "stopAlls": "stopAllEvents", "orderAudit": "orderAudit"}[group]
    prefix = f"directions.bullish.{collection}[]"
    rows = "".join(field_rows(projection, candles, prefix))
    return ("<details class='info-object'><summary>تمام واژه‌ها و objectهای همین نمونه در /info</summary>"
            "<p>نام ستون اول دقیقاً مسیر فیلد در Bridge output است. ردیف‌های object فقط ظرف‌اند؛ "
            "هر فیلد زمانی در ردیف بعدی به کندل خام متصل شده است.</p>"
            "<div class='table-wrap' tabindex='0'><table class='field-table'><thead><tr><th>مسیر دقیق /info</th><th>نوع</th>"
            "<th>مقدار مثال</th><th>معنی ساده</th><th>کندل متصل</th></tr></thead><tbody>" + rows + "</tbody></table></div></details>")


def generic_panel(title: str, projection: dict, candles: dict[int, dict]) -> str:
    rows = "".join(field_rows(projection, candles))
    return (f"<details class='info-object'><summary>{esc(title)}</summary>"
            "<div class='table-wrap' tabindex='0'><table class='field-table'><thead><tr><th>مسیر دقیق /info</th><th>نوع</th>"
            "<th>مقدار مثال</th><th>معنی ساده</th><th>کندل متصل</th></tr></thead><tbody>" + rows + "</tbody></table></div></details>")


def projection_times(value: object, key: str = "") -> set[int]:
    if isinstance(value, dict):
        output: set[int] = set()
        for child_key, child in value.items():
            output |= projection_times(child, child_key)
        return output
    if isinstance(value, list):
        output: set[int] = set()
        for child in value:
            output |= projection_times(child, key)
        return output
    return {value} if key == "time" and isinstance(value, int) else set()


def build() -> None:
    b, raw, envelope = load()
    reactions = b["reactions"]
    resets = b["resets"]
    blues = b["blueLines"]
    azones = b["aZones"]
    szones = b["sZones"]
    ezones = b["eZones"]

    reaction_a = find(reactions, firstTime=1787016450)
    reaction_b = find(reactions, firstTime=1787016510)
    reset = next(item for item in resets if item.get("secondTime") is not None)
    reset_owner = next(item for item in reactions if item["firstIndex"] == reset["fromFirstIndex"])
    scale_blue = find(blues, kind="scale", sourceTime=1787016540)
    reset_blue = find(blues, kind="reset", sourceTime=1787017080)

    a1 = find(azones, sourceTime=1787017530)
    a2 = find(azones, sourceTime=1787121150)
    a3 = find(azones, sourceTime=1787026860)
    a4 = find(azones, sourceTime=1787046990)

    s_simple_blue = find(szones, color="blue", formationType="simple")
    s_advanced_blue = find(szones, color="blue", formationType="advanced")
    s_type3 = find(szones, color="blue", formationType="type3")
    s_simple_red = find(szones, color="red", formationType="simple")
    e_blue = find(ezones, family="blue", number=1)
    e_red = find(ezones, family="red", number=1)
    stopall = b["stopAlls"][0]
    stopall_parent = b["stopAlls"][1]
    audit = b["orderAudit"][0]
    audit_multi = b["orderAudit"][4]

    reaction_a_rows = [
        role("GREEN قبل از First Red", reaction_a["boxTopSourceTime"], "بالاترین High در run سبز قبل از First Red؛ منبع BoxTop=4425.54."),
        role("First Red", reaction_a["firstTime"], "همین کندل قرمز بعد از GREEN است؛ Low آن BoxBottom=4424.155 می‌شود."),
        role("Break", reaction_a["breakTime"], "High این کندل به‌صورت strict از BoxTop بالاتر رفته است."),
    ]
    reaction_b_rows = [
        role("منبع BoxTop", reaction_b["boxTopSourceTime"], "running high قبل از First Red؛ BoxTop=4425.695."),
        role("First Red", reaction_b["firstTime"], "کندل قرمز آغاز candidate عادی Mode B."),
        role("منبع BoxBottom", reaction_b["boxBottomSourceTime"], "پایین‌ترین Low تا قبل از تأیید؛ BoxBottom=4424.365."),
        role("Break", reaction_b["breakTime"], "اولین کندل با High > BoxTop ثابت‌شده."),
    ]
    reset_rows = [
        role("First مالک Reaction", reset_owner["firstTime"], "شروع Reactionای که BoxBottom آن بعداً شکسته می‌شود."),
        role("منبع BoxBottom", reset_owner["boxBottomSourceTime"], f"سطح شکسته‌شونده برابر {reset['brokenLevel']} است."),
        role("کندل اصلی Reset", reset["time"], "main candle حاوی شکست کف."),
        role("لحظه دقیق Reset", reset["secondTime"], "اولین کندل یک‌ثانیه‌ای با Low < brokenLevel؛ تساوی کافی نیست."),
    ]
    blue_rows = [
        role("First Reaction مالک Scale", scale_blue["startTime"], "شروع Reaction شماره 2."),
        role("منبع extremeِ Scale", scale_blue["sourceTime"], f"Low decisive={scale_blue['sourceExtreme']}؛ قیمت خط={scale_blue['linePrice']}."),
        role("انتهای رسم Scale در payload", scale_blue["endTime"], "endTime فقط انتهای هندسی خط است؛ stop یا confirmation دقیق نیست."),
        role("تأیید دقیق/تشکیل Scale", 1787016583, "اولین second با High > BoxTop=4425.695؛ Blue از این لحظه موجود است."),
        role("strict stop واقعی Scale", 1787016607, "اولین second پس از confirmation با Low < 4424.365؛ این زمان در payload Blue نیست."),
        role("منبع Reset Blue", reset_blue["sourceTime"], f"کندل Reset؛ extreme={reset_blue['sourceExtreme']} و قیمت خط={reset_blue['linePrice']}."),
        role("تشکیل دقیق Reset Blue", 1787017086, "اولین second با Low < brokenLevel=4421.85."),
        role("strict stop واقعی Reset Blue", 1787017132, "اولین second از main candle بعدی با Low < 4421.735؛ این زمان در payload Blue نیست."),
    ]

    def a_rows(a: dict) -> list[tuple[str, int | None, str]]:
        return [
            role("Blue اول", a["blue1SourceTime"], f"Blue #{a['blue1Ordinal']}؛ stop سطح {a['blue1StopLevel']}."),
            role("Blue دوم", a["blue2SourceTime"], f"Blue #{a['blue2Ordinal']}؛ stop سطح {a['blue2StopLevel']}."),
            role("منبع continuation", a["continuationSourceTime"], f"continuation level={a['continuationLevel']}."),
            role("Trigger اصلی", a["triggerTime"], "main candle حاوی trigger."),
            role("Trigger دقیق", a["triggerEventTime"], "اولین strict low لازم برای فعال شدن pair."),
            role("First تأییدکننده", a["reactionFirstTime"], "First کندل Reaction صعودی تأییدکننده A."),
            role("Break تأییدکننده", a["reactionBreakTime"], "تأیید Reaction مالک A."),
            role("کندل منبع A", a["sourceTime"], f"کمترین Low بازه trigger تا break؛ قیمت A={a['price']}."),
        ]

    def s_rows(s: dict) -> list[tuple[str, int | None, str]]:
        rows = [
            role("کندل منبع A", s["aSourceTime"], f"A والد با قیمت {s['aPrice']}."),
            role("stop اصلی A", s["aStopTime"], "main candle حاوی stop والد."),
            role("stop دقیق A", s["aStopEventTime"], "اولین Low < A.price."),
        ]
        if s.get("orderFirstTime") is not None:
            rows += [
                role("First Order نزولی", s["orderFirstTime"], "اولین کندل قرمز Reaction نزولیِ واجد شرایط بعد از stop A."),
                role("Break Order", s["orderBreakTime"], "main candle تأیید Order نزولی."),
                role("تأیید دقیق Order", s["orderConfirmationTime"], "لحظه دقیق شکست geometry Order."),
                role("منبع stop Order", s["orderStopSourceTime"], f"سطح stop Order={s['orderStopLevel']}."),
            ]
        rows += [
            role("کندل منبع S", s["sourceTime"], f"محل رسم S با قیمت {s['price']}."),
            role("لحظه دقیق تصمیم", s["decisionEventTime"], "برنده race میان candidateCross و orderStop."),
        ]
        return rows

    def e_rows(e: dict) -> list[tuple[str, int | None, str]]:
        causes = " + ".join(e.get("orderCauses", []))
        return [
            role("کندل منبع والد", e["parentSourceTime"], f"والد {e['parentType']} با قیمت {e['parentPrice']}."),
            role("stop دقیق والد", e["parentStopEventTime"], "اولین Low < parent.price."),
            role("Reset leg", e.get("orderResetLegResetTime"), f"علت Order: {causes or 'parent-stop'}."),
            role("First Order", e["orderFirstTime"], "First کندل Order نزولی منتخب."),
            role("Break Order", e["orderBreakTime"], "main candle تأیید Order."),
            role("تأیید دقیق Order", e["orderConfirmationTime"], "زمان دقیق confirmation Order."),
            role("منبع stop Order", e["orderStopSourceTime"], f"stopLevel={e['orderStopLevel']}."),
            role("کندل منبع E", e["sourceTime"], f"کمترین Low از parent-stop تا order-stop؛ قیمت E={e['price']}."),
            role("تصمیم دقیق E", e["decisionEventTime"], "دیرترِ parent-stop و order-stop."),
        ]

    stopall_rows = [
        role("کندل منبع StopAll1", stopall["sourceTime"], f"E برنده به StopAll1 تبدیل شده؛ قیمت={stopall['price']}."),
        role("Gate دقیق", stopall["gateEventTime"], f"stop عضو قبلیِ گروه {stopall['stoppedBehaviorKey']}."),
        role("Reset leg Order", stopall.get("orderResetLegResetTime"), "آغاز علت reset-leg Order برنده."),
        role("First Order", stopall["orderFirstTime"], "First کندل Order نزولی حمل‌شده از E."),
        role("Break Order", stopall["orderBreakTime"], "main candle تأیید Order."),
        role("تأیید دقیق Order", stopall["orderConfirmationTime"], "زمان دقیق confirmation Order."),
        role("تصمیم دقیق StopAll", stopall["decisionEventTime"], "زمان تصمیم E جاری و تشکیل StopAll1."),
        role("stop دقیق خود StopAll", stopall["stopEventTime"], "اولین Low < StopAll.price؛ مجوز ادامه sequence."),
    ]
    stopall_parent_rows = [
        role("StopAll منبع", stopall_parent["sourceTime"], f"StopAll{stopall_parent['number']} با قیمت {stopall_parent['price']}."),
        role("stop والد / علت Order", stopall_parent["orderParentStopCauseTime"], "causeEvidence.parentStoppedAt برای Order_A."),
        role("First Order", stopall_parent["orderFirstTime"], "startedAt آبجکت Order."),
        role("تأیید دقیق Order", stopall_parent["orderConfirmationTime"], "confirmedAt آبجکت Order."),
        role("تصمیم StopAll", stopall_parent["decisionEventTime"], "decisionAt نهایی."),
        role("stop خود StopAll", stopall_parent.get("stopEventTime"), "stop بعدی این StopAll، اگر موجود باشد."),
    ]
    audit_multi_rows = [
        role("First Order چندعلتی", audit_multi["firstTime"], "یک geometry فیزیکی با چند cause."),
        role("منبع BoxTop", audit_multi["boxTopSourceTime"], f"BoxTop={audit_multi['boxTop']}."),
        role("منبع BoxBottom", audit_multi["boxBottomSourceTime"], f"BoxBottom={audit_multi['boxBottom']}."),
        role("Break", audit_multi["breakTime"], "confirmedAt اصلی در Order Audit."),
        role("منبع stop", audit_multi["stopSourceTime"], f"stopLevel={audit_multi['stopLevel']}."),
        role("stop دقیق", audit_multi["stopHitEventTime"], "hitAt strict."),
    ]
    for cause in audit_multi["causes"]:
        if cause.get("eventTime") is not None:
            audit_multi_rows.append(role(f"cause: {cause['kind']} / parent stop", cause["eventTime"], "زمان evidence همین cause."))
        if cause.get("resetTime") is not None:
            audit_multi_rows.append(role("cause: reset-leg / Reset", cause["resetTime"], "resetAt علت Order_B."))
        if cause.get("boundaryBreakTime") is not None:
            audit_multi_rows.append(role("cause: reset-leg / boundary", cause["boundaryBreakTime"], "boundaryBrokenAt علت Order_B."))

    all_groups = [reaction_a_rows, reaction_b_rows, reset_rows, blue_rows, a_rows(a1), a_rows(a2), a_rows(a3), a_rows(a4)]
    all_groups += [s_rows(x) for x in (s_simple_blue, s_advanced_blue, s_type3, s_simple_red)]
    all_groups += [e_rows(e_blue), e_rows(e_red), stopall_rows, stopall_parent_rows, audit_multi_rows]
    all_groups.append([
        role("First Order Audit", audit["firstTime"], "First ثبت‌شده در ledger."),
        role("منبع BoxTop", audit["boxTopSourceTime"], f"BoxTop={audit['boxTop']}."),
        role("منبع BoxBottom", audit["boxBottomSourceTime"], f"BoxBottom={audit['boxBottom']}."),
        role("Break Order Audit", audit["breakTime"], "Break اصلی Order."),
        role("منبع stop", audit["stopSourceTime"], f"stopLevel={audit['stopLevel']}."),
        role("stop دقیق", audit["stopHitEventTime"], "اولین High > stopLevel."),
    ])
    times = {timestamp for group in all_groups for _, timestamp, _ in group if timestamp is not None}
    info_examples = [
        ("reactions", reaction_a), ("reactions", reaction_b), ("resets", reset),
        ("blueLines", scale_blue), ("blueLines", reset_blue),
        *(("aZones", item) for item in (a1, a2, a3, a4)),
        *(("sZones", item) for item in (s_simple_blue, s_advanced_blue, s_type3, s_simple_red)),
        ("eZones", e_blue), ("eZones", e_red), ("stopAlls", stopall), ("stopAlls", stopall_parent),
        ("orderAudit", audit), ("orderAudit", audit_multi),
    ]
    for group, row in info_examples:
        times |= projection_times(info_projection(group, row, b))
    # دو آبجکت داخلی Mode A که عمداً در /info و payload عمومی serialize نمی‌شوند.
    times |= {1787015700, 1787016330, envelope["actualFrom"], envelope["actualTo"]}
    candles = candle_inventory(raw, times)
    missing = sorted(times - candles.keys())
    if missing:
        raise RuntimeError(f"کندل‌های نمونه در XAUUSD پیدا نشدند: {missing}")

    counts = {key: len(b[key]) for key in ("reactions", "resets", "blueLines", "aZones", "sZones", "eZones", "stopAlls", "orderAudit")}
    s_counts: dict[tuple[str, str], int] = {}
    for s in szones:
        key = (s["formationType"], s["color"])
        s_counts[key] = s_counts.get(key, 0) + 1

    source_info = {"source": {"timezone": "Asia/Tehran", "timeframeSeconds": envelope["timeframe"],
                              "range": {"from": {"time": envelope["actualFrom"]}, "to": {"time": envelope["actualTo"]}}}}

    sections = f"""
    <section id="basics">
      <h2>۱. اول این چهار نکته را بدانید</h2>
      <div class="rules">
        {card("رنگ کندل", "اگر Open از Close بیشتر باشد کندل قرمز است؛ در غیر این صورت سبز است. پس doji هم سبز حساب می‌شود.", "Open > Close → RED | Open ≤ Close → GREEN")}
        {card("شکست همیشه strict است", "در روند صعودی، عبور بالا فقط با High بزرگ‌تر و stop پایین فقط با Low کوچک‌تر رخ می‌دهد. مساوی بودن هیچ رویدادی نیست.", "High > level | Low < level")}
        {card("دو نوع زمان", "زمان ۳۰ثانیه‌ای محل کندل اصلی است؛ زمان یک‌ثانیه‌ای ترتیب دقیق break، reset و stop را مشخص می‌کند.")}
        {card("First یعنی چه؟", "First نام یک کندل مشخص است، نه کل الگو. در Reaction صعودی معمولاً همان اولین کندل قرمز معتبر بعد از یک کندل یا run سبز است.")}
      </div>
      <div class="facts"><span>reactions → Reaction</span><span>resets → Reset</span><span>blueLines → Blue Line</span><span>aStructures → A</span><span>sStructures → S</span><span>eStructures → E</span><span>stopAllEvents → StopAll</span><span>orderAudit → Order audit</span></div>
      {generic_panel("object منبع و بازه در بالای /info", source_info, candles)}
      <aside class="audit warning"><b>Collection اختیاری:</b> کد /info از <code>orderReactions</code> نیز پشتیبانی می‌کند و واژه‌های <code>consumed</code> و <code>stopHitAt</code> را برای آن می‌سازد؛ اما این collection در payload کامل XAUUSD حاضر وجود ندارد. ساختن مثال جعلی برای آن عمداً انجام نشده است.</aside>
      {example("مثال دقیق First Red در اولین Reaction XAUUSD", "First Red دقیقاً کندل 2026-08-18 04:57:30 است؛ نه کندل سبز قبل و نه کندل Break بعدی.", reaction_a_rows, candles, open_=True, extra=info_panel("reactions", reaction_a, b, candles))}
    </section>

    <section id="reaction">
      <h2>۲. Reaction صعودی و Reset</h2>
      <div class="rules">
        {card("Reaction Mode A", "اولین Reaction چرخه است. یک First Red معتبر بعد از GREEN می‌گیرد؛ BoxBottom از Low آن و BoxTop از بیشترین High زمینه ساخته می‌شود. اولین High > BoxTop آن را تأیید می‌کند.")}
        {card("Reaction Mode B", "بعد از Reaction اول اجرا می‌شود. با یک RED، BoxTop ثابت می‌شود؛ Lowهای بعدی BoxBottom را پایین می‌آورند و اولین High > BoxTop تأیید است.")}
        {card("Reset", "بعد از تأیید Reaction، اولین Low < BoxBottom همان Reaction یک Reset است. candidate جاری پاک می‌شود و جست‌وجوی Reaction مستقیم بعدی از پسِ reset ادامه می‌یابد.")}
      </div>
      <aside class="audit warning"><b>نقطه کور /info:</b> آبجکت‌های داخلی <code>anchor</code> و <code>legBoundary</code> در serialization عمومی Reaction حذف می‌شوند. در همین نمونه، anchor کندل قرمز <span dir="ltr">2026-08-18 04:55:30</span> با Low=4420.44 است؛ legBoundary نیز کندل آغاز leg در <span dir="ltr">04:45:00</span> با Low=4428.805 است. بنابراین صحت شرط First Red از خود /info قابل ممیزی کامل نیست.</aside>
      {example("نمونه Mode A", "BoxTop=4425.54 و BoxBottom=4424.155؛ جدول دقیقاً کندل سازنده هر آبجکت را نشان می‌دهد.", reaction_a_rows + [role("anchor داخلی", 1787016330, "آخرین RED مرجع؛ FirstRed.Low باید >= 4420.44 باشد. در /info نمایش داده نمی‌شود."), role("legBoundary داخلی", 1787015700, "Low آغاز leg=4428.805؛ fallback شرط Mode A. در /info نمایش داده نمی‌شود.")], candles, extra=info_panel("reactions", reaction_a, b, candles))}
      {example("نمونه Mode B", "First Red این نمونه کندل 04:58:30 است؛ BoxBottom بعداً با کندل 04:59:00 پایین‌تر می‌رود.", reaction_b_rows, candles, extra=info_panel("reactions", reaction_b, b, candles))}
      {example("نمونه Reset با زمان دقیق", f"Reset متعلق به Reaction با First در {local_time(reset_owner['firstTime'])} است و سطح {reset['brokenLevel']} را می‌شکند.", reset_rows, candles, extra=info_panel("resets", reset, b, candles))}
    </section>

    <section id="blue">
      <h2>۳. Blue Line صعودی</h2>
      <div class="rules">
        {card("Scale Blue", "strike وقتی زیاد می‌شود که Low از fib یا extreme قبلی پایین‌تر برود و سپس یک GREEN آن را تأیید کند. اگر strike از Reaction قبلی بیشتر شود، Scale Blue ساخته می‌شود.", "fib = BoxTop − 0.618 × (BoxTop − reference)")}
        {card("قیمت Scale", "روی کندل decisive ساخته می‌شود و خط فقط یک timeframe قبل و بعد از منبع امتداد دارد.", "price = Low + (High − Low) / 3")}
        {card("Reset Blue", "از کندل Reset و brokenLevel همان Reset ساخته می‌شود. spacing lock باید اجازه دهد؛ A فقط Blueهای calculation-valid را مصرف می‌کند.", "price = Low + (High − Low) / 5")}
        {card("stop Blue", "برای روند صعودی، اولین کندل یک‌ثانیه‌ای با Low < sourceExtreme است. برای Reset Blue جست‌وجو از main candle بعدی شروع می‌شود.")}
      </div>
      <aside class="audit danger"><b>ایراد ممیزی قطعی در /info:</b> فیلد <code>stop.time</code> برای Blue از <code>endTime</code> گرفته می‌شود؛ اما <code>endTime</code> انتهای رسم خط است، نه زمان strict stop. در مثال Scale، /info زمان 04:59:30 را نشان می‌دهد ولی stop واقعی raw در 05:00:07 رخ داده است. برای Reset Blue نیز stop واقعی 05:08:52 است. payload Blue زمان stop واقعی را serialize نمی‌کند.</aside>
      {example("نمونه Scale Blue و Reset Blue", f"Scale: strike {scale_blue['previousStrikeCount']}→{scale_blue['strikeCount']} و fib={scale_blue['fibonacciLevel']}. Reset Blue نیز در همان جدول آمده است.", blue_rows, candles, open_=True, extra=info_panel("blueLines", scale_blue, b, candles) + info_panel("blueLines", reset_blue, b, candles))}
    </section>

    <section id="a-zone">
      <h2>۴. انواع A صعودی و stop آن‌ها</h2>
      <p class="lead">دو Blue به‌تنهایی A نمی‌سازند. pair معتبر باید trigger شود و سپس یک Reaction صعودی آن را تأیید کند. قیمت A کمترین Low از کندل trigger تا Break Reaction تأییدکننده است.</p>
      <div class="rules">
        {card("مسیر ۱ — inherited Reaction", "یک Reaction بین تشکیل دو Blue، continuation low را می‌سازد؛ بعد از Blue دوم، Low < آن سطح trigger است.")}
        {card("مسیر ۲ — Blue قبلی قبلاً stop شده", "Low از stop دقیق Blue اول تا پیش از Blue دوم freeze می‌شود؛ شکست strict آن پس از Blue دوم trigger را می‌سازد.")}
        {card("مسیر ۳ — هر دو Blue زنده بوده‌اند", "stop اول continuation می‌شود؛ بعد از stop دوم باید Low از extreme stop اول پایین‌تر برود.")}
        {card("مسیر خاص double-stop", "یک Blue نامعتبر میانی می‌تواند trigger خاص بسازد؛ فقط اگر از extreme Blue معتبر قبلی عبور کند و Reaction بعدی آن را تأیید کند.")}
        {card("stop A", "بعد از confirmation دقیق A، اولین Low < A.price است. اگر A بعدی قبل از این stop تأیید شود، A قبلی اجازه ساخت S ندارد.")}
      </div>
      <aside class="audit warning"><b>نام‌گذاری قابل سوءبرداشت:</b> در مسیر inherited، فیلدهای <code>blueLines.first.stoppedAt</code> و <code>second.stoppedAt</code> داخل /info لزوماً stop فیزیکی اولیه خود Blue نیستند؛ detector A ممکن است زمان مؤثر continuation/trigger را در آن‌ها قرار دهد. برای ممیزی باید هم stop واقعی Blue و هم semantics مسیر A جدا دیده شوند.</aside>
      {example("A مسیر ۱ — نمونه پذیرفته‌شده 05:15:30", "این همان A ثبت‌شده در فایل بازبینی XAUUSD است.", a_rows(a1), candles, open_=True, extra=info_panel("aZones", a1, b, candles))}
      {example("A مسیر ۲ — Blue قبلی پیش از Blue فعلی stop شده", "طبقه‌بندی از chronology و شاخه واقعی detector انجام شده است.", a_rows(a2), candles, extra=info_panel("aZones", a2, b, candles))}
      {example("A مسیر ۳ — هر دو Blue هنگام تشکیل pair زنده‌اند", "stopهای لازم و trigger دقیق در جدول جدا شده‌اند.", a_rows(a3), candles, extra=info_panel("aZones", a3, b, candles))}
      {example("A خاص — invalid middle Blue / double-stop", "این مسیر، A عادی تکراری را تولید نمی‌کند و کنترل حذف تکرار دارد.", a_rows(a4), candles, extra=info_panel("aZones", a4, b, candles))}
    </section>

    <section id="order-s">
      <h2>۵. Order و انواع S صعودی</h2>
      <p class="lead">در روند صعودی، Order جهت نزولی دارد. First Order دقیقاً کندل قرمز شروع Reaction نزولی منتخب است؛ Break کندل دیگری است که آن Order را تأیید می‌کند.</p>
      <div class="rules">
        {card("S ساده", "اگر Reaction داخلی advanced پیدا نشود، کمترین Low از Break Order تا Break Reaction صعودی بعدی candidate می‌شود.")}
        {card("S پیشرفته", "یک Reaction صعودی باید از نظر زمان و قیمت کاملاً داخل Box همان Order نزولی باشد؛ boundary از BoxBottom Order می‌آید.")}
        {card("Race رنگ S", "پس از confirmation Order: اگر Low < candidatePrice زودتر باشد S آبی است؛ اگر High > orderStopLevel زودتر باشد S قرمز است. وقوع هم‌زمان S نمی‌سازد.")}
        {card("S نوع ۳", "میان stop A و confirmation نخستین Order بعدی، leg یک Reset نزولی بررسی می‌شود. خروجی همیشه آبی است و عمداً هیچ Order ساختگی در payload ندارد.")}
      </div>
      <div class="facts"><span>S ساده آبی: {s_counts.get(('simple','blue'),0)}</span><span>S پیشرفته آبی: {s_counts.get(('advanced','blue'),0)}</span><span>S نوع۳ آبی: {s_counts.get(('type3','blue'),0)}</span><span>S ساده قرمز: {s_counts.get(('simple','red'),0)}</span></div>
      {example("S ساده آبی — First Order دقیقاً 05:17:30", "در این نمونه candidateCross پیش از stop Order برنده شده و evidence آبی وجود دارد.", s_rows(s_simple_blue), candles, open_=True, extra=info_panel("sZones", s_simple_blue, b, candles))}
      {example("S پیشرفته آبی", "candidate از Reaction صعودیِ داخل Box Order آمده است.", s_rows(s_advanced_blue), candles, extra=info_panel("sZones", s_advanced_blue, b, candles))}
      {example("S نوع ۳ آبی — بدون Order metadata", "خالی بودن ردیف‌های Order خطا نیست؛ قرارداد Type 3 همین است.", s_rows(s_type3), candles, extra=info_panel("sZones", s_type3, b, candles))}
      {example("S ساده قرمز", "در این نمونه High > orderStopLevel زودتر از candidateCross رخ داده است.", s_rows(s_simple_red), candles, extra=info_panel("sZones", s_simple_red, b, candles))}
    </section>

    <section id="e-zone">
      <h2>۶. E صعودی</h2>
      <div class="rules">
        {card("تشکیل E", "پس از stop شدن S یا E قبلی، یک Order نزولی معتبر پیدا می‌شود. قیمت E کمترین Low از main candle والد-stop تا main candle order-stop است.")}
        {card("Order_A و Order_B", "Order_A مستقیماً بعد از stop والد می‌آید. Order_B از leg یک Reset نزولی و شکست boundary آن می‌آید. یک geometry مشترک با چند علت فقط یک Order است.")}
        {card("زنجیره و رنگ", "با stop شدن E1 همین روند برای E2 و بعدی تکرار می‌شود. family از والد می‌آید و red بر blue اولویت دارد.")}
      </div>
      <aside class="audit danger"><b>ایراد ممیزی قطعی در /info:</b> برای پیدا کردن <code>E.stop</code> فقط <code>family + number</code> با StopAll تطبیق داده می‌شود و <code>sourceTime/sourceIndex</code> در identity نیست. در همین E1 قرمزِ 2026-08-18 13:56:00، /info اشتباهاً gate مربوط به StopAll روز 2026-08-27 را به‌عنوان stop در 17:18:29 متصل می‌کند.</aside>
      {example("E1 آبی — نمونه 06:13:30", "علت Order این نمونه reset-leg است؛ First، Break و stop level آن جداگانه دیده می‌شوند.", e_rows(e_blue), candles, open_=True, extra=info_panel("eZones", e_blue, b, candles))}
      {example("E1 قرمز", "این نمونه از خانواده قرمز است و Order آن با parent-stop ساخته شده است.", e_rows(e_red), candles, extra=info_panel("eZones", e_red, b, candles))}
    </section>

    <section id="stopall">
      <h2>۷. StopAll صعودی</h2>
      <div class="rules">
        {card("StopAll1", "S/Eهای فعال در گروه‌های هم‌خانواده شمرده می‌شوند. اگر گروه حداقل دو عضو داشته باشد و عضو قبلی تا تصمیم E جاری stop شده باشد، E جاری به StopAll1 تبدیل می‌شود.")}
        {card("StopAll بعدی", "اگر StopAll فعال پیش از تصمیم E بعدی strict-stop شود، E جدید شماره max+1 می‌گیرد. source و Order همان E برنده حفظ می‌شوند.")}
        {card("اولویت", "ترتیب غالب: E قرمز، S قرمز، E آبی، S آبی. StopAll رنگ مستقل ندارد و family زیرین E را فقط برای audit نگه می‌دارد.")}
      </div>
      <aside class="audit warning"><b>کاهش اطلاعات در /info:</b> زیرآبجکت <code>sourceE</code> فقط <code>family</code> را نشان می‌دهد و <code>underlyingENumber</code> موجود در payload را حذف می‌کند؛ برای ردگیری lineage کامل باید payload خام نیز دیده شود.</aside>
      {example("اولین StopAll واقعی XAUUSD", f"این StopAll از توقف گروه {stopall['stoppedBehaviorKey']} با count={stopall['stoppedBehaviorCount']} ساخته شده است.", stopall_rows, candles, open_=True, extra=info_panel("stopAlls", stopall, b, candles))}
      {example("StopAll با Order_A و parentStoppedAt", "این مثال دوم لازم است تا زیرآبجکت causeEvidence.parentStoppedAt که در نمونه اول خالی بود، با کندل واقعی دیده شود.", stopall_parent_rows, candles, extra=info_panel("stopAlls", stopall_parent, b, candles))}
    </section>

    <section id="audit">
      <h2>۸. Order Audit و خلاصه خروجی واقعی XAUUSD</h2>
      <p class="lead">Order Audit خودِ label معاملاتی نیست؛ دفتر provenance است تا معلوم باشد هر Order از کدام First، Box، Break، stop و علت مالکیتی آمده است.</p>
      <aside class="audit warning"><b>کاهش اطلاعات در /info:</b> projection مربوط به Order Audit، با اینکه payload دارای BoxTop، BoxBottom، sourceهای آن‌ها و reactionNumber است، این فیلدها را نمایش نمی‌دهد. بنابراین هندسه Order از خود /info قابل بازسازی کامل نیست.</aside>
      {example("اولین Order ثبت‌شده در Audit", "علت این Order، stop والد A در 05:17:08 است. First Red آن دقیقاً کندل 05:17:30 است.", all_groups[-1], candles, open_=True, extra=info_panel("orderAudit", audit, b, candles))}
      {example("Order Audit چندعلتی", "یک Order فیزیکی هم‌زمان causeهای parent-stop و reset-leg دارد؛ تمام واژه‌های آرایه causes با نمونه واقعی دیده می‌شوند.", audit_multi_rows, candles, extra=info_panel("orderAudit", audit_multi, b, candles))}
      <div class="counts">
        <div><b>{counts['reactions']}</b><span>Reaction</span></div><div><b>{counts['resets']}</b><span>Reset</span></div>
        <div><b>{counts['blueLines']}</b><span>Blue Line</span></div><div><b>{counts['aZones']}</b><span>A</span></div>
        <div><b>{counts['sZones']}</b><span>S</span></div><div><b>{counts['eZones']}</b><span>E</span></div>
        <div><b>{counts['stopAlls']}</b><span>StopAll</span></div><div><b>{counts['orderAudit']}</b><span>Order Audit</span></div>
      </div>
      <aside class="note">OHLC تمام جدول‌ها مستقیماً از فایل خام ۱ثانیه‌ای XAUUSD جمع‌آوری شده است. قیمت و metadata آبجکت‌ها از payload کامل runtime گرفته شده‌اند. زمان‌ها همگی Asia/Tehran هستند.</aside>
    </section>
    """

    document = f"""<!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="راهنمای ساده الگوریتم صعودی با مثال‌های دقیق XAUUSD"><title>راهنمای ساده الگوریتم صعودی با مثال XAUUSD</title>
<style>
:root{{--bg:#f4f7fb;--paper:#fff;--ink:#172235;--muted:#5d6a7d;--line:#dce4ef;--brand:#2459d3;--soft:#edf3ff;--green:#087f69;--red:#c33846;--shadow:0 10px 30px #1d355714}}
html[data-theme=dark]{{--bg:#0d1420;--paper:#151f2e;--ink:#edf3fc;--muted:#aebbd0;--line:#2d3b50;--brand:#83a8ff;--soft:#1c3158;--green:#55d0b7;--red:#ff818d;--shadow:0 10px 30px #0005;color-scheme:dark}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth;scroll-padding-top:118px}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.9 Tahoma,"Segoe UI",sans-serif}}button{{font:inherit}}a{{color:inherit}}:focus-visible{{outline:3px solid var(--brand);outline-offset:3px}}.skip{{position:fixed;z-index:99;top:8px;right:8px;padding:8px 12px;border-radius:8px;background:var(--ink);color:var(--paper);transform:translateY(-160%)}}.skip:focus{{transform:none}}
.top{{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--paper) 94%,transparent);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}}.bar{{max-width:1180px;margin:auto;min-height:60px;padding:8px 18px;display:flex;align-items:center;gap:10px}}.brand{{font-weight:900;margin-left:auto}}.btn{{min-height:44px;border:1px solid var(--line);border-radius:10px;padding:6px 13px;background:var(--paper);color:var(--ink);cursor:pointer}}
.nav{{max-width:1180px;margin:auto;padding:0 18px 8px;display:flex;gap:7px;overflow:auto;scrollbar-width:thin}}.nav a{{white-space:nowrap;text-decoration:none;padding:5px 11px;border-radius:999px;background:var(--soft);color:var(--brand);font-size:.86rem}}
main{{width:min(1100px,calc(100% - 24px));margin:24px auto 60px}}.hero,section{{background:var(--paper);border:1px solid var(--line);border-radius:18px;box-shadow:var(--shadow)}}.hero{{padding:clamp(24px,5vw,46px);margin-bottom:18px;background:linear-gradient(145deg,var(--paper),var(--soft))}}.kicker{{color:var(--brand);font-weight:800}}h1{{font-size:clamp(1.65rem,4.5vw,2.8rem);line-height:1.45;margin:.25em 0}}.hero p,.lead{{color:var(--muted);max-width:78ch}}.flow{{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:20px;direction:ltr}}.flow span{{padding:5px 10px;border:1px solid var(--line);border-radius:8px;background:var(--paper);font-weight:700;font-size:.85rem}}.flow b{{color:var(--brand)}}
section{{padding:clamp(20px,4vw,38px);margin:18px 0}}h2{{margin:0 0 18px;font-size:clamp(1.35rem,3vw,1.8rem);line-height:1.5;text-wrap:balance}}h3{{margin:0 0 6px;font-size:1rem}}p{{margin:7px 0}}.rules{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:11px;margin:14px 0 20px}}.rule{{padding:15px;border:1px solid var(--line);border-radius:12px;background:color-mix(in srgb,var(--paper) 75%,var(--soft))}}.rule p{{color:var(--muted);font-size:.92rem;line-height:1.8}}.formula{{margin-top:9px;padding:7px 9px;border-radius:7px;background:var(--paper);border:1px dashed var(--line);color:var(--brand);font:700 .83rem/1.6 Consolas,monospace;text-align:left;overflow:auto}}
details{{margin:11px 0;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--paper)}}summary{{min-height:48px;padding:11px 15px;display:flex;align-items:center;cursor:pointer;font-weight:800;background:var(--soft);color:var(--brand)}}details>p{{padding:8px 15px;color:var(--muted)}}.info-object{{margin:12px;border-style:dashed}}.info-object>summary{{background:color-mix(in srgb,var(--paper) 70%,var(--soft));font-size:.9rem}}.table-wrap{{overflow:auto;max-width:100%}}table{{width:100%;min-width:940px;border-collapse:collapse;text-align:right;font-size:.84rem}}th,td{{padding:9px 10px;border-top:1px solid var(--line);vertical-align:top}}thead th{{position:sticky;top:0;background:var(--paper);color:var(--muted)}}tbody th{{color:var(--brand);min-width:150px}}td:last-child{{min-width:260px}}.field-table{{min-width:880px}}.field-table .object-row{{background:var(--soft)}}.field-table .object-row th{{font-weight:900}}code{{direction:ltr;unicode-bidi:embed;padding:1px 5px;border:1px solid var(--line);border-radius:5px;background:var(--paper);color:var(--red);font-family:Consolas,monospace}}.candle{{display:inline-block;padding:1px 7px;border-radius:999px;font-weight:800}}.candle.green{{color:var(--green);background:color-mix(in srgb,var(--green) 12%,transparent)}}.candle.red{{color:var(--red);background:color-mix(in srgb,var(--red) 12%,transparent)}}
.facts{{display:flex;flex-wrap:wrap;gap:7px;margin:12px 0}}.facts span{{padding:4px 10px;border-radius:999px;background:var(--soft);font-size:.85rem}}.audit{{margin:14px 0;padding:14px 16px;border-radius:10px;line-height:1.8}}.audit.warning{{border-right:4px solid #c27a09;background:#fff8e8;color:#67420a}}.audit.danger{{border-right:4px solid var(--red);background:color-mix(in srgb,var(--red) 8%,var(--paper));color:var(--ink)}}html[data-theme=dark] .audit.warning{{background:#352811;color:#f5d796}}.counts{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0}}.counts div{{padding:14px;text-align:center;border:1px solid var(--line);border-radius:12px;background:var(--soft)}}.counts b{{display:block;color:var(--brand);font-size:1.35rem}}.counts span{{font-size:.82rem;color:var(--muted)}}.note{{padding:14px 16px;border-right:4px solid var(--brand);border-radius:10px;background:var(--soft);color:var(--muted)}}footer{{text-align:center;color:var(--muted);padding:28px 12px}}
@media(max-width:640px){{body{{font-size:15px}}.bar{{flex-wrap:wrap;padding:8px 12px}}.brand{{width:100%;margin:0}}.btn{{flex:1}}.nav{{padding-inline:12px}}main{{width:min(100% - 14px,1100px);margin-top:10px}}.hero,section{{border-radius:13px}}.rules{{grid-template-columns:1fr}}.counts{{grid-template-columns:repeat(2,1fr)}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}@media print{{.top{{display:none}}body{{background:#fff;color:#111}}main{{width:100%;margin:0}}.hero,section{{box-shadow:none;border:0;break-inside:auto}}details{{break-inside:avoid}}details:not([open])>*:not(summary){{display:block}}}}
</style></head><body><a class="skip" href="#content">رفتن به متن اصلی</a>
<header class="top"><div class="bar"><div class="brand">راهنمای صعودی XAUUSD</div><button class="btn" id="theme" type="button">حالت تیره</button><button class="btn" onclick="print()" type="button">چاپ / PDF</button></div><nav class="nav" aria-label="فهرست"><a href="#basics">مفاهیم پایه</a><a href="#reaction">Reaction و Reset</a><a href="#blue">Blue</a><a href="#a-zone">A</a><a href="#order-s">Order و S</a><a href="#e-zone">E</a><a href="#stopall">StopAll</a><a href="#audit">Audit</a></nav></header>
<main id="content"><header class="hero"><div class="kicker">نسخه ساده، مثال‌محور و قابل ممیزی</div><h1>الگوریتم صعودی، کوتاه و روشن</h1><p>هر قاعده در چند خط توضیح داده شده و هر آبجکت با کندل دقیق خودش از فایل XAUUSD آمده است. زمان‌ها تهران‌اند؛ جدول‌ها را افقی حرکت دهید تا تمام OHLC دیده شود.</p><div class="facts"><span>۲۴۰ از ۲۴۰ مسیر schema صعودی /info</span><span>۱۱۴ زمان کندلی بررسی‌شده</span><span>۶ نقطه کور/ایراد ممیزی مستند</span></div><div class="flow"><span>Reaction</span><b>→</b><span>Blue</span><b>→</b><span>A</span><b>→</b><span>S</span><b>→</b><span>E</span><b>→</b><span>StopAll</span></div></header>{sections}<footer>منبع: کد اجرایی TradingBot، Vault و اجرای کامل XAUUSD در بازه 2026-08-18 تا 2026-09-05.</footer></main>
<script>const root=document.documentElement,btn=document.getElementById('theme');const saved=localStorage.getItem('bullish-simple-theme');if(saved==='dark'){{root.dataset.theme='dark';btn.textContent='حالت روشن'}}btn.addEventListener('click',()=>{{const dark=root.dataset.theme!=='dark';root.dataset.theme=dark?'dark':'light';btn.textContent=dark?'حالت روشن':'حالت تیره';localStorage.setItem('bullish-simple-theme',dark?'dark':'light')}});</script>
</body></html>"""
    OUTPUT.write_text(document, encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes, {len(times)} checked candle times)")


if __name__ == "__main__":
    build()
