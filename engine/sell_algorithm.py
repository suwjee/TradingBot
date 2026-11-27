"""Bearish Sell position entry point."""

from .pipeline.position_rules import calculate_positions


def calculate_sell_positions(group, close_at, first_crossing, *, timeframe, closed_through, source_event_at=None):
    return calculate_positions(group, close_at, first_crossing, direction="bearish",
                               timeframe=timeframe, closed_through=closed_through,
                               source_event_at=source_event_at)
