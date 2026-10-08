# Kickoff prompt — layout experiment 1.a

Start a new Claude Code session on this repo with **Fable 5.1, high effort**, then paste:

```
Layout experiment 1.a. Read CLAUDE.md, then experiments/fable_layout_01a/BRIEF.md in full; it is your spec and its
hard rules override anything else you infer. Check out the branch experiment/fable-layout-01a (it exists on origin,
created from experiment/fable-layout-01) and work only inside experiments/fable_layout_01a/. KiCad is closed; use
KiCad 9's bundled Python (pcbnew) and kicad-cli. Read experiment 01's REPORT.md, LOG.md and qe/ reports first. Run
milestones M0-M3 autonomously, committing after each with renders in out/ and an entry in LOG.md; I will not answer
questions mid-run, so write OPTIONS.md, decide, and continue. Stop and write REPORT.md if a hard rule would break or
the board must grow beyond the brief. Never merge; open a draft PR titled "EXPERIMENT (do not merge): fable layout
1.a", then spawn the Quality Engineer review of that PR as a separate session (docs/PROMPTS.md section 5), save each
report in experiments/fable_layout_01a/qe/, fix and resend until it approves, and tell me the verdict, the PR link
and the pass/fail table.
```

Review afterwards: `OPTIONS.md`, `REPORT.md`, the renders in `out/`, the draft PR and the QE reports in `qe/`.
