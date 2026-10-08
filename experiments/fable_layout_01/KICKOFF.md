# Kickoff prompt — layout experiment 01

Start a new Claude Code session on this repo with **Fable 5.1, high effort**, then paste:

```
Layout experiment 01. Read CLAUDE.md, then experiments/fable_layout_01/BRIEF.md in full; it is your spec and its
hard rules override anything else you infer. Create the branch experiment/fable-layout-01 from main and work only
inside experiments/fable_layout_01/. KiCad is closed; use KiCad 9's bundled Python (pcbnew) and kicad-cli. Run
milestones M0-M5 autonomously, committing after each with renders in out/ and an entry in LOG.md. Stop and write
REPORT.md if a hard rule would break or the board must grow beyond the brief. Never merge; open a draft PR titled
"EXPERIMENT (do not merge): fable layout 01" when done, and tell me its link and the pass/fail table from BRIEF §8.
```

Review afterwards: `REPORT.md`, the renders in `out/`, the draft PR. The QE can review the result like any PR.
