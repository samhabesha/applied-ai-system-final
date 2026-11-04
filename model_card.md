# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

- Suggests the top 5 songs from a small catalog that best fit one listener's taste.
- Assumes the listener can describe their taste with one favorite genre, one mood, a target energy level (0-1) and whether they like acoustic sound.
- Built for classroom exploration of how recommenders turn data into rankings. **Not intended** for real users, real streaming catalogs, or decisions about artists (for example, which artists get promoted or paid).

---

## 3. How the Model Works

Every song gets points, and the songs with the most points are recommended.
- A song in your favorite genre gets the most points (+2).
- A song with your favorite mood gets +1.
- Energy works like a "closeness" meter: the closer a song's energy is to the energy you want, the more points it gets (up to +1.5). A calm song is not "worse" than a loud one; it only loses points if it is far from what *you* want.
- A small bonus (up to +0.5) goes to acoustic songs if you like acoustic sound, or to produced/electronic songs if you do not.

Every song in the catalog is scored this way, then the list is sorted from highest to lowest and the top 5 are shown with the reasons for their points. Compared with the starter (which just returned the first songs in the file), the model adds real scoring, the closeness rule for energy, the acoustic preference, plain-language reasons, and adjustable weights for experiments.

---

## 4. Data

- 20 songs: the 10 starter songs plus 10 added to cover missing styles (hip hop, classical, metal, country, EDM, R&B, reggae, folk, latin, blues) and moods (confident, peaceful, aggressive, nostalgic, euphoric, romantic, melancholy, sad).
- Each song has genre, mood, energy, tempo, valence, danceability and acousticness. The scoring uses genre, mood, energy and acousticness.
- Missing from the data: lyrics and language, popularity, release year, listening history, and anything about how real people react to the songs. Most genres have only one song, while lofi has three and pop two, so those genres have more chances to appear.

---

## 5. Strengths

- Clear, single-genre tastes work well: *Chill Lofi* gets three lofi songs first, and *Deep Intense Rock* gets *Storm Runner* with a big lead.
- The energy closeness rule behaves sensibly: a low-energy listener is never pushed toward the loudest tracks.
- Every recommendation explains itself (for example "genre match: pop (+2.0); energy 0.82 vs target 0.80 (+1.47)"), so it is easy to see *why* a song ranked where it did.

---

## 6. Limitations and Bias

The clearest weakness is the **genre filter bubble combined with exact matching**. Because a genre match is worth the most points, the system strongly favors songs with the exact same label, even when another song matches the listener's mood and energy almost perfectly. *Rooftop Lights* is labeled "indie pop", so a pop fan never gets genre credit for it, and a k-pop fan gets zero genre points for every song because k-pop is not in the catalog. With only 20 songs, the same high-energy tracks (*Gym Hero*, *Storm Runner*) appear for many different users: the system is not tailoring to them, there is simply little else to choose from. A real platform with this logic could keep pushing listeners toward the biggest labeled genres and starve niche or mixed-genre artists of exposure.

---

## 7. Evaluation

Six profiles plus the default were tested, and one weight-shift experiment was run (genre 2.0 -> 1.0, energy 1.5 -> 3.0). Outputs below are from `python -m src.main`.

```
=== High-Energy Pop ===
Profile: genre=pop, mood=happy, energy=0.85, likes_acoustic=False
1. Sunrise City by Neon Echo [pop, happy]  score 4.87
   because: genre match: pop (+2.0); mood match: happy (+1.0); energy 0.82 vs target 0.85 (+1.46); produced/electronic sound (+0.41)
2. Gym Hero by Max Pulse [pop, intense]  score 3.85
   because: genre match: pop (+2.0); energy 0.93 vs target 0.85 (+1.38); produced/electronic sound (+0.47)
3. Fuego Nights by Sol Rivera [latin, happy]  score 2.88
   because: mood match: happy (+1.0); energy 0.84 vs target 0.85 (+1.48); produced/electronic sound (+0.40)
4. Rooftop Lights by Indigo Parade [indie pop, happy]  score 2.69
   because: mood match: happy (+1.0); energy 0.76 vs target 0.85 (+1.36); produced/electronic sound (+0.33)
5. Storm Runner by Voltline [rock, intense]  score 1.86
   because: energy 0.91 vs target 0.85 (+1.41); produced/electronic sound (+0.45)
```

