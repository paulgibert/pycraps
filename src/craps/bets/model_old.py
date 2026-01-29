from dataclasses import dataclass, fields, replace
from typing import Iterator

from craps.bets.protocol import Bet
from craps.bets.pass_line import PassLine
from craps.bets.pass_odds import PassOdds
from craps.bets.come_bet import ComeTraveling, Come4, Come5, Come6, Come8, Come9, Come10
from craps.bets.come_odds import ComeOdds4, ComeOdds5, ComeOdds6, ComeOdds8, ComeOdds9, ComeOdds10
from craps.bets.place_bets import Place4, Place5, Place6, Place8, Place9, Place10
from craps.bets.buy_bets import Buy4, Buy5, Buy6, Buy8, Buy9, Buy10
from craps.bets.field_bet import FieldBet
from craps.bets.hardways import Hard4, Hard6, Hard8, Hard10
from craps.bets.props import AnySeven, AnyCraps, AceDeuce, Aces, Boxcars, YoLeven, Horn, CAndE

@dataclass(frozen=True)
class ActionBets:
    """
    Player-controlled bets. Each field is a Bet instance containing its stake.
    """
    # Pass line bets
    pass_line: PassLine = PassLine()
    pass_odds: PassOdds = PassOdds()

    # Come bet (player places this, engine moves it)
    come_bet: ComeTraveling = ComeTraveling()

    # Come odds
    come_odds_4: ComeOdds4 = ComeOdds4()
    come_odds_5: ComeOdds5 = ComeOdds5()
    come_odds_6: ComeOdds6 = ComeOdds6()
    come_odds_8: ComeOdds8 = ComeOdds8()
    come_odds_9: ComeOdds9 = ComeOdds9()
    come_odds_10: ComeOdds10 = ComeOdds10()

    # Place bets
    place_4: Place4 = Place4()
    place_5: Place5 = Place5()
    place_6: Place6 = Place6()
    place_8: Place8 = Place8()
    place_9: Place9 = Place9()
    place_10: Place10 = Place10()

    # Buy bets
    buy_4: Buy4 = Buy4()
    buy_5: Buy5 = Buy5()
    buy_6: Buy6 = Buy6()
    buy_8: Buy8 = Buy8()
    buy_9: Buy9 = Buy9()
    buy_10: Buy10 = Buy10()

    # Field bet
    field_bet: FieldBet = FieldBet()

    # Hardway bets
    hard_4: Hard4 = Hard4()
    hard_6: Hard6 = Hard6()
    hard_8: Hard8 = Hard8()
    hard_10: Hard10 = Hard10()

    # One-roll proposition bets
    any_seven: AnySeven = AnySeven()
    any_craps: AnyCraps = AnyCraps()
    ace_deuce: AceDeuce = AceDeuce()
    aces: Aces = Aces()
    boxcars: Boxcars = Boxcars()
    yo_leven: YoLeven = YoLeven()

    # Combination proposition bets
    horn: Horn = Horn()
    c_and_e: CAndE = CAndE()


@dataclass(frozen=True)
class StateBets(ActionBets):
    """
    Full table state. Extends ActionBets with engine-managed bets.
    """
    # Come bets (engine-managed: traveling -> established)
    come_traveling: ComeTraveling = ComeTraveling()
    come_4: Come4 = Come4()
    come_5: Come5 = Come5()
    come_6: Come6 = Come6()
    come_8: Come8 = Come8()
    come_9: Come9 = Come9()
    come_10: Come10 = Come10()

def iter_bets(bets: ActionBets) -> Iterator[Bet]:
    """
    Iterate over all state bets, yielding (slot_name, bet_instance).
    """
    for f in fields(bets):
        yield (f.name, getattr(bets, f.name))

# TODO: Should this be separated into state and action versions?
def get_bet(bets: ActionBets, slot: str) -> Bet:
    """Get a bet by slot name."""
    return getattr(bets, slot)

# TODO: Should this be separated into state and action versions?
def set_stake(bets: ActionBets, slot: str, stake: int) -> ActionBets:
    """
    Return new StateBets with the specified bet's stake updated.
    """
    current_bet = getattr(bets, slot)
    new_bet = replace(current_bet, stake=stake)
    return replace(bets, **{slot: new_bet})
