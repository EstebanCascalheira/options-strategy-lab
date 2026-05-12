from datetime import timedelta

from core.models import OptionLeg, StockLeg, MarketParams
from core.pnl import (
    strategy_current_value,
    strategy_initial_cost,
    strategy_pnl,
    strategy_greeks,
)


def clone_legs_with_iv(
    legs: list,
    implied_volatility: float,
) -> list:
    """
    Copie les jambes d'une stratégie avec une IV commune simulée.

    Compatible avec :
    - OptionLeg
    - StockLeg

    Les jambes actions ne reçoivent pas d'IV.
    """

    cloned_legs = []

    for leg in legs:
        if isinstance(leg, StockLeg):
            cloned_legs.append(
                StockLeg(
                    side=leg.side,
                    quantity=leg.quantity,
                    entry_price=leg.entry_price,
                    multiplier=leg.multiplier,
                )
            )
        else:
            cloned_legs.append(
                OptionLeg(
                    option_type=leg.option_type,
                    side=leg.side,
                    strike=leg.strike,
                    quantity=leg.quantity,
                    expiry=leg.expiry,
                    implied_volatility=implied_volatility,
                    entry_price=leg.entry_price,
                    multiplier=leg.multiplier,
                )
            )

    return cloned_legs


def generate_scenario_comment(
    pnl: float,
    delta: float,
    vega: float,
    theta: float,
) -> str:
    """
    Génère un commentaire court pour une ligne de scénario.
    """

    comments = []

    if pnl > 0:
        comments.append("P&L positif")
    elif pnl < 0:
        comments.append("P&L négatif")
    else:
        comments.append("P&L proche de zéro")

    if delta > 20:
        comments.append("exposition haussière")
    elif delta < -20:
        comments.append("exposition baissière")
    else:
        comments.append("exposition plutôt neutre")

    if vega > 5:
        comments.append("bénéficie d'une hausse d'IV")
    elif vega < -5:
        comments.append("bénéficie d'une baisse d'IV")
    else:
        comments.append("faible sensibilité IV")

    if theta > 1:
        comments.append("temps favorable")
    elif theta < -1:
        comments.append("temps défavorable")
    else:
        comments.append("theta modéré")

    return " ; ".join(comments)


def build_scenario_table(
    legs: list[OptionLeg],
    market: MarketParams,
    scenario_inputs: list[dict],
) -> list[dict]:
    """
    Construit un tableau de scénarios.

    Chaque scénario doit contenir :
    - name : nom du scénario
    - days_elapsed : nombre de jours écoulés
    - underlying_price : prix simulé du sous-jacent
    - implied_volatility : IV simulée, ex: 0.20 pour 20%

    La fonction retourne une liste de dictionnaires utilisable
    directement avec st.dataframe().
    """

    rows = []

    initial_cost = strategy_initial_cost(legs)

    for scenario in scenario_inputs:
        scenario_name = scenario["name"]
        days_elapsed = int(scenario["days_elapsed"])
        simulated_underlying_price = float(scenario["underlying_price"])
        simulated_iv = float(scenario["implied_volatility"])

        simulated_date = market.valuation_date + timedelta(days=days_elapsed)

        scenario_legs = clone_legs_with_iv(
            legs=legs,
            implied_volatility=simulated_iv,
        )

        simulated_market = MarketParams(
            underlying_price=simulated_underlying_price,
            risk_free_rate=market.risk_free_rate,
            dividend_yield=market.dividend_yield,
            valuation_date=simulated_date,
        )

        theoretical_value = strategy_current_value(
            legs=scenario_legs,
            market=simulated_market,
        )

        pnl = strategy_pnl(
            legs=scenario_legs,
            market=simulated_market,
        )

        greeks = strategy_greeks(
            legs=scenario_legs,
            market=simulated_market,
        )

        comment = generate_scenario_comment(
            pnl=pnl,
            delta=greeks["delta"],
            vega=greeks["vega"],
            theta=greeks["theta"],
        )

        rows.append(
            {
                "Scénario": scenario_name,
                "Date simulée": simulated_date,
                "Jours écoulés": days_elapsed,
                "Sous-jacent simulé": round(simulated_underlying_price, 2),
                "IV simulée": f"{simulated_iv * 100:.2f}%",
                "Valeur théorique": round(theoretical_value, 2),
                "Coût initial": round(initial_cost, 2),
                "P&L théorique": round(pnl, 2),
                "Delta": round(float(greeks["delta"]), 2),
                "Gamma": round(float(greeks["gamma"]), 2),
                "Vega": round(float(greeks["vega"]), 2),
                "Theta / jour": round(float(greeks["theta"]), 2),
                "Rho": round(float(greeks["rho"]), 2),
                "Commentaire": comment,
            }
        )

    return rows

