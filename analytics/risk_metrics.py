from math import inf

from core.models import OptionLeg, StockLeg
from core.payoff import strategy_pnl_at_expiry


def _leg_right_slope(leg) -> float:
    """
    Pente du P&L quand le sous-jacent devient très grand.

    Call acheté : +quantité * multiplicateur
    Call vendu  : -quantité * multiplicateur
    Put         : 0 à droite
    Stock achat : +quantité
    Stock vente : -quantité
    """

    if isinstance(leg, StockLeg):
        sign = 1 if leg.side == "buy" else -1
        return sign * leg.quantity * leg.multiplier

    if isinstance(leg, OptionLeg):
        if leg.option_type == "call":
            return leg.sign() * leg.quantity * leg.multiplier

        if leg.option_type == "put":
            return 0.0

    return 0.0


def _get_key_prices(legs: list) -> list[float]:
    """
    Les extrêmes d'une stratégie options/action se trouvent aux strikes,
    à zéro, ou à l'infini.

    On teste donc :
    - S = 0
    - tous les strikes
    """

    prices = {0.0}

    for leg in legs:
        if isinstance(leg, OptionLeg):
            prices.add(float(leg.strike))

    return sorted(prices)


def calculate_expiry_risk_metrics(legs: list) -> dict:
    """
    Calcule le gain max et la perte max théoriques à l'échéance.

    Retourne :
    - max_profit
    - max_loss
    - max_profit_is_infinite
    - max_loss_is_infinite
    """

    if not legs:
        raise ValueError("La stratégie doit contenir au moins une jambe")

    key_prices = _get_key_prices(legs)

    pnl_values = [
        strategy_pnl_at_expiry(
            legs=legs,
            underlying_price=price,
        )
        for price in key_prices
    ]

    right_slope = sum(_leg_right_slope(leg) for leg in legs)

    max_profit_is_infinite = right_slope > 0
    max_loss_is_infinite = right_slope < 0

    if max_profit_is_infinite:
        max_profit = inf
    else:
        max_profit = max(pnl_values)

    if max_loss_is_infinite:
        max_loss = -inf
    else:
        max_loss = min(pnl_values)

    return {
        "max_profit": max_profit,
        "max_loss": max_loss,
        "max_profit_is_infinite": max_profit_is_infinite,
        "max_loss_is_infinite": max_loss_is_infinite,
        "right_slope": right_slope,
        "tested_prices": key_prices,
    }


def format_risk_value(value: float) -> str:
    """
    Format lisible pour Streamlit.
    """

    if value == inf:
        return "Illimité"

    if value == -inf:
        return "Illimitée"

    return f"{value:,.2f}"