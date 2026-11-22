#!/usr/bin/env python3
"""Shed energy sizing — physics first, cost second, both labelled.

Sizes an off-grid/standalone supply for a remote outbuilding served (or not) by a
limited grid feed, then prices it against stated benchmarks. Designed for the
case where the house feed is a 10A/120V GFCI circuit, i.e. 1.2 kW continuous,
which is below the peak draw of most workshop loads.

Every assumption is a named parameter with the default shown. Nothing is
estimated silently; override anything and the output changes.

    python3 shed_sizing.py --kwh-day 4 --peak-kw 3.0 --autonomy-h 24
    python3 shed_sizing.py --table
"""
import argparse

# ---- stated defaults (override on the command line) -------------------------
PSH_DEFAULT = 4.5      # peak sun hours, San Diego winter-low design month
DERATE_DEFAULT = 0.80  # soiling, wiring, temperature, inverter losses
DOD_DEFAULT = 0.90     # depth of discharge, LFP
RTE_DEFAULT = 0.90     # round-trip efficiency, LFP + inverter
INV_MARGIN = 1.25      # continuous inverter rating vs continuous load
SURGE = 2.0            # motor/spindle inrush multiple

# Grid feed: 10 A x 120 V
FEED_AMPS, FEED_VOLTS = 10, 120

# ---- cost benchmarks (sourced, dated; replace with local quotes) ------------
SOLAR_USD_PER_W = 2.57      # EnergySage marketplace median, Jan-Jun 2026 (pv-magazine 2026-10-24)
SOLAR_USD_PER_W_DIY = 1.00  # equipment-only placeholder range low end; NOT a quote
BATT_USD_PER_KWH_LO = 342   # EnergySage, MidNite Solar, 2026
BATT_USD_PER_KWH_HI = 1149  # EnergySage, EG4, 2026
UTILITY_USD_PER_KWH = 0.53956   # SDG&E TOU-DR1 off-peak (user-supplied)
EXPORT_CREDIT = 0.54           # NEM 2.0 full-retail export credit (user-supplied)


def size(kwh_day, peak_kw, autonomy_h, psh, derate, dod, rte):
    feed_kw = FEED_AMPS * FEED_VOLTS / 1000.0
    pv_kw = kwh_day / (psh * derate) if psh * derate > 0 else float("nan")
    batt_kwh = (kwh_day * autonomy_h / 24.0) / (dod * rte)
    inv_kw = peak_kw * INV_MARGIN
    return {
        "feed_kw_max": round(feed_kw, 2),
        "peak_exceeds_feed": peak_kw > feed_kw,
        "peak_excess_kw": round(max(0.0, peak_kw - feed_kw), 2),
        "pv_kw": round(pv_kw, 2),
        "battery_kwh": round(batt_kwh, 2),
        "inverter_kw": round(inv_kw, 2),
        "inverter_surge_kw": round(inv_kw * SURGE, 2),
    }


def price(s):
    pv_w = s["pv_kw"] * 1000.0
    return {
        "pv_full_service_usd": round(pv_w * SOLAR_USD_PER_W),
        "pv_equipment_only_usd": round(pv_w * SOLAR_USD_PER_W_DIY),
        "battery_usd_range": [round(s["battery_kwh"] * BATT_USD_PER_KWH_LO),
                              round(s["battery_kwh"] * BATT_USD_PER_KWH_HI)],
    }


def economics(kwh_day, s):
    """What the build is actually worth, given the tariff."""
    self_consume_value = kwh_day * UTILITY_USD_PER_KWH
    forgone_export = kwh_day * EXPORT_CREDIT
    net_advantage = self_consume_value - forgone_export
    return {
        "annual_kwh": round(kwh_day * 365),
        "value_if_it_displaces_import_usd_yr": round(self_consume_value * 365),
        "export_credit_forgone_usd_yr": round(forgone_export * 365),
        "net_annual_advantage_usd": round(net_advantage * 365),
        "storage_breakeven_peak_over_offpeak": round(1 / RTE_DEFAULT, 3),
        "storage_breakeven_peak_rate_usd": round(UTILITY_USD_PER_KWH / RTE_DEFAULT, 4),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kwh-day", type=float)
    ap.add_argument("--peak-kw", type=float)
    ap.add_argument("--autonomy-h", type=float, default=24.0)
    ap.add_argument("--psh", type=float, default=PSH_DEFAULT)
    ap.add_argument("--derate", type=float, default=DERATE_DEFAULT)
    ap.add_argument("--dod", type=float, default=DOD_DEFAULT)
    ap.add_argument("--rte", type=float, default=RTE_DEFAULT)
    ap.add_argument("--table", action="store_true", help="print a scenario grid")
    a = ap.parse_args()

    if a.table:
        print(f"{'kWh/day':>8} {'peak kW':>8} {'PV kW':>7} {'batt kWh':>9} "
              f"{'inv kW':>7} {'PV $ (svc)':>11} {'batt $ lo-hi':>17}")
        for kwh in (2, 4, 8, 16):
            for peak in (1.2, 2.5, 5.0):
                s = size(kwh, peak, a.autonomy_h, a.psh, a.derate, a.dod, a.rte)
                p = price(s)
                print(f"{kwh:>8} {peak:>8} {s['pv_kw']:>7} {s['battery_kwh']:>9} "
                      f"{s['inverter_kw']:>7} {p['pv_full_service_usd']:>11,} "
                      f"{p['battery_usd_range'][0]:>8,}-{p['battery_usd_range'][1]:<8,}")
        print("\nBenchmarks: solar ${}/W median installed (EnergySage Jan-Jun 2026); "
              "battery ${}-{}/kWh (EnergySage 2026 brand survey).".format(
                  SOLAR_USD_PER_W, BATT_USD_PER_KWH_LO, BATT_USD_PER_KWH_HI))
        print("Autonomy = {} h. PV uses {} PSH x {} derate. Battery uses {} DoD x {} RTE.".format(
            a.autonomy_h, a.psh, a.derate, a.dod, a.rte))
        return

    if a.kwh_day is None or a.peak_kw is None:
        ap.error("--kwh-day and --peak-kw are required (or use --table)")

    s = size(a.kwh_day, a.peak_kw, a.autonomy_h, a.psh, a.derate, a.dod, a.rte)
    p = price(s)
    e = economics(a.kwh_day, s)
    print("SIZING")
    for k, v in s.items():
        print(f"  {k:>22}: {v}")
    print("COST (benchmarks, replace with local quotes)")
    for k, v in p.items():
        print(f"  {k:>22}: {v}")
    print("ECONOMICS")
    for k, v in e.items():
        print(f"  {k:>36}: {v}")
    if s["peak_exceeds_feed"]:
        print(f"\nVERDICT: peak {a.peak_kw} kW exceeds the {s['feed_kw_max']} kW feed by "
              f"{s['peak_excess_kw']} kW. Local supply is a capability requirement, "
              f"not a cost optimisation.")


if __name__ == "__main__":
    main()
