"""
REPL-style CLI for testing the craps game engine.
"""
import random
from dataclasses import fields, replace

from craps.state import TableState
from craps.action import Action
from craps.bets.model import ActionBets, StateBets, iter_bets
from craps.bets.registry import BET_REGISTRY
from craps.dice import Roll
from craps.env import step
from craps.rules.legality import validate_action
from craps.exceptions import IllegalAction

# Default table configuration
DEFAULT_BANKROLL = 1000
DEFAULT_TABLE_MIN = 5
DEFAULT_TABLE_MAX = 500
DEFAULT_MAX_ODDS = 3
DEFAULT_PROP_MIN = 1


def create_initial_state(bankroll: int = DEFAULT_BANKROLL) -> TableState:
    """Create an initial table state."""
    return TableState(
        bankroll=bankroll,
        roll_count=0,
        point=None,
        bets=StateBets(),
        last_roll=None,
        is_terminal=False,
        table_min=DEFAULT_TABLE_MIN,
        table_max=DEFAULT_TABLE_MAX,
        max_odds=DEFAULT_MAX_ODDS,
        prop_min=DEFAULT_PROP_MIN,
    )


def display_table(state: TableState) -> None:
    """Display the current table state."""
    point_display = state.point if state.point else "OFF"
    print(f"\nCRAPS TABLE | Bankroll: ${state.bankroll} | Point: {point_display} | Roll #{state.roll_count}")
    print("\u2501" * 52)

    if state.last_roll:
        d1, d2 = state.last_roll
        print(f"Last Roll: {d1} + {d2} = {state.last_roll.total()}")

    active_bets = [(name, stake) for name, stake in iter_bets(state.bets) if stake > 0]
    if active_bets:
        print("Active Bets:")
        for name, stake in active_bets:
            print(f"  {name}: ${stake}")
    else:
        print("Active Bets: (none)")
    print()


def display_pending_bets(pending: ActionBets) -> None:
    """Display pending bets that will be placed on the next roll."""
    pending_list = []
    for field in fields(ActionBets):
        stake = getattr(pending, field.name)
        if stake > 0:
            pending_list.append((field.name, stake))

    if pending_list:
        print("Pending bets for next roll:")
        for name, stake in pending_list:
            print(f"  {name}: ${stake}")
        print()


def build_action_bets(state: TableState, pending: ActionBets) -> ActionBets:
    """
    Build ActionBets by merging current state bets with pending changes.
    For each field in ActionBets, use the pending value if set, otherwise
    carry over from the current state.
    """
    # Map state fields back to action fields
    state_to_action = {'come_traveling': 'come_bet'}

    updates = {}
    for field in fields(ActionBets):
        action_field = field.name
        # Find the corresponding state field
        state_field = action_field
        if action_field == 'come_bet':
            state_field = 'come_traveling'

        pending_value = getattr(pending, action_field)
        state_value = getattr(state.bets, state_field)

        # Use pending value if it's set (non-zero or explicitly changed), otherwise keep state value
        # For simplicity, pending tracks explicit changes - we'll use pending directly
        updates[action_field] = pending_value if pending_value > 0 else state_value

    return ActionBets(**updates)


def cmd_bet(state: TableState, pending: ActionBets, args: list[str]) -> ActionBets:
    """Handle the bet command."""
    if len(args) < 2:
        print("Usage: bet <name> <amount>")
        print("Example: bet pass_line 10")
        return pending

    bet_name = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        print(f"Error: Invalid amount '{args[1]}'")
        return pending

    if amount < 0:
        print("Error: Bet amount cannot be negative")
        return pending

    # Check if this is a valid bet name in ActionBets
    if not hasattr(pending, bet_name):
        print(f"Error: Unknown bet '{bet_name}'")
        print("Use 'info bets' to see available bet names")
        return pending

    # Create new pending bets with the change
    new_pending = replace(pending, **{bet_name: amount})

    # Build full action bets and validate
    action_bets = build_action_bets(state, new_pending)

    try:
        validate_action(state, action_bets)
        if amount == 0:
            print(f"Removed bet: {bet_name}")
        else:
            print(f"Set bet: {bet_name} = ${amount}")
        return new_pending
    except IllegalAction as e:
        print(f"Illegal bet: {e}")
        return pending


