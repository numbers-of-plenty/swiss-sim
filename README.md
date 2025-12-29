# swiss-sim
Simulation of swiss-system outcomes for demonstration purposes

## Tournament Simulation

This repository contains a simulation of a 12-player Swiss-system tournament.

### Rules

- **Players**: 12 players with normally distributed skill levels
- **Scoring Probability**: When a player with skill x2 plays against a player with skill x1, the probability that x2 scores is: `e^(x2-x1) / (e^(x2-x1) + 1)`
- **Game**: First player to reach 11 points with at least a 2-point lead wins (e.g., 11-9, 14-12)
- **Match**: Best of 3 games (first to win 2 games)
- **Tournament**: 4 rounds of Swiss-system pairing
- **Ranking**: Players are sorted by:
  1. Number of matches won
  2. Game difference (games won - games lost)
  3. Score difference (total score - opponent score)

### Usage

Run the simulation:

```bash
python3 tournament_sim.py
```

The output is in TSV (tab-separated values) format, showing:
- Rank
- Player ID
- Skill level
- Matches won
- Games won/lost
- Score statistics
