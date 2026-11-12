"""Load and save the board with no edit, so later diffs show only real changes."""
import boardio

boardio.save(boardio.load())
print("normalized", boardio.BOARD)
