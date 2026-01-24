from dataclasses import dataclass, replace, fields
from typing import Iterator

@dataclass(frozen=True)
class ActionBets:
    """
    Represents bet amounts controlled by the player in an Action.
    These are the bets the player can directly set/modify.
    """
    # Pass line bets
    pass_line: int = 0
    pass_odds: int = 0

    # Come bets
    come_bet: int = 0  # Amount to place as traveling come bet
    come_odds_4: int = 0
    come_odds_5: int = 0
    come_odds_6: int = 0
    come_odds_8: int = 0
    come_odds_9: int = 0
    come_odds_10: int = 0

    # Place bets
    place_4: int = 0
    place_5: int = 0
    place_6: int = 0
    place_8: int = 0
    place_9: int = 0
    place_10: int = 0

    # Buy bets
    buy_4: int = 0
    buy_5: int = 0
    buy_6: int = 0
    buy_8: int = 0
    buy_9: int = 0
    buy_10: int = 0

    # Field bet
    field: int = 0

    # Future: Don't pass/come
    # dont_pass: int = 0
    # dont_pass_odds: int = 0


@dataclass(frozen=True)
class StateBets:
    """
    Represents the full bet state on the table, including engine-managed bets.
    This includes both player-controlled and engine-established bets.
    """
    # Pass line bets
    pass_line: int = 0
    pass_odds: int = 0

    # Come bets (engine-managed)
    come_traveling: int = 0  # Traveling come bet
    come_4: int = 0          # Established come bets
    come_5: int = 0
    come_6: int = 0
    come_8: int = 0
    come_9: int = 0
    come_10: int = 0

    # Come odds
    come_odds_4: int = 0
    come_odds_5: int = 0
    come_odds_6: int = 0
    come_odds_8: int = 0
    come_odds_9: int = 0
    come_odds_10: int = 0

    # Place bets
    place_4: int = 0
    place_5: int = 0
    place_6: int = 0
    place_8: int = 0
    place_9: int = 0
    place_10: int = 0

    # Buy bets
    buy_4: int = 0
    buy_5: int = 0
    buy_6: int = 0
    buy_8: int = 0
    buy_9: int = 0
    buy_10: int = 0

    # Field bet
    field: int = 0

    # Future: Don't pass/come
    # dont_pass: int = 0
    # dont_pass_odds: int = 0

    # Future: Lay, hardways, props
    # lay: Dict[int, int]
    # hardways: Dict[int, int]      # 4,6,8,10
    # props: Dict[str, int]

def set_bets(bets: StateBets, slot: str, stake: int) -> StateBets:
    """
    Returns a new StateBets object with the specified bet slot set to the given stake.
    Auto-scales with StateBets dataclass fields.
    """
    if not hasattr(bets, slot):
        raise KeyError(f"Unknown bet slot: {slot}")
    return replace(bets, **{slot: stake})

def iter_bets(bets: StateBets) -> Iterator[tuple[str, int]]:
    """
    Iterates over bet slots and their stakes.
    Auto-scales with StateBets dataclass fields.
    """
    for field in fields(StateBets):
        yield (field.name, getattr(bets, field.name))
