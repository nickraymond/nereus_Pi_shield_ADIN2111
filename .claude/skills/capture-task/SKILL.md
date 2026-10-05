---
name: capture-task
description: Capture a new task in docs/TRACKER.md without acting on it. Use when Nick says "capture", "add to the tracker", or "/capture-task <description>".
---

# /capture-task <one-line description>

1. **Size it:** one bite, several bites, or a sprint of its own.
2. **Place it:**
   - current sprint, if it blocks the sprint goal or demo
   - a later sprint, if it fits that sprint's goal
   - the Icebox, otherwise
3. **Write it** as a `- [ ]` line in TRACKER.md using the sprint's wording
   style. If it raises an unknown, also add it to SPEC.md §Open questions.
4. **Show Nick the TRACKER diff** and wait for an OK.
5. **Return to the current bite.** Don't start the captured task.
