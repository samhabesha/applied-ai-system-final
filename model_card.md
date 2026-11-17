# 🎧 Model Card: VibeFinder 2.0

## 1. Model name and version
**VibeFinder 2.0.** It extends VibeFinder 1.0 (the Module 3 Music Recommender Simulation) with retrieval over custom notes, a Claude-powered parser and writer, guardrails, a confidence score and logging.

## 2. Intended use
- A listener describes what they want in plain English ("sad acoustic songs for a rainy day") and gets 3 picks from a 20-song catalog, each with reasons.
- Built as a classroom portfolio project to show RAG, guardrails and evaluation. **Not intended** for real users, real catalogs, or any decision about artists (promotion, payment).

## 3. How it works
1. Input guardrails reject empty, overly long, prompt-injection and off-topic requests.
2. The retriever finds relevant notes in `knowledge/` (genre families and slang, moods, activities).
3. A parser turns the request into a profile. With an API key, Claude (`claude-opus-5-5` by default) returns schema-constrained JSON grounded in the notes; otherwise a rule-based parser uses the same notes. Either way, `validate_profile` cleans the result.
4. The VibeFinder 1.0 scorer ranks every song; the notes add partial credit for related genres and moods and a penalty for "nothing too heavy".
5. A confidence score (0–1) is computed. Under 0.5 the answer admits the match is weak.
6. Claude (or a template) writes the answer from the retrieved songs only. Output guardrails block invented titles, ungrounded answers and leaked keys, and fall back to the template.
7. Everything is logged to `logs/vibefinder.jsonl`.

## 4. Data
- `data/songs.csv`: 20 fictional songs, 15 genres, 14 moods, numeric energy and acousticness.
- `knowledge/*.md`: 42 hand-written notes (18 genres, 14 moods, 10 activities) with aliases and family groupings. I wrote these, so they carry my own idea of which genres are "related".

## 5. Evaluation results
- **pytest:** 27/27 passing, including fake-model tests for hallucinated titles, invalid JSON, API errors and injection.
- **eval.py:** 12/12 cases pass offline (8 normal or edge requests, 1 vague request that must score low, 3 attacks that must be blocked). Average confidence on answered requests: 0.77.
- **RAG before/after:** right genre family in the top 3 for 2/8 slang or out-of-catalog requests without notes, versus 8/8 with notes.
- Full tables are in the [README](README.md#testing-and-reliability) and [`assets/eval_results.md`](assets/eval_results.md).

## 6. Limitations and bias
- **Tiny catalog.** With 20 songs and one song for most genres, "related genre" often means "the only song we have"; *Sunrise City* and *Rooftop Lights* show up for many pop-ish requests.
- **My notes are the bias.** The families (k-pop → pop, reggae → latin, blues → soul) are my judgment calls. Someone who disagrees, for example who sees reggae as its own world, gets results shaped by my map. Genres I didn't write a note for, like polka, aren't understood at all.
- **Keyword retrieval misses paraphrase.** "Music that feels like a movie hero walking away from an explosion" matches nothing; an embedding retriever would do better.
- **Simple negation only.** "Nothing too heavy" and a few phrases are handled, but "anything except country" is not.
- **Rule conflicts.** When a mood word and an activity disagree ("upbeat" + "gym"), the mood wins. That's a design choice, not a learned behavior.
- **English only**, no lyrics, no listening history.

## 7. Misuse and how it's prevented
- **Prompt injection** (making the assistant ignore its rules, reveal its prompt or its key): input patterns block it before any model call, the system prompts tell Claude to treat the request as untrusted data, and the output check blocks anything that looks like an API key.
- **Using it as a general chatbot:** the off-topic guardrail refuses non-music requests.
- **Fabricated recommendations** (e.g., claiming a real artist is in the catalog): the output guardrail only allows catalog titles and artists in bold and requires at least one retrieved song.
- **Key leakage:** keys live in a git-ignored `.env`, never in code or logs.
- **Residual risk:** the regex filters can be dodged with creative wording. The impact is low, since the worst case is an odd music answer, and it's limited because Claude never ranks songs and every answer is checked against the catalog.

## 8. What surprised me in testing
The eval harness found problems that a few hand-typed tests would have missed. "Happy k-pop to dance to" returned EDM first, because the knowledge base listed "dance" as an EDM alias, so one word overrode the genre the listener actually named. "Workout music but nothing too heavy" first scored only 0.44: the workout note asked for *intense* songs while the heavy-music rule punished intense songs, so two rules were fighting each other. The before/after comparison surprised me too. Without the knowledge notes, the system didn't just give worse answers to "chillhop for coding", it refused the request as off-topic, because it didn't recognize a single word. Retrieval affected the guardrails, not only the recommendations.

## 9. Reflection and AI collaboration

**How I used AI.** I built this with Claude Code as my pair programmer. It drafted most of the code (retriever, guardrails, pipeline, tests and eval harness) from my plan: upgrade VibeFinder 1.0 with RAG, guardrails, logging and a confidence score. My job was to decide what the system should and shouldn't do, run the tests and the eval, read the results, and decide what to fix. The project also uses Claude inside the app, to parse requests and write answers.

**A suggestion I accepted.** Treat the LLM as untrusted: it may parse the request and write the answer, but it never ranks songs, and its JSON is validated before use. I accepted it because it keeps every recommendation explainable with the original scorer, and because a hallucinated song can't be ranked when the model doesn't rank anything.

**A suggestion I changed.** The first knowledge base listed "dance" as an EDM alias, and the eval showed it hijacking "k-pop to dance to". It was removed, because "dance" describes an activity, not a genre. The first workout rule also conflicted with "nothing too heavy", so the profile now switches an intense mood to *confident* when the listener asks to avoid heavy music. In both cases the AI's first version looked reasonable, and only measuring it showed the problem.

**What this project says about me as an AI engineer.** I build AI features the way production teams need them: the model gets a narrow job, everything around it is tested, and the system says so when it isn't sure. In VibeFinder 2.0 I added retrieval over my own knowledge base to a transparent scorer, used Claude with schema-validated output, put guardrails on both input and output, and proved the improvement with numbers (right genre family 2/8 → 8/8) instead of claims. My work building Copilot Studio agents shaped this: I care less about clever prompts and more about what happens when the model is wrong.
