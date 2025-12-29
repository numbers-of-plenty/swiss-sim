#!/usr/bin/env python3
"""
Swiss-system tournament simulation for 12 players.
Each player has a skill level (normally distributed).
Scoring probability: e^(k*(x2-x1))/(e^(k*(x2-x1)) + 1) where k ≈ 0.663
This ensures 1 std dev gives ~66% chance to score against median.
Game: First to 11 with at least 2-point lead
Match: Best of 3 games (first to win 2 games)
Tournament: 4 rounds of Swiss-system pairing
"""

import random
import math
from typing import List, Tuple, Optional

# Skill multiplier: ensures 1 std dev gives ~66% scoring probability vs median
SKILL_MULTIPLIER = math.log(0.66 / 0.34)  # ≈ 0.663


class MatchResult:
    """Stores the result of a match between two players."""
    
    def __init__(self, player1_id: int, player2_id: int):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.game_scores = []  # List of (score1, score2) tuples
        self.player1_games_won = 0
        self.player2_games_won = 0
    
    def add_game(self, score1: int, score2: int):
        """Add a game result."""
        self.game_scores.append((score1, score2))
        if score1 > score2:
            self.player1_games_won += 1
        else:
            self.player2_games_won += 1


class Player:
    """Represents a player in the tournament."""
    
    def __init__(self, player_id: int, skill: float):
        self.id = player_id
        self.skill = skill
        self.matches_won = 0
        self.matches_lost = 0
        self.games_won = 0
        self.games_lost = 0
        self.total_score = 0
        self.opponent_score = 0
        self.last_opponent_id: Optional[int] = None
        self.match_results = []  # List of MatchResult objects
    
    def game_diff(self) -> int:
        """Calculate game difference."""
        return self.games_won - self.games_lost
    
    def score_diff(self) -> int:
        """Calculate score difference."""
        return self.total_score - self.opponent_score
    
    def __repr__(self):
        return f"Player{self.id}(skill={self.skill:.2f})"


def score_probability(skill_scorer: float, skill_opponent: float) -> float:
    """
    Calculate probability that scorer scores a point against opponent.
    Formula: e^(k*diff) / (e^(k*diff) + 1) where k ≈ 0.663
    This ensures 1 std dev difference gives ~66% scoring probability.
    """
    diff = skill_scorer - skill_opponent
    exp_diff = math.exp(SKILL_MULTIPLIER * diff)
    return exp_diff / (exp_diff + 1)


def simulate_game(player1: Player, player2: Player) -> Tuple[int, int]:
    """
    Simulate a single game between two players.
    Returns (score1, score2) where the winner has at least 11 points and leads by at least 2.
    """
    score1 = 0
    score2 = 0
    
    # Probabilities for each player to score
    p1_scores = score_probability(player1.skill, player2.skill)
    
    while True:
        # Determine who scores this point
        if random.random() < p1_scores:
            score1 += 1
        else:
            score2 += 1
        
        # Check if someone has won (at least 11 points and leads by at least 2)
        if score1 >= 11 and score1 - score2 >= 2:
            break
        if score2 >= 11 and score2 - score1 >= 2:
            break
    
    return score1, score2


def simulate_match(player1: Player, player2: Player) -> MatchResult:
    """
    Simulate a match (best of 3 games) between two players.
    Updates player statistics and returns match result.
    """
    match_result = MatchResult(player1.id, player2.id)
    games_won_p1 = 0
    games_won_p2 = 0
    
    # Play until one player wins 2 games
    while games_won_p1 < 2 and games_won_p2 < 2:
        score1, score2 = simulate_game(player1, player2)
        match_result.add_game(score1, score2)
        
        # Update game statistics
        player1.total_score += score1
        player1.opponent_score += score2
        player2.total_score += score2
        player2.opponent_score += score1
        
        if score1 > score2:
            games_won_p1 += 1
            player1.games_won += 1
            player2.games_lost += 1
        else:
            games_won_p2 += 1
            player2.games_won += 1
            player1.games_lost += 1
    
    # Update match statistics and last opponent
    if games_won_p1 > games_won_p2:
        player1.matches_won += 1
        player2.matches_lost += 1
    else:
        player2.matches_won += 1
        player1.matches_lost += 1
    
    player1.last_opponent_id = player2.id
    player2.last_opponent_id = player1.id
    
    player1.match_results.append(match_result)
    player2.match_results.append(match_result)
    
    return match_result


def swiss_pairing(players: List[Player], round_num: int) -> List[Tuple[Player, Player]]:
    """
    Create pairings for a Swiss-system round.
    Players are sorted by current standings and paired sequentially.
    """
    # Sort players by current standings
    sorted_players = sorted(
        players,
        key=lambda p: (-p.matches_won, -p.game_diff(), -p.score_diff(), p.id)
    )
    
    # Pair players sequentially (1 vs 2, 3 vs 4, etc.)
    pairings = []
    for i in range(0, len(sorted_players), 2):
        pairings.append((sorted_players[i], sorted_players[i + 1]))
    
    return pairings


