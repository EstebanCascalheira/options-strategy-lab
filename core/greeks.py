import math
from scipy.stats import norm

from core.black_scholes import calculate_d1, calculate_d2


def delta(
    option_type: str,
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
) -> float:
    """
    Calcule le delta d'une option.

    Delta mesure la sensibilité du prix de l'option
    à une variation du prix du sous-jacent.

    Pour un call :
    delta = e^(-qT) * N(d1)

    Pour un put :
    delta = e^(-qT) * [N(d1) - 1]
    """

    if T <= 0:
        if option_type == "call":
            return 1.0 if S > K else 0.0
        if option_type == "put":
            return -1.0 if S < K else 0.0
        raise ValueError("option_type doit être 'call' ou 'put'")

    d1 = calculate_d1(S, K, T, r, q, sigma)

    if option_type == "call":
        return math.exp(-q * T) * norm.cdf(d1)

    if option_type == "put":
        return math.exp(-q * T) * (norm.cdf(d1) - 1)

    raise ValueError("option_type doit être 'call' ou 'put'")


def gamma(
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
) -> float:
    """
    Calcule le gamma d'une option.

    Gamma mesure la sensibilité du delta
    à une variation du prix du sous-jacent.

    Même formule pour call et put.
    """

    if T <= 0:
        return 0.0

    d1 = calculate_d1(S, K, T, r, q, sigma)

    return (
        math.exp(-q * T)
        * norm.pdf(d1)
        / (S * sigma * math.sqrt(T))
    )


def vega(
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
) -> float:
    """
    Calcule le vega d'une option.

    Vega mesure la sensibilité du prix de l'option
    à une variation de la volatilité implicite.

    Ici, on retourne le vega pour +1 point de volatilité,
    c'est-à-dire pour une variation de 1%, pas de 100%.

    Exemple :
    vega = 0.28 signifie qu'une hausse de l'IV de 1 point
    augmente théoriquement le prix de l'option d'environ 0.28.
    """

    if T <= 0:
        return 0.0

    d1 = calculate_d1(S, K, T, r, q, sigma)

    raw_vega = S * math.exp(-q * T) * norm.pdf(d1) * math.sqrt(T)

    return raw_vega / 100


def theta(
    option_type: str,
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
) -> float:
    """
    Calcule le theta d'une option.

    Theta mesure la sensibilité du prix de l'option
    au passage du temps.

    Ici, on retourne le theta par jour.

    Un theta de -0.03 signifie que l'option perd
    théoriquement environ 0.03 par jour, toutes choses égales par ailleurs.
    """

    if T <= 0:
        return 0.0

    d1 = calculate_d1(S, K, T, r, q, sigma)
    d2 = calculate_d2(d1, sigma, T)

    first_term = (
        -S
        * math.exp(-q * T)
        * norm.pdf(d1)
        * sigma
        / (2 * math.sqrt(T))
    )

    if option_type == "call":
        annual_theta = (
            first_term
            - r * K * math.exp(-r * T) * norm.cdf(d2)
            + q * S * math.exp(-q * T) * norm.cdf(d1)
        )
        return annual_theta / 365

    if option_type == "put":
        annual_theta = (
            first_term
            + r * K * math.exp(-r * T) * norm.cdf(-d2)
            - q * S * math.exp(-q * T) * norm.cdf(-d1)
        )
        return annual_theta / 365

    raise ValueError("option_type doit être 'call' ou 'put'")


def rho(
    option_type: str,
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
) -> float:
    """
    Calcule le rho d'une option.

    Rho mesure la sensibilité du prix de l'option
    à une variation du taux sans risque.

    Ici, on retourne le rho pour +1 point de taux,
    c'est-à-dire pour une variation de 1%, pas de 100%.

    Exemple :
    rho = 0.22 signifie qu'une hausse du taux de 1 point
    augmente théoriquement le prix du call d'environ 0.22.
    """

    if T <= 0:
        return 0.0

    d1 = calculate_d1(S, K, T, r, q, sigma)
    d2 = calculate_d2(d1, sigma, T)

    if option_type == "call":
        raw_rho = K * T * math.exp(-r * T) * norm.cdf(d2)
        return raw_rho / 100

    if option_type == "put":
        raw_rho = -K * T * math.exp(-r * T) * norm.cdf(-d2)
        return raw_rho / 100

    raise ValueError("option_type doit être 'call' ou 'put'")