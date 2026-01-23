from craps.bets.pass_line import PassLine
from craps.bets.pass_odds import PassOdds

BET_REGISTRY = {
    'pass_line': PassLine(),
    'pass_odds': PassOdds(),
}