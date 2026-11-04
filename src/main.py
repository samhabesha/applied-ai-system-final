"""
Command line runner for the Music Recommender Simulation.

Run from the repo root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Print a readable ranked list with scores and reasons for one profile."""
    print(f"\n=== {name} ===")
    print("Profile: " + ", ".join(f"{key}={value}" for key, value in user_prefs.items()))
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=k), start=1):
        print(f"{rank}. {song['title']} by {song['artist']} [{song['genre']}, {song['mood']}]  score {score:.2f}")
        print(f"   because: {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print_recommendations("Default: Pop / Happy", {"genre": "pop", "mood": "happy", "energy": 0.8}, songs)


if __name__ == "__main__":
    main()
