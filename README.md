Live demo: https://ehowells.github.io/Stardew-Valley-Perfection-Tracker/ (Note: the backend is hosted on Render's free tier and may take ~30 seconds to wake up on the first request)
Don't have a Stardew Valley save file? Download the demo file below and upload it:
(demo still in progress)

This project combines Stardew Valley’s internal game metadata (.xnb files, unpacked to JSON) with player save data (.xml) to track progress toward the end-game “perfection” goal.
It automates milestones including (but not limited to):

- Catching all fish species (including festival / 1.6 additions)

- Cooking every recipe at least once

- Crafting all items

- Completing the Community Center or Joja route

The tracker works offline and does not modify your save.
All data is sourced from your local Stardew Valley installation and can be explored using Python, pandas, and SQL.