def simulate_tournament():
    """
    Simulate a complete 12-player Swiss-system tournament with 4 rounds.
    Outputs TSV after each round and concatenated final view.
    """
    # Generate 12 players with normally distributed skills (mean=0, std=1)
    players = [Player(i + 1, random.gauss(0, 1)) for i in range(12)]
    
    # Store outputs for each round
    round_outputs = []
    
    # Run 4 rounds of Swiss-system
    for round_num in range(1, 5):
        pairings = swiss_pairing(players, round_num)
        
        # Simulate all matches in this round
        for player1, player2 in pairings:
            simulate_match(player1, player2)
        
        # Output TSV for this round
        round_output = output_round_tsv(players, round_num)
        round_outputs.append(round_output)
    
    # Output concatenated view
    output_concatenated_tsv(round_outputs)


def output_round_tsv(players: List[Player], round_num: int) -> List[List[str]]:
    """
    Output tournament results after a round in TSV format.
    Returns the data for later concatenation.
    """
    # Sort players by current standings
    sorted_players = sorted(
        players,
        key=lambda p: (-p.matches_won, -p.game_diff(), -p.score_diff(), p.id)
    )
    
    print(f"\n{'='*80}")
    print(f"ROUND {round_num} RESULTS")
    print(f"{'='*80}")
    
    # Header
    header = [
        "Rank",
        "Player",
        "Skill",
        "Last_Opp",
        "Games_Detail",
        "Match_W",
        "Match_L",
        "Game_W",
        "Game_L",
        "Game_Diff",
        "Score_W",
        "Score_L",
        "Score_Diff"
    ]
    print("\t".join(header))
    
    # Collect data for return
    data_rows = [header]
    
    # Player data
    for rank, player in enumerate(sorted_players, start=1):
        # Get last match details
        last_opp = f"P{player.last_opponent_id}" if player.last_opponent_id else "-"
        
        # Get games detail from last match
        games_detail = "-"
        if player.match_results:
            last_match = player.match_results[-1]
            game_strs = []
            for score1, score2 in last_match.game_scores:
                if last_match.player1_id == player.id:
                    game_strs.append(f"{score1}-{score2}")
                else:
                    game_strs.append(f"{score2}-{score1}")
            games_detail = ",".join(game_strs)
        
        row = [
            str(rank),
            f"P{player.id}",
            f"{player.skill:.4f}",
            last_opp,
            games_detail,
            str(player.matches_won),
            str(player.matches_lost),
            str(player.games_won),
            str(player.games_lost),
            str(player.game_diff()),
            str(player.total_score),
            str(player.opponent_score),
            str(player.score_diff())
        ]
        
        print("\t".join(row))
        data_rows.append(row)
    
    return data_rows


def output_concatenated_tsv(round_outputs: List[List[List[str]]]) -> None:
    """
    Output all rounds concatenated side-by-side.
    """
    print(f"\n\n{'='*120}")
    print("FULL TOURNAMENT VIEW (ALL ROUNDS CONCATENATED)")
    print(f"{'='*120}\n")
    
    # Columns that should not be prefixed with round number (static player info)
    STATIC_COLUMNS = {"Player", "Skill"}
    MISSING_VALUE = "-"
    
    # Create a mapping of player ID to row index for each round
    # First, output headers for all rounds
    header_parts = []
    for i, round_data in enumerate(round_outputs, 1):
        round_header = [f"R{i}_{col}" if col not in STATIC_COLUMNS else col 
                       for col in round_data[0]]
        header_parts.append("\t".join(round_header))
    
    print("\t".join(header_parts))
    
    # Get all unique player IDs
    all_players = set()
    for round_data in round_outputs:
        for row in round_data[1:]:  # Skip header
            player_id = row[1]  # Player column
            all_players.add(player_id)
    
    # Sort player IDs numerically by extracting the number
    def player_sort_key(player_id: str) -> int:
        """Extract numeric part from player ID (e.g., 'P12' -> 12)"""
        return int(player_id[1:])
    
    # For each player, concatenate their rows across all rounds
    for player_id in sorted(all_players, key=player_sort_key):
        row_parts = []
        for round_data in round_outputs:
            # Find this player's row in this round
            player_row = None
            for row in round_data[1:]:  # Skip header
                if row[1] == player_id:
                    player_row = row
                    break
            
            if player_row:
                row_parts.append("\t".join(player_row))
            else:
                # Should not happen, but handle gracefully
                row_parts.append("\t".join([MISSING_VALUE] * len(round_data[0])))
        
        print("\t".join(row_parts))


def main():
    """Main function to run the tournament simulation."""
    random.seed()  # Use system time for randomness
    
    # Run tournament (outputs results internally)
    simulate_tournament()


if __name__ == "__main__":
    main()
