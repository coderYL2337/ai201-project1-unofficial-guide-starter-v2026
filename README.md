# The Unofficial Guide

<!-- Yan Lu campus_life -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none, because the grader can't
> read it.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Week 1

## What This Does

This is a question-answering system over `campus_life`, a corpus of 88 short
posts written by students about dorms, dining halls, courses, and the
administrative rules nobody explains properly (add/drop deadlines, pass/fail,
printing quotas, the housing lottery). Ask it something like "what are the
wait times at Kestrel Commons during lunch?" or "by what week can I declare
pass/fail?" and it retrieves the post that actually answers it, refuses to
answer questions the corpus doesn't cover (like general trivia or other
schools' policies), and always names the source file its answer came from.

## Chunking Strategy

**Chunk size:** 350 characters (used as a paragraph-merge cap, not a fixed slice width)
**Overlap:** 0

The starter's `fallback_split` cuts at 800 characters, but every `campus_life`
post is 178-549 characters — under that window, so it never actually splits
anything: 88 documents in, 88 chunks out. That's not nothing, though. Several
posts hold more than one thought as separate paragraphs — a title, a
description, then a "the good" / "the bad" pair (see `housing_morrow_house.txt`
below) — and merging them all into one chunk means a question about just the
"bad" part is answered by a chunk that's a third irrelevant.

My chunker (`chunker.py::split_documents`, calling the new `paragraph_split`)
splits on blank-line paragraph breaks and merges consecutive paragraphs until
the next one would push the chunk past 350 characters. 350 is roughly the
length of two or three of these short paragraphs together — big enough to hold
a title with its first paragraph, small enough that a distinct "good"/"bad"
split still separates out in longer posts. No overlap, because splits land on
paragraph boundaries already, never mid-sentence — there's no risk of cutting
a thought in half for overlap to patch over.

One thing I changed after testing: a strict 350-character cap on its own
turned a handful of short title paragraphs ("On the housing lottery") into
their own 22-character chunk, because the paragraph right after them was long
enough to blow the cap. I added a 80-character floor — a chunk won't close
until it's at least that long, even if that means going over 350 once — which
removed every fragment under 71 characters without merging unrelated posts
together.

Result: 115 chunks from 88 documents, averaging 242 characters (shortest 71,
longest 397) — versus 88 chunks averaging 317 characters under the starter's
fallback.

## Sample Chunks

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_210_exams.txt#0` — produced by: `chunker.py::split_documents`

```
CS 210 Data Structures — assessment

Two midterms and a final, all drawn from lecture material rather than the textbook. Midterms are curved, the final is not.

Do the labs even though they're only 10% — the exams reuse the lab problems.
```

**Chunk 3** — source: `course_phys_130.txt#1` — produced by: `chunker.py::split_documents`

```
The one piece of advice: the lab practical is worth 20% and almost nobody prepares for it.
```

**Chunk 4** — source: `dining_the_ridgeway_cafe_followup.txt#1` — produced by: `chunker.py::split_documents`

```
Also worth saying: seating is tight; about 40 seats for a building of 900. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#0` — produced by: `chunker.py::split_documents`

```
Morrow House — what it's actually like

Just finished a year in this building. Built 1954, partially renovated 2008. Rooms are singles and doubles, hall bathrooms.

The good: cheapest housing tier by about $900 a year, and the singles are real singles.

The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.
```

Each of these stands on its own: chunk 1 is a complete rule with its caveat,
chunk 3 is one full piece of advice, and chunk 5 is a title plus two full
topics — none is a sentence cut in half, and none is a title stranded alone.

## Sample Answer

**Question:**
"By what week can I still declare a pass/fail option?"

**Answer:**

You can declare the pass/fail option as late as week eight, after you've seen your midterm. This comes from `admin_pass_fail_option.txt`.

Sources retrieved: admin_add_drop_deadline.txt, admin_pass_fail_option.txt, admin_withdrawal_deadline.txt, course_biol_160.txt, course_cs_340.txt

**My relevance cutoff:**

I set `THRESHOLD = 0.6` in `config.py`. I ran the five questions from
`QUESTIONS` and the five from `OUT_OF_SCOPE` through `store.search` and
recorded the best (lowest) distance for each. Every in-corpus question came
back under 0.39; every out-of-corpus question came back over 0.82 — a clean
gap of more than 0.4 with nothing in between. 0.6 sits in the middle of that
gap rather than near either edge, so a slightly harder in-scope question or a
slightly closer out-of-scope one both still land on the correct side.

| Question | In corpus? | Best distance |
|---|---|---|
| What are the wait times at Kestrel Commons during lunch? | Yes | 0.173 |
| How much printing quota does each student get per semester? | Yes | 0.308 |
| By what week can I still declare a pass/fail option? | Yes | 0.358 |
| What happens on my transcript if I drop a course after week two? | Yes | 0.254 |
| Are CS 210 exams based on the textbook or on lecture material? | Yes | 0.387 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.874 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.840 |
| How do I write a for loop in Rust? | No | 0.891 |

