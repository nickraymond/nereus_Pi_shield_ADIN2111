# JLC parts buy: critical parts for the first build (S8.a)

*Read Thu 2026-10-15. Stock and prices change daily, so recheck on the buy screen. **Nick places the order**: agents never
log in to JLC, enter payment details or buy. Policy: DESIGN D26 (critical parts, exact part, JLC global sourcing) and D27
(flagged passives wait for Sofar's review).*

**Build (Nick, Wed 2026-10-14; DESIGN D32):** 20 boards: 6 for Sofar (paid on receipt, due at Sofar Mon 11/30), 10 for
Nick, 4 for scrap. Dev units, no potting. JLC PCBA order target is Fri 10/30, with Tue 11/3 as the fallback.

## In short

- **Buy 8 lines for ≈ $556** (table below). 7 lines go through **JLC global sourcing**. **J5 is back in JLC's own stock**
  (34,285 on 10/15; it was 0 on 10/6), so buy it straight into your parts library.
- **The parts lead time sets the schedule, not the board build.** JLC quotes global sourcing at **9–20 business days**.
  Paid Fri 10/16, the parts land at JLC between **Thu 10/29 and Fri 11/13** (Wed 11/18 if the 1–3-day review comes on
  top). A PCBA order can only use them once they arrive. So **10/30 works only in the best case**, 11/3 is realistic, and
  each day you wait moves the whole window. **Pay today if you can.**
- **The PCBA estimate holds.** An order on 10/30 arrives about **Tue 11/10 to Wed 11/18**, so your ~11/13–16 is the middle
  of that range. Sofar's 11/30 is at risk only if global sourcing runs to the end of its window (see Timeline).

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
sets the final figure when you place the PCBA order. ⚑ Y1 has no listing, so 0 is assumed from the ten sibling ABM11W-25
MHz listings (all 0). **Not verified.**
² jlcpcb.com parts search, 2026-10-15. The 10/6 lifecycle check found no LCSC listing for U1, L3/L6, D1 or MP1–MP4. JLC
lists them now, but with no stock.
³ Under JLC's rules, a part used in one PCBA order comes either from JLC stock plus JLC pre-order, or from global sourcing
plus consignment, never a mix ([global sourcing guide], [consignment T&C]). JLC stock (27 and 10) is short, so buy all 40
through global sourcing (D26).
⁴ JLC lists other ABM11W 25 MHz variants (‑6‑B1U, ‑8‑K1Z …). They are not the specified part, so don't pick them.
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

**1. Parts arrive at JLC** (business days, paid Fri 10/16; a day earlier for each if you pay Thu 10/15):

| Global-sourcing lead time | Parts at JLC | PCBA order |
|---|---|---|
| 9 BD (best) | Thu 10/29 | Fri 10/30 ✓ |
| 9 BD + 3 BD review | Tue 11/3 | Tue 11/3 (fallback) ✓ |
| 15 BD (JLC's sourcing page: "9–15 days") | Fri 11/6 | Fri 11/6 |
| 20 BD (JLC's guide: "normally 9–20 business days") | Fri 11/13 | Fri 11/13 |
| 20 BD + 3 BD review (worst) | Wed 11/18 | Wed 11/18 |

JLC's two pages disagree on the range: the guide says 9–20 business days and the sourcing page says 9–15 days. Neither
says whether the 1–3-day review is included. **The checkout shows a lead time per part. Read it there, and tell me (or
put it in the record below) if any line shows more than 15 BD.**

**2. PCBA order → boards in hand** (method in the next section):

| PCBA order | Production done | Arrives (DHL Express) |
|---|---|---|
| Fri 10/30 | Sun 11/8 – Thu 11/12 | **Tue 11/10 – Wed 11/18** |
| Tue 11/3 | Thu 11/12 – Mon 11/16 | Mon 11/16 – Fri 11/20 |
| Fri 11/13 | Sun 11/22 – Thu 11/26 | Tue 11/24 – Wed 12/2 ✗ |
| Wed 11/18 | Fri 11/27 – Tue 12/1 | Tue 12/1 – Mon 12/7 ✗ |

A PCBA order by about 11/6 arrives by Wed 11/25 at worst. Any later and 11/30 depends on luck, and that's before your
own check of the boards, the forwarding time to Sofar, and the Thanksgiving week (Thu 11/26). If the checkout shows long lead times,
JLC's 4–5-day PCB expedite (on the quote page) wins back about 4 days.

## JLC 6-layer PCBA lead time (as of 2026-10-15)

- **PCB build: 8–9 days.** This is the standard option on JLC's instant quote for 6 layers, 49 × 68 mm (experiment 1.a's
  outline), 20 pcs, read 2026-10-15. Expedite options: 4–5, 3–4 or 2–3 days at extra cost. It matches JLC's 2026-08-26
  notice ("production lead time 5 days … shown on the website: approximately 8–9 days"). JLC counts build time from the
  start of production to ready-to-ship ([quote page]).
- **Assembly: 1–2 days to 4+ days.** JLC's PCBA FAQ says assembly starts right after the PCB and 90 % of orders finish
  within 24 h, 48 h at most. Its capabilities page lists Standard PCBA at "≥ 4 days". **This board needs Standard PCBA**:
  JLC marks AP22913CN4-7 "PCBA Type: Standard Only, X-ray Inspection: Required", and the layout plans bottom-side
  parts (D31). So the range above uses 1–4 days.
- **Shipping: DHL Express (DDP), 2–4 business days**, as the quote page showed on 2026-10-15.
- **Not verified:** the PCBA build time JLC quotes for this exact board. It appears only after a Gerber upload, which is
  yours to do at order time. I didn't upload anything.
- **For the order (no action now):** Standard PCBA needs a board or panel of at least 70 × 70 mm with edge rails
  ([capabilities]), so JLC will add rails or a panel to the ~49 × 68 mm shield. Sofar Q8 (licence to share the derived
  files with JLC) is still open, and the PCBA order shares the board files. This parts buy shares none.

## Steps: buy the parts on JLC (Nick)

From JLC's global sourcing guide (updated 2026-09-08). A global-sourcing order **cannot be cancelled or returned once
paid**, so check each MPN before you pay.

1. Sign in at jlcpcb.com and open **Parts Manager → Order Parts → Global Sourcing Parts**.
2. For each of the 7 global-sourcing lines (U1, U2/U3, L3/L6, Y1, D1, D2/D3, MP1–MP4), search the **exact MPN** from the
   table. Use `SMA6F33A-M3/H` for D1, not the obsolete ST `SMA6F33A`.
3. JLC lists several suppliers per part. Pick the one with stock ≥ the Buy qty, an MOQ ≤ the Buy qty and the **shortest
   lead time**; the price is secondary. Check that the maker and the full MPN match exactly. For Y1, the `-6-K1Z-T3`
   suffix is the specified part. Enter the **Buy** qty and click **Add**.
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

**Purchase record** (fill in after checkout):

| Line | Supplier picked | Qty | Unit price | Lead time shown | Order # |
|---|---|---|---|---|---|
| U1 | | 20 | | | |
| U2/U3 | | 40 | | | |
| L3/L6 | | 40 | | | |
| Y1 | | 20 | | | |
| D1 | | 25 | | | |
| D2/D3 | | 40 | | | |
| MP1–MP4 | | 81 | | | |
| J5 (JLC stock) | JLC | 22 | $0.5397 | in stock | |

## Fallback: consign a line yourself

Use this only for a line global sourcing can't supply. It's slower and dearer for a buyer outside mainland China
([consignment guide], [consignment T&C], both updated 2026-09-08):

- Buy from Digi-Key or Mouser and ship to **JLC's Hong Kong warehouse**. First register the shipment under **Consigned
  Parts Shipments** as "Outside Mainland China", with price, maker, HS code and the other details the form asks for. JLC
  reviews the price within 2 BD, and **you must wait for approval before dispatch**.
- Fees: an import-duty and 13 % VAT deposit (refunded once the parts are used in a PCBA order), a 2 % handling fee (minimum
  $10 per shipment) and an overseas-consignment service fee of $85 for 1–50 part numbers.
- For the same part, consigned stock can be combined with global sourcing but not with JLC stock.

## Not in this buy

- **Flagged passives** (R8, R15/R16, C22/C23 and the commodity R/C lines): bought after Sofar's review picks the planned
  part (D27). See the schedule note above about R8, R15/R16 and C22/C23.
- **J1** Pi socket: no part number yet (height open).
- **Everything else** in `bom.csv`: LCSC/JLC-stocked parts, chosen when you place the PCBA order.

## Sources (all read 2026-10-15)

- [global sourcing guide]: JLCPCB, "How to use JLCPCB Global Sourcing Parts Service?", updated 2026-09-08,
  https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service
- [sourcing page]: JLCPCB, "PCBA Parts Sourcing Instruction", updated 2026-09-09 (global sourcing "Lead time: 9-15
  days"), https://jlcpcb.com/help/article/pcba-parts-sourcing-instruction
- [consignment guide]: JLCPCB, "Overseas Component Consignment User Guide", updated 2026-09-08,
  https://jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb
- [consignment T&C]: JLCPCB, "Consignment Parts Terms & Conditions", updated 2026-09-08,
  https://jlcpcb.com/help/article/consignment-part-terms-conditions
- [quote page]: https://cart.jlcpcb.com/quote (Advanced PCB, 6 layers, 49 × 68 mm, 20 pcs; nothing uploaded or saved)
- [capabilities]: https://jlcpcb.com/capabilities/pcb-assembly-capabilities (Economic vs Standard PCBA)
- JLCPCB PCB Assembly FAQs, updated 2026-09-08, Q13 turn-time: https://jlcpcb.com/help/article/pcb-assembly-faqs
- JLCPCB news, 2026-08-26, "High Multilayer PCB Lead Time Update":
  https://jlcpcb.com/news/multilayer-pcb-lead-time-update-august-2026
- JLC library listings, stock, prices and attrition: jlcpcb.com parts search (the data behind
  jlcpcb.com/parts/componentSearch), and the part pages jlcpcb.com/partdetail/C2150198 and C189893
- Digi-Key product pages (stock, price at qty, Part Status Active, Manufacturer Standard Lead Time): ADIN2111BCPZ
  15906334, AP22913CN4-7 10294903, PA5432.822NLT 13693982, ABM11W-25.0000MHZ-6-K1Z-T3 7172619, SMA6F33A-M3/H 16683710,
  RB058LAM-60TFTR 8028525, 78614015360 15792302, SM02B-GHS-TB 807786, UR73D1JTTD10L0F 9845673. Digi-Key then showed a
  bot check, so the last two optional lines use Findchips/Mouser.
- findchips.com search for each MPN: the Mouser, Newark and Richardson rows
