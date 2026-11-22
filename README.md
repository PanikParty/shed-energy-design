# Shed energy design — what it costs, and what it is actually worth

Two questions, kept separate: **can it be sized** (physics, deterministic) and **is
it worth building** (tariff arithmetic). The answers diverge sharply, and the
divergence is the whole point of this repo.

Run it:

```
python3 shed_sizing.py --table
python3 shed_sizing.py --kwh-day 4 --peak-kw 3.0 --autonomy-h 24
```

## 1. The binding constraint is amperage, not money

The shed is fed by a **10 A / 120 V GFCI circuit — 1.2 kW continuous**. That is
below the peak draw of a CNC spindle plus dust collection plus lighting. So the
first finding is not economic:

> Any load above 1.2 kW **cannot be served from the house feed at all**, at any
> price. Local generation is therefore a *capability* purchase. It is not an
> efficiency play, and pricing it as one produces the wrong answer.

## 2. Sized output (24 h autonomy, San Diego winter PSH)

| Load | Peak | PV | Battery | Inverter | PV installed | Battery |
|---|---|---|---|---|---|---|
| 2 kWh/day | 1.2 kW | 0.56 kW | 2.47 kWh | 1.50 kW | $1,439 | $845–2,838 |
| 2 kWh/day | 5.0 kW | 0.56 kW | 2.47 kWh | 6.25 kW | $1,439 | $845–2,838 |
| 4 kWh/day | 3.0 kW | 1.11 kW | 4.94 kWh | 3.75 kW | $2,853 | $1,689–5,676 |
| 8 kWh/day | 3.0 kW | 2.22 kW | 9.88 kWh | 3.75 kW | $5,705 | $3,379–11,352 |
| 16 kWh/day | 5.0 kW | 4.44 kW | 19.75 kWh | 6.25 kW | $11,411 | $6,754–22,693 |

Assumptions, all overridable: 4.5 peak-sun-hours (winter design month), 0.80
system derate, 0.90 depth of discharge, 0.90 round-trip efficiency, 1.25×
inverter margin, 2× surge for motor loads.

Cost benchmarks are **published national medians, not quotes**: solar **$2.57/W**
installed (EnergySage marketplace median Jan–Jun 2026, via pv-magazine
2026-10-24), battery **$342–1,149/kWh** (EnergySage 2026 brand survey, MidNite to
EG4). Replace both with local quotes before committing capital.

## 3. What it is worth on NEM 2.0 — approximately nothing

At a full-retail export credit of **$0.54/kWh** and an off-peak import rate of
**$0.53956/kWh**, the export/import ratio is **1.0008**. Every kWh consumed
on-site instead of exported:

- saves `$0.53956` of import, and
- forgoes `$0.54` of export credit.

Net advantage: **−$0.0004/kWh**, i.e. **about −$1 a year** on a 4 kWh/day load
(1,460 kWh/yr: $788 displaced import against $788 forgone credit).

**Consequence:** under equal rates, self-consumption and storage are value-neutral
at best, and negative once round-trip losses are counted. A battery is only
rational across a **time-of-use spread**, and the break-even is explicit:

> **peak ÷ off-peak > 1 ÷ round-trip efficiency ≈ 1.11**
> → peak must clear **≈ $0.60/kWh** against a $0.53956 off-peak rate.

Below that, storage is a decoration. Above it, storage earns `(peak − off-peak)
× kWh × efficiency` per cycle and nothing more.

## 4. What this does not yet include

Two inputs are needed for the final design, and neither is invented here:

1. **The machine's duty cycle** — CNC spindle + dust collection: peak kW and
   kWh/day. Until that lands, the table above is a parameter sweep, not a design.
2. **The actual peak TOU rate** on the tariff, to settle the $0.60 test in §3.

Also excluded: panel/inverter replacement over life, permitting, the GFCI
constraint on any VFD-driven equipment (a known leakage-trip problem on this
property), grounding/bonding for a detached structure, and battery degradation.

## 5. The honest conclusion

For this property, a shed supply is a **capability purchase priced against "the
machine does not run"**, not against an electricity bill. Sized for a 4 kWh/day
workshop it costs roughly **$2,800–8,500** depending on service level and battery
brand, and returns approximately **$0/yr** in energy savings. That is not a
failure of the design; it is what full-retail net metering does to the economics
of self-consumption. Build it because the 10 A circuit cannot run the machine —
and size it for the machine, not for the bill.
