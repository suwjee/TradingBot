# Lifecycle and Primary

Source-only Phase 07 checkpoint. These clauses describe pinned main, not proposed algorithm changes.

## CH29

StopAll strict stop starts inclusive, scans physical lower length; null if no hit. E dominance same family requires larger number, red dominates blue.

[Source engine/pipeline/lifecycle_engine.py:170–194](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L170-L194)

## CH30

StopAll S/E iteration sorts (source time, kind string, source index); E before S on same source time, not physical intrarow order.

[Source engine/pipeline/lifecycle_engine.py:350–359](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L350-L359)

## CH31

Armed stop normally strictly before boundary; E donor exception requires stop <= donor decision, either inside source main bucket with matching mapped index and strict directional price, or exact matching parent kind/index/time/price/stop event.

[Source engine/pipeline/lifecycle_engine.py:368–416](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L368-L416)

## CH32

StopAll final strict-stop starts at decision or max(decision, optional after); absent crossing retains null stop fields.

[Source engine/pipeline/lifecycle_engine.py:525–531](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/lifecycle_engine.py#L525-L531)

## CH33

Reversal uses confirmed physical number-three points; first strictly later crossing wins by (event time, source index, cycle ID or empty); bullish target PH3 upward, bearish target PL3 downward. PH3 optional cross is chosen by truthiness; PL3 always uses native P12. Only non-null hits enter transition selection.

[Source engine/pipeline/PL_PH_detector.py:101–125](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L101-L125)

## CH34

PH gate confirmation >= event irrespective of First; PL requires First >= gate main and confirmation > event. Primary strict cross excludes equal timestamp via upper bound; extreme main endpoints inclusive, earliest equal. Exact PH is the special case; all other kinds short-circuit First before strict confirmation. RAW exclusive right=len(seconds), position zero valid, clamp main mapping. Extreme selects complete inclusive main window and re-reads normalized value.

[Source engine/pipeline/PL_PH_detector.py:211–245](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L211-L245)

## CH35

Primary seek: no hits waits, equal-time up/down ambiguous, else earliest sets phase. Cursor >= reversal cutoff waits before commitment.

[Source engine/pipeline/PL_PH_detector.py:518–553](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L518-L553)

## CH36

Primary Orders stop strictly after confirmation; rank (stop event, negative First, Break). Earlier cancellation takes precedence; opposing extreme in the selected cancellation row may make the race ambiguous. Post-PL3 branch is evaluated before ordinary equal cancellation/winner ambiguity: it accepts only stops strictly before cancellation (all eligible if cancellation absent), no PL4. Ordinary equal cancellation/winner is ambiguous. Source extreme gate main through stop main inclusive, committed cursor advances to stop event.

[Source engine/pipeline/PL_PH_detector.py:554–621](https://github.com/suwjee/TradingBot/blob/466eb875070f02cd0dbfb105033422bbe2fd8c70/engine/pipeline/PL_PH_detector.py#L554-L621)
