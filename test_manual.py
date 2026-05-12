from datetime import date

from core.black_scholes import (
    year_fraction,
    calculate_d1,
    calculate_d2,
    black_scholes_price,
    intrinsic_value,
    time_value,
)


S = 100
K = 100
r = 0.04
q = 0.00
sigma = 0.20

valuation_date = date(2026, 5, 11)
expiry = date(2026, 11, 11)

T = year_fraction(valuation_date, expiry)

d1 = calculate_d1(S, K, T, r, q, sigma)
d2 = calculate_d2(d1, sigma, T)

call_price = black_scholes_price(
    option_type="call",
    S=S,
    K=K,
    T=T,
    r=r,
    q=q,
    sigma=sigma,
)

put_price = black_scholes_price(
    option_type="put",
    S=S,
    K=K,
    T=T,
    r=r,
    q=q,
    sigma=sigma,
)

print("Temps restant en années :", round(T, 4))
print("d1 :", round(d1, 4))
print("d2 :", round(d2, 4))
print("Prix théorique call :", round(call_price, 4))
print("Prix théorique put :", round(put_price, 4))
print("Valeur intrinsèque call :", intrinsic_value("call", S, K))
print("Valeur temps call :", round(time_value(call_price, "call", S, K), 4))