def build_preset_scenarios(
    preset_name: str,
    current_underlying_price: float,
    current_implied_volatility: float,
) -> list[dict]:
    """
    Génère des scénarios prédéfinis.
    """

    if preset_name == "Neutre":
        return [
            {
                "label": "Aujourd'hui",
                "days_elapsed": 0,
                "underlying_price": current_underlying_price,
                "implied_volatility": current_implied_volatility,
            },
            {
                "label": "J+30 stable",
                "days_elapsed": 30,
                "underlying_price": current_underlying_price,
                "implied_volatility": current_implied_volatility,
            },
            {
                "label": "J+60 stable",
                "days_elapsed": 60,
                "underlying_price": current_underlying_price,
                "implied_volatility": current_implied_volatility,
            },
        ]

    if preset_name == "Haussier":
        return [
            {
                "label": "Hausse légère",
                "days_elapsed": 15,
                "underlying_price": current_underlying_price * 1.03,
                "implied_volatility": current_implied_volatility,
            },
            {
                "label": "Hausse modérée",
                "days_elapsed": 30,
                "underlying_price": current_underlying_price * 1.07,
                "implied_volatility": current_implied_volatility,
            },
            {
                "label": "Hausse forte",
                "days_elapsed": 60,
                "underlying_price": current_underlying_price * 1.12,
                "implied_volatility": current_implied_volatility,
            },
        ]

    if preset_name == "Baissier":
        return [
            {
                "label": "Baisse légère",
                "days_elapsed": 15,
                "underlying_price": current_underlying_price * 0.97,
                "implied_volatility": current_implied_volatility,
            },
            {
                "label": "Baisse modérée",
                "days_elapsed": 30,
                "underlying_price": current_underlying_price * 0.93,
                "implied_volatility": current_implied_volatility,
            },
            {
                "label": "Baisse forte",
                "days_elapsed": 60,
                "underlying_price": current_underlying_price * 0.88,
                "implied_volatility": current_implied_volatility,
            },
        ]

    if preset_name == "IV en hausse":
        return [
            {
                "label": "IV +5 points",
                "days_elapsed": 0,
                "underlying_price": current_underlying_price,
                "implied_volatility": current_implied_volatility + 0.05,
            },
            {
                "label": "IV +10 points",
                "days_elapsed": 0,
                "underlying_price": current_underlying_price,
                "implied_volatility": current_implied_volatility + 0.10,
            },
            {
                "label": "IV +15 points",
                "days_elapsed": 0,
                "underlying_price": current_underlying_price,
                "implied_volatility": current_implied_volatility + 0.15,
            },
        ]

    if preset_name == "IV en baisse":
        return [
            {
                "label": "IV -5 points",
                "days_elapsed": 0,
                "underlying_price": current_underlying_price,
                "implied_volatility": max(current_implied_volatility - 0.05, 0.01),
            },
            {
                "label": "IV -10 points",
                "days_elapsed": 0,
                "underlying_price": current_underlying_price,
                "implied_volatility": max(current_implied_volatility - 0.10, 0.01),
            },
            {
                "label": "IV -15 points",
                "days_elapsed": 0,
                "underlying_price": current_underlying_price,
                "implied_volatility": max(current_implied_volatility - 0.15, 0.01),
            },
        ]

    if preset_name == "Optimiste":
        return [
            {
                "label": "Optimiste court terme",
                "days_elapsed": 15,
                "underlying_price": current_underlying_price * 1.05,
                "implied_volatility": current_implied_volatility + 0.03,
            },
            {
                "label": "Optimiste moyen terme",
                "days_elapsed": 30,
                "underlying_price": current_underlying_price * 1.10,
                "implied_volatility": current_implied_volatility + 0.02,
            },
            {
                "label": "Optimiste fort",
                "days_elapsed": 60,
                "underlying_price": current_underlying_price * 1.15,
                "implied_volatility": current_implied_volatility,
            },
        ]

    if preset_name == "Pessimiste":
        return [
            {
                "label": "Pessimiste court terme",
                "days_elapsed": 15,
                "underlying_price": current_underlying_price * 0.95,
                "implied_volatility": current_implied_volatility + 0.05,
            },
            {
                "label": "Pessimiste moyen terme",
                "days_elapsed": 30,
                "underlying_price": current_underlying_price * 0.90,
                "implied_volatility": current_implied_volatility + 0.08,
            },
            {
                "label": "Pessimiste fort",
                "days_elapsed": 60,
                "underlying_price": current_underlying_price * 0.85,
                "implied_volatility": current_implied_volatility + 0.10,
            },
        ]

    raise ValueError(f"Scénario prédéfini inconnu : {preset_name}")

