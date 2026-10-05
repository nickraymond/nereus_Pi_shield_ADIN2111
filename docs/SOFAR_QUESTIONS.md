# SOFAR_QUESTIONS.md — Open Questions for Sofar

*Questions about the Sofar mote design that only Sofar can answer. Nick sends
them; record the answer, date and who answered, then move the fact into
SPEC.md or POWER_PATH.md with "Sofar, <name>, <date>" as its source.*
*Last updated: 2026-10-05*

State key: `[ ]` not sent · `[>]` sent, waiting · `[x]` answered · `[-]` deferred (don't send yet)

| # | State | Question | Why we're asking | Answer (who, date) |
|---|---|---|---|---|
| Q1 | [ ] | Is there a fuse or e-fuse on the mote's through-power path in any revision? Our 000639-AB copy has none, and you say the mote has no through-current protection. Your 50W/100W guide mentions a Bel C1F2 2 A fuse as a "placeholder". What do you recommend for a ~50 W potted design? | Nick remembered a fuse. The 50 W path needs protection that works in both directions and is safe to pot (POWER_PATH P4) | |
| Q2 | [ ] | Is R11 (0 Ω, 1210, across the U9 load switch) fitted on production motes? | Fitted means the payload port is always on | |
| Q3 | [ ] | What current limit does R34 (374 kΩ) set on the FPF2700 (U9)? | Payload port rating vs ~50 W; we can't get the datasheet | |
| Q4 | [ ] | Why is the load switch controlled from the mezzanine side? | We're moving that control to Pi GPIO16 | |
| Q5 | [-] | Has MSD1514-473MED (one per port) been built or tested since the guide was written? Any recommended damping values (R15/R16, C22/C23) to go with it? | The guide says it's not qualified at 50 W and that damping should be retuned for new magnetics. **Deferred with the 50 W revision** (DESIGN D12, 2026-10-05) | |
