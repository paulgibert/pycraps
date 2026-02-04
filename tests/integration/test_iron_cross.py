"""
Tests an iron cross strategy.
"""
from craps.state import TableState, TableConfig
from craps.bets import Field, PlaceBets
from craps.phase import TablePhase
from craps.dice import Roll

def test_iron_cross():
    # 0. Setup
    config = TableConfig(
        table_min=15,
        table_max=10000,
        odds_max=3,
        prop_min=5
    )
    init_phase = TablePhase(point=None)
    bets = {
        'place_bets': PlaceBets(init_phase),
        'field': Field(init_phase)
    }
    bankroll = 200.0
    state = TableState(config, bets, bankroll)

    # 1. Wait for a point
    state.step(Roll((5,2)))
    state.step(Roll((2,2))) # Point on 4

    # 2. Lay down the cross (field, place 5, place 6, place 8)
    state.set_bet_stake('field', 15.0)
    state.set_bet_stake('place_bets', 15.0, target=5)
    state.set_bet_stake('place_bets', 18.0, target=6)
    state.set_bet_stake('place_bets', 18.0, target=8)
    assert state.get_bankroll_size() == 134.0

    # 3. Wait it out, replacing the field every turn
    state.step(Roll((3,3))) # Hit
    state.set_bet_stake('field', 15.0)
    state.step(Roll((4,4))) # Hit
    state.set_bet_stake('field', 15.0)
    state.step(Roll((6,6))) # Hit
    state.set_bet_stake('field', 15.0)
    state.step(Roll((2,1))) # Hit
    state.set_bet_stake('field', 15.0)
    state.step(Roll((2,2))) # Hit and point!
    assert state.get_bankroll_size() == 236.0

    # 4. Wait for a new point
    state.step(Roll((2,1)))
    state.step(Roll((3,4)))
    state.step(Roll((5,3))) # Point on 8
    assert state.get_bankroll_size() == 236.0

    # 5. Resume the cross
    state.set_bet_stake('field', 15.0)
    state.step(Roll((3,3))) # Hit
    state.set_bet_stake('field', 15.0)
    state.step(Roll((3,4))) # Seven out! Time to leave...
    assert state.get_bankroll_size() == 227.0
