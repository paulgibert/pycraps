from craps.bets.pass_line import PassLine
from craps.bets.pass_odds import PassOdds
from craps.bets.come_bet import ComeTraveling, Come4, Come5, Come6, Come8, Come9, Come10
from craps.bets.come_odds import ComeOdds
from craps.bets.place_bets import PlaceBet
from craps.bets.buy_bets import BuyBet
from craps.bets.field_bet import FieldBet

# Register the same instance under both come_bet (ActionBets) and come_traveling (StateBets)
come_bet_type = ComeTraveling()

BET_REGISTRY = {
    # Pass line
    'pass_line': PassLine(),
    'pass_odds': PassOdds(),

    # Come bets
    'come_bet': come_bet_type,       # For ActionBets validation
    'come_traveling': come_bet_type,  # For StateBets validation (same instance)
    'come_4': Come4(),
    'come_5': Come5(),
    'come_6': Come6(),
    'come_8': Come8(),
    'come_9': Come9(),
    'come_10': Come10(),

    # Come odds
    'come_odds_4': ComeOdds(4),
    'come_odds_5': ComeOdds(5),
    'come_odds_6': ComeOdds(6),
    'come_odds_8': ComeOdds(8),
    'come_odds_9': ComeOdds(9),
    'come_odds_10': ComeOdds(10),

    # Place bets
    'place_4': PlaceBet(4),
    'place_5': PlaceBet(5),
    'place_6': PlaceBet(6),
    'place_8': PlaceBet(8),
    'place_9': PlaceBet(9),
    'place_10': PlaceBet(10),

    # Buy bets
    'buy_4': BuyBet(4),
    'buy_5': BuyBet(5),
    'buy_6': BuyBet(6),
    'buy_8': BuyBet(8),
    'buy_9': BuyBet(9),
    'buy_10': BuyBet(10),

    # Field bet
    'field': FieldBet(),
}