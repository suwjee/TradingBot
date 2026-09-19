export const BEARISH_MIRROR_FAMILIES = Object.freeze(["reaction", "reset", "blue_line", "a"]);

const PRICE_OPERATORS = Object.freeze({ "<": ">", ">": "<", "<=": ">=", ">=": "<=" });

function escapeRegExp(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function swapPairs(value, pairs, { words = false } = {}) {
  let text = String(value ?? "");
  const placeholders = [];
  pairs.forEach(([left, right], index) => {
    const leftToken = `\uE000${index}L\uE001`;
    const rightToken = `\uE000${index}R\uE001`;
    const leftPattern = words ? new RegExp(`\\b${escapeRegExp(left)}\\b`, "g") : new RegExp(escapeRegExp(left), "g");
    const rightPattern = words ? new RegExp(`\\b${escapeRegExp(right)}\\b`, "g") : new RegExp(escapeRegExp(right), "g");
    text = text.replace(leftPattern, leftToken).replace(rightPattern, rightToken);
    placeholders.push([leftToken, rightToken, left, right]);
  });
  placeholders.forEach(([leftToken, rightToken, left, right]) => {
    const swapToken = `${leftToken}X`;
    text = text.replaceAll(leftToken, swapToken).replaceAll(rightToken, left).replaceAll(swapToken, right);
  });
  return text;
}

function protect(text, pattern, protectedValues) {
  return text.replace(pattern, (value) => {
    const token = `\uE100${protectedValues.length}\uE101`;
    protectedValues.push([token, value]);
    return token;
  });
}

function protectSwapPairs(text, pairs, protectedValues) {
  let result = text;
  pairs.forEach(([left, right], index) => {
    const leftToken = `\uE100${protectedValues.length + index}L\uE101`;
    const rightToken = `\uE100${protectedValues.length + index}R\uE101`;
    result = result.replaceAll(left, leftToken).replaceAll(right, rightToken);
    protectedValues.push([leftToken, right], [rightToken, left]);
  });
  return result;
}

function restore(text, protectedValues) {
  return protectedValues.reduce((result, [token, value]) => result.replaceAll(token, value), text);
}

function mirrorPriceOperators(value) {
  let text = String(value ?? "");
  const directionalAtom = String.raw`(?:[A-Za-z_][A-Za-z0-9_]*\.)*(?:low|high|Low|High|price|level|Price|Level|extreme|Extreme|boundary|Boundary|floor|Floor|ceiling|Ceiling|box_top|box_bottom|BoxTop|BoxBottom|stop_level|line_price|fibonacci_level)`;
  const comparison = new RegExp(`(${directionalAtom})\\s*(<=|>=|<|>)`, "g");
  text = text.replace(comparison, (full, left, operator) => `${left} ${PRICE_OPERATORS[operator]}`);
  return text.replace(/\bvalue\s*(<=|>=|<|>)\s*level/g, (full, operator) => `value ${PRICE_OPERATORS[operator]} level`);
}

function mirrorPriceExtremaFunctions(value) {
  const directionalWord = String.raw`(?:low|high|Low|High|price|Price|level|Level|extreme|Extreme|box_top|box_bottom|BoxTop|BoxBottom|peak|Peak|bottom|Bottom|top|Top|floor|Floor|ceiling|Ceiling)`;
  return String(value ?? "").replace(new RegExp(`\\b(max|min)\\(([^()\\n]*\\b${directionalWord}\\b[^()\\n]*)\\)`, "g"), (full, name, args) => `${name === "max" ? "min" : "max"}(${args})`);
}

function mirrorDirectionalLexemes(value, { swapMarketRoles = false } = {}) {
  let text = String(value ?? "");
  const protectedValues = [];

  const formulaPairs = [
    ["top - Decimal('0.618') * (top - reference)", "bottom + Decimal('0.618') * (reference - bottom)"],
    ["top - 0.618 * (top-reference)", "bottom + 0.618 * (reference-bottom)"],
    ["low + (high-low)/3", "high - (high-low)/3"],
    ["low + (high - low) / 3", "high - (high - low) / 3"],
    ["source.low + (source.high - source.low) / Decimal(3)", "source.high - (source.high - source.low) / Decimal(3)"],
    ["source.low + (source.high - source.low) / 3", "source.high - (source.high - source.low) / 3"],
    ["low + (high-low)/5", "high - (high-low)/5"],
    ["low + (high - low) / 5", "high - (high - low) / 5"],
    ["source.low + (source.high - source.low) / Decimal(5)", "source.high - (source.high - source.low) / Decimal(5)"],
    ["source.low + (source.high - source.low) / 5", "source.high - (source.high - source.low) / 5"],
  ];
  text = protectSwapPairs(text, formulaPairs, protectedValues);

  // Market classification and doji semantics are invariant in both directions.
  text = protect(text, /\b(?:Modules|indicator)[^\s;]+/g, protectedValues);
  text = protect(text, /\bOpen\s*<=\s*Close\b[^.\n]*\.?/gi, protectedValues);
  text = protect(text, /\bopen\s*<=\s*close\b[^.\n]*\.?/g, protectedValues);
  text = protect(text, /GREEN\/RED classification|RED\/GREEN classification/g, protectedValues);
  text = protect(text, /سبز\/قرمز|قرمز\/سبز/g, protectedValues);

  text = mirrorPriceExtremaFunctions(text);
  text = mirrorPriceOperators(text);

  // Specific role/geometry names come before their shorter components.
  text = swapPairs(text, [
    ["find_bullish_reactions", "find_bearish_reactions"],
    ["build_bullish_blue_lines", "build_bearish_blue_lines"],
    ["build_bullish_a_zones", "build_bearish_a_zones"],
    ["first_red_after_green", "first_green_after_red"],
    ["post_breakout", "post_breakdown"],
    ["confirmed_reset_before_breakout", "confirmed_reset_before_breakdown"],
    ["breakout_analysis", "breakdown_analysis"],
    ["after_breakout", "after_breakdown"],
    ["running_peak", "running_bottom"],
    ["running_peak_source", "running_bottom_source"],
    ["previous_reaction_floor", "previous_reaction_ceiling"],
    ["frozen_owner_floor", "frozen_owner_ceiling"],
    ["frozen_leg_floor", "frozen_leg_ceiling"],
    ["local_floor", "local_ceiling"],
    ["anchor_red", "anchor_green"],
    ["green_high", "red_low"],
    ["green_source", "red_source"],
    ["contiguous_green_run_before", "contiguous_red_run_before"],
    ["highest_in_contiguous_green_run_before", "lowest_in_contiguous_red_run_before"],
    ["lower_second_low_happens_before_high", "lower_second_high_happens_before_low"],
    ["refine_bottom_using_seconds_before_exact_break", "refine_top_using_seconds_before_exact_break"],
    ["first_later_second_low_below", "first_later_second_high_above"],
    ["candidate_from_whole_red_break_candle", "candidate_from_whole_green_break_candle"],
    ["top_source", "bottom_source"],
    ["bottom_start", "top_start"],
    ["owner_floor", "owner_ceiling"],
    ["leg_floor", "leg_ceiling"],
    ["max_with_earliest_source", "min_with_earliest_source"],
    ["max_high", "min_low"],
    ["maximum_high", "minimum_low"],
    ["BoxTop", "BoxBottom"],
    ["box_top", "box_bottom"],
    ["boxTop", "boxBottom"],
    ["FirstRed", "FirstGreen"],
    ["first_red", "first_green"],
    ["upper break", "lower breakdown"],
    ["strict upper crossing", "strict lower crossing"],
    ["upper crossing", "lower crossing"],
    ["upper boundary", "lower boundary"],
    ["upper bound", "lower bound"],
    ["may not be lower than", "may not be higher than"],
    ["not lower than", "not higher than"],
    ["lower than", "higher than"],
    ["above", "below"],
    ["Above", "Below"],
    ["lower lows", "higher highs"],
    ["lower Low", "higher High"],
    ["bullish", "bearish"],
    ["Bullish", "Bearish"],
    ["BULLISH", "BEARISH"],
    ["breakout", "breakdown"],
    ["Breakout", "Breakdown"],
    ["minimum", "maximum"],
    ["Minimum", "Maximum"],
    ["highest", "lowest"],
    ["Highest", "Lowest"],
    ["greater of", "lesser of"],
    ["Greater of", "Lesser of"],
    ["top", "bottom"],
    ["Top", "Bottom"],
    ["floor", "ceiling"],
    ["Floor", "Ceiling"],
    ["low", "high"],
    ["Low", "High"],
    ["LOW", "HIGH"],
  ], { words: true });

  if (swapMarketRoles) {
    text = swapPairs(text, [["GREEN", "RED"], ["Green", "Red"], ["green", "red"], ["سبز", "قرمز"]], { words: true });
  }

  text = swapPairs(text, [
    ["روند صعودی", "روند نزولی"],
    ["صعودی", "نزولی"],
    ["صعود", "نزول"],
    ["پایین‌تر از", "بالاتر از"],
    ["پایین‌تر", "بالاتر"],
    ["سقف", "کف"],
    ["کمینه", "بیشینه"],
    ["حداقل", "حداکثر"],
  ]);

  return restore(text, protectedValues);
}

export function isBearishMirrorFamily(familyId) {
  return BEARISH_MIRROR_FAMILIES.includes(String(familyId));
}

export function mirrorDirectionalText(value, familyId) {
  if (!isBearishMirrorFamily(familyId)) return String(value ?? "");
  return mirrorDirectionalLexemes(value, { swapMarketRoles: familyId === "reaction" || familyId === "blue_line" || familyId === "a" });
}
