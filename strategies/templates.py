from datetime import date

from core.models import OptionLeg, StockLeg


def create_long_call(
    strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée une stratégie long call.

    Structure :
    +1 call
    """

    return [
        OptionLeg(
            option_type="call",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=entry_price,
            multiplier=multiplier,
        )
    ]


def create_long_put(
    strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée une stratégie long put.

    Structure :
    +1 put
    """

    return [
        OptionLeg(
            option_type="put",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=entry_price,
            multiplier=multiplier,
        )
    ]


def create_vertical_call_spread(
    lower_strike: float,
    upper_strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    lower_entry_price: float,
    upper_entry_price: float,
    spread_type: str = "debit",
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un vertical call spread.

    Debit call spread :
    - achat call strike bas
    - vente call strike haut

    Credit call spread :
    - vente call strike bas
    - achat call strike haut
    """

    if lower_strike >= upper_strike:
        raise ValueError("lower_strike doit être inférieur à upper_strike")

    if spread_type == "debit":
        lower_side = "buy"
        upper_side = "sell"
    elif spread_type == "credit":
        lower_side = "sell"
        upper_side = "buy"
    else:
        raise ValueError("spread_type doit être 'debit' ou 'credit'")

    return [
        OptionLeg(
            option_type="call",
            side=lower_side,
            strike=lower_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side=upper_side,
            strike=upper_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_vertical_put_spread(
    lower_strike: float,
    upper_strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    lower_entry_price: float,
    upper_entry_price: float,
    spread_type: str = "debit",
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un vertical put spread.

    Debit put spread :
    - achat put strike haut
    - vente put strike bas

    Credit put spread :
    - vente put strike haut
    - achat put strike bas
    """

    if lower_strike >= upper_strike:
        raise ValueError("lower_strike doit être inférieur à upper_strike")

    if spread_type == "debit":
        lower_side = "sell"
        upper_side = "buy"
    elif spread_type == "credit":
        lower_side = "buy"
        upper_side = "sell"
    else:
        raise ValueError("spread_type doit être 'debit' ou 'credit'")

    return [
        OptionLeg(
            option_type="put",
            side=lower_side,
            strike=lower_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side=upper_side,
            strike=upper_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_long_straddle(
    strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    call_entry_price: float,
    put_entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un long straddle.

    Structure :
    +1 call ATM
    +1 put ATM
    """

    return [
        OptionLeg(
            option_type="call",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=call_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=put_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_long_strangle(
    put_strike: float,
    call_strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    put_entry_price: float,
    call_entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un long strangle.

    Structure :
    +1 put OTM
    +1 call OTM
    """

    if put_strike >= call_strike:
        raise ValueError("put_strike doit être inférieur à call_strike")

    return [
        OptionLeg(
            option_type="put",
            side="buy",
            strike=put_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=put_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=call_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=call_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_call_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    lower_entry_price: float,
    middle_entry_price: float,
    upper_entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un call butterfly classique.

    Structure :
    +1 call strike bas
    -2 calls strike central
    +1 call strike haut
    """

    if not lower_strike < middle_strike < upper_strike:
        raise ValueError("Les strikes doivent respecter lower < middle < upper")

    return [
        OptionLeg(
            option_type="call",
            side="buy",
            strike=lower_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="sell",
            strike=middle_strike,
            quantity=2 * quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=middle_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=upper_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_iron_condor(
    lower_put_strike: float,
    upper_put_strike: float,
    lower_call_strike: float,
    upper_call_strike: float,
    expiry: date,
    quantity: int,
    implied_volatility: float,
    lower_put_entry_price: float,
    upper_put_entry_price: float,
    lower_call_entry_price: float,
    upper_call_entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un iron condor classique.

    Structure :
    +1 put strike bas
    -1 put strike haut
    -1 call strike bas
    +1 call strike haut

    Exemple typique :
    + put 85
    - put 90
    - call 110
    + call 115
    """

    if not lower_put_strike < upper_put_strike < lower_call_strike < upper_call_strike:
        raise ValueError(
            "Les strikes doivent respecter : "
            "lower_put < upper_put < lower_call < upper_call"
        )

    return [
        OptionLeg(
            option_type="put",
            side="buy",
            strike=lower_put_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_put_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="sell",
            strike=upper_put_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_put_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="sell",
            strike=lower_call_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_call_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=upper_call_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_call_entry_price,
            multiplier=multiplier,
        ),
    ]

def create_short_call(
    strike: float,
    expiry,
    quantity: int,
    implied_volatility: float,
    entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée une stratégie short call simple.
    """

    return [
        OptionLeg(
            option_type="call",
            side="sell",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=entry_price,
            multiplier=multiplier,
        )
    ]


def create_short_put(
    strike: float,
    expiry,
    quantity: int,
    implied_volatility: float,
    entry_price: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée une stratégie short put simple.
    """

    return [
        OptionLeg(
            option_type="put",
            side="sell",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=entry_price,
            multiplier=multiplier,
        )
    ]


def create_long_straddle(
    strike: float,
    expiry,
    quantity: int,
    call_entry_price: float,
    put_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un long straddle :
    - achat d'un call
    - achat d'un put
    même strike, même échéance.
    """

    return [
        OptionLeg(
            option_type="call",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=call_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=put_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_long_strangle(
    put_strike: float,
    call_strike: float,
    expiry,
    quantity: int,
    put_entry_price: float,
    call_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Crée un long strangle :
    - achat d'un put OTM
    - achat d'un call OTM
    strikes différents, même échéance.
    """

    return [
        OptionLeg(
            option_type="put",
            side="buy",
            strike=put_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=put_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=call_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=call_entry_price,
            multiplier=multiplier,
        ),
    ]

def create_short_straddle(
    strike: float,
    expiry,
    quantity: int,
    call_entry_price: float,
    put_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    return [
        OptionLeg(
            option_type="call",
            side="sell",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=call_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="sell",
            strike=strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=put_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_short_strangle(
    put_strike: float,
    call_strike: float,
    expiry,
    quantity: int,
    put_entry_price: float,
    call_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    return [
        OptionLeg(
            option_type="put",
            side="sell",
            strike=put_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=put_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="sell",
            strike=call_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=call_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_put_credit_spread(
    lower_strike: float,
    upper_strike: float,
    expiry,
    quantity: int,
    lower_entry_price: float,
    upper_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Put Credit Spread :
    - achat put strike bas
    - vente put strike haut
    """

    return [
        OptionLeg(
            option_type="put",
            side="buy",
            strike=lower_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="sell",
            strike=upper_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_call_credit_spread(
    lower_strike: float,
    upper_strike: float,
    expiry,
    quantity: int,
    lower_entry_price: float,
    upper_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Call Credit Spread :
    - vente call strike bas
    - achat call strike haut
    """

    return [
        OptionLeg(
            option_type="call",
            side="sell",
            strike=lower_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=upper_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_put_debit_spread(
    lower_strike: float,
    upper_strike: float,
    expiry,
    quantity: int,
    lower_entry_price: float,
    upper_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Put Debit Spread :
    - achat put strike haut
    - vente put strike bas
    """

    return [
        OptionLeg(
            option_type="put",
            side="sell",
            strike=lower_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="buy",
            strike=upper_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_iron_butterfly(
    lower_put_strike: float,
    middle_strike: float,
    upper_call_strike: float,
    expiry,
    quantity: int,
    lower_put_entry_price: float,
    middle_put_entry_price: float,
    middle_call_entry_price: float,
    upper_call_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Iron Butterfly :
    - achat put OTM
    - vente put ATM
    - vente call ATM
    - achat call OTM
    """

    return [
        OptionLeg(
            option_type="put",
            side="buy",
            strike=lower_put_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_put_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="sell",
            strike=middle_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=middle_put_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="sell",
            strike=middle_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=middle_call_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=upper_call_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_call_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_call_broken_wing_butterfly(
    lower_strike: float,
    middle_strike: float,
    upper_strike: float,
    expiry,
    quantity: int,
    lower_entry_price: float,
    middle_entry_price: float,
    upper_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Call Broken-Wing Butterfly :
    - achat call strike bas
    - vente 2 calls strike central
    - achat call strike haut
    Les distances entre strikes peuvent être asymétriques.
    """

    return [
        OptionLeg(
            option_type="call",
            side="buy",
            strike=lower_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=lower_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="sell",
            strike=middle_strike,
            quantity=quantity * 2,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=middle_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=upper_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=upper_entry_price,
            multiplier=multiplier,
        ),
    ]

def create_covered_call(
    stock_entry_price: float,
    call_strike: float,
    expiry,
    quantity: int,
    call_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list:
    """
    Covered Call :
    - achat de l'action
    - vente d'un call
    """

    return [
        StockLeg(
            side="buy",
            quantity=quantity * multiplier,
            entry_price=stock_entry_price,
            multiplier=1,
        ),
        OptionLeg(
            option_type="call",
            side="sell",
            strike=call_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=call_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_protective_put(
    stock_entry_price: float,
    put_strike: float,
    expiry,
    quantity: int,
    put_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list:
    """
    Protective Put :
    - achat de l'action
    - achat d'un put de protection
    """

    return [
        StockLeg(
            side="buy",
            quantity=quantity * multiplier,
            entry_price=stock_entry_price,
            multiplier=1,
        ),
        OptionLeg(
            option_type="put",
            side="buy",
            strike=put_strike,
            quantity=quantity,
            expiry=expiry,
            implied_volatility=implied_volatility,
            entry_price=put_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_call_calendar_spread(
    strike: float,
    near_expiry,
    far_expiry,
    quantity: int,
    near_entry_price: float,
    far_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Call Calendar Spread :
    - vente call échéance courte
    - achat call échéance longue
    même strike.
    """

    return [
        OptionLeg(
            option_type="call",
            side="sell",
            strike=strike,
            quantity=quantity,
            expiry=near_expiry,
            implied_volatility=implied_volatility,
            entry_price=near_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=far_expiry,
            implied_volatility=implied_volatility,
            entry_price=far_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_put_calendar_spread(
    strike: float,
    near_expiry,
    far_expiry,
    quantity: int,
    near_entry_price: float,
    far_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Put Calendar Spread :
    - vente put échéance courte
    - achat put échéance longue
    même strike.
    """

    return [
        OptionLeg(
            option_type="put",
            side="sell",
            strike=strike,
            quantity=quantity,
            expiry=near_expiry,
            implied_volatility=implied_volatility,
            entry_price=near_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="buy",
            strike=strike,
            quantity=quantity,
            expiry=far_expiry,
            implied_volatility=implied_volatility,
            entry_price=far_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_call_diagonal_spread(
    short_strike: float,
    long_strike: float,
    near_expiry,
    far_expiry,
    quantity: int,
    short_entry_price: float,
    long_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Call Diagonal Spread :
    - vente call échéance courte
    - achat call échéance longue
    strikes différents.
    """

    return [
        OptionLeg(
            option_type="call",
            side="sell",
            strike=short_strike,
            quantity=quantity,
            expiry=near_expiry,
            implied_volatility=implied_volatility,
            entry_price=short_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="call",
            side="buy",
            strike=long_strike,
            quantity=quantity,
            expiry=far_expiry,
            implied_volatility=implied_volatility,
            entry_price=long_entry_price,
            multiplier=multiplier,
        ),
    ]


def create_put_diagonal_spread(
    short_strike: float,
    long_strike: float,
    near_expiry,
    far_expiry,
    quantity: int,
    short_entry_price: float,
    long_entry_price: float,
    implied_volatility: float,
    multiplier: int = 100,
) -> list[OptionLeg]:
    """
    Put Diagonal Spread :
    - vente put échéance courte
    - achat put échéance longue
    strikes différents.
    """

    return [
        OptionLeg(
            option_type="put",
            side="sell",
            strike=short_strike,
            quantity=quantity,
            expiry=near_expiry,
            implied_volatility=implied_volatility,
            entry_price=short_entry_price,
            multiplier=multiplier,
        ),
        OptionLeg(
            option_type="put",
            side="buy",
            strike=long_strike,
            quantity=quantity,
            expiry=far_expiry,
            implied_volatility=implied_volatility,
            entry_price=long_entry_price,
            multiplier=multiplier,
        ),
    ]