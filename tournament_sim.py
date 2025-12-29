#!/usr/bin/env python3
"""
Swiss-system tournament simulation for 12 players.
Each player has a skill level (normally distributed).
Scoring probability: e^(x2-x1)/(e^(x2-x1) + 1)
Game: First to 11 with at least 2-point lead
Match: Best of 3 games (first to win 2 games)
Tournament: 4 rounds of Swiss-system pairing
"""

import random
import math
from typing import List, Tuple


class Player:
    """Represents a player in the tournament."""
    
    def __init__(self, player_id: int, skill: float):
        self.id = player_id
        self.skill = skill
        self.matches_won = 0
        self.games_won = 0
        self.games_lost = 0
        self.total_score = 0
        self.opponent_score = 0
    
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
    Formula: e^(skill_scorer - skill_opponent) / (e^(skill_scorer - skill_opponent) + 1)
    """
    diff = skill_scorer - skill_opponent
    exp_diff = math.exp(diff)
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


def simulate_match(player1: Player, player2: Player) -> None:
    """
    Simulate a match (best of 3 games) between two players.
    Updates player statistics.
    """
    games_won_p1 = 0
    games_won_p2 = 0
    
    # Play until one player wins 2 games
    while games_won_p1 < 2 and games_won_p2 < 2:
        score1, score2 = simulate_game(player1, player2)
        
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
    
    # Update match statistics
    if games_won_p1 > games_won_p2:
        player1.matches_won += 1
    else:
        player2.matches_won += 1


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


def simulate_tournament() -> List[Player]:
    """
    Simulate a complete 12-player Swiss-system tournament with 4 rounds.
    Returns the list of players sorted by final standings.
    """
    # Generate 12 players with normally distributed skills (mean=0, std=1)
    players = [Player(i + 1, random.gauss(0, 1)) for i in range(12)]
    
    # Run 4 rounds of Swiss-system
    for round_num in range(1, 5):
        pairings = swiss_pairing(players, round_num)
        for player1, player2 in pairings:
            simulate_match(player1, player2)
    
    # Sort players by final standings
    final_standings = sorted(
        players,
        key=lambda p: (-p.matches_won, -p.game_diff(), -p.score_diff(), p.id)
    )
    
    return final_standings


def output_tsv(players: List[Player]) -> None:
    """
    Output tournament results in TSV format.
    """
    # Header
    print("Rank\tPlayer\tSkill\tMatches_Won\tGames_Won\tGames_Lost\tGame_Diff\tTotal_Score\tOpponent_Score\tScore_Diff")
    
    # Player data
    for rank, player in enumerate(players, start=1):
        print(f"{rank}\t"
              f"Player{player.id}\t"
              f"{player.skill:.4f}\t"
              f"{player.matches_won}\t"
              f"{player.games_won}\t"
              f"{player.games_lost}\t"
              f"{player.game_diff()}\t"
              f"{player.total_score}\t"
              f"{player.opponent_score}\t"
              f"{player.score_diff()}")


def main():
    """Main function to run the tournament simulation."""
    random.seed()  # Use system time for randomness
    
    # Run tournament
    final_standings = simulate_tournament()
    
    # Output results
    output_tsv(final_standings)


if __name__ == "__main__":
    main()
