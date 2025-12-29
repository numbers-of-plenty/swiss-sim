# swiss-sim
Simulation of swiss-system outcomes for demonstration purposes

## Tournament Simulation

This repository contains a simulation of a 12-player Swiss-system tournament.

### Rules

- **Players**: 12 players with normally distributed skill levels (μ=0, σ=1)
- **Scoring Probability**: When a player with skill x2 plays against a player with skill x1, the probability that x2 scores is: `e^(k*(x2-x1)) / (e^(k*(x2-x1)) + 1)` where k ≈ 0.663
  - This ensures that a player with +1 standard deviation skill has approximately **66% chance** to score against a median-skilled player
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

### Output Format

The simulation outputs two types of reports:

#### 1. Round-by-Round Results
After each of the 4 rounds, a TSV table is displayed showing:
- **Rank**: Current standing after this round
- **Player**: Player ID (P1-P12)
- **Skill**: Player's skill level
- **Last_Opp**: ID of the last opponent faced
- **Games_Detail**: Scores of all games in the last match (e.g., "11-9,5-11,11-6")
- **Match_W/Match_L**: Cumulative match wins/losses
- **Game_W/Game_L/Game_Diff**: Cumulative game wins/losses and difference
- **Score_W/Score_L/Score_Diff**: Cumulative total score and difference

#### 2. Concatenated Tournament View
At the end, all 4 rounds are displayed side-by-side with column prefixes (R1_, R2_, R3_, R4_), allowing you to see each player's complete tournament progression in a single wide table. Players are sorted by ID (P1, P2, ..., P12) for easy tracking.
