# news-image-20261127

[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/a5044673838-gif/news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/a5044673838-gif/news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

A one-day world news infographic for make.fun's "Sum up 27 November's world
news in one image" bounty ($100 shared pot). The program draws a 1024x1024
PNG with six verified stories from the 27 November 2026 news cycle:
two Italians killed in a drone strike in Kuwait that Iran denies,
Israel killing 9 people in Gaza overnight as Hamas weighs its response,
the Thanksgiving storm that postponed the Macy's parade and cut power
to 400,000, Elon Musk pledging two SpaceX shares for every US child
(about $18 billion), Gerard Depardieu ordered to stand trial on a rape
charge, and a diesel tanker capsizing off Ibiza killing one person.
Every story was checked against Reuters, the Associated Press, the BBC,
the New York Times or The Hindu reporting; nothing is invented. Pure
Python standard library, no network, fully deterministic.

## Run it

```
python3 main.py
```

Writes `entry.png` to `/output` (`MAKEFUN_OUTPUT_DIR` overrides).
