def describe_cost_structure(initial_cost: float) -> str:
    """
    Commente la structure de coût de la stratégie.
    """

    if initial_cost > 0:
        return (
            f"La stratégie est ouverte en débit net : le coût initial est de "
            f"{initial_cost:.2f}. Cela signifie que la perte à l'échéance peut "
            f"inclure au minimum ce débit si la stratégie expire sans valeur."
        )

    if initial_cost < 0:
        return (
            f"La stratégie est ouverte en crédit net : le crédit initial reçu est de "
            f"{abs(initial_cost):.2f}. Une stratégie en crédit peut bénéficier du "
            f"passage du temps, mais elle peut aussi comporter un risque important "
            f"si le sous-jacent sort de la zone profitable."
        )

    return (
        "La stratégie a un coût initial net proche de zéro. Cela peut arriver "
        "lorsque les primes achetées et vendues se compensent."
    )


def describe_current_pnl(current_pnl: float) -> str:
    """
    Commente le P&L actuel.
    """

    if current_pnl > 0:
        return (
            f"Le P&L actuel théorique est positif : {current_pnl:.2f}. "
            "Selon les hypothèses utilisées, la valeur théorique actuelle de la "
            "position est supérieure à son coût initial."
        )

    if current_pnl < 0:
        return (
            f"Le P&L actuel théorique est négatif : {current_pnl:.2f}. "
            "Selon les hypothèses utilisées, la valeur théorique actuelle de la "
            "position est inférieure à son coût initial."
        )

    return (
        "Le P&L actuel théorique est proche de zéro. La valeur actuelle de la "
        "position est proche de son coût initial."
    )


def describe_breakevens(breakevens: list[float]) -> str:
    """
    Commente les break-even estimés.
    """

    if not breakevens:
        return (
            "Aucun break-even n'a été détecté sur la grille testée. Cela peut "
            "signifier que la position est toujours profitable ou toujours "
            "déficitaire dans l'intervalle de prix analysé."
        )

    if len(breakevens) == 1:
        return (
            f"Un break-even estimé a été détecté autour de {breakevens[0]:.2f}. "
            "À l'échéance, la stratégie devient théoriquement profitable d'un "
            "côté de ce niveau, selon la forme du payoff."
        )

    formatted = ", ".join([f"{be:.2f}" for be in breakevens])

    return (
        f"Plusieurs break-even estimés ont été détectés : {formatted}. "
        "Cela indique une stratégie avec une zone centrale ou extérieure de "
        "profit/perte, typique de structures comme les straddles, butterflies "
        "ou iron condors."
    )


def describe_profitable_ranges(profitable_ranges: list[dict]) -> str:
    """
    Commente les zones profitables.
    """

    if not profitable_ranges:
        return (
            "Aucune zone profitable n'a été détectée sur la grille testée. "
            "Il faut vérifier si la grille de prix est assez large ou si les "
            "paramètres de la stratégie sont cohérents."
        )

    if len(profitable_ranges) == 1:
        zone = profitable_ranges[0]
        return (
            f"La zone profitable estimée se situe entre {zone['from']:.2f} "
            f"et {zone['to']:.2f}. À l'échéance, le sous-jacent doit se trouver "
            "dans cette zone pour que le P&L net soit positif."
        )

    zones_text = "; ".join(
        [
            f"de {zone['from']:.2f} à {zone['to']:.2f}"
            for zone in profitable_ranges
        ]
    )

    return (
        f"Plusieurs zones profitables ont été détectées : {zones_text}. "
        "Cela correspond souvent à des stratégies qui profitent d'un mouvement "
        "important dans une direction ou dans les deux directions."
    )


def describe_delta(delta: float) -> str:
    """
    Commente le delta de la stratégie.
    """

    if delta > 50:
        return (
            f"Le delta est fortement positif ({delta:.2f}). La stratégie est "
            "directionnelle haussière : une hausse du sous-jacent tend à améliorer "
            "la valeur théorique de la position."
        )

    if delta > 10:
        return (
            f"Le delta est positif ({delta:.2f}). La stratégie a une exposition "
            "plutôt haussière au sous-jacent."
        )

    if delta < -50:
        return (
            f"Le delta est fortement négatif ({delta:.2f}). La stratégie est "
            "directionnelle baissière : une baisse du sous-jacent tend à améliorer "
            "la valeur théorique de la position."
        )

    if delta < -10:
        return (
            f"Le delta est négatif ({delta:.2f}). La stratégie a une exposition "
            "plutôt baissière au sous-jacent."
        )

    return (
        f"Le delta est proche de zéro ({delta:.2f}). La stratégie est relativement "
        "neutre directionnellement à cet instant, même si cela peut changer avec "
        "le mouvement du sous-jacent."
    )