def cmd_info_table(state: TableState) -> None:
    """Display table limits."""
    print("\nTable Limits:")
    print(f"  Minimum bet: ${state.table_min}")
    print(f"  Maximum bet: ${state.table_max}")
    print(f"  Max odds:    {state.max_odds}x")
    print(f"  Prop minimum: ${state.prop_min}")
    print()


def cmd_info_bets() -> None:
    """Display all available bet names by category."""
    print("\nAvailable Bets:")
    print("-" * 40)

    categories = {
        "Line": ["pass_line", "pass_odds"],
        "Come": ["come_bet", "come_odds_4", "come_odds_5", "come_odds_6",
                 "come_odds_8", "come_odds_9", "come_odds_10"],
        "Place": ["place_4", "place_5", "place_6", "place_8", "place_9", "place_10"],
        "Buy": ["buy_4", "buy_5", "buy_6", "buy_8", "buy_9", "buy_10"],
        "Field": ["field"],
        "Hardways": ["hard_4", "hard_6", "hard_8", "hard_10"],
        "Props": ["any_seven", "any_craps", "aces", "ace_deuce",
                  "yo_leven", "boxcars", "horn", "c_and_e"],
    }

    for category, bets in categories.items():
        print(f"\n{category}:")
        print(f"  {', '.join(bets)}")
    print()


def calculate_equity(state: TableState) -> int:
    """Calculate total equity (bankroll + active bets)."""
    total_bets = sum(stake for _, stake in iter_bets(state.bets))
    return state.bankroll + total_bets


def cmd_roll(state: TableState, pending: ActionBets) -> tuple[TableState, ActionBets]:
    """Execute a roll and settle bets."""
    # Build action bets from current state + pending changes
    action_bets = build_action_bets(state, pending)
    action = Action(bets=action_bets)

    # Calculate equity before roll (includes any new bets being placed)
    equity_before = calculate_equity(state)

    # Generate random roll
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    roll = Roll((d1, d2))

    # Execute step
    new_state = step(state, action, roll)

    # Report results
    print(f"\nRolled: {d1} + {d2} = {roll.total()}")

    # Calculate profit/loss as change in equity
    equity_after = calculate_equity(new_state)
    profit = equity_after - equity_before
    if profit > 0:
        print(f"Won: ${profit}")
    elif profit < 0:
        print(f"Lost: ${-profit}")

    # Clear pending bets (they've been applied)
    return new_state, ActionBets()


def cmd_help() -> None:
    """Display help information."""
    print("\nCraps CLI Commands:")
    print("-" * 40)
    print("  bet <name> <amount>  Set a bet (0 to remove)")
    print("  info table           Show table limits")
    print("  info bets            List available bet names")
    print("  roll                 Roll dice and settle bets")
    print("  help                 Show this help message")
    print("  quit                 Exit the CLI")
    print()


def main() -> None:
    """Main REPL loop."""
    state = create_initial_state()
    pending = ActionBets()

    print("\nWelcome to the Craps CLI!")
    print("Type 'help' for available commands.\n")

    display_table(state)

    while not state.is_terminal:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        parts = user_input.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == "quit" or cmd == "exit":
            print("Goodbye!")
            break
        elif cmd == "help":
            cmd_help()
        elif cmd == "bet":
            pending = cmd_bet(state, pending, args)
            display_pending_bets(pending)
        elif cmd == "info":
            if args and args[0] == "table":
                cmd_info_table(state)
            elif args and args[0] == "bets":
                cmd_info_bets()
            else:
                print("Usage: info table | info bets")
        elif cmd == "roll":
            state, pending = cmd_roll(state, pending)
            display_table(state)
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands.")


if __name__ == "__main__":
    main()
