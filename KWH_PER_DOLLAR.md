# kWh per dollar — buying energy vs. generating it

Alex's framing, taken seriously: *energy is not just generated, it is purchased*,
and trading capital may be more scalable than kilowatts on a city plot. This
converts both sides into one unit — **kilowatt-hours per year at the tariff** —
so the comparison is arithmetic rather than preference.

Run `python3 income_to_kwh.py`. Inputs are measured from 60-day realized
volatility or published market rates; the method is Black-Scholes at a 30-delta
strike, 30 days to expiry.

## The comparison

| Leg | Basis | Capital | kWh/yr secured | Capital per kWh/yr |
|---|---|---|---|---|
| PV, 1.11 kW | 4 kWh/day, 4.5 PSH, 0.80 derate | **$2,853 spent** | 1,460 | **$1.95** |
| Short 30-delta calls on gold | 23.6% realized vol → 1.24%/30d → 15.1%/yr | $10,000 **retained** | 2,799 | $3.57 |
| Short 30-delta calls on silver | 40.9% realized vol → 2.10%/30d → 25.6%/yr | $10,000 **retained** | 4,744 | **$2.11** |

At $0.53956/kWh.

**They are within 8% of each other per unit of capital** — $1.95 for the roof
against $2.11 for silver premium. So the question is not which is more efficient
per dollar. It is what each one *costs you beyond the dollar*:

- The PV dollar is **spent and depreciating**; the income dollar is **retained
  and reversible**. You can stop selling calls in a week. You cannot un-buy a
  roof, and the capital does not come back.
- The PV kilowatt is **behind the meter** — immune to tariffs, outages and market
  access, and it works when markets are closed. The premium is **contingent on
  someone paying it** every cycle.
- The premium is **paid out of the right tail.** At 30 delta the call is in the
  money roughly 30% of the time at expiry, and on a fast move you part with the
  asset at the strike. Selling optionality is not a yield in the coupon sense; it
  is a transfer, and the transfer runs against you in exactly the scenario where
  the hedge was supposed to work.

## The rule this produces

**Generate for capability. Buy for scale.**

- Where a load cannot be served at all — the 10 A / 120 V feed against a spindle —
  generation is the only answer and its cost per kWh is irrelevant, because the
  alternative is zero kWh.
- Where the question is how to secure *more* energy than the footprint allows,
  the income leg wins on reversibility at essentially the same capital
  efficiency, and it scales without land, permitting or interconnection queue.

## What is not in the table, and why

- **ETH/SOL staking**: the income mechanism is staking rather than premium, and
  the rates differ by provider and lockup. Not quoted here because a number
  without a dated source is worse than a blank.
- **Assignment cost**: the table shows premium collected, not the expected
  give-up from being called away. At 30 delta that is the larger half of the
  trade and it is not netted here — treat the annualised figure as gross.
- **Vol persistence**: annualising a 30-day premium × 12 assumes the same
  volatility reprints every cycle. Realized vol was 23.6% (gold) over 60 days
  against a 20-day figure distorted upward by the November de-rating, so 60 days
  was used deliberately.

## The NEM caveat that survives all of this

At $0.54 export against $0.53956 import (ratio 1.0008) **self-consumption is
worth approximately zero** on this property. So the PV column buys *capability*
— the machine runs — and buys **no energy economics at all**. Anyone comparing
"generate vs. buy" on this tariff without that sentence is comparing the wrong
two numbers.