def describe_gamma(gamma: float) -> str:
    """
    Commente le gamma de la stratégie.
    """

    if gamma > 1:
        return (
            f"Le gamma est positif ({gamma:.2f}). Le delta peut augmenter lorsque "
            "le sous-jacent monte et diminuer lorsqu'il baisse. La position est "
            "sensible aux mouvements du sous-jacent."
        )

    if gamma < -1:
        return (
            f"Le gamma est négatif ({gamma:.2f}). Le delta peut évoluer contre la "
            "position lors de mouvements importants du sous-jacent. Cela peut "
            "augmenter le risque dynamique."
        )

    return (
        f"Le gamma est relativement faible ({gamma:.2f}). La sensibilité du delta "
        "aux petits mouvements du sous-jacent semble modérée."
    )


def describe_vega(vega: float) -> str:
    """
    Commente le vega de la stratégie.
    """

    if vega > 5:
        return (
            f"Le vega est positif ({vega:.2f}). Une hausse de la volatilité "
            "implicite tend à augmenter la valeur théorique de la stratégie."
        )

    if vega < -5:
        return (
            f"Le vega est négatif ({vega:.2f}). Une baisse de la volatilité "
            "implicite tend à favoriser la stratégie, tandis qu'une hausse de "
            "volatilité peut la pénaliser."
        )

    return (
        f"Le vega est proche de zéro ({vega:.2f}). La stratégie semble peu sensible "
        "aux petites variations de volatilité implicite dans les hypothèses actuelles."
    )


def describe_theta(theta: float) -> str:
    """
    Commente le theta de la stratégie.
    """

    if theta > 1:
        return (
            f"Le theta est positif ({theta:.2f} par jour). Toutes choses égales par "
            "ailleurs, le passage du temps tend à favoriser la stratégie."
        )

    if theta < -1:
        return (
            f"Le theta est négatif ({theta:.2f} par jour). Toutes choses égales par "
            "ailleurs, le passage du temps tend à pénaliser la stratégie."
        )

    return (
        f"Le theta est proche de zéro ({theta:.2f} par jour). L'effet du passage "
        "du temps semble modéré dans les hypothèses actuelles."
    )


def describe_risk_reward(max_profit: float, max_loss: float) -> str:
    """
    Commente le rapport gain/perte estimé.
    """

    if max_loss >= 0:
        return (
            "La grille testée ne montre pas de perte nette. Il faut toutefois "
            "vérifier si la grille est suffisamment large et si la stratégie "
            "comporte un risque hors de l'intervalle analysé."
        )

    if max_profit <= 0:
        return (
            "La grille testée ne montre pas de gain net. Il faut vérifier les "
            "prix d'entrée, les strikes et la cohérence de la stratégie."
        )

    risk = abs(max_loss)
    reward = max_profit

    ratio = reward / risk if risk != 0 else None

    if ratio is None:
        return "Le rapport gain/perte ne peut pas être calculé."

    if ratio > 2:
        return (
            f"Le gain maximum estimé ({max_profit:.2f}) est nettement supérieur "
            f"à la perte maximum estimée ({max_loss:.2f}) sur la grille testée. "
            f"Le ratio gain/risque estimé est d'environ {ratio:.2f}."
        )

    if ratio >= 1:
        return (
            f"Le gain maximum estimé ({max_profit:.2f}) est supérieur ou comparable "
            f"à la perte maximum estimée ({max_loss:.2f}). Le ratio gain/risque "
            f"estimé est d'environ {ratio:.2f}."
        )

    return (
        f"Le gain maximum estimé ({max_profit:.2f}) est inférieur à la perte maximum "
        f"estimée ({max_loss:.2f}) sur la grille testée. Le ratio gain/risque estimé "
        f"est d'environ {ratio:.2f}."
    )


def generate_strategy_comments(
    initial_cost: float,
    current_pnl: float,
    greeks: dict,
    breakevens: list[float],
    max_profit: float,
    max_loss: float,
    profitable_ranges: list[dict],
) -> list[str]:
    """
    Génère une liste de commentaires automatiques sur la stratégie.
    """

    comments = []

    comments.append(describe_cost_structure(initial_cost))
    comments.append(describe_current_pnl(current_pnl))
    comments.append(describe_breakevens(breakevens))
    comments.append(describe_profitable_ranges(profitable_ranges))

    comments.append(describe_delta(greeks["delta"]))
    comments.append(describe_gamma(greeks["gamma"]))
    comments.append(describe_vega(greeks["vega"]))
    comments.append(describe_theta(greeks["theta"]))

    comments.append(describe_risk_reward(max_profit, max_loss))

    comments.append(
        "Ces commentaires sont basés sur les paramètres saisis et sur le modèle "
        "utilisé. Ils sont pédagogiques et ne constituent pas une recommandation "
        "d'achat, de vente ou de conservation."
    )

    return comments