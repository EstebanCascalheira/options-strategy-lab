import math
from scipy.stats import norm


def year_fraction(start_date, end_date) -> float:
    """
    Calcule le temps restant en années.

    Convention simple :
    T = nombre de jours / 365
    """
    days = (end_date - start_date).days
    return max(days / 365.0, 0.0)


def calculate_d1(
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
) -> float:
    """
    Calcule d1 dans le modèle Black-Scholes.

    d1 = [ln(S/K) + (r - q + sigma²/2)T] / [sigma * sqrt(T)]
    """
    if S <= 0:
        raise ValueError("S doit être positif")

    if K <= 0:
        raise ValueError("K doit être positif")

    if T <= 0:
        raise ValueError("T doit être strictement positif pour calculer d1")

    if sigma <= 0:
        raise ValueError("sigma doit être strictement positif")

    return (
        math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T
    ) / (sigma * math.sqrt(T))


def calculate_d2(
    d1: float,
    sigma: float,
    T: float,
) -> float:
    """
    Calcule d2.

    d2 = d1 - sigma * sqrt(T)
    """
    if T <= 0:
        raise ValueError("T doit être strictement positif pour calculer d2")

    if sigma <= 0:
        raise ValueError("sigma doit être strictement positif")

    return d1 - sigma * math.sqrt(T)


def intrinsic_value(
    option_type: str,
    S: float,
    K: float,
) -> float:
    """
    Calcule la valeur intrinsèque d'une option.
    """
    if option_type == "call":
        return max(S - K, 0.0)

    if option_type == "put":
        return max(K - S, 0.0)

    raise ValueError("option_type doit être 'call' ou 'put'")


def black_scholes_price(
    option_type: str,
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
) -> float:
    """
    Calcule le prix théorique Black-Scholes d'un call ou d'un put.

    option_type : "call" ou "put"
    S : prix du sous-jacent
    K : strike
    T : temps restant en années
    r : taux sans risque
    q : dividend yield
    sigma : volatilité implicite
    """

    if T <= 0:
        return intrinsic_value(option_type, S, K)

    d1 = calculate_d1(S, K, T, r, q, sigma)
    d2 = calculate_d2(d1, sigma, T)

    if option_type == "call":
        return (
            S * math.exp(-q * T) * norm.cdf(d1)
            - K * math.exp(-r * T) * norm.cdf(d2)
        )

    if option_type == "put":
        return (
            K * math.exp(-r * T) * norm.cdf(-d2)
            - S * math.exp(-q * T) * norm.cdf(-d1)
        )

    raise ValueError("option_type doit être 'call' ou 'put'")


def time_value(
    option_price: float,
    option_type: str,
    S: float,
    K: float,
) -> float:
    """
    Calcule la valeur temps.

    valeur temps = prix option - valeur intrinsèque
    """
    return option_price - intrinsic_value(option_type, S, K)