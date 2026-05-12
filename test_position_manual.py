from datetime import date

from core.models import OptionLeg, MarketParams
from core.pnl import (
    leg_current_value,
    leg_initial_cost,
    leg_pnl,
    strategy_current_value,
    strategy_initial_cost,
    strategy_pnl,
    strategy_greeks,
)
from core.payoff import strategy_payoff_at_expiry, strategy_pnl_at_expiry


valuation_date = date(2026, 5, 11)
expiry = date(2026, 11, 11)

market = MarketParams(
    underlying_price=100,
    risk_free_rate=0.04,
    dividend_yield=0.00,
    valuation_date=valuation_date,
)


# ============================
# EXEMPLE 1 : LONG CALL
# ============================

long_call = OptionLeg(
    option_type="call",
    side="buy",
    strike=100,
    quantity=1,
    expiry=expiry,
    implied_volatility=0.20,
    entry_price=5.00,
    multiplier=100,
)

long_call_strategy = [long_call]

print("================================")
print("EXEMPLE 1 : LONG CALL")
print("================================")

print("Valeur actuelle jambe :", round(leg_current_value(long_call, market), 2))
print("Coût initial jambe    :", round(leg_initial_cost(long_call), 2))
print("P&L jambe             :", round(leg_pnl(long_call, market), 2))

print("Valeur stratégie      :", round(strategy_current_value(long_call_strategy, market), 2))
print("Coût initial stratégie:", round(strategy_initial_cost(long_call_strategy), 2))
print("P&L stratégie         :", round(strategy_pnl(long_call_strategy, market), 2))

print("Payoff si S=90        :", round(strategy_payoff_at_expiry(long_call_strategy, 90), 2))
print("Payoff si S=100       :", round(strategy_payoff_at_expiry(long_call_strategy, 100), 2))
print("Payoff si S=110       :", round(strategy_payoff_at_expiry(long_call_strategy, 110), 2))

print("P&L échéance si S=90  :", round(strategy_pnl_at_expiry(long_call_strategy, 90), 2))
print("P&L échéance si S=100 :", round(strategy_pnl_at_expiry(long_call_strategy, 100), 2))
print("P&L échéance si S=110 :", round(strategy_pnl_at_expiry(long_call_strategy, 110), 2))

greeks = strategy_greeks(long_call_strategy, market)
print("Greeks stratégie      :", {k: float(round(v, 2)) for k, v in greeks.items()})


# ============================
# EXEMPLE 2 : VERTICAL CALL DEBIT SPREAD
# Achat call 100
# Vente call 110
# ============================

buy_call_100 = OptionLeg(
    option_type="call",
    side="buy",
    strike=100,
    quantity=1,
    expiry=expiry,
    implied_volatility=0.20,
    entry_price=5.00,
    multiplier=100,
)

sell_call_110 = OptionLeg(
    option_type="call",
    side="sell",
    strike=110,
    quantity=1,
    expiry=expiry,
    implied_volatility=0.20,
    entry_price=2.00,
    multiplier=100,
)

vertical_spread = [buy_call_100, sell_call_110]

print("\n================================")
print("EXEMPLE 2 : VERTICAL CALL DEBIT SPREAD")
print("================================")

print("Valeur stratégie      :", round(strategy_current_value(vertical_spread, market), 2))
print("Coût initial stratégie:", round(strategy_initial_cost(vertical_spread), 2))
print("P&L stratégie         :", round(strategy_pnl(vertical_spread, market), 2))

print("Payoff si S=90        :", round(strategy_payoff_at_expiry(vertical_spread, 90), 2))
print("Payoff si S=100       :", round(strategy_payoff_at_expiry(vertical_spread, 100), 2))
print("Payoff si S=105       :", round(strategy_payoff_at_expiry(vertical_spread, 105), 2))
print("Payoff si S=110       :", round(strategy_payoff_at_expiry(vertical_spread, 110), 2))
print("Payoff si S=120       :", round(strategy_payoff_at_expiry(vertical_spread, 120), 2))

print("P&L échéance si S=90  :", round(strategy_pnl_at_expiry(vertical_spread, 90), 2))
print("P&L échéance si S=100 :", round(strategy_pnl_at_expiry(vertical_spread, 100), 2))
print("P&L échéance si S=105 :", round(strategy_pnl_at_expiry(vertical_spread, 105), 2))
print("P&L échéance si S=110 :", round(strategy_pnl_at_expiry(vertical_spread, 110), 2))
print("P&L échéance si S=120 :", round(strategy_pnl_at_expiry(vertical_spread, 120), 2))

greeks = strategy_greeks(vertical_spread, market)
print("Greeks stratégie      :", {k: float(round(v, 2)) for k, v in greeks.items()})