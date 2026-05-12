from datetime import date

from core.black_scholes import year_fraction, black_scholes_price
from core.greeks import delta, gamma, vega, theta, rho


S = 100
K = 100
r = 0.04
q = 0.00
sigma = 0.20

valuation_date = date(2026, 5, 11)
expiry = date(2026, 11, 11)

T = year_fraction(valuation_date, expiry)

call_price = black_scholes_price("call", S, K, T, r, q, sigma)
put_price = black_scholes_price("put", S, K, T, r, q, sigma)

print("=== PARAMÈTRES ===")
print("Prix sous-jacent :", S)
print("Strike :", K)
print("Temps restant :", round(T, 4))
print("Taux sans risque :", r)
print("Dividend yield :", q)
print("Volatilité implicite :", sigma)

print("\n=== PRIX BLACK-SCHOLES ===")
print("Call :", round(call_price, 4))
print("Put  :", round(put_price, 4))

print("\n=== GREEKS CALL ===")
print("Delta :", round(delta("call", S, K, T, r, q, sigma), 4))
print("Gamma :", round(gamma(S, K, T, r, q, sigma), 4))
print("Vega  :", round(vega(S, K, T, r, q, sigma), 4))
print("Theta :", round(theta("call", S, K, T, r, q, sigma), 4))
print("Rho   :", round(rho("call", S, K, T, r, q, sigma), 4))

print("\n=== GREEKS PUT ===")
print("Delta :", round(delta("put", S, K, T, r, q, sigma), 4))
print("Gamma :", round(gamma(S, K, T, r, q, sigma), 4))
print("Vega  :", round(vega(S, K, T, r, q, sigma), 4))
print("Theta :", round(theta("put", S, K, T, r, q, sigma), 4))
print("Rho   :", round(rho("put", S, K, T, r, q, sigma), 4))