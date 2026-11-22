#!/usr/bin/env python3
"""kWh per dollar: income method vs. generating on the roof.

Converts what an asset can *earn* into what it can *buy*, in the only unit that
matters here — kilowatt-hours at the tariff. Answers the question "is trading
capital a more scalable way to secure energy than building kilowatts?" with
arithmetic instead of opinion.

Method is stated, every input is either measured from price history or a named
market rate. Nothing is a forecast.

    python3 income_to_kwh.py
"""
import json, math, datetime, statistics

SPOT = {"gold": 3515.40, "silver": 41.07}   # 2026-11-20 settles
FILES = {"gold": "/root/.hermes/cache/scratch/y_gold.json",
         "silver": "/root/.hermes/cache/scratch/y_silver.json"}

SOFR = 0.0391              # published SOFR, 2026-11-19
UTILITY = 0.53956          # SDG&E TOU-DR1 off-peak
EXPORT = 0.54              # NEM 2.0 full-retail export credit
DELTA = 0.30               # short-call strike at 30 delta
DTE = 30                   # days to expiry
CAPITAL = 10_000.0


def ncdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def realized_vol(path, window):
    d = json.load(open(path))
    r = d["chart"]["result"][0]
    cl = [c for c in r["indicators"]["quote"][0]["close"] if c]
    cl = cl[-(window + 1):]
    rets = [math.log(cl[i] / cl[i - 1]) for i in range(1, len(cl))]
    return statistics.stdev(rets) * math.sqrt(252)


def short_call_yield(S, vol, r=SOFR, T=DTE / 365):
    """Premium as a fraction of spot for a call struck at N(d1)=DELTA."""
    d1_target = -0.5244 if DELTA == 0.30 else None
    if d1_target is None:
        raise ValueError("only the 30-delta point is tabulated")
    sd = vol * math.sqrt(T)
    lnS_K = d1_target * sd - (r + vol**2 / 2) * T
    K = S * math.exp(-lnS_K)
    d1 = (math.log(S / K) + (r + vol**2 / 2) * T) / sd
    d2 = d1 - sd
    prem = S * ncdf(d1) - K * math.exp(-r * T) * ncdf(d2)
    return prem, prem / S, K


def main():
    print(f"{'asset':7} {'vol60':>7} {'annualised':>11} {'strike':>9} "
          f"{'prem/spot':>10} {'$/yr on $10k':>13} {'kWh/yr bought':>14}")
    rows = []
    for name, spot in SPOT.items():
        vol60 = realized_vol(FILES[name], 60)
        prem, ratio, K = short_call_yield(spot, vol60)
        annual = ratio * (365 / DTE)
        usd_yr = CAPITAL * annual
        kwh_yr = usd_yr / UTILITY
        rows.append((name, vol60, annual, K, ratio, usd_yr, kwh_yr))
        print(f"{name:7} {vol60*100:6.1f}% {annual*100:10.1f}% {K:9,.2f} "
              f"{ratio*100:9.2f}% {usd_yr:13,.0f} {kwh_yr:14,.0f}")

    print("\n--- the generating comparison ---")
    solar_usd_per_w = 2.57
    pv_kw, kwh_day = 1.11, 4.0
    capex = pv_kw * 1000 * solar_usd_per_w
    gen = kwh_day * 365
    print(f"  PV {pv_kw} kW costs ${capex:,.0f} and yields {gen:,.0f} kWh/yr")
    print(f"  -> ${capex/gen:,.2f} of CAPEX per kWh/yr of output")
    best = max(rows, key=lambda r: r[6])
    print(f"  best income leg ({best[0]}) buys {best[6]:,.0f} kWh/yr on the same "
          f"$10k while keeping the capital")
    print(f"  -> ${CAPITAL/best[6]:,.2f} of CAPITAL per kWh/yr, capital retained")

    print("\n--- caveats that change the answer ---")
    print(f"  * annualising a 30-day premium x{365//DTE} assumes re-selling every cycle "
          f"at the same vol; it ignores assignment.")
    print(f"  * at {DELTA:.0%} delta the short call is ITM ~{DELTA:.0%} of the time at "
          f"expiry: you part with the asset at the strike on the way up.")
    print(f"  * a call written against a crisis hedge caps it exactly when it is "
          f"needed; income must come from the excess, never the core.")
    print(f"  * export credit ${EXPORT:.2f} vs import ${UTILITY:.5f}: ratio "
          f"{EXPORT/UTILITY:.4f} — self-consumption is worth ~0 here, so the PV "
          f"column buys capability, not kWh.")


if __name__ == "__main__":
    main()
