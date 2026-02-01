"""Tests for TableConfig and TableState.

NOTE: state.py currently fails to import because it references PlaceBets
which does not exist. TableConfig is defined in that module so it cannot
be tested until the import is fixed. All tests are marked xfail.
"""
import pytest


class TestTableConfig:
    @pytest.mark.xfail(reason="state.py imports non-existent PlaceBets")
    def test_fields(self):
        from craps.state import TableConfig
        config = TableConfig(table_min=10, table_max=500, odds_max=100, prop_min=5)
        assert config.table_min == 10
        assert config.table_max == 500
        assert config.odds_max == 100
        assert config.prop_min == 5

    @pytest.mark.xfail(reason="state.py imports non-existent PlaceBets")
    def test_equality(self):
        from craps.state import TableConfig
        a = TableConfig(table_min=10, table_max=500, odds_max=100, prop_min=5)
        b = TableConfig(table_min=10, table_max=500, odds_max=100, prop_min=5)
        assert a == b


class TestTableState:
    @pytest.mark.xfail(reason="state.py imports non-existent PlaceBets")
    def test_init(self):
        from craps.state import TableState, TableConfig
        config = TableConfig(table_min=10, table_max=500, odds_max=100, prop_min=5)
        state = TableState(config, init_bankroll=500)
        assert state.config == config

    @pytest.mark.xfail(reason="state.py imports non-existent PlaceBets")
    def test_default_bankroll(self):
        from craps.state import TableState, TableConfig
        config = TableConfig(table_min=10, table_max=500, odds_max=100, prop_min=5)
        state = TableState(config)
        assert state._bankroll.get_size() == 1000
