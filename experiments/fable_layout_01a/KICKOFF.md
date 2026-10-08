# Kickoff prompt — layout experiment 1.a

Start a new Claude Code session on this repo with **Fable 5.1, high effort**, then paste:

```
Layout experiment 1.a. Read CLAUDE.md, then experiments/fable_layout_01a/BRIEF.md in full; it is your spec and its
hard rules override anything else you infer. Check out the branch experiment/fable-layout-01a (it exists on origin,
created from experiment/fable-layout-01) and work only inside experiments/fable_layout_01a/. KiCad is closed; use
KiCad 9's bundled Python (pcbnew) and kicad-cli. Read experiment 01's REPORT.md, LOG.md and qe/ reports first. Run
milestones M0-M4 autonomously, committing after each with renders in out/ and an entry in LOG.md; I will not answer
questions mid-run, so write OPTIONS.md, decide, and continue. The DFM sweep (M3) takes every JLCPCB limit from
their published pages, cited, never from memory. Stop and write REPORT.md if a hard rule would break or the board
must grow beyond the brief. Never merge; open a draft PR titled "EXPERIMENT (do not merge): fable layout 1.a", then
spawn the Quality Engineer review of that PR as a separate session (docs/PROMPTS.md section 5), save each report in
experiments/fable_layout_01a/qe/, fix and resend until it approves, and tell me the verdict, the PR link and the
pass/fail table.
```

Review afterwards: `OPTIONS.md`, `DFM.md`, `REPORT.md`, the renders in `out/`, the draft PR and the QE reports in `qe/`.

## Session 2 — pick up after QE round 1 (2026-10-08)

The first session ran M0–M2 and stopped on Nick's instruction; QE round 1 of PR #31 is CHANGES REQUESTED. Start a new
Claude Code session (Fable 5.1, high effort) and paste:

```
Layout experiment 1.a, session 2. Read CLAUDE.md, then experiments/fable_layout_01a/BRIEF.md in full (your spec; its
hard rules override anything else), OPTIONS.md, REPORT.md, LOG.md, HANDOFF.md and qe/S7b_01a_round1.md. Check out the
branch experiment/fable-layout-01a (origin, last commit 293dc11; never merge it; PR #31 is the draft PR, base
experiment/fable-layout-01) and work only inside experiments/fable_layout_01a/. KiCad is closed; use KiCad 9's bundled
Python (pcbnew) and kicad-cli; the pipeline is tools/build_all.sh (first run from m0 on a fresh checkout; START=m4
reruns the routing from the M3 snapshot). Never run a milestone script on a board left by a later step.

Finish M2 to the brief's bar, in this order, committing after each with renders in out/ and a LOG.md entry:
1. QE F1 (MAJOR): both ADIN pairs are shorted P-N at the transformer pads (the pair emitter's last segment runs
   through the opposite leg's pad: BM1_DATA_P through T1 pad 2, BM2_DATA_N through T2 pad 1), and
   tools/drcexclude.py's T1/T2 patterns hid them as "Sofar's transformer footprint". Fix the final pad approach in
   router.commit_pair (add the real-board case to tools/test_pair.py first), tighten the exclusion patterns to the
   no-net pads only, and correct REPORT.md: the true split at 293dc11 is 111 Sofar-copied errors + 16 of new copper.
2. QE F2 (MINOR): the ADIN copy region's west clip (mote y 107.9) dropped Sofar's ~{ADIN_INT} via at mote
   (156.571, 107.509), so the pre-route trim removed INT's fan-out (14 items). Keep that connection (re-add the via
   by hand inside the board, or route INT from U1.39 to R1.1 as Sofar did), make tools/dangling.py refuse to trim
   items on a mote pad-to-pad path, and correct REPORT §6 #3's cause.
3. The rest of REPORT.md §6 / HANDOFF.md: the port-1 swap figure colliding with itself (11 DRC errors, BM1_DATA_P
   10.7 mm > 9.5), the VBUS link at U11 pin 1, the two 5V_PI pours, the 3V3 via vs R21 pad 2, VBUS_OUT's 6
   class-clearance items, the dangling zone via. M2's bar (BRIEF §7): 0 unconnected but J1's no-connect pair,
   errors only Sofar's copied features with reasons, 0 copper-defect warnings, check_rules clean, pairs within the
   mote's lengths, Kelvin yes.
4. Then M3 (the JLCPCB DFM sweep, BRIEF §6: every limit fetched from JLCPCB's published pages, cited in DFM.md,
   encoded in the design rules) and M4 (REPORT.md per BRIEF §8, renders, the draft PR updated).

I will not answer questions mid-run; decide, record, continue. Stop and write REPORT.md if a hard rule would break
or the board must grow beyond the brief. When M2 is at its bar (and again after M4), send QE round 2 to the standing
S7 QE session ("QE review S7.a layout experiment brief (PR #29)"; docs/PROMPTS.md §5; name your session in the
request so the report comes to you), save each report in qe/, fix and resend until it approves, and tell me the
verdict, the PR link and the pass/fail table. Give me a one-line status after every rebuild, and stop to report if
a milestone stalls after three rebuilds.
```