```
=== Chill Lofi ===
Profile: genre=lofi, mood=chill, energy=0.35, likes_acoustic=True
1. Library Rain by Paper Lanterns [lofi, chill]  score 4.93
   because: genre match: lofi (+2.0); mood match: chill (+1.0); energy 0.35 vs target 0.35 (+1.50); acoustic sound (+0.43)
2. Midnight Coding by LoRoom [lofi, chill]  score 4.75
   because: genre match: lofi (+2.0); mood match: chill (+1.0); energy 0.42 vs target 0.35 (+1.40); acoustic sound (+0.35)
3. Focus Flow by LoRoom [lofi, focused]  score 3.81
   because: genre match: lofi (+2.0); energy 0.40 vs target 0.35 (+1.42); acoustic sound (+0.39)
4. Spacewalk Thoughts by Orbit Bloom [ambient, chill]  score 2.85
   because: mood match: chill (+1.0); energy 0.28 vs target 0.35 (+1.40); acoustic sound (+0.46)
5. Coffee Shop Stories by Slow Stereo [jazz, relaxed]  score 1.92
   because: energy 0.37 vs target 0.35 (+1.47); acoustic sound (+0.45)
```

```
=== Deep Intense Rock ===
Profile: genre=rock, mood=intense, energy=0.92, likes_acoustic=False
1. Storm Runner by Voltline [rock, intense]  score 4.93
   because: genre match: rock (+2.0); mood match: intense (+1.0); energy 0.91 vs target 0.92 (+1.48); produced/electronic sound (+0.45)
2. Gym Hero by Max Pulse [pop, intense]  score 2.96
   because: mood match: intense (+1.0); energy 0.93 vs target 0.92 (+1.48); produced/electronic sound (+0.47)
3. Laser Bloom by Kiro Volt [edm, euphoric]  score 1.94
   because: energy 0.95 vs target 0.92 (+1.46); produced/electronic sound (+0.48)
4. Iron Pulse by Grave Signal [metal, aggressive]  score 1.91
   because: energy 0.97 vs target 0.92 (+1.43); produced/electronic sound (+0.48)
5. Fuego Nights by Sol Rivera [latin, happy]  score 1.78
   because: energy 0.84 vs target 0.92 (+1.38); produced/electronic sound (+0.40)
```

```
=== Conflicted: high energy but sad ===
Profile: genre=blues, mood=sad, energy=0.9, likes_acoustic=False
1. Rainy Blues Alley by Otis Grey [blues, sad]  score 3.75
   because: genre match: blues (+2.0); mood match: sad (+1.0); energy 0.33 vs target 0.90 (+0.64); produced/electronic sound (+0.10)
2. Storm Runner by Voltline [rock, intense]  score 1.94
   because: energy 0.91 vs target 0.90 (+1.48); produced/electronic sound (+0.45)
3. Gym Hero by Max Pulse [pop, intense]  score 1.93
   because: energy 0.93 vs target 0.90 (+1.46); produced/electronic sound (+0.47)
4. Laser Bloom by Kiro Volt [edm, euphoric]  score 1.91
   because: energy 0.95 vs target 0.90 (+1.43); produced/electronic sound (+0.48)
5. Iron Pulse by Grave Signal [metal, aggressive]  score 1.88
   because: energy 0.97 vs target 0.90 (+1.40); produced/electronic sound (+0.48)
```

```
=== Unknown genre (k-pop) ===
Profile: genre=k-pop, mood=happy, energy=0.7, likes_acoustic=False
1. Rooftop Lights by Indigo Parade [indie pop, happy]  score 2.73
   because: mood match: happy (+1.0); energy 0.76 vs target 0.70 (+1.41); produced/electronic sound (+0.33)
2. Sunrise City by Neon Echo [pop, happy]  score 2.73
   because: mood match: happy (+1.0); energy 0.82 vs target 0.70 (+1.32); produced/electronic sound (+0.41)
3. Fuego Nights by Sol Rivera [latin, happy]  score 2.69
   because: mood match: happy (+1.0); energy 0.84 vs target 0.70 (+1.29); produced/electronic sound (+0.40)
4. Concrete Crown by Verse Theory [hip hop, confident]  score 1.82
   because: energy 0.78 vs target 0.70 (+1.38); produced/electronic sound (+0.44)
5. Night Drive Loop by Neon Echo [synthwave, moody]  score 1.81
   because: energy 0.75 vs target 0.70 (+1.42); produced/electronic sound (+0.39)
```

```
=== Acoustic EDM fan ===
Profile: genre=edm, mood=euphoric, energy=0.95, likes_acoustic=True
1. Laser Bloom by Kiro Volt [edm, euphoric]  score 4.51
   because: genre match: edm (+2.0); mood match: euphoric (+1.0); energy 0.95 vs target 0.95 (+1.50); acoustic sound (+0.01)
2. Gym Hero by Max Pulse [pop, intense]  score 1.50
   because: energy 0.93 vs target 0.95 (+1.47); acoustic sound (+0.03)
3. Storm Runner by Voltline [rock, intense]  score 1.49
   because: energy 0.91 vs target 0.95 (+1.44); acoustic sound (+0.05)
4. Iron Pulse by Grave Signal [metal, aggressive]  score 1.49
   because: energy 0.97 vs target 0.95 (+1.47); acoustic sound (+0.02)
5. Fuego Nights by Sol Rivera [latin, happy]  score 1.44
   because: energy 0.84 vs target 0.95 (+1.33); acoustic sound (+0.10)
```

