from datetime import date

from core.models import OptionLeg
from analytics.breakeven import analyze_expiry_profile


expiry = date(2026, 11, 11)


# ============================
# EXEMPLE 1 : LONG CALL
# ============================

long_call = [
    OptionLeg(
        option_type="call",
        side="buy",
        strike=100,
        quantity=1,
        expiry=expiry,
        implied_volatility=0.20,
        entry_price=5.00,
        multiplier=100,
    )
]

analysis_long_call = analyze_expiry_profile(
    legs=long_call,
    current_underlying_price=100,
    lower_multiplier=0.5,
    upper_multiplier=1.5,
    steps=501,
)

print("================================")
print("EXEMPLE 1 : LONG CALL")
print("================================")
print("Break-even estimés :", [round(x, 2) for x in analysis_long_call["breakevens"]])
print("Gain max estimé     :", round(analysis_long_call["max_profit"], 2))
print("Perte max estimée   :", round(analysis_long_call["max_loss"], 2))
print("Zones profitables   :", analysis_long_call["profitable_ranges"])


# ============================
# EXEMPLE 2 : VERTICAL CALL DEBIT SPREAD
# ============================

vertical_spread = [
    OptionLeg(
        option_type="call",
        side="buy",
        strike=100,
        quantity=1,
        expiry=expiry,
        implied_volatility=0.20,
        entry_price=5.00,
        multiplier=100,
    ),
    OptionLeg(
        option_type="call",
        side="sell",
        strike=110,
        quantity=1,
        expiry=expiry,
        implied_volatility=0.20,
        entry_price=2.00,
        multiplier=100,
    ),
]

analysis_vertical = analyze_expiry_profile(
    legs=vertical_spread,
    current_underlying_price=100,
    lower_multiplier=0.5,
    upper_multiplier=1.5,
    steps=501,
)

print("\n================================")
print("EXEMPLE 2 : VERTICAL CALL DEBIT SPREAD")
print("================================")
print("Break-even estimés :", [round(x, 2) for x in analysis_vertical["breakevens"]])
print("Gain max estimé     :", round(analysis_vertical["max_profit"], 2))
print("Perte max estimée   :", round(analysis_vertical["max_loss"], 2))
print("Zones profitables   :", analysis_vertical["profitable_ranges"])


# ============================
# EXEMPLE 3 : LONG STRADDLE
# Achat call 100 + achat put 100
# ============================

long_straddle = [
    OptionLeg(
        option_type="call",
        side="buy",
        strike=100,
        quantity=1,
        expiry=expiry,
        implied_volatility=0.20,
        entry_price=5.00,
        multiplier=100,
    ),
    OptionLeg(
        option_type="put",
        side="buy",
        strike=100,
        quantity=1,
        expiry=expiry,
        implied_volatility=0.20,
        entry_price=4.00,
        multiplier=100,
    ),
]

analysis_straddle = analyze_expiry_profile(
    legs=long_straddle,
    current_underlying_price=100,
    lower_multiplier=0.5,
    upper_multiplier=1.5,
    steps=501,
)

print("\n================================")
print("EXEMPLE 3 : LONG STRADDLE")
print("================================")
print("Break-even estimés :", [round(x, 2) for x in analysis_straddle["breakevens"]])
print("Gain max estimé     :", round(analysis_straddle["max_profit"], 2))
print("Perte max estimée   :", round(analysis_straddle["max_loss"], 2))
print("Zones profitables   :", analysis_straddle["profitable_ranges"])