def build_monthly_evolution_inputs(
    market: MarketParams,
    expiry_date,
    underlying_profile: str,
    iv_profile: str,
    final_underlying_price: float,
    final_implied_volatility: float,
) -> list[dict]:
    """
    Génère des scénarios mensuels entre la date de valorisation et l'échéance.

    underlying_profile :
    - "Stable"
    - "Hausse progressive"
    - "Baisse progressive"
    - "Vers prix final"

    iv_profile :
    - "Stable"
    - "Hausse progressive"
    - "Baisse progressive"
    - "Vers IV finale"

    final_underlying_price :
    - prix cible du sous-jacent à l'échéance

    final_implied_volatility :
    - IV cible à l'échéance, au format décimal
      exemple : 0.20 = 20%
    """

    total_days = (expiry_date - market.valuation_date).days

    if total_days <= 0:
        raise ValueError("L'échéance doit être postérieure à la date de valorisation")

    # On crée une ligne tous les 30 jours, puis une dernière ligne à l'échéance.
    days_list = list(range(0, total_days, 30))

    if total_days not in days_list:
        days_list.append(total_days)

    rows = []

    current_underlying = market.underlying_price

    for days_elapsed in days_list:
        progress = days_elapsed / total_days

        # Prix du sous-jacent
        if underlying_profile == "Stable":
            simulated_underlying = current_underlying

        elif underlying_profile == "Hausse progressive":
            simulated_underlying = current_underlying * (1 + 0.10 * progress)

        elif underlying_profile == "Baisse progressive":
            simulated_underlying = current_underlying * (1 - 0.10 * progress)

        elif underlying_profile == "Vers prix final":
            simulated_underlying = (
                current_underlying
                + (final_underlying_price - current_underlying) * progress
            )

        else:
            raise ValueError(f"Profil sous-jacent inconnu : {underlying_profile}")

        # IV
        current_iv = None

        # On prend l'IV de la première jambe comme IV de référence.
        # Cette valeur sera réellement fournie au moment de construire le tableau.
        # Elle sera remplacée dans build_monthly_evolution_table().
        # Ici on ne fait que préparer la structure.
        if iv_profile == "Stable":
            simulated_iv = None

        elif iv_profile == "Hausse progressive":
            simulated_iv = "increase"

        elif iv_profile == "Baisse progressive":
            simulated_iv = "decrease"

        elif iv_profile == "Vers IV finale":
            simulated_iv = ("target", final_implied_volatility)

        else:
            raise ValueError(f"Profil IV inconnu : {iv_profile}")

        rows.append(
            {
                "name": f"Mois {round(days_elapsed / 30, 1)}",
                "days_elapsed": days_elapsed,
                "underlying_price": simulated_underlying,
                "iv_profile_value": simulated_iv,
                "progress": progress,
            }
        )

    return rows


