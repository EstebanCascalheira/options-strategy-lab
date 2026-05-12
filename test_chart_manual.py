from datetime import date

from strategies.templates import (
    create_vertical_call_spread,
    create_call_butterfly,
    create_iron_condor,
)

from visualization.charts import create_expiry_pnl_chart


expiry = date(2026, 11, 11)


# ============================
# Choisis ici la stratégie à afficher
# ============================

strategy = create_vertical_call_spread(
    lower_strike=100,
    upper_strike=110,
    expiry=expiry,
    quantity=1,
    implied_volatility=0.20,
    lower_entry_price=5.00,
    upper_entry_price=2.00,
    spread_type="debit",
)

# Tu peux tester aussi le butterfly :
# strategy = create_call_butterfly(
#     lower_strike=90,
#     middle_strike=100,
#     upper_strike=110,
#     expiry=expiry,
#     quantity=1,
#     implied_volatility=0.20,
#     lower_entry_price=12.00,
#     middle_entry_price=5.00,
#     upper_entry_price=2.00,
# )

# Ou l'iron condor :
# strategy = create_iron_condor(
#     lower_put_strike=85,
#     upper_put_strike=90,
#     lower_call_strike=110,
#     upper_call_strike=115,
#     expiry=expiry,
#     quantity=1,
#     implied_volatility=0.20,
#     lower_put_entry_price=1.00,
#     upper_put_entry_price=2.00,
#     lower_call_entry_price=2.00,
#     upper_call_entry_price=1.00,
# )

fig = create_expiry_pnl_chart(
    legs=strategy,
    current_underlying_price=100,
    title="Vertical Call Debit Spread - P&L à l'échéance",
    lower_multiplier=0.5,
    upper_multiplier=1.5,
    steps=501,
)

fig.show()