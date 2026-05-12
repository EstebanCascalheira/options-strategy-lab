from datetime import date, timedelta

import pandas as pd
import streamlit as st

from strategies.templates import (
    create_long_call,
    create_long_put,
    create_short_call,
    create_short_put,
    create_vertical_call_spread,
    create_call_butterfly,
    create_iron_condor,
    create_long_straddle,
    create_long_strangle,
    create_short_straddle,
    create_short_strangle,
    create_put_credit_spread,
    create_call_credit_spread,
    create_put_debit_spread,
    create_iron_butterfly,
    create_call_broken_wing_butterfly,
    create_covered_call,
    create_protective_put,
    create_call_calendar_spread,
    create_put_calendar_spread,
    create_call_diagonal_spread,
    create_put_diagonal_spread,
)

from core.models import OptionLeg, StockLeg, MarketParams
from core.pnl import (
    strategy_current_value,
    strategy_initial_cost,
    strategy_pnl,
    strategy_greeks,
)
from analytics.breakeven import analyze_expiry_profile
from analytics.comments import generate_strategy_comments
from analytics.scenarios import (
    build_scenario_table,
    build_preset_scenarios,
    build_monthly_evolution_table,
    summarize_monthly_evolution,
)
from analytics.risk_metrics import (
    calculate_expiry_risk_metrics,
    format_risk_value,
)
from visualization.charts import (
    create_expiry_pnl_chart,
    create_theoretical_pnl_chart,
    create_scenario_theoretical_pnl_chart,
    create_monthly_pnl_evolution_chart,
    create_monthly_greeks_evolution_chart,
)


st.set_page_config(
    page_title="Options Strategy Lab",
    layout="wide",
)