## How I Used AI

**1.** `python app.py index` was silently leaving an empty index behind, and
`python app.py ask` then crashed with `TypeError: Number of requested results
0, cannot be negative, or zero.` I asked Copilot what happened. It re-ran
indexing directly (not through `ask`) and found the real error underneath:
`onnxruntime`'s CoreML execution provider was crashing on my Intel Mac while
embedding, which left `build_index` failing partway through and the Chroma
collection created-but-empty. It fixed this by pinning `_OnnxEmbedder` to
`preferred_providers=["CPUExecutionProvider"]` in `store.py`, skipping CoreML
entirely. I kept that fix as given, and also asked it to add a check in
`store.search()` that raises a clear error on an empty index — the original
`TypeError` gave no hint that the actual problem was upstream in indexing.

**2.** I asked Copilot to replace `campus_life`'s chunker with a paragraph-
aware strategy instead of the fixed 800-character window, since none of my
documents are long enough for that window to ever fire. Its first version
grouped paragraphs up to a 350-character cap, but testing it against
`admin_housing_lottery.txt` turned up a bad case it hadn't caught: a short
title paragraph ("On the housing lottery") followed by one long paragraph
that alone exceeds 350 characters, so the title flushed as its own
22-character chunk. I had it add an 80-character floor so a chunk can't close
until it reaches that length, even if that means going over 350 once. I then
checked the shortest chunk in the corpus myself (71 characters) to confirm
the fragment was actually gone rather than just hidden.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Week 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     week 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

Full run log: [`results/run_2026-09-20_1620_before.md`](results/run_2026-09-20_1620_before.md),
produced by `run_eval.py::main` (criteria 1, 2, 5) and `run_eval.py::check_out_of_scope`
(criterion 3). Criterion 4 isn't something `run_eval.py` measures — it's a
property of the chunks themselves, counted directly from `chunker.py::paragraph_split`'s
output, so it doesn't vary between runs either.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. No chunk shorter than 150 / longer than 600 chars, ≥4 of 5 sampled read as a complete thought | 0 chunks outside 150–600 | shortest chunk 71 chars | (same — deterministic) | (same — deterministic) | MISS |
| 5. Source attribution is correct, not just present | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

### Real output

**Criterion 1** — the chunk retrieval actually returns, containing the expected phrase.
`store.py::search` on "By what week can I still declare a pass/fail option?" returns
`admin_pass_fail_option.txt#0`:

```
On the pass/fail option

Any course outside your major can be taken pass/fail, and — the part nobody mentions — you can declare it as late as week eight, after you've seen your midterm. A pass needs a C- or better. Two per year, maximum eight across a degree.
```

**Criterion 2** — every answer names a source. Run 1, "How much printing quota does each
student get per semester?" (`generate.py`, via `run_eval.py::main`):

```
Each student gets $30 of printing per semester (admin_printing_quota.txt).
```

**Criterion 3** — the gate on out-of-corpus questions, from `run_eval.py::check_out_of_scope`:

| Out-of-scope question | Best distance | Gate |
|---|---|---|
| What is the capital of Mongolia? | 0.825 | refused |
| How do I change the oil in a diesel engine? | 0.934 | refused |
| Who won the 1994 World Cup? | 0.874 | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.840 | refused |
| How do I write a for loop in Rust? | 0.891 | refused |

**Criterion 4** — from the Week 1 "Chunking Strategy" section above
(`chunker.py::split_documents`): 115 chunks from 88 documents, averaging 242
characters, **shortest 71, longest 397**. The shortest chunk alone is below
this criterion's 150-character floor, so the target is missed on the length
half even though the sampled chunks (see "Sample Chunks" above) all read as
complete thoughts.

**Criterion 5** — the source named is the one that actually contains the answer, not
just any plausibly-related file. Run 1, "Are CS 210 exams based on the textbook or on
lecture material?" retrieved both `course_cs_210.txt` and `course_cs_210_exams.txt`,
and the answer cites both:

```
CS 210 exams are drawn from lecture material rather than the textbook (source: `course_cs_210.txt` and `course_cs_210_exams.txt`).
```

Checking the documents directly: both contain "all drawn from lecture material rather
than the textbook" verbatim, so citing either (or both) is correct — this was the
question I expected to be hardest to score cleanly, per `criteria.md`, and it held up.

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunks contain the answer (target: 4 of 5) | MET | All 3 runs in the log came back 5 of 5 — every question's retrieved chunks included the one containing the `expects` phrase, not just 4 — so the target holds with room to spare. |
| 2 | Every answer names a source (target: 5 of 5) | MET | All 3 runs came back 5 of 5; every one of the 15 answers in the run log names at least one source file, exactly what the target requires. |
| 3 | The relevance gate stops out-of-corpus questions (target: 4 of 5) | MET | The gate refused all 5 `OUT_OF_SCOPE` questions in the one deterministic pass, clearing the 4-of-5 target with none in the borderline zone (best distance 0.825, worst 0.934, both well above the 0.6 cutoff). |
| 4 | No chunk shorter than 150 / longer than 600 chars, ≥4 of 5 sampled read as a complete thought (target: 0 chunks outside 150–600) | MISSED | The Week 1 chunking stats show a shortest chunk of 71 characters, under the 150-character floor I set — the sampled chunks all read as complete thoughts, but the length half of the target is violated, so I'm calling the whole criterion missed rather than half-crediting it. |
| 5 | Source attribution is correct, not just present (target: 4 of 5) | MET | All 3 runs came back 5 of 5; for every question I checked the cited file(s) against the actual corpus text and the `expects` phrase was verbatim in each one, including the CS 210 case I expected to be hardest. |

