---
title: Bullish trend icon clarity verification
document_role: evidence
lifecycle: historical
owner: chart
created_at: 2026-11-01T16:51:41+03:30
last_modified_at: 2026-11-01T16:59:08+03:30
---

# Bullish icon clarity

The user requested a slightly larger, clearer bullish icon. The selected display size is 28x28 CSS pixels, increased from 20x20. The normalized vector scales with a stronger screen stroke and a filled arrowhead. Green color, actual candle50 (start1) anchoring and 100px High-to-bottom clearance are preserved.

Only the existing Chart renderer, its geometry expectations and the presentation paragraph in both accepted References changed. Engine calculations and event metadata are unchanged.

- PASS: the existing geometry tests first failed at20px and passed at28px.
- PASS: full Chart suite,255 tests.
- PASS: production build; Vite's size warning remains.
- PASS: both accepted References reconstruct the unchanged production Engine Source exactly.
- PASS: actual Chrome/Playwright rendering on desktop/laptop, no page errors. The measured icon box is28x28 and its bottom is100px above the target High.
- NOT RUN: a new Engine market replay; no Engine Source or trading rule changed in this task.

The existing full-RAW output from the preceding PH3 change was used only as rendering input. Its earlier market acceptance is historical evidence, not a fresh market PASS for this visual edit.

Browser plugin was unavailable, so regular Playwright was used. Browser-only test exports are not part of production.

[Desktop preview](chart-desktop.png) | [Icon detail](icon-detail.png) | [Browser measurement](browser-qa.json)


Live checkout: the original port5173 service was restarted only after confirming no active child work. The served renderer contains the28px icon and filled head; calculation Source fingerprint remains unchanged, confirming no Engine calculation change.