def build_monthly_evolution_table(
    legs: list[OptionLeg],
    market: MarketParams,
    expiry_date,
    underlying_profile: str,
    iv_profile: str,
    final_underlying_price: float,
    final_implied_volatility: float,
) -> list[dict]:
    """
    Construit un tableau d'évolution mensuelle de la stratégie.

    Cette fonction utilise :
    - un profil d'évolution du sous-jacent
    - un profil d'évolution de l'IV
    - les dates mensuelles jusqu'à l'échéance
    """

    if not legs:
        raise ValueError("La stratégie doit contenir au moins une jambe")

    option_legs = [leg for leg in legs if isinstance(leg, OptionLeg)]

    if not option_legs:
        raise ValueError("Le tableau mensuel nécessite au moins une jambe option.")

    base_iv = option_legs[0].implied_volatility

    monthly_inputs = build_monthly_evolution_inputs(
        market=market,
        expiry_date=expiry_date,
        underlying_profile=underlying_profile,
        iv_profile=iv_profile,
        final_underlying_price=final_underlying_price,
        final_implied_volatility=final_implied_volatility,
    )

    scenario_inputs = []

    for item in monthly_inputs:
        progress = item["progress"]
        iv_profile_value = item["iv_profile_value"]

        if iv_profile_value is None:
            simulated_iv = base_iv

        elif iv_profile_value == "increase":
            simulated_iv = base_iv + 0.10 * progress

        elif iv_profile_value == "decrease":
            simulated_iv = max(base_iv - 0.10 * progress, 0.01)

        elif isinstance(iv_profile_value, tuple) and iv_profile_value[0] == "target":
            target_iv = iv_profile_value[1]
            simulated_iv = base_iv + (target_iv - base_iv) * progress

        else:
            raise ValueError("Profil IV invalide")

        scenario_inputs.append(
            {
                "name": item["name"],
                "days_elapsed": item["days_elapsed"],
                "underlying_price": item["underlying_price"],
                "implied_volatility": simulated_iv,
            }
        )

    return build_scenario_table(
        legs=legs,
        market=market,
        scenario_inputs=scenario_inputs,
    )

def summarize_monthly_evolution(
    monthly_table: list[dict],
) -> dict:
    """
    Résume automatiquement le tableau d'évolution mensuelle.

    Retourne :
    - P&L initial
    - P&L final
    - variation du P&L
    - meilleure ligne
    - pire ligne
    - tendance globale
    """

    if not monthly_table:
        raise ValueError("Le tableau mensuel est vide")

    first_row = monthly_table[0]
    last_row = monthly_table[-1]

    initial_pnl = float(first_row["P&L théorique"])
    final_pnl = float(last_row["P&L théorique"])
    pnl_change = final_pnl - initial_pnl

    best_row = max(monthly_table, key=lambda row: float(row["P&L théorique"]))
    worst_row = min(monthly_table, key=lambda row: float(row["P&L théorique"]))

    if pnl_change > 0:
        trend = "favorable"
        trend_comment = (
            "La trajectoire simulée améliore le P&L entre le début et la fin "
            "de la période analysée."
        )
    elif pnl_change < 0:
        trend = "défavorable"
        trend_comment = (
            "La trajectoire simulée dégrade le P&L entre le début et la fin "
            "de la période analysée."
        )
    else:
        trend = "stable"
        trend_comment = (
            "Le P&L final est proche du P&L initial dans cette simulation."
        )

    return {
        "initial_pnl": initial_pnl,
        "final_pnl": final_pnl,
        "pnl_change": pnl_change,
        "best_scenario": best_row["Scénario"],
        "best_pnl": float(best_row["P&L théorique"]),
        "worst_scenario": worst_row["Scénario"],
        "worst_pnl": float(worst_row["P&L théorique"]),
        "trend": trend,
        "trend_comment": trend_comment,
    }