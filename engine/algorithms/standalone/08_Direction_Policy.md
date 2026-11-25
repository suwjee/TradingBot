# DP — Direction policy

```text
POLICY(direction):
  IF direction = bullish: RETURN (low, high, RED, GREEN)
  IF direction = bearish: RETURN (high, low, GREEN, RED)
  OTHERWISE: RAISE invalid direction
STRICT_CROSS(direction, x, level):
  RETURN x < level IF bullish ELSE x > level
BETTER_EXTREME(direction,x,current): RETURN STRICT_CROSS(direction,x,current)
CHOOSE_EXTREME(direction,a,b): RETURN min(a,b) IF bullish ELSE max(a,b)
CONFIRMATION_CROSS(direction,x,level):
  RETURN x > level IF bullish ELSE x < level
```
Opposite direction swaps bullish/bearish. Equal values do not cross. This policy does not own chronology, numbering or lifecycle. The isolated strict/confirm/better-extreme primitives were compared in 450 cases.
