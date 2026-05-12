from datetime import date

from strategies.templates import (
    create_long_call,
    create_long_put,
    create_vertical_call_spread,
    create_long_straddle,
    create_call_butterfly,
    create_iron_condor,
)

from core.pnl import strategy_initial_cost
from analytics.breakeven import analyze_expiry_profile


expiry = date(2026, 11, 11)


def print_strategy_analysis(name, legs):
    """
    Affiche une analyse simple d'une stratégie.
    """

    analysis = analyze_expiry_profile(
        legs=legs,
        current_underlying_price=100,
        lower_multiplier=0.5,
        upper_multiplier=1.5,
        steps=501,
    )

    print("\n================================")
    print(name)
    print("================================")

    print("Nombre de jambes :", len(legs))
    print("Coût initial net :", round(strategy_initial_cost(legs), 2))

    print("Jambes :")
    for leg in legs:
        print(
            f"- {leg.side.upper()} {leg.quantity} "
            f"{leg.option_type.upper()} strike {leg.strike} "
            f"prix entrée {leg.entry_price}"
        )

    print("Break-even estimés :", [round(x, 2) for x in analysis["breakevens"]])
    print("Gain max estimé     :", round(analysis["max_profit"], 2))
    print("Perte max estimée   :", round(analysis["max_loss"], 2))
    print("Zones profitables   :", analysis["profitable_ranges"])


# 1. Long call
long_call = create_long_call(
    strike=100,
    expiry=expiry,
    quantity=1,
    implied_volatility=0.20,
    entry_price=5.00,
)

print_strategy_analysis("LONG CALL", long_call)


# 2. Long put
long_put = create_long_put(
    strike=100,
    expiry=expiry,
    quantity=1,
    implied_volatility=0.20,
    entry_price=4.00,
)

print_strategy_analysis("LONG PUT", long_put)


# 3. Vertical call debit spread
vertical_call = create_vertical_call_spread(
    lower_strike=100,
    upper_strike=110,
    expiry=expiry,
    quantity=1,
    implied_volatility=0.20,
    lower_entry_price=5.00,
    upper_entry_price=2.00,
    spread_type="debit",
)

print_strategy_analysis("VERTICAL CALL DEBIT SPREAD", vertical_call)


# 4. Long straddle
long_straddle = create_long_straddle(
    strike=100,
    expiry=expiry,
    quantity=1,
    implied_volatility=0.20,
    call_entry_price=5.00,
    put_entry_price=4.00,
)

print_strategy_analysis("LONG STRADDLE", long_straddle)


# 5. Call butterfly
call_butterfly = create_call_butterfly(
    lower_strike=90,
    middle_strike=100,
    upper_strike=110,
    expiry=expiry,
    quantity=1,
    implied_volatility=0.20,
    lower_entry_price=12.00,
    middle_entry_price=5.00,
    upper_entry_price=2.00,
)

print_strategy_analysis("CALL BUTTERFLY", call_butterfly)


# 6. Iron condor
iron_condor = create_iron_condor(
    lower_put_strike=85,
    upper_put_strike=90,
    lower_call_strike=110,
    upper_call_strike=115,
    expiry=expiry,
    quantity=1,
    implied_volatility=0.20,
    lower_put_entry_price=1.00,
    upper_put_entry_price=2.00,
    lower_call_entry_price=2.00,
    upper_call_entry_price=1.00,
)

print_strategy_analysis("IRON CONDOR", iron_condor)