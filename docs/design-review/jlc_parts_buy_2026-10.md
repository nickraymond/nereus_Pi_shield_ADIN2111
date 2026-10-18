# JLC parts buy: critical parts for the first build (S8.a)

*Read Thu 2026-10-15; dates re-anchored Sat 10/17 on a Mon 10/19 payment. Stock and prices change daily, so recheck on the buy screen. **Nick places the order**: agents never
log in to JLC, enter payment details or buy. Policy: DESIGN D26 (critical parts, exact part, JLC global sourcing) and D27
(flagged passives wait for Sofar's review).*

**Build (Nick, Wed 2026-10-14; DESIGN D32):** 20 boards: 6 for Sofar (paid on receipt, due at Sofar Mon 11/30), 10 for
Nick, 4 for scrap. Dev units, no potting. JLC PCBA order target is Fri 10/30, with Tue 11/3 as the fallback.

## In short

- **Bought (Nick, 2026-10-18 14:24 PT, which is Mon 10/19 in China):** JLC global-sourcing order **DOB202610190524705**,
  **$956.05**, all 7 lines from Digi-Key (the shortest lead, 10–14 days, and the lowest price on JLC's supplier list).
  JLC estimates **ready for assembly Thu 11/5** (13 BD), so the PCBA order moves to about **11/5** and the boards arrive
  about **Thu 11/19 – Tue 11/24 or later**. That keeps Sofar's 11/30 with a few days to spare; 10/30 and 11/3 are out.
  **J5 isn't pre-bought** (Nick): it's picked from JLC's stock (31,805 on 10/18) when the PCBA order is placed. The bullets
  below are the plan as written before the buy.
- **Buy 8 lines for ≈ $556** (table below). 7 lines go through **JLC global sourcing**. **J5 is back in JLC's own stock**
  (34,285 on 10/15; it was 0 on 10/6), so buy it straight into your parts library.
- **The parts lead time sets the schedule, not the board build.** JLC quotes global sourcing at **9–20 business days**.
  Paid Mon 10/19 China time, the parts land at JLC between **Fri 10/30 and Mon 11/16** (Thu 11/19 if the 1–3-day review
  comes on top). A PCBA order can only use them once they arrive. So **10/30 needs the very best case (9 BD and a
  same-day PCBA order), the 11/3 fallback needs ≤ 11 BD; plan on 11/9–11/16** until the checkout shows each line's lead
  time.
- **When to pay: to keep 10/30 possible, pay between Sun 10/18 09:00 PT and Mon 10/19 09:00 PT** (Monday in China).
  Paying during your Monday workday is already Tuesday in China. That rules out 10/30 (best case Mon 11/2) and moves every
  date one business day: the 11/3 fallback then needs ≤ 10 BD and Sofar's 11/6 cutoff ≤ 13 BD.
- **Your ~11/13–16 board estimate holds only in the best case.** That needs parts in 9 BD and a 10/30 PCBA order, with boards
  arriving Fri 11/13 – Wed 11/18 or later (up to 3 days earlier if JLC's 1–2-day assembly figure applies). **In the
  planning case (parts 11/9–11/16) the boards arrive about Tue 11/24 – Thu 12/3 or later, so Sofar's 11/30 is at risk.**
  Making 11/30 needs the parts within 14 BD (PCBA order by about 11/6, boards by Wed 11/25 at the 4-day assembly floor),
  or JLC's 4–5-day PCB expedite, which wins back about 4 days. Thanksgiving, your check and the forwarding to Sofar
  still come after that. The PCBA order also waits on Sofar's review of the planned passives.

## What to buy

Quantities per board are from `docs/design-review/bom.csv`. Buy = 20 × per board + JLC attrition.

| Ref | MPN (maker) | Per board | 20 boards | JLC attrition ¹ | **Buy** | JLC library today ² | Route |
|---|---|---|---|---|---|---|---|
| U1 | ADIN2111BCPZ (Analog Devices) | 1 | 20 | 0 | **20** | C3226964 listed, stock 0 | Global sourcing |
| U2, U3 | AP22913CN4-7 (Diodes Inc.) | 2 | 40 | 0 | **40** | C2150198, stock 33 (27 orderable) | Global sourcing, all 40 ³ |
| L3, L6 | PA5432.822NLT (Pulse) | 2 | 40 | 0 | **40** | C17230195 listed, stock 0 | Global sourcing |
| Y1 | ABM11W-25.0000MHZ-6-K1Z-T3 (Abracon) | 1 | 20 | 0 ⚑ | **20** | no listing for this exact MPN ⁴ | Global sourcing |
| D1 | SMA6F33A-M3/H (Vishay; Sofar's listed second source, D27) ⁵ | 1 | 20 | 5 | **25** | C7083040 listed, stock 0 | Global sourcing |
| D2, D3 | RB058LAM-60TFTR (ROHM) | 2 | 40 | 0 | **40** | C3757753, stock 10 | Global sourcing, all 40 ³ |
| MP1–MP4 | 78614015360 (Würth) | 4 | 80 | 1 | **81** | C17256375 listed, stock 0 | Global sourcing |
| J5 | SM02B-GHS-TB (JST; ordered as SM02B-GHS-TB(LF)(SN)) ⁶ | 1 | 20 | 2 | **22** | **C189893, stock 34,285** | **JLC stock** → My Parts Lib |

¹ JLC's attrition (`lossNumber`) for the library listing of the same MPN, from jlcpcb.com's parts search, 2026-10-15. JLC
sets the final figure when you place the PCBA order. ⚑ Y1 has no listing, so 0 is assumed from the 13 sibling ABM11W 25 MHz
listings (all 0). **Not verified.**
² jlcpcb.com parts search, 2026-10-15. The 10/6 lifecycle check found no LCSC listing for U1, L3/L6, D1 or MP1–MP4. JLC
lists them now, but with no stock.
³ Under JLC's rules, a part used in one PCBA order comes either from JLC stock plus JLC pre-order, or from global sourcing
plus consignment, never a mix ([global sourcing guide], [consignment T&C]). JLC stock (27 and 10) is short, so buy all 40
through global sourcing (D26).
⁴ JLC lists 13 other ABM11W 25 MHz variants. The closest look-alike is ‑6‑K2Z‑T3 (C7060656), one character off the
specified ‑6‑K1Z‑T3; others include ‑6‑B1U and ‑8‑K1Z. None is the specified part, so don't pick them.
⁵ Sofar Q7 is still open. The Vishay part is Sofar's own listed second source (D27), and the ST part is obsolete.
⁶ Digi-Key lists SM02B-GHS-TB(LF)(SN) as an alias of SM02B-GHS-TB. D26 routed J5 through global sourcing only because
LCSC was out of stock on 10/6. JLC stock is now the simpler route: it's cheaper, needs no wait, and avoids the $20
commodity-inspection fee global sourcing charges per connector type ([global sourcing guide]).

### Price, stock and lead time (read 2026-10-15)

JLC shows global-sourcing prices, suppliers and per-part lead times only to a signed-in account, so **these are not
verified**. JLC says global-sourcing prices differ "slightly" from overseas distributors ([global sourcing guide]). The
estimate below uses Digi-Key's price at the buy quantity (cut tape or tray), with Mouser as a cross-check.

| Ref | Buy | Digi-Key unit @ qty (stock) | Line est. | Mouser unit @ qty (stock) ⁷ | Mfr std lead time (DK) | JLC lead time |
|---|---|---|---|---|---|---|
| U1 | 20 | $15.387 @10+ (115) | $307.74 | $15.39 @10+ (80) | 10 wk | GS 9–20 BD ⚑ |
| U2, U3 | 40 | $0.2388 @25+ (51,903) | $9.55 | $0.221 @25+ (17,719) | 40 wk | GS 9–20 BD ⚑ |
| L3, L6 | 40 | $1.461 @10+ (200) | $58.44 | $1.61 @25+ (2,035) | 14 wk | GS 9–20 BD ⚑ |
| Y1 | 20 | $0.407 @10+ (67) | $8.14 | $0.407 @10+ (3,549) | 14 wk | GS 9–20 BD ⚑ |
| D1 | 25 | $0.450 @10+ (11,792) | $11.25 | $0.323 @10+ (8,757) | 53 wk | GS 9–20 BD ⚑ |
| D2, D3 | 40 | $0.538 @10+ (40,747) | $21.52 | $0.394 @10+ (5,758) | 12 wk | GS 9–20 BD ⚑ |
| MP1–MP4 | 81 | $1.569 @50+ (7,835) | $127.09 | $1.57 @50+ (3,602) | 40 wk | GS 9–20 BD ⚑ |
| J5 | 22 | $0.296 @10+ (623), not used | **$11.87** at JLC's $0.5397 @1+ | (0) | 16 wk | **in stock now** |

⁷ Mouser figures come from findchips.com, 2026-10-15. Stock in brackets is distributor stock. Every global-sourcing line
has enough stock for its buy quantity at both Digi-Key and Mouser today; the thinnest is Y1 at Digi-Key (67 for 20). The
long manufacturer lead times only matter if distributor stock runs out. D1's 53 weeks is the reason to buy it now.

**If the screen offers only ADIN2111BCPZ-R7 for U1:** that is the same part on a reel (Richardson lists BCPZ as tray and
‑R7 as T/R, via findchips, 2026-10-15). Mouser has 1,500 at $19.33 @10+. It's a packaging change only, but it's your call
before buying.

## Estimated total

| Basis | Total |
|---|---|
| Digi-Key prices (above) + J5 from JLC stock | **$555.60** |
| Mouser prices + J5 from JLC stock | $552.06 |
| **Actual: JLC global-sourcing order, 2026-10-18** (with +2 spares) | **$956.05** (+ J5 ≈ $11 from JLC stock at the PCBA order) |

**Why the actual is higher:** JLC charged $27.76 for U1 against Digi-Key's own $15.39 (10+), which is +$270 on 22. On
top of that come the +2 spares on five lines (≈ $36 at Digi-Key prices), $8.92 duty on MP1–MP4, a JLC markup of
roughly 15–35 % on the other lines, and $1 per line. U1 was also offered as a JLC pre-order at an estimated $15.48.
Nick kept Digi-Key because the pre-order price is only fixed after payment and its purchasing can take up to 18 days
without asking ([pre-order T&C]), while Digi-Key showed a known 10–14 days.

**Plan on ≈ $560.** It may run a little higher. JLC's global-sourcing markup isn't visible to us, and JLC can add customs
duty of 3–30 % on some part types; its examples are relays, modules and cables, none of which are in this buy
([global sourcing guide]). JLC doesn't charge shipping for global-sourcing parts.

**Optional, your call (not in the total):**
- **Spares on the zero-attrition lines.** JLC lists 0 attrition for U1, U2/U3, L3/L6, D2/D3 (and Y1, assumed). With
  none, one mis-pick costs a board. Adding +2 to each of those five lines costs ≈ **$36**, mostly the two extra U1.
- **The schedule risk outside this buy:** R8 (UR73D1JTTD10L0F) and R15/R16 (CRCW08057R50FKEAHP) have no JLC listing, and
  C22/C23 (EEEFT1H470AP) has JLC stock 3 (all 2026-10-15). Their D27 planned part is Sofar's own, so if Sofar keeps
  them, they also need global sourcing (another 9–20 BD) **after** Sofar's review, which would move the PCBA order date
  again. Buying them now costs ≈ **$30** (R8 20 × $0.365 DK; R15/R16 40 × $0.06 and C22/C23 40 × $0.493 Mouser; attrition
  unknown). If Sofar later picks an alternate, that $30 is wasted.

## Timeline

**1. Parts arrive at JLC** (business days, China time; JLC runs on UTC+8). The table starts from payment on Mon 10/19 in
China, which is Sun 10/18 09:00 PT to Mon 10/19 09:00 PT. Paying later on Monday, Pacific time, lands on Tuesday in China: every date
one business day later. (The 10/15 version started from Fri 10/16, which has passed.)

| Global-sourcing lead time | Parts at JLC | PCBA order |
|---|---|---|
| 9 BD (best) | Fri 10/30 | Fri 10/30 ✓ (same day) |
| 9 BD + 3 BD review | Wed 11/4 | Wed 11/4 (misses the 11/3 fallback by a day) |
| 15 BD (JLC's sourcing page: "9–15 days") | Mon 11/9 | Mon 11/9 |
| 20 BD (JLC's guide: "normally 9–20 business days") | Mon 11/16 | Mon 11/16 |
| 20 BD + 3 BD review (worst) | Thu 11/19 | Thu 11/19 |

Table 2 below is keyed by the PCBA order date, so it still applies: look up the date the parts land.

JLC's two pages disagree on the range: the guide says 9–20 business days and the sourcing page says 9–15 days. Neither
says whether the 1–3-day review is included. **The checkout shows a lead time per part. Read it there, and tell me (or
put it in the record below) if any line shows more than 15 BD.**

**The PCBA order also waits on Sofar's review (D27).** The first build buys the planned passives after that review. If
Sofar rejects one of the 9 passive lines D27 changes (R34, R20/R39, R21/R35/R37/R43, C31, C17/C26, C21,
C16/C18/C24/C25, C19/C27, R14/R18), that line falls back to its specified part. None of those had LCSC stock on 10/6
(`bom_lifecycle.md`), so it would need global sourcing too: another 9–20 BD from the day it's bought. R8, R15/R16 and
C22/C23 are the same case (see the optional items above).

**2. PCBA order → boards in hand.** PCB 8–9 days, then Standard PCBA assembly at its "≥ 4 days" floor, then DHL 2–4 BD
(method in the next section). The "+" marks the open upper end.

| PCBA order | Production done | Arrives (DHL Express) |
|---|---|---|
| Fri 10/30 | Wed 11/11 – Thu 11/12+ | **Fri 11/13 – Wed 11/18+** |
| Tue 11/3 | Sun 11/15 – Mon 11/16+ | Tue 11/17 – Fri 11/20+ |
| Fri 11/6 | Wed 11/18 – Thu 11/19+ | Fri 11/20 – Wed 11/25+ |
| **Thu 11/5 (parts ready, JLC est.)** | Tue 11/17 – Wed 11/18+ | **Thu 11/19 – Tue 11/24+** |
| Mon 11/9 | Sat 11/21 – Sun 11/22+ | Tue 11/24 – Thu 11/26+ (at risk) |
| Mon 11/16 | Sat 11/28 – Sun 11/29+ | Tue 12/1 – Thu 12/3+ ✗ |
| Thu 11/19 | Tue 12/1 – Wed 12/2+ | Thu 12/3 – Tue 12/8+ ✗ |

A PCBA order by about 11/6 arrives by Wed 11/25 if assembly takes 4 days. Any later and 11/30 depends on luck, and that's
before your own check of the boards, the forwarding time to Sofar, and the Thanksgiving week (Thu 11/26). If JLC's FAQ
figure applies (assembly in 1–2 days), each date comes up to 3 days earlier. If the checkout shows long lead times, JLC's
4–5-day PCB expedite (on the quote page) wins back about 4 days.

## JLC 6-layer PCBA lead time (as of 2026-10-15)

- **PCB build: 8–9 days.** This is the standard option on JLC's instant quote for 6 layers, 49 × 68 mm (experiment 1.a's
  outline), 20 pcs, read 2026-10-15. Expedite options: 4–5, 3–4 or 2–3 days at extra cost. It matches JLC's 2026-08-26
  notice ("production lead time 5 days … shown on the website: approximately 8–9 days"). JLC counts build time from the
  start of production to ready-to-ship ([quote page]).
- **Assembly: 4+ days for this board.** **This board needs Standard PCBA**: JLC marks AP22913CN4-7 "PCBA Type: Standard
  Only, X-ray Inspection: Required", and the layout plans bottom-side parts (D31). JLC's capabilities page lists Standard
  PCBA at "≥ 4 days" (Economic "1 - 3 days") without saying whether that includes the PCB. JLC's PCBA FAQ says assembly
  starts right after the PCB and 90 % of orders finish within 24 h, 48 h at most. The timeline takes 4 days as the floor
  and leaves the upper end open; the FAQ figure would make it up to 3 days earlier.
- **Shipping: DHL Express (DDP), 2–4 business days**, as the quote page showed on 2026-10-15.
- **Not verified:** the PCBA build time JLC quotes for this exact board. It appears only after a Gerber upload, which is
  yours to do at order time. I didn't upload anything.
- **For the order (no action now):** Standard PCBA needs a board or panel of at least 70 × 70 mm with edge rails
  ([capabilities]), so JLC will add rails or a panel to the ~49 × 68 mm shield. Sofar Q8 (licence to share the derived
  files with JLC) is still open, and the PCBA order shares the board files. This parts buy shares none.

## Steps: buy the parts on JLC (Nick)

From JLC's global sourcing guide (updated 2026-09-08/09). A global-sourcing order **cannot be cancelled or returned once
paid**, so check each MPN before you pay.

1. Sign in at jlcpcb.com and open **Parts Manager → Order Parts → Global Sourcing Parts**.
2. For each of the 7 global-sourcing lines (U1, U2/U3, L3/L6, Y1, D1, D2/D3, MP1–MP4), search the **exact MPN** from the
   table. Use `SMA6F33A-M3/H` for D1, not the obsolete ST `SMA6F33A`.
3. JLC lists several suppliers per part. Pick the one with stock ≥ the Buy qty, an MOQ ≤ the Buy qty and the **shortest
   lead time**; the price is secondary. Check that the maker and the full MPN match exactly. For Y1, the `-6-K1Z-T3`
   suffix is the specified part, not the look-alike `-6-K2Z-T3`. Enter the **Buy** qty and click **Add**.
4. **J5 from JLC stock:** open jlcpcb.com/partdetail/C189893, set qty **22** and click **Add to My Part Lib for
   Assembly**.
5. Open **Cart**. JLC library parts and global-sourcing parts are listed and paid separately. Select the global-sourcing
   parts → **Secure Checkout** → check the contact email and billing address → **Submit Order** → agree to the
   global-sourcing T&C → **pay within one hour** (JLC cancels unpaid orders after one hour).
6. Back in **Cart**, check out J5 (JLC library part) the same way.
7. Track the order under **Parts Order History**: Reviewing (1–3 BD) → Purchasing (lead time shown; tracking appears when
   the supplier ships) → Complete. Parts show up in your parts library as they arrive.
8. Fill in the record below, or tell me and I'll do it: the order number and each line's lead time and price. **If any line
   shows more than 15 BD, flag it**: it moves the 10/30 date.
9. If JLC cancels a line at review (it "doesn't support assembly"; refunds take 1–7 days), use the consignment fallback.

**Purchase record** (from Nick's cart and order screenshots, 2026-10-18): order **DOB202610190524705**, invoice
11666342A, paid 2026-10-18 14:24 PT. Status was Reviewing; **Ready for Assembly: 2026-11-05**.

| Line | Supplier (Digi-Key #) | Qty | Unit price | Line total | Ready for assembly (JLC est.) |
|---|---|---|---|---|---|
| U1 | 505-ADIN2111BCPZ-ND | 22 | $27.7563 | $611.64 | 2026-11-05 |
| U2/U3 | AP22913CN4-7DICT-ND | 42 | $0.3077 | $13.93 | 2026-11-05 |
| L3/L6 | 553-PA5432.822NLTCT-ND | 42 | $1.8824 | $80.07 | 2026-11-05 |
| Y1 | 535-13848-1-ND | 22 | $0.5244 | $12.54 | 2026-11-05 |
| D1 | 112-SMA6F33A-M3/HCT-ND | 27 | $0.6088 | $17.44 | 2026-11-05 |
| D2/D3 | RB058LAM-60TFCT-ND | 45 | $0.6932 | $32.20 ⁸ | order: 2026-11-05 ⁸ |
| MP1–MP4 | 732-78614015360CT-ND | 84 | $2.1227 | $188.23 incl. $8.92 duty ⁸ | order: 2026-11-05 ⁸ |
| **Total** | | | | **$956.05** | |
| J5 (JLC stock) | C189893 | 22 | $0.5055 (cart, 10/18) | ≈ $11, paid with the PCBA order | not pre-bought: picked from JLC stock at the PCBA order (31,805 available 10/18; Nick) |

⁸ These two lines were behind "Show All" in the order screenshot. Their totals are the cart totals plus $1: each of the
five visible lines is $1.00 above qty × unit price, and with that the 7 lines sum exactly to the $956.05 order total.
Quantities include Nick's +2 spares (D1: 25 + 2; D2/D3 45 and MP1–MP4 84 as Nick chose).

## Fallback: consign a line yourself

Use this only for a line global sourcing can't supply. It's slower and dearer for a buyer outside mainland China
([consignment guide], [consignment T&C], both updated 2026-09-08/09):

- Buy from Digi-Key or Mouser and ship to **JLC's Hong Kong warehouse**. First register the shipment under **Consigned
  Parts Shipments** as "Outside Mainland China", with price, maker, HS code and the other details the form asks for. JLC
  reviews the price within 2 BD, and **you must wait for approval before dispatch**.
- Fees: import duty at a rate JLC sets, plus a 13 % VAT deposit (refunded once the parts are used in a PCBA order); a 2 %
  handling fee (minimum $10 per shipment); and an overseas-consignment service fee of $85 for 1–50 part numbers.
- For the same part, consigned stock can be combined with global sourcing but not with JLC stock.

## Not in this buy

- **Flagged passives** (R8, R15/R16, C22/C23 and the commodity R/C lines): bought after Sofar's review picks the planned
  part (D27). See the schedule note above about R8, R15/R16 and C22/C23.
- **J1** Pi socket: no part number yet (height open).
- **Everything else** in `bom.csv`: LCSC/JLC-stocked parts, chosen when you place the PCBA order.

## Sources (all read 2026-10-15 unless dated)

JLC probably shows each help page's "Last updated" date in the reader's time zone (likely, not verified): this session saw Sep 08 (the sourcing page Sep
09), and the QE saw Sep 09.

- [global sourcing guide]: JLCPCB, "How to use JLCPCB Global Sourcing Parts Service?", updated 2026-09-08/09,
  https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service
- [sourcing page]: JLCPCB, "PCBA Parts Sourcing Instruction", updated 2026-09-09 (global sourcing "Lead time: 9-15
  days"), https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction
- [consignment guide]: JLCPCB, "Overseas Component Consignment User Guide", updated 2026-09-08/09,
  https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb
- [consignment T&C]: JLCPCB, "Consignment Parts Terms & Conditions", updated 2026-09-08/09,
  https://jlcpcb.com/help/article/consignment-part-terms-conditions
- [pre-order T&C]: JLCPCB, "Pre-Ordering Parts Terms & Conditions", updated 2026-09-09, read 2026-10-18
  (estimated price "for reference only", final quote after payment; buys without asking if lead time ≤ 18 days),
  https://jlcpcb.com/help/article/pre-ordering-parts-terms-conditions
- [quote page]: https://cart.jlcpcb.com/quote (Advanced PCB, 6 layers, 49 × 68 mm, 20 pcs; nothing uploaded or saved)
- [capabilities]: https://jlcpcb.com/capabilities/pcb-assembly-capabilities (Economic vs Standard PCBA)
- JLCPCB PCB Assembly FAQs, updated 2026-09-08/09, Q13 turn-time: https://jlcpcb.com/help/article/pcb-assembly-faqs
- JLCPCB news, 2026-08-26, "High Multilayer PCB Lead Time Update":
  https://jlcpcb.com/news/multilayer-pcb-lead-time-update-august-2026
- JLC library listings, stock, prices and attrition: jlcpcb.com parts search (the data behind
  jlcpcb.com/parts/componentSearch), and the part pages jlcpcb.com/partdetail/C2150198 and C189893
- Digi-Key product pages (stock, price at qty, Part Status Active, Manufacturer Standard Lead Time): ADIN2111BCPZ
  15906334, AP22913CN4-7 10294903, PA5432.822NLT 13693982, ABM11W-25.0000MHZ-6-K1Z-T3 7172619, SMA6F33A-M3/H 16683710,
  RB058LAM-60TFTR 8028525, 78614015360 15792302, SM02B-GHS-TB 807786, UR73D1JTTD10L0F 9845673. Digi-Key then showed a
  bot check, so the last two optional lines use Findchips/Mouser.
- findchips.com search for each MPN: the Mouser, Newark and Richardson rows
