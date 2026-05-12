from dataclasses import dataclass
from datetime import date


@dataclass
class OptionLeg:
    """
    Représente une jambe individuelle d'une stratégie d'options.

    Exemple :
    - long call : une jambe
    - vertical spread : deux jambes
    - butterfly : trois jambes
    - iron condor : quatre jambes
    """

    option_type: str
    side: str
    strike: float
    quantity: int
    expiry: date
    implied_volatility: float
    entry_price: float
    multiplier: int = 100

    def sign(self) -> int:
        """
        Retourne +1 pour une option achetée et -1 pour une option vendue.
        """
        if self.side == "buy":
            return 1
        if self.side == "sell":
            return -1

        raise ValueError("side doit être 'buy' ou 'sell'")

    def validate(self) -> None:
        """
        Vérifie que les paramètres de la jambe sont valides.
        """
        if self.option_type not in ["call", "put"]:
            raise ValueError("option_type doit être 'call' ou 'put'")

        if self.side not in ["buy", "sell"]:
            raise ValueError("side doit être 'buy' ou 'sell'")

        if self.strike <= 0:
            raise ValueError("Le strike doit être positif")

        if self.quantity <= 0:
            raise ValueError("La quantité doit être positive")

        if self.implied_volatility <= 0:
            raise ValueError("La volatilité implicite doit être positive")

        if self.entry_price < 0:
            raise ValueError("Le prix d'entrée ne peut pas être négatif")

        if self.multiplier <= 0:
            raise ValueError("Le multiplicateur doit être positif")

@dataclass
class StockLeg:
    """
    Représente une jambe action.

    Exemple :
    - achat de 100 actions
    - vente à découvert de 100 actions
    """

    side: str
    quantity: int
    entry_price: float
    multiplier: int = 1
    
@dataclass
class MarketParams:
    """
    Paramètres de marché nécessaires au pricing.
    """

    underlying_price: float
    risk_free_rate: float
    dividend_yield: float
    valuation_date: date

    def validate(self) -> None:
        """
        Vérifie que les paramètres de marché sont valides.
        """
        if self.underlying_price <= 0:
            raise ValueError("Le prix du sous-jacent doit être positif")

        if self.risk_free_rate < -1:
            raise ValueError("Le taux sans risque semble invalide")

        if self.dividend_yield < 0:
            raise ValueError("Le dividend yield ne peut pas être négatif")