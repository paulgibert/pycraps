import pytest
from craps.bankroll import Bankroll
from craps.exceptions import InsufficientFunds


class TestInit:
    def test_initial_size(self):
        assert Bankroll(1000).get_size() == 1000

    def test_zero_initial(self):
        assert Bankroll(0).get_size() == 0

    def test_negative_initial_errors(self):
        with pytest.raises(ValueError):
            Bankroll(-1)


class TestDeposit:
    def test_deposit_increases_size(self):
        b = Bankroll(100)
        b.deposit(50)
        assert b.get_size() == 150

    def test_deposit_zero(self):
        b = Bankroll(100)
        b.deposit(0)
        assert b.get_size() == 100

    def test_deposit_negative_errors(self):
        b = Bankroll(100)
        with pytest.raises(ValueError):
            b.deposit(-1)


class TestWithdraw:
    def test_withdraw_decreases_size(self):
        b = Bankroll(100)
        b.withdraw(40)
        assert b.get_size() == 60

    def test_withdraw_zero(self):
        b = Bankroll(100)
        b.withdraw(0)
        assert b.get_size() == 100

    def test_withdraw_exact_balance(self):
        b = Bankroll(100)
        b.withdraw(100)
        assert b.get_size() == 0

    def test_withdraw_exceeds_balance_errors(self):
        b = Bankroll(100)
        with pytest.raises(InsufficientFunds):
            b.withdraw(101)

    def test_withdraw_negative_errors(self):
        b = Bankroll(100)
        with pytest.raises(ValueError):
            b.withdraw(-1)


class TestUpdate:
    def test_positive_deposits(self):
        b = Bankroll(100)
        b.update(50)
        assert b.get_size() == 150

    def test_negative_withdraws(self):
        b = Bankroll(100)
        b.update(-40)
        assert b.get_size() == 60

    def test_zero_no_change(self):
        b = Bankroll(100)
        b.update(0)
        assert b.get_size() == 100

    def test_negative_exceeding_balance_errors(self):
        b = Bankroll(100)
        with pytest.raises(InsufficientFunds):
            b.update(-101)
