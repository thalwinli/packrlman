# ASCII Mockups: Basic Pacman Game

**Generated**: 2026-04-17
**Window**: ~560 x 452 px (20 cols x 15 rows @ 28px/cell + 32px HUD)
**Legend**: `#` wall (blue), `.` dot (white), `P` player (yellow), `G` ghost (red), ` ` empty floor

---

## 1. Playing State

```
####################
#P.....#..#...#...G#
#.###.....##....##.#
#...#..#...#..#....#
##....##..#...###..#
#..#....#....#.....#
#.###..#..##...#..##
#....#....#...##...#
#.#....##...#....#.#
#..##....#....##...#
##....#.....##...#.#
#.G.#...##..#....#.#
#.....#....#...##..#
#..##...#......#..G#
####################
 Score: 12   Status: playing
```

*The player (P) has just entered the maze near the top-left and is eating dots. Three ghosts (G) roam the corners and middle. HUD bar at the bottom shows live score and status.*

---

## 2. WIN Overlay

```
####################
#P.....#..#...#... G#
#.###.....##....##.#
#...#..#...#..#....#
##....##..#...###..#
#..#..+------------+#
#.###.|            |#
#....#| YOU WIN -- |#
#.#...| press R    |#
#..##.|            |#
##....+------------+#
#.G.#...##..#....#.#
#.....#....#...##..#
#..##...#......#..G#
####################
 Score: 45   Status: won
```

*All dots cleared. Grid dims behind a semi-transparent overlay; a centered box announces the win in green text. Pressing R regenerates a fresh random map.*

---

## 3. LOSE Overlay

```
####################
#......#..#...#....#
#.###.....##....##.#
#...#..#...#..#....#
##....##..#...###..#
#..#..+--------------+
#.###.|              |
#....#| GAME OVER -- |
#.#...| press R      |
#..##.|              |
##....+--------------+
#...#...##..#....#.#
#.....#....#...##..#
#..##...#......#...#
####################
 Score: 12   Status: lost
```

*A ghost caught the player — P is gone from the grid (overlapped by G at collision). Dim overlay with red text announces game over. R starts a new random map.*
