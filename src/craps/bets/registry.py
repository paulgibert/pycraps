from craps.bets.pass_line import PassLine
from craps.bets.pass_odds import PassOdds
from craps.bets.come_bet import ComeTraveling, Come4, Come5, Come6, Come8, Come9, Come10

# Register the same instance under both come_bet (ActionBets) and come_traveling (StateBets)
come_bet_type = ComeTraveling()

BET_REGISTRY = {
    'pass_line': PassLine(),
    'pass_odds': PassOdds(),
    'come_bet': come_bet_type,       # For ActionBets validation
    'come_traveling': come_bet_type,  # For StateBets validation (same instance)
    'come_4': Come4(),
    'come_5': Come5(),
    'come_6': Come6(),
    'come_8': Come8(),
    'come_9': Come9(),
    'come_10': Come10(),
}