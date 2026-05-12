from core.models import OptionLeg, StockLeg


def option_intrinsic_value(
    option_type: str,
    underlying_price: float,
    strike: float,
) -> float:
    """
    Calcule la valeur intrinsèque d'une option.

    Call :
    max(S - K, 0)

    Put :
    max(K - S, 0)
    """

    if option_type == "call":
        return max(underlying_price - strike, 0)

    if option_type == "put":
        return max(strike - underlying_price, 0)

    raise ValueError("Le type d'option doit être 'call' ou 'put'.")


def leg_payoff_at_expiry(
    leg,
    underlying_price: float,
) -> float:
    """
    Calcule le payoff brut d'une jambe à l'échéance.

    Compatible avec :
    - OptionLeg
    - StockLeg

    Attention :
    ce payoff ne tient pas encore compte du coût initial.
    Le P&L à l'échéance est calculé ensuite en retirant le coût initial.
    """

    if isinstance(leg, StockLeg):
        sign = 1 if leg.side == "buy" else -1
        return underlying_price * sign * leg.quantity * leg.multiplier

    leg.validate()

    intrinsic_value = option_intrinsic_value(
        option_type=leg.option_type,
        underlying_price=underlying_price,
        strike=leg.strike,
    )

    return intrinsic_value * leg.sign() * leg.quantity * leg.multiplier


def strategy_payoff_at_expiry(
    legs: list,
    underlying_price: float,
) -> float:
    """
    Calcule le payoff brut total de la stratégie à l'échéance.
    """

    total_payoff = 0.0

    for leg in legs:
        total_payoff += leg_payoff_at_expiry(
            leg=leg,
            underlying_price=underlying_price,
        )

    return total_payoff


def strategy_pnl_at_expiry(
    legs: list,
    underlying_price: float = None,
    underlying_price_at_expiry: float = None,
) -> float:
    """
    Calcule le P&L net à l'échéance.

    Compatible avec deux noms de paramètres :
    - underlying_price
    - underlying_price_at_expiry

    Formule :
    P&L échéance = payoff brut à l'échéance - coût initial total
    """

    from core.pnl import strategy_initial_cost

    if underlying_price is None:
        underlying_price = underlying_price_at_expiry

    if underlying_price is None:
        raise ValueError("Il faut fournir un prix du sous-jacent à l'échéance.")

    payoff = strategy_payoff_at_expiry(
        legs=legs,
        underlying_price=underlying_price,
    )

    initial_cost = strategy_initial_cost(legs)

    return payoff - initial_cost