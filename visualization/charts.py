import plotly.graph_objects as go

from core.models import OptionLeg, StockLeg, MarketParams
from analytics.breakeven import analyze_expiry_profile


def create_expiry_pnl_chart(
    legs: list[OptionLeg],
    current_underlying_price: float,
    title: str = "P&L à l'échéance",
    lower_multiplier: float = 0.5,
    upper_multiplier: float = 1.5,
    steps: int = 501,
):
    """
    Crée un graphique Plotly du P&L à l'échéance.

    Axe X :
    - prix du sous-jacent à l'échéance

    Axe Y :
    - P&L net à l'échéance

    Le graphique affiche :
    - la courbe de P&L
    - une ligne horizontale à zéro
    - une ligne verticale au prix actuel du sous-jacent
    - les break-even estimés
    """

    analysis = analyze_expiry_profile(
        legs=legs,
        current_underlying_price=current_underlying_price,
        lower_multiplier=lower_multiplier,
        upper_multiplier=upper_multiplier,
        steps=steps,
    )

    profile = analysis["profile"]
    breakevens = analysis["breakevens"]

    x_values = [point["underlying_price"] for point in profile]
    y_values = [point["pnl"] for point in profile]

    fig = go.Figure()

    # Courbe principale du P&L
    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines",
            name="P&L à l'échéance",
            hovertemplate=(
                "Prix sous-jacent: %{x:.2f}<br>"
                "P&L: %{y:.2f}<extra></extra>"
            ),
        )
    )

    # Ligne horizontale P&L = 0
    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="P&L = 0",
        annotation_position="top left",
    )

    # Ligne verticale prix actuel
    fig.add_vline(
        x=current_underlying_price,
        line_dash="dot",
        annotation_text="Prix actuel",
        annotation_position="top",
    )

    # Lignes verticales break-even
    for breakeven in breakevens:
        fig.add_vline(
            x=breakeven,
            line_dash="dash",
            annotation_text=f"BE {breakeven:.2f}",
            annotation_position="bottom",
        )

    fig.update_layout(
        title=title,
        xaxis_title="Prix du sous-jacent à l'échéance",
        yaxis_title="P&L net à l'échéance",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig

from core.pnl import strategy_current_value, strategy_initial_cost


def create_theoretical_pnl_chart(
    legs: list[OptionLeg],
    market: MarketParams,
    title: str = "P&L théorique avant échéance",
    lower_multiplier: float = 0.5,
    upper_multiplier: float = 1.5,
    steps: int = 501,
):
    """
    Crée un graphique Plotly du P&L théorique avant échéance.

    Contrairement au payoff à l'échéance, ce graphique utilise Black-Scholes
    pour recalculer la valeur théorique de la stratégie à différents prix
    simulés du sous-jacent.

    Axe X :
    - prix simulé du sous-jacent

    Axe Y :
    - P&L théorique = valeur théorique simulée - coût initial

    Ce graphique tient compte de :
    - la volatilité implicite
    - le temps restant
    - le taux sans risque
    - le dividend yield
    - la valeur temps
    """

    if market.underlying_price <= 0:
        raise ValueError("Le prix du sous-jacent doit être positif")

    lower_bound = market.underlying_price * lower_multiplier
    upper_bound = market.underlying_price * upper_multiplier

    price_grid = [
        lower_bound + i * (upper_bound - lower_bound) / (steps - 1)
        for i in range(steps)
    ]

    initial_cost = strategy_initial_cost(legs)

    x_values = []
    y_values = []

    for simulated_price in price_grid:
        simulated_market = MarketParams(
            underlying_price=simulated_price,
            risk_free_rate=market.risk_free_rate,
            dividend_yield=market.dividend_yield,
            valuation_date=market.valuation_date,
        )

        simulated_value = strategy_current_value(
            legs=legs,
            market=simulated_market,
        )

        simulated_pnl = simulated_value - initial_cost

        x_values.append(simulated_price)
        y_values.append(simulated_pnl)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines",
            name="P&L théorique avant échéance",
            hovertemplate=(
                "Prix sous-jacent simulé: %{x:.2f}<br>"
                "P&L théorique: %{y:.2f}<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="P&L = 0",
        annotation_position="top left",
    )

    fig.add_vline(
        x=market.underlying_price,
        line_dash="dot",
        annotation_text="Prix actuel",
        annotation_position="top",
    )

    fig.update_layout(
        title=title,
        xaxis_title="Prix simulé du sous-jacent",
        yaxis_title="P&L théorique avant échéance",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig

def clone_legs_with_new_iv(
    legs: list,
    new_implied_volatility: float | None,
) -> list:
    """
    Copie les jambes d'une stratégie en remplaçant éventuellement l'IV.

    Compatible avec :
    - OptionLeg
    - StockLeg

    Si new_implied_volatility vaut None, on conserve l'IV originale de chaque jambe.
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
            if new_implied_volatility is None:
                implied_volatility = leg.implied_volatility
            else:
                implied_volatility = new_implied_volatility

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


def create_scenario_theoretical_pnl_chart(
    legs: list[OptionLeg],
    market: MarketParams,
    scenarios: list[dict],
    title: str = "Comparaison de scénarios théoriques",
    lower_multiplier: float = 0.5,
    upper_multiplier: float = 1.5,
    steps: int = 501,
):
    """
    Crée un graphique comparant plusieurs scénarios de P&L théorique.

    Chaque scénario peut contenir :
    - name : nom du scénario
    - valuation_date : date de simulation
    - implied_volatility : IV simulée, ex: 0.25 pour 25%

    Le coût initial reste celui de la stratégie d'origine.
    Seules les hypothèses de valorisation changent.
    """

    if market.underlying_price <= 0:
        raise ValueError("Le prix du sous-jacent doit être positif")

    lower_bound = market.underlying_price * lower_multiplier
    upper_bound = market.underlying_price * upper_multiplier

    price_grid = [
        lower_bound + i * (upper_bound - lower_bound) / (steps - 1)
        for i in range(steps)
    ]

    initial_cost = strategy_initial_cost(legs)

    fig = go.Figure()

    for scenario in scenarios:
        scenario_name = scenario["name"]
        scenario_date = scenario["valuation_date"]
        scenario_iv = scenario.get("implied_volatility")

        scenario_legs = clone_legs_with_new_iv(
            legs=legs,
            new_implied_volatility=scenario_iv,
        )

        x_values = []
        y_values = []

        for simulated_price in price_grid:
            simulated_market = MarketParams(
                underlying_price=simulated_price,
                risk_free_rate=market.risk_free_rate,
                dividend_yield=market.dividend_yield,
                valuation_date=scenario_date,
            )

            simulated_value = strategy_current_value(
                legs=scenario_legs,
                market=simulated_market,
            )

            simulated_pnl = simulated_value - initial_cost

            x_values.append(simulated_price)
            y_values.append(simulated_pnl)

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines",
                name=scenario_name,
                hovertemplate=(
                    f"{scenario_name}<br>"
                    "Prix sous-jacent simulé: %{x:.2f}<br>"
                    "P&L théorique: %{y:.2f}<extra></extra>"
                ),
            )
        )

    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="P&L = 0",
        annotation_position="top left",
    )

    fig.add_vline(
        x=market.underlying_price,
        line_dash="dot",
        annotation_text="Prix actuel",
        annotation_position="top",
    )

    fig.update_layout(
        title=title,
        xaxis_title="Prix simulé du sous-jacent",
        yaxis_title="P&L théorique",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig

def create_monthly_pnl_evolution_chart(
    monthly_table: list[dict],
    title: str = "Évolution mensuelle du P&L",
):
    """
    Crée un graphique Plotly montrant l'évolution du P&L théorique
    mois par mois.

    Le tableau mensuel doit contenir au minimum :
    - Scénario
    - Date simulée
    - P&L théorique
    """

    if not monthly_table:
        raise ValueError("Le tableau mensuel est vide")

    x_values = [row["Scénario"] for row in monthly_table]
    y_values = [float(row["P&L théorique"]) for row in monthly_table]

    dates = [row["Date simulée"] for row in monthly_table]
    underlying_prices = [row["Sous-jacent simulé"] for row in monthly_table]
    iv_values = [row["IV simulée"] for row in monthly_table]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x_values,
            y=y_values,
            mode="lines+markers",
            name="P&L théorique",
            customdata=list(zip(dates, underlying_prices, iv_values)),
            hovertemplate=(
                "Période: %{x}<br>"
                "Date: %{customdata[0]}<br>"
                "Sous-jacent simulé: %{customdata[1]}<br>"
                "IV simulée: %{customdata[2]}<br>"
                "P&L théorique: %{y:.2f}<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="P&L = 0",
        annotation_position="top left",
    )

    fig.update_layout(
        title=title,
        xaxis_title="Période simulée",
        yaxis_title="P&L théorique",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig

def create_monthly_greeks_evolution_chart(
    monthly_table: list[dict],
    title: str = "Évolution mensuelle des Greeks",
    selected_greek: str = "Tous",
):
    """
    Crée un graphique Plotly montrant l'évolution des Greeks mois par mois.

    selected_greek peut être :
    - "Tous"
    - "Delta"
    - "Gamma"
    - "Vega"
    - "Theta"
    - "Rho"
    """

    if not monthly_table:
        raise ValueError("Le tableau mensuel est vide")

    x_values = [row["Scénario"] for row in monthly_table]

    dates = [row["Date simulée"] for row in monthly_table]
    underlying_prices = [row["Sous-jacent simulé"] for row in monthly_table]
    iv_values = [row["IV simulée"] for row in monthly_table]

    custom_data = list(zip(dates, underlying_prices, iv_values))

    fig = go.Figure()

    all_greek_columns = [
        ("Delta", "Delta"),
        ("Gamma", "Gamma"),
        ("Vega", "Vega"),
        ("Theta / jour", "Theta"),
        ("Rho", "Rho"),
    ]

    if selected_greek == "Tous":
        greek_columns = all_greek_columns
    else:
        greek_columns = [
            item for item in all_greek_columns if item[1] == selected_greek
        ]

    for column_name, display_name in greek_columns:
        y_values = [float(row[column_name]) for row in monthly_table]

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers",
                name=display_name,
                customdata=custom_data,
                hovertemplate=(
                    f"{display_name}<br>"
                    "Période: %{x}<br>"
                    "Date: %{customdata[0]}<br>"
                    "Sous-jacent simulé: %{customdata[1]}<br>"
                    "IV simulée: %{customdata[2]}<br>"
                    "Valeur: %{y:.2f}<extra></extra>"
                ),
            )
        )

    fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="0",
        annotation_position="top left",
    )

    fig.update_layout(
        title=title,
        xaxis_title="Période simulée",
        yaxis_title="Valeur du Greek",
        hovermode="x unified",
        template="plotly_white",
    )

    return fig