```
=== Default (experiment) ===
Profile: genre=pop, mood=happy, energy=0.8
1. Sunrise City by Neon Echo [pop, happy]  score 4.94
   because: genre match: pop (+1.0); mood match: happy (+1.0); energy 0.82 vs target 0.80 (+2.94)
2. Rooftop Lights by Indigo Parade [indie pop, happy]  score 3.88
   because: mood match: happy (+1.0); energy 0.76 vs target 0.80 (+2.88)
3. Fuego Nights by Sol Rivera [latin, happy]  score 3.88
   because: mood match: happy (+1.0); energy 0.84 vs target 0.80 (+2.88)
4. Gym Hero by Max Pulse [pop, intense]  score 3.61
   because: genre match: pop (+1.0); energy 0.93 vs target 0.80 (+2.61)
5. Concrete Crown by Verse Theory [hip hop, confident]  score 2.94
   because: energy 0.78 vs target 0.80 (+2.94)
```

```
=== Conflicted: high energy but sad (experiment) ===
Profile: genre=blues, mood=sad, energy=0.9, likes_acoustic=False
1. Storm Runner by Voltline [rock, intense]  score 3.42
   because: energy 0.91 vs target 0.90 (+2.97); produced/electronic sound (+0.45)
2. Rainy Blues Alley by Otis Grey [blues, sad]  score 3.39
   because: genre match: blues (+1.0); mood match: sad (+1.0); energy 0.33 vs target 0.90 (+1.29); produced/electronic sound (+0.10)
3. Gym Hero by Max Pulse [pop, intense]  score 3.38
   because: energy 0.93 vs target 0.90 (+2.91); produced/electronic sound (+0.47)
4. Laser Bloom by Kiro Volt [edm, euphoric]  score 3.33
   because: energy 0.95 vs target 0.90 (+2.85); produced/electronic sound (+0.48)
5. Iron Pulse by Grave Signal [metal, aggressive]  score 3.27
   because: energy 0.97 vs target 0.90 (+2.79); produced/electronic sound (+0.48)
```

**Comparing profiles:**
- *High-Energy Pop vs Chill Lofi:* the pop profile pulls bright, high-energy, low-acoustic songs (*Sunrise City*, *Gym Hero*), while lofi shifts completely to quiet, acoustic tracks (*Library Rain*, *Midnight Coding*). The two profiles disagree on genre, mood, energy *and* acoustics, so their top 5 lists do not overlap.
- *High-Energy Pop vs Deep Intense Rock:* both include *Gym Hero*, because it is high energy and its mood is "intense". Rock gets it on mood; pop gets it on genre. This is why *Gym Hero* keeps appearing for people who just want happy pop: it is the only other "pop" song and its energy is close to theirs.
- *Deep Intense Rock vs Conflicted (blues/sad/0.9):* after the one blues song, the conflicted list is almost the same as the rock list (*Storm Runner*, *Gym Hero*, *Laser Bloom*, *Iron Pulse*), because energy 0.9 drags it toward loud tracks once genre and mood stop matching. The system cannot tell that "sad but energetic" is a real, different taste.
- *Unknown genre (k-pop) vs Default pop:* with no genre matches, the k-pop list is decided only by mood and energy, so the happy songs tie near the top. The genre weight silently disappears for anyone outside the catalog's labels.
- *Acoustic EDM fan vs High-Energy Pop:* the EDM fan gets *Laser Bloom* far ahead (genre + mood + energy), then a cluster of loud songs with nearly equal scores. The "likes acoustic" preference barely matters, because no high-energy song in the catalog is acoustic: the data cannot satisfy that taste.

**Weight-shift experiment:** for the default profile *Gym Hero* fell from #2 to #4 and happy non-pop songs rose; for the conflicted profile the only blues song lost first place to a rock song. Two numbers changed what the system "believes" the user wants, which shows how much power the weights have.

---

## 8. Future Work

1. Replace exact genre matching with genre *families* (so "indie pop" earns partial credit for pop) and handle genres not in the catalog.
2. Add a diversity rule so the top 5 cannot be dominated by one artist or genre (avoiding the filter bubble).
3. Learn the weights from real feedback (likes and skips) instead of picking them by hand, and grow the catalog so each genre has several songs.

---

## 9. Personal Reflection

_(To be written by Samson in his own words.)_
