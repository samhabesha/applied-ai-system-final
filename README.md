# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

**How real recommenders work.** Platforms like Spotify mix two ideas. *Collaborative filtering* looks at people: "listeners who liked what you like also liked X", using plays, skips, likes and playlists from millions of users. *Content-based filtering* looks at the songs themselves: genre, mood, tempo, energy and audio features, and recommends tracks that resemble what you already enjoy. Real systems blend both and retrain constantly on behavior. This simulation uses **content-based filtering only**, because we have song attributes but no other users.

**What my version prioritizes.** It tries to match a listener's *vibe*: first the style (genre), then the feeling (mood), then how intense the music feels (energy), with a small nudge for acoustic sound.

**Song features used:** `genre`, `mood`, `energy` (0-1), `acousticness` (0-1). The catalog also stores `tempo_bpm`, `valence` and `danceability` for experiments.

**UserProfile stores:** `favorite_genre`, `favorite_mood`, `target_energy` (0-1) and `likes_acoustic` (True/False).

### Algorithm Recipe
Scoring rule (one song):
- **+2.0** if the song's genre matches the favorite genre
- **+1.0** if the mood matches the favorite mood
- **Energy similarity: up to +1.5**, computed as `1.5 x (1 - |song energy - target energy|)`, so songs *closer* to the target score higher; it rewards closeness, not "more" or "less" energy
- **Acoustic nudge: up to +0.5** (`0.5 x acousticness` if the user likes acoustic, `0.5 x (1 - acousticness)` if not)

Ranking rule (the list): score every song in the catalog with the scoring rule, sort from highest to lowest, return the top *k* along with the reasons for each score.

Data flow: **Input** (user preferences) -> **Process** (loop: judge every song in the CSV with `score_song`) -> **Output** (ranking: top *k* with scores and reasons).

**Biases I expect:** genre is worth the most, so the system will probably over-prioritize genre and ignore great songs that match the mood but not the label (e.g., "indie pop" never counts as "pop"). Exact string matching also means near-genres get no credit, and a small catalog with several lofi and pop songs gives those styles more chances to appear.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` (default pop/happy profile):

```
Loaded songs: 20

=== Default: Pop / Happy ===
Profile: genre=pop, mood=happy, energy=0.8
1. Sunrise City by Neon Echo [pop, happy]  score 4.47
   because: genre match: pop (+2.0); mood match: happy (+1.0); energy 0.82 vs target 0.80 (+1.47)
2. Gym Hero by Max Pulse [pop, intense]  score 3.31
   because: genre match: pop (+2.0); energy 0.93 vs target 0.80 (+1.30)
3. Rooftop Lights by Indigo Parade [indie pop, happy]  score 2.44
   because: mood match: happy (+1.0); energy 0.76 vs target 0.80 (+1.44)
4. Fuego Nights by Sol Rivera [latin, happy]  score 2.44
   because: mood match: happy (+1.0); energy 0.84 vs target 0.80 (+1.44)
5. Concrete Crown by Verse Theory [hip hop, confident]  score 1.47
   because: energy 0.78 vs target 0.80 (+1.47)
```

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