## Diagnoses

**Criterion 4 — chunk length floor (MISSED)**

**Stage: chunking** (`chunker.py::paragraph_split`).

The 80-character floor I added in Week 1 only fires when there's a *next*
paragraph left to merge into the current chunk — it stops a chunk from
closing early while more content is still coming. It does nothing for the
*last* paragraph of a document, because there's nothing left to merge it
with; whatever that final paragraph's length is, it closes as its own chunk
regardless of the floor.

That's exactly the shape of all 23 chunks under 150 characters: every one is
the trailing `#1` chunk of a two-paragraph post, where the post's last
paragraph is a short tag-on line. `dining_pellew_dining_hall.txt#1` (71
characters) is the shortest example —

```
Hours are 7:00am to 8:00pm daily. Costs one meal swipe, or $11.75 cash.
```

— the hours/cost line at the end of a dining post, or (in the course
documents) a one-line "expect N hours a week" or "one piece of advice" tag.
This is one problem, not 23: the floor only guards against merging *forward*,
never against a short *final* paragraph with nothing after it.

No other criterion was missed, so there's no diagnosis to write for 1, 2, 3,
or 5 — but criterion 4's own target may have been set a little tight for this
corpus: several of these trailing lines (like the `dining_pellew_dining_hall.txt`
hours/cost line) are genuinely one complete, self-contained fact, just a short
one. A 100-character floor instead of 150 would still catch the 22-character
title fragments Week 1 was written to avoid, without flagging every short but
complete trailing sentence as a failure.

## The Improvement

**What I changed:** In `chunker.py::paragraph_split`, raised `MIN_CHUNK_SIZE`
from 80 to 150, and added a check to the final `flush()` call: if a
document's last paragraph closes under `MIN_CHUNK_SIZE`, it now merges
backward into the chunk before it instead of standing alone as its own short
chunk.

**Why I picked it:** This is the exact mechanism the Diagnoses section named
for the one miss (criterion 4) — the floor only guarded a chunk from closing
*early* while a following paragraph still had to be merged in; it never
applied to a document's *last* paragraph, which always flushed regardless of
length. Every one of the 23 too-short chunks was that trailing paragraph, so
fixing the floor to also catch that case addresses the whole miss with one
change, rather than patching each short chunk individually.

### Run Log — After

Full run log: [`results/run_2026-09-21_0058_after.md`](results/run_2026-09-21_0058_after.md),
same format as the "before" run — `run_eval.py::main` for criteria 1, 2, 5,
`run_eval.py::check_out_of_scope` for criterion 3. Corpus was re-chunked and
re-indexed (`python app.py index`) with the fixed `chunker.py::paragraph_split`
before this run.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. No chunk shorter than 150 / longer than 600 chars, ≥4 of 5 sampled read as a complete thought | 0 chunks outside 150–600 | 0 chunks outside 150–600 | (same — deterministic) | (same — deterministic) | MET |
| 5. Source attribution is correct, not just present | 4 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |

**Criterion 4, real output** — re-running `chunker.py::split_documents` after
the fix: 92 chunks from 88 documents, averaging 303 characters, shortest
**157**, longest **461** (down from 115 chunks, shortest 71). No chunk is
outside the 150–600 range any more, and the merged chunks (e.g.
`dining_kestrel_commons.txt#0`, now 369 characters, holding both the wait
times and the hours/cost paragraph in one piece) still read as complete
thoughts — merging two already-complete paragraphs together didn't cut
anything in half.

**Did it help?**

Yes, on the one criterion it targeted, and it didn't cost anything on the
other four. Criterion 4 goes from MISSED (shortest chunk 71 characters) to
MET (shortest chunk 157, longest 461, zero chunks outside 150–600).
Criteria 1, 2, 3, and 5 stay at 5 of 5 across all three after-runs, same as
before — retrieval still returns the right document for every question (now
as a single merged chunk instead of two), every answer still names a source,
the gate still refuses all 5 out-of-scope questions (distances 0.825-0.934,
still clear of the 0.6 cutoff), and every citation still points at a document
that actually contains the answer. The only visible side effect is cosmetic:
`Sources retrieved` lists shifted slightly (e.g. `dining_north_kitchen_followup.txt`
and `admin_declaring_a_major.txt` appear where different files did before),
because re-chunking changed the embeddings, but the top hit and the cited
source for every question stayed correct.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
