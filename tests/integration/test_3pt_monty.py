"""
Tests a 3-point monty strategy.
"""
from craps.state import TableState, TableConfig
from craps.bets import PassLine, ComeBets
from craps.phase import TablePhase
from craps.dice import Roll

def test_6_8_explosion():
    # 0. Setup
    config = TableConfig(
        table_min=15,
        table_max=10000,
        odds_max=3,
        prop_min=5
    )
    init_phase = TablePhase(point=None)
    bets = {
        'pass_line': PassLine(init_phase),
        'come_bets': ComeBets(init_phase)
    }
    bankroll = 200.0
    state = TableState(config, bets, bankroll)

    # 1. Put in a passline and get a point
    state.set_bet_stake('pass_line', 15.0)
    state.step(Roll((1,1))) # Craps :(
    state.set_bet_stake('pass_line', 15.0)
    state.step(Roll((2,2))) # Point on 4
    assert state.get_bankroll().get_size() == 170.0

    # 2. Work in come bets for a max of 3 numbers covered total. Odds on everything
    state.set_bet_odds('pass_line', 30.0) # Set pass line odds
    state.set_bet_stake('come_bets', 15.0) # Work in a come bet
    state.step(Roll((4,5))) # Come bet goes to 9
    state.set_bet_odds('come_bets', 30.0, target=9) # Odds on the 9
    state.set_bet_stake('come_bets', 15.0) # Work in another come bet
    state.step(Roll((6,6)))
    state.set_bet_stake('come_bets', 15.0) # Craps :( Replace the come bet
    state.step(Roll((5,5))) # Come bet goes to 10
    state.set_bet_odds('come_bets', 30.0, target=10) # Odds on the 10
    assert state.get_bankroll().get_size() == 35.0

    # 3. Wait it out, replacing come bets as they hit
    state.step(Roll((4,5))) # Hit the come 9!
    state.set_bet_stake('come_bets', 15.0) # Another come bet
    assert state.get_bankroll().get_size() == 125.0
    state.step(Roll((1,3))) # Hit the point! Come goes to 4.
    assert state.get_bankroll().get_size() == 245.0

    # 4. 2 big hits... Ride it out and then time to leave!
    state.step(Roll((5,2))) # Seven cleas our remaining come bets
    assert state.get_bankroll().get_size() == 245.0
