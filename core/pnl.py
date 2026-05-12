from core.models import OptionLeg, StockLeg, MarketParams
from core.black_scholes import black_scholes_price, year_fraction
from core.greeks import delta, gamma, vega, theta, rho


def stock_leg_current_value(
    leg: StockLeg,
    market: MarketParams,
) -> float:
    """
    Calcule la valeur actuelle d'une jambe action.

    Achat de 100 actions à un sous-jacent de 100 :
    valeur = +10 000

    Vente à découvert de 100 actions :
    valeur = -10 000
    """

    market.validate()

    sign = 1 if leg.side == "buy" else -1

    return market.underlying_price * sign * leg.quantity * leg.multiplier


def stock_leg_initial_cost(
    leg: StockLeg,
) -> float:
    """
    Calcule le coût initial d'une jambe action.

    Achat :
    coût positif.

    Vente à découvert :
    coût négatif.
    """

    sign = 1 if leg.side == "buy" else -1

    return leg.entry_price * sign * leg.quantity * leg.multiplier


def stock_leg_greeks(
    leg: StockLeg,
) -> dict:
    """
    Greeks simplifiés d'une action.

    Une action a :
    - delta = 1 par action achetée
    - gamma = 0
    - vega = 0
    - theta = 0
    - rho = 0
    """

    sign = 1 if leg.side == "buy" else -1
    factor = sign * leg.quantity * leg.multiplier

    return {
        "delta": factor,
        "gamma": 0.0,
        "vega": 0.0,
        "theta": 0.0,
        "rho": 0.0,
    }


def leg_current_value(
    leg,
    market: MarketParams,
) -> float:
    """
    Calcule la valeur actuelle théorique d'une jambe.

    Compatible avec :
    - OptionLeg
    - StockLeg
    """

    if isinstance(leg, StockLeg):
        return stock_leg_current_value(leg, market)

    leg.validate()
    market.validate()

    T = year_fraction(market.valuation_date, leg.expiry)

    option_price = black_scholes_price(
        option_type=leg.option_type,
        S=market.underlying_price,
        K=leg.strike,
        T=T,
        r=market.risk_free_rate,
        q=market.dividend_yield,
        sigma=leg.implied_volatility,
    )

    return option_price * leg.sign() * leg.quantity * leg.multiplier


def leg_initial_cost(
    leg,
) -> float:
    """
    Calcule le coût initial d'une jambe.

    Compatible avec :
    - OptionLeg
    - StockLeg
    """

    if isinstance(leg, StockLeg):
        return stock_leg_initial_cost(leg)

    leg.validate()

    return leg.entry_price * leg.sign() * leg.quantity * leg.multiplier


def leg_pnl(
    leg,
    market: MarketParams,
) -> float:
    """
    Calcule le P&L actuel d'une jambe.

    Formule :
    P&L = valeur actuelle - coût initial
    """

    return leg_current_value(leg, market) - leg_initial_cost(leg)


def strategy_current_value(
    legs: list,
    market: MarketParams,
) -> float:
    """
    Calcule la valeur actuelle totale d'une stratégie.
    """

    total_value = 0.0

    for leg in legs:
        total_value += leg_current_value(leg, market)

    return total_value


def strategy_initial_cost(
    legs: list,
) -> float:
    """
    Calcule le coût initial net de la stratégie.
    """

    total_cost = 0.0

    for leg in legs:
        total_cost += leg_initial_cost(leg)

    return total_cost


def strategy_pnl(
    legs: list,
    market: MarketParams,
) -> float:
    """
    Calcule le P&L total de la stratégie.

    Formule :
    P&L = valeur actuelle totale - coût initial total
    """

    return strategy_current_value(legs, market) - strategy_initial_cost(legs)


def leg_greeks(
    leg,
    market: MarketParams,
) -> dict:
    """
    Calcule les Greeks d'une jambe.

    Compatible avec :
    - OptionLeg
    - StockLeg
    """

    if isinstance(leg, StockLeg):
        return stock_leg_greeks(leg)

    leg.validate()
    market.validate()

    T = year_fraction(market.valuation_date, leg.expiry)

    sign = leg.sign()
    factor = sign * leg.quantity * leg.multiplier

    return {
        "delta": delta(
            leg.option_type,
            market.underlying_price,
            leg.strike,
            T,
            market.risk_free_rate,
            market.dividend_yield,
            leg.implied_volatility,
        )
        * factor,
        "gamma": gamma(
            market.underlying_price,
            leg.strike,
            T,
            market.risk_free_rate,
            market.dividend_yield,
            leg.implied_volatility,
        )
        * factor,
        "vega": vega(
            market.underlying_price,
            leg.strike,
            T,
            market.risk_free_rate,
            market.dividend_yield,
            leg.implied_volatility,
        )
        * factor,
        "theta": theta(
            leg.option_type,
            market.underlying_price,
            leg.strike,
            T,
            market.risk_free_rate,
            market.dividend_yield,
            leg.implied_volatility,
        )
        * factor,
        "rho": rho(
            leg.option_type,
            market.underlying_price,
            leg.strike,
            T,
            market.risk_free_rate,
            market.dividend_yield,
            leg.implied_volatility,
        )
        * factor,
    }


def strategy_greeks(
    legs: list,
    market: MarketParams,
) -> dict:
    """
    Calcule les Greeks totaux d'une stratégie multi-jambes.
    """

    totals = {
        "delta": 0.0,
        "gamma": 0.0,
        "vega": 0.0,
        "theta": 0.0,
        "rho": 0.0,
    }

    for leg in legs:
        greeks = leg_greeks(leg, market)

        for greek_name in totals:
            totals[greek_name] += greeks[greek_name]

    return totals