st.markdown(
    """
    <style>
        .main-header {
            padding: 1.5rem 1.8rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #0f172a 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 2rem;
        }

        .main-header-title {
            font-size: 2.6rem;
            font-weight: 800;
            margin-bottom: 0.4rem;
            color: #f9fafb;
            letter-spacing: -0.03em;
        }

        .main-header-subtitle {
            font-size: 1.05rem;
            color: #d1d5db;
            margin-bottom: 1rem;
        }

        .main-header-badges {
            display: flex;
            gap: 0.6rem;
            flex-wrap: wrap;
        }

        .main-header-badge {
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.15);
            color: #93c5fd;
            font-size: 0.85rem;
            border: 1px solid rgba(147, 197, 253, 0.25);
        }
    </style>

    <div class="main-header">
        <div class="main-header-title">Options Strategy Lab</div>
        <div class="main-header-subtitle">
            Analyse théorique, scénarios, Greeks et visualisation de stratégies d’options.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================
# SIDEBAR : PARAMÈTRES GÉNÉRAUX
# ============================

st.sidebar.header("Paramètres de marché")

ticker = st.sidebar.text_input("Ticker / Nom de l'action", value="AAPL")

underlying_price = st.sidebar.number_input(
    "Prix actuel du sous-jacent",
    min_value=0.01,
    value=100.00,
    step=1.00,
)

valuation_date = st.sidebar.date_input(
    "Date de valorisation",
    value=date.today(),
)

expiry = st.sidebar.date_input(
    "Échéance",
    value=date(2026, 11, 11),
)

risk_free_rate_percent = st.sidebar.number_input(
    "Taux sans risque (%)",
    value=4.00,
    step=0.25,
)

dividend_yield_percent = st.sidebar.number_input(
    "Dividend yield (%)",
    value=0.00,
    step=0.25,
)

implied_volatility_percent = st.sidebar.number_input(
    "Volatilité implicite (%)",
    min_value=0.01,
    value=20.00,
    step=1.00,
)

multiplier = st.sidebar.number_input(
    "Multiplicateur",
    min_value=1,
    value=100,
    step=1,
)

quantity = st.sidebar.number_input(
    "Quantité",
    min_value=1,
    value=1,
    step=1,
)


risk_free_rate = risk_free_rate_percent / 100
dividend_yield = dividend_yield_percent / 100
implied_volatility = implied_volatility_percent / 100


market = MarketParams(
    underlying_price=underlying_price,
    risk_free_rate=risk_free_rate,
    dividend_yield=dividend_yield,
    valuation_date=valuation_date,
)

def legs_to_table(legs):
    """
    Transforme une liste de jambes en tableau éditable.
    Compatible avec :
    - OptionLeg
    - StockLeg
    """

    rows = []

    for i, leg in enumerate(legs, start=1):
        if isinstance(leg, StockLeg):
            rows.append(
                {
                    "Jambe": i,
                    "Type": "stock",
                    "Sens": leg.side,
                    "Strike": 0.0,
                    "Quantité": int(leg.quantity),
                    "Échéance": expiry,
                    "IV (%)": 0.0,
                    "Prix entrée": float(leg.entry_price),
                    "Multiplicateur": int(leg.multiplier),
                }
            )
        else:
            rows.append(
                {
                    "Jambe": i,
                    "Type": leg.option_type,
                    "Sens": leg.side,
                    "Strike": float(leg.strike),
                    "Quantité": int(leg.quantity),
                    "Échéance": leg.expiry,
                    "IV (%)": float(leg.implied_volatility * 100),
                    "Prix entrée": float(leg.entry_price),
                    "Multiplicateur": int(leg.multiplier),
                }
            )

    return rows


def table_to_legs(table_rows, expiry):
    """
    Reconstruit une liste de jambes depuis le tableau édité.
    Compatible avec :
    - options
    - actions
    """

    edited_legs = []

    for row in table_rows:
        leg_type = row["Type"]

        if leg_type == "stock":
            edited_legs.append(
                StockLeg(
                    side=row["Sens"],
                    quantity=int(row["Quantité"]),
                    entry_price=float(row["Prix entrée"]),
                    multiplier=int(row["Multiplicateur"]),
                )
            )
        else:
            edited_legs.append(
                OptionLeg(
                    option_type=leg_type,
                    side=row["Sens"],
                    strike=float(row["Strike"]),
                    quantity=int(row["Quantité"]),
                    expiry=row["Échéance"],
                    implied_volatility=float(row["IV (%)"]) / 100,
                    entry_price=float(row["Prix entrée"]),
                    multiplier=int(row["Multiplicateur"]),
                )
            )

    return edited_legs

def has_manual_changes(original_table, edited_table) -> bool:
    """
    Détecte si l'utilisateur a modifié les jambes générées automatiquement.

    On compare les colonnes importantes :
    - Type
    - Sens
    - Strike
    - Quantité
    - IV (%)
    - Prix entrée
    - Multiplicateur

    On ignore la colonne 'Jambe', qui sert seulement d'identifiant visuel.
    """

    columns_to_compare = [
        "Type",
        "Sens",
        "Strike",
        "Quantité",
        "Échéance",
        "IV (%)",
        "Prix entrée",
        "Multiplicateur",
    ]

    if len(original_table) != len(edited_table):
        return True

    for original_row, edited_row in zip(original_table, edited_table):
        for column in columns_to_compare:
            original_value = original_row[column]
            edited_value = edited_row[column]

            if isinstance(original_value, float) or isinstance(edited_value, float):
                if abs(float(original_value) - float(edited_value)) > 1e-9:
                    return True
            else:
                if original_value != edited_value:
                    return True

    return False
# ============================
# CHOIX DE LA STRATÉGIE
# ============================

st.sidebar.header("Stratégie")

strategy_name = st.sidebar.selectbox(
    "Choisir une stratégie",
    [
        "Long Call",
        "Long Put",
        "Short Call",
        "Short Put",
        "Vertical Call Debit Spread",
        "Put Debit Spread",
        "Call Credit Spread",
        "Put Credit Spread",
        "Call Butterfly",
        "Call Broken-Wing Butterfly",
        "Iron Condor",
        "Iron Butterfly",
        "Long Straddle",
        "Short Straddle",
        "Long Strangle",
        "Short Strangle",
        "Covered Call",
        "Protective Put",
        "Call Calendar Spread",
        "Put Calendar Spread",
        "Call Diagonal Spread",
        "Put Diagonal Spread",
    ],
)


st.header(f"Stratégie : {strategy_name}")
st.caption(f"Ticker : {ticker}")


# ============================
# FORMULAIRE STRATÉGIE
# ============================

legs = []


if strategy_name == "Long Call":
    st.subheader("Paramètres du Long Call")

    col1, col2 = st.columns(2)

    with col1:
        strike = st.number_input(
            "Strike du call",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

    with col2:
        entry_price = st.number_input(
            "Prix d'entrée du call",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    legs = create_long_call(
        strike=strike,
        expiry=expiry,
        quantity=quantity,
        implied_volatility=implied_volatility,
        entry_price=entry_price,
        multiplier=multiplier,
    )


elif strategy_name == "Long Put":
    st.subheader("Paramètres du Long Put")

    col1, col2 = st.columns(2)

    with col1:
        strike = st.number_input(
            "Strike du put",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

    with col2:
        entry_price = st.number_input(
            "Prix d'entrée du put",
            min_value=0.00,
            value=4.00,
            step=0.10,
        )

    legs = create_long_put(
        strike=strike,
        expiry=expiry,
        quantity=quantity,
        implied_volatility=implied_volatility,
        entry_price=entry_price,
        multiplier=multiplier,
    )

elif strategy_name == "Short Call":
    st.subheader("Paramètres du Short Call")

    col1, col2 = st.columns(2)

    with col1:
        strike = st.number_input(
            "Strike du call vendu",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

    with col2:
        entry_price = st.number_input(
            "Prime reçue du call",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    legs = create_short_call(
        strike=strike,
        expiry=expiry,
        quantity=quantity,
        implied_volatility=implied_volatility,
        entry_price=entry_price,
        multiplier=multiplier,
    )


elif strategy_name == "Short Put":
    st.subheader("Paramètres du Short Put")

    col1, col2 = st.columns(2)

    with col1:
        strike = st.number_input(
            "Strike du put vendu",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

    with col2:
        entry_price = st.number_input(
            "Prime reçue du put",
            min_value=0.00,
            value=4.00,
            step=0.10,
        )

    legs = create_short_put(
        strike=strike,
        expiry=expiry,
        quantity=quantity,
        implied_volatility=implied_volatility,
        entry_price=entry_price,
        multiplier=multiplier,
    )


elif strategy_name == "Vertical Call Debit Spread":
    st.subheader("Paramètres du Vertical Call Debit Spread")

    col1, col2 = st.columns(2)

    with col1:
        lower_strike = st.number_input(
            "Strike bas",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

        lower_entry_price = st.number_input(
            "Prix d'entrée call strike bas",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    with col2:
        upper_strike = st.number_input(
            "Strike haut",
            min_value=0.01,
            value=110.00,
            step=1.00,
        )

        upper_entry_price = st.number_input(
            "Prix d'entrée call strike haut",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    legs = create_vertical_call_spread(
        lower_strike=lower_strike,
        upper_strike=upper_strike,
        expiry=expiry,
        quantity=quantity,
        implied_volatility=implied_volatility,
        lower_entry_price=lower_entry_price,
        upper_entry_price=upper_entry_price,
        spread_type="debit",
        multiplier=multiplier,
    )


elif strategy_name == "Call Butterfly":
    st.subheader("Paramètres du Call Butterfly")

    col1, col2, col3 = st.columns(3)

    with col1:
        lower_strike = st.number_input(
            "Strike bas",
            min_value=0.01,
            value=90.00,
            step=1.00,
        )

        lower_entry_price = st.number_input(
            "Prix call strike bas",
            min_value=0.00,
            value=12.00,
            step=0.10,
        )

    with col2:
        middle_strike = st.number_input(
            "Strike central",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

        middle_entry_price = st.number_input(
            "Prix call strike central",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    with col3:
        upper_strike = st.number_input(
            "Strike haut",
            min_value=0.01,
            value=110.00,
            step=1.00,
        )

        upper_entry_price = st.number_input(
            "Prix call strike haut",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    legs = create_call_butterfly(
        lower_strike=lower_strike,
        middle_strike=middle_strike,
        upper_strike=upper_strike,
        expiry=expiry,
        quantity=quantity,
        implied_volatility=implied_volatility,
        lower_entry_price=lower_entry_price,
        middle_entry_price=middle_entry_price,
        upper_entry_price=upper_entry_price,
        multiplier=multiplier,
    )


elif strategy_name == "Iron Condor":
    st.subheader("Paramètres de l'Iron Condor")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        lower_put_strike = st.number_input(
            "Put acheté - strike bas",
            min_value=0.01,
            value=85.00,
            step=1.00,
        )

        lower_put_entry_price = st.number_input(
            "Prix put acheté",
            min_value=0.00,
            value=1.00,
            step=0.10,
        )

    with col2:
        upper_put_strike = st.number_input(
            "Put vendu - strike haut",
            min_value=0.01,
            value=90.00,
            step=1.00,
        )

        upper_put_entry_price = st.number_input(
            "Prix put vendu",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    with col3:
        lower_call_strike = st.number_input(
            "Call vendu - strike bas",
            min_value=0.01,
            value=110.00,
            step=1.00,
        )

        lower_call_entry_price = st.number_input(
            "Prix call vendu",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    with col4:
        upper_call_strike = st.number_input(
            "Call acheté - strike haut",
            min_value=0.01,
            value=115.00,
            step=1.00,
        )

        upper_call_entry_price = st.number_input(
            "Prix call acheté",
            min_value=0.00,
            value=1.00,
            step=0.10,
        )

    legs = create_iron_condor(
        lower_put_strike=lower_put_strike,
        upper_put_strike=upper_put_strike,
        lower_call_strike=lower_call_strike,
        upper_call_strike=upper_call_strike,
        expiry=expiry,
        quantity=quantity,
        implied_volatility=implied_volatility,
        lower_put_entry_price=lower_put_entry_price,
        upper_put_entry_price=upper_put_entry_price,
        lower_call_entry_price=lower_call_entry_price,
        upper_call_entry_price=upper_call_entry_price,
        multiplier=multiplier,
    )

elif strategy_name == "Long Straddle":
    st.subheader("Paramètres du Long Straddle")

    col1, col2, col3 = st.columns(3)

    with col1:
        strike = st.number_input(
            "Strike central",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

    with col2:
        call_entry_price = st.number_input(
            "Prix d'entrée du call",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    with col3:
        put_entry_price = st.number_input(
            "Prix d'entrée du put",
            min_value=0.00,
            value=4.00,
            step=0.10,
        )

    legs = create_long_straddle(
        strike=strike,
        expiry=expiry,
        quantity=quantity,
        call_entry_price=call_entry_price,
        put_entry_price=put_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )


elif strategy_name == "Long Strangle":
    st.subheader("Paramètres du Long Strangle")

    col1, col2 = st.columns(2)

    with col1:
        put_strike = st.number_input(
            "Strike du put",
            min_value=0.01,
            value=95.00,
            step=1.00,
        )

        put_entry_price = st.number_input(
            "Prix d'entrée du put",
            min_value=0.00,
            value=3.00,
            step=0.10,
        )

    with col2:
        call_strike = st.number_input(
            "Strike du call",
            min_value=0.01,
            value=105.00,
            step=1.00,
        )

        call_entry_price = st.number_input(
            "Prix d'entrée du call",
            min_value=0.00,
            value=3.00,
            step=0.10,
        )

    legs = create_long_strangle(
        put_strike=put_strike,
        call_strike=call_strike,
        expiry=expiry,
        quantity=quantity,
        put_entry_price=put_entry_price,
        call_entry_price=call_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Put Debit Spread":
    st.subheader("Paramètres du Put Debit Spread")

    col1, col2 = st.columns(2)

    with col1:
        lower_strike = st.number_input(
            "Strike bas du put vendu",
            min_value=0.01,
            value=90.00,
            step=1.00,
        )

        lower_entry_price = st.number_input(
            "Prix du put vendu",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    with col2:
        upper_strike = st.number_input(
            "Strike haut du put acheté",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

        upper_entry_price = st.number_input(
            "Prix du put acheté",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    legs = create_put_debit_spread(
        lower_strike=lower_strike,
        upper_strike=upper_strike,
        expiry=expiry,
        quantity=quantity,
        lower_entry_price=lower_entry_price,
        upper_entry_price=upper_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Call Credit Spread":
    st.subheader("Paramètres du Call Credit Spread")

    col1, col2 = st.columns(2)

    with col1:
        lower_strike = st.number_input(
            "Strike bas du call vendu",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

        lower_entry_price = st.number_input(
            "Prix du call vendu",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    with col2:
        upper_strike = st.number_input(
            "Strike haut du call acheté",
            min_value=0.01,
            value=110.00,
            step=1.00,
        )

        upper_entry_price = st.number_input(
            "Prix du call acheté",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    legs = create_call_credit_spread(
        lower_strike=lower_strike,
        upper_strike=upper_strike,
        expiry=expiry,
        quantity=quantity,
        lower_entry_price=lower_entry_price,
        upper_entry_price=upper_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Put Credit Spread":
    st.subheader("Paramètres du Put Credit Spread")

    col1, col2 = st.columns(2)

    with col1:
        lower_strike = st.number_input(
            "Strike bas du put acheté",
            min_value=0.01,
            value=90.00,
            step=1.00,
        )

        lower_entry_price = st.number_input(
            "Prix du put acheté",
            min_value=0.00,
            value=1.00,
            step=0.10,
        )

    with col2:
        upper_strike = st.number_input(
            "Strike haut du put vendu",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

        upper_entry_price = st.number_input(
            "Prix du put vendu",
            min_value=0.00,
            value=4.00,
            step=0.10,
        )

    legs = create_put_credit_spread(
        lower_strike=lower_strike,
        upper_strike=upper_strike,
        expiry=expiry,
        quantity=quantity,
        lower_entry_price=lower_entry_price,
        upper_entry_price=upper_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Short Straddle":
    st.subheader("Paramètres du Short Straddle")

    col1, col2, col3 = st.columns(3)

    with col1:
        strike = st.number_input(
            "Strike central",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

    with col2:
        call_entry_price = st.number_input(
            "Prime reçue du call",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    with col3:
        put_entry_price = st.number_input(
            "Prime reçue du put",
            min_value=0.00,
            value=4.00,
            step=0.10,
        )

    legs = create_short_straddle(
        strike=strike,
        expiry=expiry,
        quantity=quantity,
        call_entry_price=call_entry_price,
        put_entry_price=put_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Short Strangle":
    st.subheader("Paramètres du Short Strangle")

    col1, col2 = st.columns(2)

    with col1:
        put_strike = st.number_input(
            "Strike du put vendu",
            min_value=0.01,
            value=95.00,
            step=1.00,
        )

        put_entry_price = st.number_input(
            "Prime reçue du put",
            min_value=0.00,
            value=3.00,
            step=0.10,
        )

    with col2:
        call_strike = st.number_input(
            "Strike du call vendu",
            min_value=0.01,
            value=105.00,
            step=1.00,
        )

        call_entry_price = st.number_input(
            "Prime reçue du call",
            min_value=0.00,
            value=3.00,
            step=0.10,
        )

    legs = create_short_strangle(
        put_strike=put_strike,
        call_strike=call_strike,
        expiry=expiry,
        quantity=quantity,
        put_entry_price=put_entry_price,
        call_entry_price=call_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Iron Butterfly":
    st.subheader("Paramètres de l'Iron Butterfly")

    col1, col2, col3 = st.columns(3)

    with col1:
        lower_put_strike = st.number_input(
            "Put acheté - strike bas",
            min_value=0.01,
            value=90.00,
            step=1.00,
        )

        lower_put_entry_price = st.number_input(
            "Prix put acheté",
            min_value=0.00,
            value=1.00,
            step=0.10,
        )

    with col2:
        middle_strike = st.number_input(
            "Strike central vendu",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

        middle_put_entry_price = st.number_input(
            "Prix put vendu central",
            min_value=0.00,
            value=4.00,
            step=0.10,
        )

        middle_call_entry_price = st.number_input(
            "Prix call vendu central",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    with col3:
        upper_call_strike = st.number_input(
            "Call acheté - strike haut",
            min_value=0.01,
            value=110.00,
            step=1.00,
        )

        upper_call_entry_price = st.number_input(
            "Prix call acheté",
            min_value=0.00,
            value=1.00,
            step=0.10,
        )

    legs = create_iron_butterfly(
        lower_put_strike=lower_put_strike,
        middle_strike=middle_strike,
        upper_call_strike=upper_call_strike,
        expiry=expiry,
        quantity=quantity,
        lower_put_entry_price=lower_put_entry_price,
        middle_put_entry_price=middle_put_entry_price,
        middle_call_entry_price=middle_call_entry_price,
        upper_call_entry_price=upper_call_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Call Broken-Wing Butterfly":
    st.subheader("Paramètres du Call Broken-Wing Butterfly")

    col1, col2, col3 = st.columns(3)

    with col1:
        lower_strike = st.number_input(
            "Strike bas",
            min_value=0.01,
            value=95.00,
            step=1.00,
        )

        lower_entry_price = st.number_input(
            "Prix call strike bas",
            min_value=0.00,
            value=8.00,
            step=0.10,
        )

    with col2:
        middle_strike = st.number_input(
            "Strike central",
            min_value=0.01,
            value=100.00,
            step=1.00,
        )

        middle_entry_price = st.number_input(
            "Prix call strike central vendu",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    with col3:
        upper_strike = st.number_input(
            "Strike haut éloigné",
            min_value=0.01,
            value=115.00,
            step=1.00,
        )

        upper_entry_price = st.number_input(
            "Prix call strike haut",
            min_value=0.00,
            value=1.00,
            step=0.10,
        )

    legs = create_call_broken_wing_butterfly(
        lower_strike=lower_strike,
        middle_strike=middle_strike,
        upper_strike=upper_strike,
        expiry=expiry,
        quantity=quantity,
        lower_entry_price=lower_entry_price,
        middle_entry_price=middle_entry_price,
        upper_entry_price=upper_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Covered Call":
    st.subheader("Paramètres du Covered Call")

    col1, col2 = st.columns(2)

    with col1:
        stock_entry_price = st.number_input(
            "Prix d'achat de l'action",
            min_value=0.01,
            value=float(underlying_price),
            step=1.00,
        )

    with col2:
        call_strike = st.number_input(
            "Strike du call vendu",
            min_value=0.01,
            value=float(underlying_price * 1.05),
            step=1.00,
        )

        call_entry_price = st.number_input(
            "Prime reçue du call",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    legs = create_covered_call(
        stock_entry_price=stock_entry_price,
        call_strike=call_strike,
        expiry=expiry,
        quantity=quantity,
        call_entry_price=call_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Protective Put":
    st.subheader("Paramètres du Protective Put")

    col1, col2 = st.columns(2)

    with col1:
        stock_entry_price = st.number_input(
            "Prix d'achat de l'action",
            min_value=0.01,
            value=float(underlying_price),
            step=1.00,
        )

    with col2:
        put_strike = st.number_input(
            "Strike du put acheté",
            min_value=0.01,
            value=float(underlying_price * 0.95),
            step=1.00,
        )

        put_entry_price = st.number_input(
            "Prix du put acheté",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    legs = create_protective_put(
        stock_entry_price=stock_entry_price,
        put_strike=put_strike,
        expiry=expiry,
        quantity=quantity,
        put_entry_price=put_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Call Calendar Spread":
    st.subheader("Paramètres du Call Calendar Spread")

    col1, col2, col3 = st.columns(3)

    with col1:
        strike = st.number_input(
            "Strike",
            min_value=0.01,
            value=float(underlying_price),
            step=1.00,
        )

    with col2:
        near_expiry = st.date_input(
            "Échéance courte",
            value=valuation_date + timedelta(days=30),
        )

        near_entry_price = st.number_input(
            "Prix du call vendu court",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    with col3:
        far_expiry = st.date_input(
            "Échéance longue",
            value=valuation_date + timedelta(days=120),
        )

        far_entry_price = st.number_input(
            "Prix du call acheté long",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    legs = create_call_calendar_spread(
        strike=strike,
        near_expiry=near_expiry,
        far_expiry=far_expiry,
        quantity=quantity,
        near_entry_price=near_entry_price,
        far_entry_price=far_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Put Calendar Spread":
    st.subheader("Paramètres du Put Calendar Spread")

    col1, col2, col3 = st.columns(3)

    with col1:
        strike = st.number_input(
            "Strike",
            min_value=0.01,
            value=float(underlying_price),
            step=1.00,
        )

    with col2:
        near_expiry = st.date_input(
            "Échéance courte",
            value=valuation_date + timedelta(days=30),
        )

        near_entry_price = st.number_input(
            "Prix du put vendu court",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    with col3:
        far_expiry = st.date_input(
            "Échéance longue",
            value=valuation_date + timedelta(days=120),
        )

        far_entry_price = st.number_input(
            "Prix du put acheté long",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    legs = create_put_calendar_spread(
        strike=strike,
        near_expiry=near_expiry,
        far_expiry=far_expiry,
        quantity=quantity,
        near_entry_price=near_entry_price,
        far_entry_price=far_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Call Diagonal Spread":
    st.subheader("Paramètres du Call Diagonal Spread")

    col1, col2 = st.columns(2)

    with col1:
        short_strike = st.number_input(
            "Strike du call vendu court",
            min_value=0.01,
            value=float(underlying_price * 1.05),
            step=1.00,
        )

        near_expiry = st.date_input(
            "Échéance courte",
            value=valuation_date + timedelta(days=30),
        )

        short_entry_price = st.number_input(
            "Prix du call vendu court",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    with col2:
        long_strike = st.number_input(
            "Strike du call acheté long",
            min_value=0.01,
            value=float(underlying_price),
            step=1.00,
        )

        far_expiry = st.date_input(
            "Échéance longue",
            value=valuation_date + timedelta(days=120),
        )

        long_entry_price = st.number_input(
            "Prix du call acheté long",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    legs = create_call_diagonal_spread(
        short_strike=short_strike,
        long_strike=long_strike,
        near_expiry=near_expiry,
        far_expiry=far_expiry,
        quantity=quantity,
        short_entry_price=short_entry_price,
        long_entry_price=long_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

elif strategy_name == "Put Diagonal Spread":
    st.subheader("Paramètres du Put Diagonal Spread")

    col1, col2 = st.columns(2)

    with col1:
        short_strike = st.number_input(
            "Strike du put vendu court",
            min_value=0.01,
            value=float(underlying_price * 0.95),
            step=1.00,
        )

        near_expiry = st.date_input(
            "Échéance courte",
            value=valuation_date + timedelta(days=30),
        )

        short_entry_price = st.number_input(
            "Prix du put vendu court",
            min_value=0.00,
            value=2.00,
            step=0.10,
        )

    with col2:
        long_strike = st.number_input(
            "Strike du put acheté long",
            min_value=0.01,
            value=float(underlying_price),
            step=1.00,
        )

        far_expiry = st.date_input(
            "Échéance longue",
            value=valuation_date + timedelta(days=120),
        )

        long_entry_price = st.number_input(
            "Prix du put acheté long",
            min_value=0.00,
            value=5.00,
            step=0.10,
        )

    legs = create_put_diagonal_spread(
        short_strike=short_strike,
        long_strike=long_strike,
        near_expiry=near_expiry,
        far_expiry=far_expiry,
        quantity=quantity,
        short_entry_price=short_entry_price,
        long_entry_price=long_entry_price,
        implied_volatility=implied_volatility,
        multiplier=multiplier,
    )

# ============================
# CALCULS ET AFFICHAGE
# ============================

# ============================
# ÉDITEUR MANUEL DES JAMBES
# ============================

st.divider()
st.subheader("Éditeur manuel des jambes")

st.write(
    "Tu peux modifier chaque jambe de la stratégie avant les calculs. "
    "Les résultats seront recalculés automatiquement."
)

legs_table_default = legs_to_table(legs)

edited_legs_table = st.data_editor(
    legs_table_default,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Jambe": st.column_config.NumberColumn(
            "Jambe",
            disabled=True,
        ),
        "Type": st.column_config.SelectboxColumn(
            "Type",
            options=["call", "put", "stock"],
            required=True,
        ),
        "Échéance": st.column_config.DateColumn(
            "Échéance",
            required=True,
        ),
        "Sens": st.column_config.SelectboxColumn(
            "Sens",
            options=["buy", "sell"],
            required=True,
        ),
        "Strike": st.column_config.NumberColumn(
            "Strike",
            min_value=0.0,
            step=1.0,
            required=True,
        ),
        "Quantité": st.column_config.NumberColumn(
            "Quantité",
            min_value=1,
            step=1,
            required=True,
        ),
        "IV (%)": st.column_config.NumberColumn(
            "IV (%)",
            min_value=0.0,
            step=1.0,
            required=True,
        ),
        "Prix entrée": st.column_config.NumberColumn(
            "Prix entrée",
            min_value=0.0,
            step=0.1,
            required=True,
        ),
        "Multiplicateur": st.column_config.NumberColumn(
            "Multiplicateur",
            min_value=1,
            step=1,
            required=True,
        ),
    },
)

manual_changes_detected = has_manual_changes(
    original_table=legs_table_default,
    edited_table=edited_legs_table,
)

legs = table_to_legs(
    table_rows=edited_legs_table,
    expiry=expiry,
)

if manual_changes_detected:
    displayed_strategy_name = f"Stratégie personnalisée dérivée de {strategy_name}"
else:
    displayed_strategy_name = strategy_name

try:
    current_value = strategy_current_value(legs, market)
    initial_cost = strategy_initial_cost(legs)
    current_pnl = strategy_pnl(legs, market)
    greeks = strategy_greeks(legs, market)

    analysis = analyze_expiry_profile(
        legs=legs,
        current_underlying_price=underlying_price,
        lower_multiplier=0.5,
        upper_multiplier=1.5,
        steps=501,
    )

    breakevens = analysis["breakevens"]
    profitable_ranges = analysis["profitable_ranges"]

    risk_metrics = calculate_expiry_risk_metrics(legs)

    max_profit = risk_metrics["max_profit"]
    max_loss = risk_metrics["max_loss"]

    st.divider()

    if manual_changes_detected:
        st.warning(
            f"Les jambes ont été modifiées manuellement. "
            f"Les calculs ci-dessous correspondent à une stratégie personnalisée "
            f"dérivée de : {strategy_name}."
        )
    else:
        st.success(
            f"Les jambes correspondent au template standard : {strategy_name}."
        )
    
    st.write(f"**Stratégie utilisée pour les calculs :** {displayed_strategy_name}")

    tab_resume, tab_expiry, tab_scenarios, tab_monthly, tab_graphs, tab_export, tab_help = st.tabs(
        [
            "Résumé",
            "Échéance",
            "Scénarios",
            "Évolution mensuelle",
            "Graphiques",
            "Export",
            "Aide / Lecture",
        ]
    )

    def convert_table_to_csv(table_data):
        """
        Convertit une liste de dictionnaires en fichier CSV téléchargeable.
        """
        dataframe = pd.DataFrame(table_data)
        return dataframe.to_csv(index=False).encode("utf-8-sig")

    with tab_resume:
        st.subheader("Résumé de la position")

        col1, col2, col3 = st.columns(3)

        col1.metric("Valeur actuelle théorique", f"{current_value:,.2f}")
        col2.metric("Coût initial net", f"{initial_cost:,.2f}")
        col3.metric("P&L actuel théorique", f"{current_pnl:,.2f}")

        st.subheader("Greeks de la stratégie")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Delta", f"{greeks['delta']:.2f}")
        col2.metric("Gamma", f"{greeks['gamma']:.2f}")
        col3.metric("Vega", f"{greeks['vega']:.2f}")
        col4.metric("Theta / jour", f"{greeks['theta']:.2f}")
        col5.metric("Rho", f"{greeks['rho']:.2f}")

        st.subheader("Commentaires automatiques")

        comments = generate_strategy_comments(
            initial_cost=initial_cost,
            current_pnl=current_pnl,
            greeks=greeks,
            breakevens=breakevens,
            max_profit=max_profit,
            max_loss=max_loss,
            profitable_ranges=profitable_ranges,
        )

        st.markdown("#### Synthèse")

        for i, comment in enumerate(comments, start=1):
            st.markdown(f"**{i}.** {comment}")

        st.caption(
            "Commentaires générés automatiquement à partir des paramètres saisis. "
            "Ils sont pédagogiques et ne constituent pas une recommandation financière."
        )

        st.subheader("Jambes utilisées pour le calcul")

        legs_table = []

        for i, leg in enumerate(legs, start=1):
            if isinstance(leg, StockLeg):
                legs_table.append(
                    {
                        "Jambe": i,
                        "Type": "stock",
                        "Sens": leg.side,
                        "Strike": "",
                        "Quantité": leg.quantity,
                        "Échéance": "",
                        "IV": "",
                        "Prix entrée": leg.entry_price,
                        "Multiplicateur": leg.multiplier,
                    }
                )
            else:
                legs_table.append(
                    {
                        "Jambe": i,
                        "Type": leg.option_type,
                        "Sens": leg.side,
                        "Strike": leg.strike,
                        "Quantité": leg.quantity,
                        "Échéance": leg.expiry,
                        "IV": f"{leg.implied_volatility * 100:.2f}%",
                        "Prix entrée": leg.entry_price,
                        "Multiplicateur": leg.multiplier,
                    }
                )

        st.dataframe(legs_table, use_container_width=True)

    with tab_expiry:
        st.subheader("Analyse à l'échéance")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Break-even estimés",
            ", ".join([f"{be:.2f}" for be in breakevens]) if breakevens else "Aucun",
        )

        col2.metric(
            "Gain max théorique",
            format_risk_value(max_profit),
        )

        col3.metric(
            "Perte max théorique",
            format_risk_value(max_loss),
        )

        st.write("Zones profitables estimées sur la grille :")

        if profitable_ranges:
            for zone in profitable_ranges:
                st.write(f"- de {zone['from']:.2f} à {zone['to']:.2f}")
        else:
            st.write("- Aucune zone profitable détectée sur la grille testée.")

        st.subheader("Graphique du P&L à l'échéance")

        fig = create_expiry_pnl_chart(
            legs=legs,
            current_underlying_price=underlying_price,
            title=f"{displayed_strategy_name} - P&L à l'échéance",
            lower_multiplier=0.5,
            upper_multiplier=1.5,
            steps=501,
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab_graphs:
        st.subheader("Graphique du P&L théorique avant échéance")

        theoretical_fig = create_theoretical_pnl_chart(
            legs=legs,
            market=market,
            title=f"{displayed_strategy_name} - P&L théorique avant échéance",
            lower_multiplier=0.5,
            upper_multiplier=1.5,
            steps=501,
        )

        st.plotly_chart(theoretical_fig, use_container_width=True)
    
    with tab_help:
        st.subheader("Aide / Lecture des résultats")

        st.write(
            "Cet onglet explique comment interpréter les principaux résultats de l'application. "
            "Les calculs sont pédagogiques et dépendent entièrement des paramètres saisis manuellement."
        )

        st.divider()

        st.markdown("### 1. Résumé de la position")

        st.write(
            "**Valeur actuelle théorique** : estimation de la valeur de la stratégie selon le modèle utilisé "
            "et les hypothèses saisies."
        )

        st.write(
            "**Coût initial net** : montant payé ou reçu au départ. "
            "Un coût positif correspond généralement à un débit. "
            "Un coût négatif correspond généralement à un crédit."
        )

        st.write(
            "**P&L actuel théorique** : différence entre la valeur théorique actuelle et le coût initial. "
            "Il ne s'agit pas d'un prix de marché réel, mais d'une estimation selon les hypothèses."
        )

        st.divider()

        st.markdown("### 2. Analyse à l'échéance")

        st.write(
            "**Break-even** : niveau estimé du sous-jacent où le P&L à l'échéance passe autour de zéro."
        )

        st.write(
            "**Gain maximum estimé** : meilleur P&L observé sur la grille de prix testée. "
            "Attention : pour certaines stratégies, le gain peut être théoriquement illimité. "
            "Dans ce cas, l'application affiche seulement le meilleur résultat sur la plage testée."
        )

        st.write(
            "**Perte maximum estimée** : pire P&L observé sur la grille de prix testée. "
            "Là aussi, cela dépend de la plage de prix utilisée pour l'analyse."
        )

        st.write(
            "**Zones profitables** : zones de prix du sous-jacent où le P&L à l'échéance est positif "
            "sur la grille testée."
        )

        st.divider()

        st.markdown("### 3. Greeks")

        st.write(
            "**Delta** : sensibilité de la stratégie à une variation du prix du sous-jacent. "
            "Un delta positif indique une exposition plutôt haussière. "
            "Un delta négatif indique une exposition plutôt baissière."
        )

        st.write(
            "**Gamma** : sensibilité du delta aux variations du sous-jacent. "
            "Un gamma élevé signifie que le delta peut changer rapidement."
        )

        st.write(
            "**Vega** : sensibilité à la volatilité implicite. "
            "Un vega positif signifie qu'une hausse d'IV tend à augmenter la valeur théorique de la stratégie. "
            "Un vega négatif signifie l'inverse."
        )

        st.write(
            "**Theta** : sensibilité au passage du temps. "
            "Un theta négatif signifie que le temps tend à pénaliser la stratégie, toutes choses égales par ailleurs. "
            "Un theta positif signifie que le passage du temps peut être favorable."
        )

        st.write(
            "**Rho** : sensibilité au taux sans risque. "
            "Dans beaucoup de stratégies court terme, son impact est souvent plus faible que celui du delta, du vega ou du theta."
        )

        st.divider()

        st.markdown("### 4. Scénarios")

        st.write(
            "La section scénarios permet de comparer plusieurs hypothèses de temps écoulé, "
            "de volatilité implicite et de prix du sous-jacent."
        )

        st.write(
            "Le graphique de scénarios trace des courbes sur une plage de prix du sous-jacent. "
            "Le tableau de scénarios calcule des points précis, par exemple S=103, S=107 ou S=112."
        )

        st.write(
            "Les profils prédéfinis comme **Haussier**, **Baissier**, **Optimiste** ou **Pessimiste** "
            "sont des hypothèses pédagogiques. Ils ne prédisent pas le marché."
        )

        st.divider()

        st.markdown("### 5. Évolution mensuelle")

        st.write(
            "Le tableau mensuel montre comment la stratégie pourrait évoluer mois par mois jusqu'à l'échéance."
        )

        st.write(
            "Tu peux choisir un profil d'évolution du sous-jacent : stable, hausse progressive, baisse progressive "
            "ou trajectoire vers un prix final."
        )

        st.write(
            "Tu peux aussi choisir un profil d'évolution de la volatilité implicite : stable, hausse progressive, "
            "baisse progressive ou trajectoire vers une IV finale."
        )

        st.write(
            "Le résumé mensuel met en évidence le P&L initial, le P&L final, le meilleur point simulé, "
            "le pire point simulé et la tendance globale."
        )

        st.divider()

        st.markdown("### 6. Limites importantes")

        st.warning(
            "Cette application ne donne pas de recommandation d'achat, de vente ou de conservation. "
            "Elle sert à comprendre des comportements théoriques selon les hypothèses saisies."
        )

        st.write(
            "Les résultats dépendent fortement des hypothèses : volatilité implicite, taux, dividendes, temps restant, "
            "prix d'entrée et modèle utilisé."
        )

        st.write(
            "La version actuelle est sans API : les prix, IV et paramètres doivent être saisis manuellement."
        )

        st.write(
            "Les calculs reposent actuellement sur une logique de type Black-Scholes pour les options européennes. "
            "Les options américaines, l'exercice anticipé, les bid/ask réels, la liquidité et les frais ne sont pas encore modélisés."
        )

    with tab_scenarios:
        st.subheader("Comparaison de scénarios théoriques")

        st.write(
            "Ce graphique compare plusieurs hypothèses de temps restant, "
            "de volatilité implicite et de prix du sous-jacent. "
            "Le coût initial reste identique ; seules les conditions de valorisation changent."
        )

        scenario_chart_mode = st.selectbox(
            "Mode du graphique de scénarios",
            [
                "Manuel",
                "Neutre",
                "Haussier",
                "Baissier",
                "IV en hausse",
                "IV en baisse",
                "Optimiste",
                "Pessimiste",
            ],
            key="scenario_chart_mode",
        )

        if scenario_chart_mode == "Manuel":
            st.write(
                "Mode manuel : tu peux choisir les jours écoulés et l'IV pour chaque courbe."
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                scenario_1_days = st.number_input(
                    "Graphique - scénario 1 - jours écoulés",
                    min_value=0,
                    value=0,
                    step=1,
                )

                scenario_1_iv_percent = st.number_input(
                    "Graphique - scénario 1 - IV (%)",
                    min_value=0.01,
                    value=float(implied_volatility_percent),
                    step=1.0,
                )

            with col2:
                scenario_2_days = st.number_input(
                    "Graphique - scénario 2 - jours écoulés",
                    min_value=0,
                    value=30,
                    step=1,
                )

                scenario_2_iv_percent = st.number_input(
                    "Graphique - scénario 2 - IV (%)",
                    min_value=0.01,
                    value=float(implied_volatility_percent),
                    step=1.0,
                )

            with col3:
                scenario_3_days = st.number_input(
                    "Graphique - scénario 3 - jours écoulés",
                    min_value=0,
                    value=60,
                    step=1,
                )

                scenario_3_iv_percent = st.number_input(
                    "Graphique - scénario 3 - IV (%)",
                    min_value=0.01,
                    value=float(implied_volatility_percent + 5),
                    step=1.0,
                )

            scenario_1_date = valuation_date + timedelta(days=int(scenario_1_days))
            scenario_2_date = valuation_date + timedelta(days=int(scenario_2_days))
            scenario_3_date = valuation_date + timedelta(days=int(scenario_3_days))

            scenarios = [
                {
                    "name": f"J+{scenario_1_days} | IV {scenario_1_iv_percent:.1f}%",
                    "valuation_date": scenario_1_date,
                    "implied_volatility": scenario_1_iv_percent / 100,
                },
                {
                    "name": f"J+{scenario_2_days} | IV {scenario_2_iv_percent:.1f}%",
                    "valuation_date": scenario_2_date,
                    "implied_volatility": scenario_2_iv_percent / 100,
                },
                {
                    "name": f"J+{scenario_3_days} | IV {scenario_3_iv_percent:.1f}%",
                    "valuation_date": scenario_3_date,
                    "implied_volatility": scenario_3_iv_percent / 100,
                },
            ]

        else:
            st.write(
                f"Mode prédéfini : le graphique utilise le profil **{scenario_chart_mode}**."
            )

            preset_scenarios_for_chart = build_preset_scenarios(
                preset_name=scenario_chart_mode,
                current_underlying_price=underlying_price,
                current_implied_volatility=implied_volatility,
            )

            scenarios = []

            for preset in preset_scenarios_for_chart:
                scenario_date = valuation_date + timedelta(
                    days=int(preset["days_elapsed"])
                )

                scenarios.append(
                    {
                        "name": (
                            f"{preset['label']} | "
                            f"S={preset['underlying_price']:.2f} | "
                            f"IV {preset['implied_volatility'] * 100:.1f}%"
                        ),
                        "valuation_date": scenario_date,
                        "implied_volatility": preset["implied_volatility"],
                    }
                )

            chart_assumptions_table = []

            for preset in preset_scenarios_for_chart:
                chart_assumptions_table.append(
                    {
                        "Scénario": preset["label"],
                        "Jours écoulés": preset["days_elapsed"],
                        "Sous-jacent de référence": round(preset["underlying_price"], 2),
                        "IV simulée": f"{preset['implied_volatility'] * 100:.2f}%",
                    }
                )

            st.write("Hypothèses utilisées pour le graphique :")
            st.dataframe(
                chart_assumptions_table,
                use_container_width=True,
            )

        scenario_fig = create_scenario_theoretical_pnl_chart(
            legs=legs,
            market=market,
            scenarios=scenarios,
            title=f"{displayed_strategy_name} - comparaison de scénarios",
            lower_multiplier=0.5,
            upper_multiplier=1.5,
            steps=501,
        )

        st.plotly_chart(scenario_fig, use_container_width=True)

        st.subheader("Tableau de simulation des scénarios")

        st.write(
            "Ce tableau calcule la valeur théorique, le P&L et les Greeks "
            "pour plusieurs combinaisons de prix du sous-jacent, de temps écoulé "
            "et de volatilité implicite."
        )

        preset_name = st.selectbox(
            "Choisir un scénario prédéfini",
            [
                "Manuel",
                "Neutre",
                "Haussier",
                "Baissier",
                "IV en hausse",
                "IV en baisse",
                "Optimiste",
                "Pessimiste",
            ],
        )

        if preset_name == "Manuel":
            st.write(
                "Mode manuel : tu peux définir toi-même le prix du sous-jacent simulé "
                "pour chaque scénario. Les jours écoulés et l'IV viennent des champs "
                "de la section précédente."
            )

            st.write("Hypothèses manuelles pour le tableau :")

            day_col1, day_col2, day_col3 = st.columns(3)

            with day_col1:
                table_scenario_1_days = st.number_input(
                    "Tableau - scénario 1 - jours écoulés",
                    min_value=0,
                    value=0,
                    step=1,
                )

                table_scenario_1_iv_percent = st.number_input(
                    "Tableau - scénario 1 - IV (%)",
                    min_value=0.01,
                    value=float(implied_volatility_percent),
                    step=1.0,
                )

            with day_col2:
                table_scenario_2_days = st.number_input(
                    "Tableau - scénario 2 - jours écoulés",
                    min_value=0,
                    value=30,
                    step=1,
                )

                table_scenario_2_iv_percent = st.number_input(
                    "Tableau - scénario 2 - IV (%)",
                    min_value=0.01,
                    value=float(implied_volatility_percent),
                    step=1.0,
                )

            with day_col3:
                table_scenario_3_days = st.number_input(
                    "Tableau - scénario 3 - jours écoulés",
                    min_value=0,
                    value=60,
                    step=1,
                )

                table_scenario_3_iv_percent = st.number_input(
                    "Tableau - scénario 3 - IV (%)",
                    min_value=0.01,
                    value=float(implied_volatility_percent),
                    step=1.0,
                )

            col1, col2, col3 = st.columns(3)

            with col1:
                scenario_1_underlying = st.number_input(
                    "Scénario 1 - sous-jacent simulé",
                    min_value=0.01,
                    value=float(underlying_price),
                    step=1.0,
                )

            with col2:
                scenario_2_underlying = st.number_input(
                    "Scénario 2 - sous-jacent simulé",
                    min_value=0.01,
                    value=float(underlying_price * 1.05),
                    step=1.0,
                )

            with col3:
                scenario_3_underlying = st.number_input(
                    "Scénario 3 - sous-jacent simulé",
                    min_value=0.01,
                    value=float(underlying_price * 0.95),
                    step=1.0,
                )

            scenario_table_inputs = [
                {
                    "name": f"Scénario 1 | S={scenario_1_underlying:.2f}",
                    "days_elapsed": table_scenario_1_days,
                    "underlying_price": scenario_1_underlying,
                    "implied_volatility": table_scenario_1_iv_percent / 100,
                },
                {
                    "name": f"Scénario 2 | S={scenario_2_underlying:.2f}",
                    "days_elapsed": table_scenario_2_days,
                    "underlying_price": scenario_2_underlying,
                    "implied_volatility": table_scenario_2_iv_percent / 100,
                },
                {
                    "name": f"Scénario 3 | S={scenario_3_underlying:.2f}",
                    "days_elapsed": table_scenario_3_days,
                    "underlying_price": scenario_3_underlying,
                    "implied_volatility": table_scenario_3_iv_percent / 100,
                },
            ]

        else:
            st.write(
                f"Mode prédéfini : les hypothèses sont générées automatiquement "
                f"à partir du profil **{preset_name}**."
            )

            preset_scenarios = build_preset_scenarios(
                preset_name=preset_name,
                current_underlying_price=underlying_price,
                current_implied_volatility=implied_volatility,
            )

            scenario_table_inputs = []

            for preset in preset_scenarios:
                scenario_table_inputs.append(
                    {
                        "name": preset["label"],
                        "days_elapsed": preset["days_elapsed"],
                        "underlying_price": preset["underlying_price"],
                        "implied_volatility": preset["implied_volatility"],
                    }
                )

            assumptions_table = []

            for scenario in scenario_table_inputs:
                assumptions_table.append(
                    {
                        "Scénario": scenario["name"],
                        "Jours écoulés": scenario["days_elapsed"],
                        "Sous-jacent simulé": round(scenario["underlying_price"], 2),
                        "IV simulée": f"{scenario['implied_volatility'] * 100:.2f}%",
                    }
                )

            st.write("Hypothèses générées automatiquement :")
            st.dataframe(
                assumptions_table,
                use_container_width=True,
            )

        scenario_table = build_scenario_table(
            legs=legs,
            market=market,
            scenario_inputs=scenario_table_inputs,
        )

        st.write("Résultats des scénarios :")
        st.dataframe(
            scenario_table,
            use_container_width=True,
        )
    
    with tab_monthly : 
        st.subheader("Tableau d'évolution mensuelle")

        st.write(
            "Ce tableau simule l'évolution de la stratégie mois par mois jusqu'à "
            "l'échéance, selon un profil d'évolution du sous-jacent et de la volatilité implicite."
        )

        col1, col2 = st.columns(2)

        with col1:
            underlying_profile = st.selectbox(
                "Profil du sous-jacent",
                [
                    "Stable",
                    "Hausse progressive",
                    "Baisse progressive",
                    "Vers prix final",
                ],
            )

            final_underlying_price = st.number_input(
                "Prix final du sous-jacent à l'échéance",
                min_value=0.01,
                value=float(underlying_price),
                step=1.0,
            )

        with col2:
            iv_profile = st.selectbox(
                "Profil de volatilité implicite",
                [
                    "Stable",
                    "Hausse progressive",
                    "Baisse progressive",
                    "Vers IV finale",
                ],
            )

            final_iv_percent = st.number_input(
                "IV finale à l'échéance (%)",
                min_value=0.01,
                value=float(implied_volatility_percent),
                step=1.0,
            )

        monthly_table = build_monthly_evolution_table(
            legs=legs,
            market=market,
            expiry_date=expiry,
            underlying_profile=underlying_profile,
            iv_profile=iv_profile,
            final_underlying_price=final_underlying_price,
            final_implied_volatility=final_iv_percent / 100,
        )

        monthly_summary = summarize_monthly_evolution(monthly_table)

        st.write("Résumé de l'évolution mensuelle :")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "P&L initial",
            f"{monthly_summary['initial_pnl']:,.2f}",
        )

        col2.metric(
            "P&L final",
            f"{monthly_summary['final_pnl']:,.2f}",
            delta=f"{monthly_summary['pnl_change']:,.2f}",
        )

        col3.metric(
            "Tendance",
            monthly_summary["trend"].capitalize(),
        )

        col1, col2 = st.columns(2)

        with col1:
            st.info(
                f"Meilleur point simulé : "
                f"{monthly_summary['best_scenario']} "
                f"avec un P&L de {monthly_summary['best_pnl']:,.2f}."
            )

        with col2:
            st.warning(
                f"Pire point simulé : "
                f"{monthly_summary['worst_scenario']} "
                f"avec un P&L de {monthly_summary['worst_pnl']:,.2f}."
            )

        st.write(monthly_summary["trend_comment"])

        st.subheader("Graphique d'évolution mensuelle du P&L")

        monthly_pnl_fig = create_monthly_pnl_evolution_chart(
            monthly_table=monthly_table,
            title=f"{displayed_strategy_name} - évolution mensuelle du P&L",
        )

        st.plotly_chart(
            monthly_pnl_fig,
            use_container_width=True,
        )

        st.subheader("Graphique d'évolution mensuelle des Greeks")

        selected_monthly_greek = st.selectbox(
            "Greek à afficher",
            [
                "Tous",
                "Delta",
                "Gamma",
                "Vega",
                "Theta",
                "Rho",
            ],
        )

        monthly_greeks_fig = create_monthly_greeks_evolution_chart(
            monthly_table=monthly_table,
            title=f"{displayed_strategy_name} - évolution mensuelle des Greeks",
            selected_greek=selected_monthly_greek,
        )

        st.plotly_chart(
            monthly_greeks_fig,
            use_container_width=True,
        )

        st.dataframe(
            monthly_table,
            use_container_width=True,
        )
    
    with tab_export:
        st.subheader("Export des résultats")

        st.write(
            "Cette section permet de télécharger les principaux résultats de la simulation "
            "au format CSV pour les ouvrir dans Excel, Google Sheets ou les archiver."
        )

        st.divider()

        st.markdown("### 1. Jambes de la stratégie")

        st.write(
            "Ce fichier contient les jambes réellement utilisées pour les calculs, "
            "après éventuelles modifications manuelles."
        )

        legs_csv = convert_table_to_csv(legs_table)

        st.download_button(
            label="Télécharger les jambes en CSV",
            data=legs_csv,
            file_name=f"{ticker}_{displayed_strategy_name}_jambes.csv",
            mime="text/csv",
        )

        st.divider()

        st.markdown("### 2. Résultats des scénarios")

        st.write(
            "Ce fichier contient les résultats du tableau de scénarios : valeur théorique, "
            "P&L, Greeks et commentaire pour chaque hypothèse."
        )

        scenario_csv = convert_table_to_csv(scenario_table)

        st.download_button(
            label="Télécharger les scénarios en CSV",
            data=scenario_csv,
            file_name=f"{ticker}_{displayed_strategy_name}_scenarios.csv",
            mime="text/csv",
        )

        st.divider()

        st.markdown("### 3. Évolution mensuelle")

        st.write(
            "Ce fichier contient l'évolution mensuelle de la stratégie jusqu'à l'échéance."
        )

        monthly_csv = convert_table_to_csv(monthly_table)

        st.download_button(
            label="Télécharger l'évolution mensuelle en CSV",
            data=monthly_csv,
            file_name=f"{ticker}_{displayed_strategy_name}_evolution_mensuelle.csv",
            mime="text/csv",
        )

        st.divider()

        st.markdown("### Résumé exportable")

        export_summary = [
            {
                "Ticker": ticker,
                "Stratégie": displayed_strategy_name,
                "Prix sous-jacent": underlying_price,
                "Date de valorisation": valuation_date,
                "Échéance": expiry,
                "Valeur actuelle théorique": current_value,
                "Coût initial net": initial_cost,
                "P&L actuel théorique": current_pnl,
                "Delta": greeks["delta"],
                "Gamma": greeks["gamma"],
                "Vega": greeks["vega"],
                "Theta / jour": greeks["theta"],
                "Rho": greeks["rho"],
                "Break-even": ", ".join([f"{be:.2f}" for be in breakevens]),
                "Gain max estimé": max_profit,
                "Perte max estimée": max_loss,
            }
        ]

        summary_csv = convert_table_to_csv(export_summary)

        st.download_button(
            label="Télécharger le résumé en CSV",
            data=summary_csv,
            file_name=f"{ticker}_{displayed_strategy_name}_resume.csv",
            mime="text/csv",
        )

except Exception as error:
    st.error(f"Erreur dans les paramètres : {error}")

