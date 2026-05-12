import numpy as np

from core.models import OptionLeg
from core.payoff import strategy_pnl_at_expiry


def generate_price_grid(
    current_underlying_price: float,
    lower_multiplier: float = 0.5,
    upper_multiplier: float = 1.5,
    steps: int = 501,
) -> np.ndarray:
    """
    Génère une grille de prix possibles du sous-jacent.

    Exemple :
    Si le sous-jacent vaut 100 :
    - borne basse = 100 * 0.5 = 50
    - borne haute = 100 * 1.5 = 150

    On teste ensuite 501 prix entre 50 et 150.
    """

    if current_underlying_price <= 0:
        raise ValueError("Le prix du sous-jacent doit être positif")

    if lower_multiplier <= 0:
        raise ValueError("lower_multiplier doit être positif")

    if upper_multiplier <= lower_multiplier:
        raise ValueError("upper_multiplier doit être supérieur à lower_multiplier")

    if steps < 10:
        raise ValueError("steps doit être au moins égal à 10")

    lower_bound = current_underlying_price * lower_multiplier
    upper_bound = current_underlying_price * upper_multiplier

    return np.linspace(lower_bound, upper_bound, steps)


def pnl_profile_at_expiry(
    legs: list[OptionLeg],
    price_grid: np.ndarray,
) -> list[dict]:
    """
    Calcule le P&L net à l'échéance pour chaque prix du sous-jacent.

    Retourne une liste de dictionnaires :
    [
        {"underlying_price": 90, "pnl": -300},
        {"underlying_price": 100, "pnl": -300},
        {"underlying_price": 110, "pnl": 700},
    ]
    """

    profile = []

    for price in price_grid:
        pnl = strategy_pnl_at_expiry(
            legs=legs,
            underlying_price_at_expiry=float(price),
        )

        profile.append(
            {
                "underlying_price": float(price),
                "pnl": float(pnl),
            }
        )

    return profile


def estimate_breakevens(
    pnl_profile: list[dict],
) -> list[float]:
    """
    Estime les break-even à partir d'un profil de P&L.

    Méthode :
    - On regarde où le P&L change de signe.
    - On interpole entre les deux points autour de zéro.

    Cette méthode fonctionne pour beaucoup de stratégies :
    - long call
    - long put
    - vertical spread
    - butterfly
    - iron condor
    - straddle
    - strangle
    """

    breakevens = []

    for i in range(1, len(pnl_profile)):
        previous_price = pnl_profile[i - 1]["underlying_price"]
        previous_pnl = pnl_profile[i - 1]["pnl"]

        current_price = pnl_profile[i]["underlying_price"]
        current_pnl = pnl_profile[i]["pnl"]

        # Si un point tombe exactement à zéro
        if current_pnl == 0:
            breakevens.append(current_price)

        # Si le P&L change de signe, il y a un break-even entre les deux points
        if previous_pnl * current_pnl < 0:
            # Interpolation linéaire
            breakeven = previous_price + (
                (0 - previous_pnl)
                * (current_price - previous_price)
                / (current_pnl - previous_pnl)
            )

            breakevens.append(float(breakeven))

    # Supprime les doublons très proches
    cleaned_breakevens = []

    for be in breakevens:
        if not any(abs(be - existing) < 0.01 for existing in cleaned_breakevens):
            cleaned_breakevens.append(be)

    return cleaned_breakevens


def estimate_max_profit(
    pnl_profile: list[dict],
) -> float:
    """
    Estime le gain maximum sur la grille testée.

    Attention :
    Pour certaines stratégies, le gain peut être théoriquement illimité.
    Dans ce cas, cette fonction retourne seulement le gain maximum
    observé dans la grille de prix.
    """

    return max(point["pnl"] for point in pnl_profile)


def estimate_max_loss(
    pnl_profile: list[dict],
) -> float:
    """
    Estime la perte maximum sur la grille testée.

    Attention :
    Pour certaines stratégies, la perte peut être théoriquement illimitée.
    Dans ce cas, cette fonction retourne seulement la perte maximum
    observée dans la grille de prix.
    """

    return min(point["pnl"] for point in pnl_profile)


def estimate_profitable_ranges(
    pnl_profile: list[dict],
) -> list[dict]:
    """
    Estime les zones où la stratégie est profitable à l'échéance.

    Retourne une liste de zones :
    [
        {"from": 103.0, "to": 150.0}
    ]

    ou pour un iron condor :
    [
        {"from": 85.0, "to": 115.0}
    ]
    """

    ranges = []
    in_profitable_zone = False
    start_price = None

    for point in pnl_profile:
        price = point["underlying_price"]
        pnl = point["pnl"]

        if pnl > 0 and not in_profitable_zone:
            in_profitable_zone = True
            start_price = price

        if pnl <= 0 and in_profitable_zone:
            in_profitable_zone = False
            end_price = price
            ranges.append(
                {
                    "from": float(start_price),
                    "to": float(end_price),
                }
            )

    # Si la zone profitable continue jusqu'à la fin de la grille
    if in_profitable_zone:
        ranges.append(
            {
                "from": float(start_price),
                "to": float(pnl_profile[-1]["underlying_price"]),
            }
        )

    return ranges


def analyze_expiry_profile(
    legs: list[OptionLeg],
    current_underlying_price: float,
    lower_multiplier: float = 0.5,
    upper_multiplier: float = 1.5,
    steps: int = 501,
) -> dict:
    """
    Fonction principale d'analyse.

    Elle génère une grille de prix, calcule le P&L à l'échéance,
    puis estime :
    - break-even
    - gain maximum
    - perte maximum
    - zones profitables
    """

    price_grid = generate_price_grid(
        current_underlying_price=current_underlying_price,
        lower_multiplier=lower_multiplier,
        upper_multiplier=upper_multiplier,
        steps=steps,
    )

    profile = pnl_profile_at_expiry(
        legs=legs,
        price_grid=price_grid,
    )

    return {
        "profile": profile,
        "breakevens": estimate_breakevens(profile),
        "max_profit": estimate_max_profit(profile),
        "max_loss": estimate_max_loss(profile),
        "profitable_ranges": estimate_profitable_ranges(profile),
    }