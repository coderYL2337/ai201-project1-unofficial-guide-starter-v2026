# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in week 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next week costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** I picked 4 of 5, not 5 of 5, because one of my questions
("Are CS 210 exams based on the textbook or on lecture material?") sits among
five other course codes (cs_210, cs_340, econ_101, engl_205, hist_118, ...)
that each have near-identical `_exams` / `_workload` files. If embedding
similarity blurs across those near-duplicate course documents, that's the one
I'd expect to misfire — the other four each use vocabulary specific enough to
a single document ("Kestrel Commons", "printing quota", "pass/fail", "add/drop")
that I'd be surprised to see them miss.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** All five, not four, because naming a source isn't a hard
retrieval problem — it's `store.py` attaching each retrieved chunk's
`metadata.source` to the prompt, and `generate.py` printing it back out. There
is no borderline case where retrieval was ambiguous but the citation should
fairly be dropped; a missing source means the wiring broke, not that the
question was hard, so I'm not giving it any slack.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:** When I ran my five `QUESTIONS` and the five `OUT_OF_SCOPE`
questions through `store.search`, the best distance for every in-scope question
fell between 0.173 and 0.387, and every out-of-scope question fell between
0.825 and 0.934 — a clean gap with nothing in between. My threshold of 0.6 sits
in the middle of that gap, not near either edge, so I expect 5 of 5 most runs.
I'm still writing 4 of 5 rather than 5 of 5 because I only measured this gap on
five questions per side, and I'd rather leave room for a sixth question that
lands closer to the boundary than declare a guarantee I haven't tested.

---

## 4. Something about your chunks

No chunk is shorter than 150 characters or longer than 600 characters, and at
least 4 of 5 chunks sampled with `python app.py chunks` read as a complete
thought, with no sentence cut in half at either end.

**Why this target:** `campus_life` is made of short posts and admin notices,
not long guides — the baseline chunker (`fallback_split` at 800 characters)
already produces one chunk per document (88 documents, 88 chunks), with
lengths ranging from 178 to 549 characters in my own run. 150–600 gives a
little headroom around that observed range rather than a number I invented.
I'm allowing 1 of 5 to fail rather than requiring all 5, because a couple of
the longer thread-style documents (like `thread_group_project.txt`) run
several short paragraphs together, and I'd rather find out honestly whether my
Milestone 3 strategy handles that than pick a target I'm certain to hit.

---

## 5. Your choice

Source attribution is correct, not just present: for at least 4 of my 5 test
questions, the source(s) named in the answer include the specific document
that actually contains the `expects` phrase — not merely any plausibly-related
document.

**Why this target:** Criterion 2 only checks that a source is named at all,
which a system could satisfy by citing the wrong document every time and still
pass. That's worse than refusing to answer, because a citation makes a wrong
answer look trustworthy. I picked 4 of 5 instead of 5 of 5 because my dining
question ("wait times at Kestrel Commons") has both a primary write-up
(`dining_kestrel_commons.txt`) and a `_followup` file covering the same place —
the correct fact could legitimately live in either, so I expect that one to be
the hardest to score cleanly.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     WEEK 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in week 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
