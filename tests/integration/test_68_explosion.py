"""
Tests a 6-8 explosion strategy.
"""
from craps.state import TableState, TableConfig
from craps.bets import PlaceBets
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
    bets = {'place_bets': PlaceBets(TablePhase(point=None))}
    bankroll = 200.0
    state = TableState(config, bets, bankroll)

    # 1. Wait to establish a point
    state.step(Roll((3,4))) # Natural winner
    state.step(Roll((1,1))) # Craps
    state.step(Roll((2,3))) # Point on 5

    # 2. Place $18 each on the 6 and 8. Wait for 1 hit
    state.set_bet_stake('place_bets', 18.0, target=6)
    state.set_bet_stake('place_bets', 18.0, target=8)
    assert state.get_bankroll().get_size() == 164.0

    state.step(Roll((6,6)))
    state.step(Roll((1,1)))
    state.step(Roll((5,4)))
    state.step(Roll((3,3))) # Hit!
    assert state.get_bankroll().get_size() == 185.0

    # 3. Push both the 6 and 8 up to $30 each
    state.set_bet_stake('place_bets', 30.0, target=6)
    state.set_bet_stake('place_bets', 30.0, target=8)
    assert state.get_bankroll().get_size() == 161.0

    state.step(Roll((2,1)))
    state.step(Roll((5,5)))
    state.step(Roll((2,3))) # Point is hit. Bets go off
    state.step(Roll((3,4))) # Seven should not affect bets
    assert state.get_bet_stake('place_bets', target=6) == 30.0
    assert state.get_bet_stake('place_bets', target=8) == 30.0
    state.step(Roll((1,3))) # Point on 4
    state.step(Roll((1,4)))
    state.step(Roll((4,4))) # Hit!
    assert state.get_bankroll().get_size() == 196.0

    # 4. Place 96 across and push winnings until 3 hits total
    state.set_bet_stake('place_bets', 15.0, target=4)
    state.set_bet_stake('place_bets', 15.0, target=5)
    state.set_bet_stake('place_bets', 18.0, target=6)
    state.set_bet_stake('place_bets', 18.0, target=8)
    state.set_bet_stake('place_bets', 15.0, target=9)
    state.set_bet_stake('place_bets', 15.0, target=10)
    assert state.get_bankroll().get_size() == 160.0

    state.step(Roll((1,1)))
    state.step(Roll((4,6))) # Hit #1! Push the 10
    state.set_bet_stake('place_bets', 40.0, target=10.0)
    assert state.get_bankroll().get_size() == 162.0
    state.step(Roll((5,5))) # Hit #2! Push the 10 again
    state.set_bet_stake('place_bets', 110.0, target=10)
    assert state.get_bankroll().get_size() == 164.0
    state.step(Roll((2,3))) # Hit #3! Bring it all down and run!

    state.set_bet_stake('place_bets', 0.0, target=4)
    state.set_bet_stake('place_bets', 0.0, target=5)
    state.set_bet_stake('place_bets', 0.0, target=6)
    state.set_bet_stake('place_bets', 0.0, target=8)
    state.set_bet_stake('place_bets', 0.0, target=9)
    state.set_bet_stake('place_bets', 0.0, target=10)
    assert state.get_bankroll().get_size() == 376.0
