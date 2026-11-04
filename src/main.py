"""
Command line runner for the Music Recommender Simulation.

Run from the repo root with:  python -m src.main
"""

from src.recommender import load_songs, recommend_songs


PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
    # adversarial / edge cases
    "Conflicted: high energy but sad": {"genre": "blues", "mood": "sad", "energy": 0.9, "likes_acoustic": False},
    "Unknown genre (k-pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.7, "likes_acoustic": False},
    "Acoustic EDM fan": {"genre": "edm", "mood": "euphoric", "energy": 0.95, "likes_acoustic": True},
}
EXPERIMENT_WEIGHTS = {"genre": 1.0, "energy": 3.0}   # weight shift: half genre, double energy


def print_recommendations(name: str, user_prefs: dict, songs: list, k: int = 5, weights: dict = None) -> None:
    """Print a readable ranked list with scores and reasons for one profile."""
    print(f"\n=== {name} ===")
    print("Profile: " + ", ".join(f"{key}={value}" for key, value in user_prefs.items()))
    for rank, (song, score, explanation) in enumerate(recommend_songs(user_prefs, songs, k=k, weights=weights), start=1):
        print(f"{rank}. {song['title']} by {song['artist']} [{song['genre']}, {song['mood']}]  score {score:.2f}")
        print(f"   because: {explanation}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print_recommendations("Default: Pop / Happy", {"genre": "pop", "mood": "happy", "energy": 0.8}, songs)
    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs)
    print("\n##### EXPERIMENT: genre weight 2.0 -> 1.0, energy weight 1.5 -> 3.0 #####")
    for name in ["Default", "Chill Lofi", "Conflicted: high energy but sad"]:
        prefs = PROFILES.get(name, {"genre": "pop", "mood": "happy", "energy": 0.8})
        print_recommendations(name + " (experiment)", prefs, songs, weights=EXPERIMENT_WEIGHTS)


if __name__ == "__main__":
    main()
