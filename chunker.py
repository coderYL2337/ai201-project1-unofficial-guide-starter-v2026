"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in week 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?
    """
    return paragraph_split(documents)


def paragraph_split(
    documents: list[Document],
    chunk_size: int | None = None,
) -> list[Chunk]:
    """
    campus_life's own chunker: group paragraphs, don't slice characters.

    Every document here is short enough (178-549 characters) that
    `fallback_split`'s 800-character window never fires — one post already
    comes out as one chunk. The problem `fallback_split` doesn't catch is that
    several posts hold more than one thought as separate paragraphs (a title,
    a description, then a "the good" / "the bad" pair) with nothing to force
    them apart.

    This splits on blank-line paragraph breaks and merges consecutive
    paragraphs until adding the next one would push a chunk past
    `chunk_size`. That keeps a lone heading from becoming its own
    near-empty chunk (the failure mode fixed-size slicing hits on
    `advice_threads`), while still letting a long, multi-topic post separate
    into pieces that each answer one question. No character overlap is
    needed — every split falls on a paragraph boundary, never mid-sentence.

    One extra rule earned its way in after testing on this corpus: several
    posts open with a short title paragraph ("On the housing lottery")
    immediately followed by one long paragraph that alone exceeds
    `chunk_size`. Without a floor, the title would flush on its own — a
    22-character chunk nobody could answer a question from. `MIN_CHUNK_SIZE`
    forces a chunk to reach a minimum length before it's allowed to close,
    even if that means going over `chunk_size` once.
    """
    MIN_CHUNK_SIZE = 80

    chunk_size = chunk_size or config.CHUNK_SIZE
    chunks: list[Chunk] = []

    for doc in documents:
        paragraphs = [p.strip() for p in doc.text.split("\n\n") if p.strip()]
        if not paragraphs:
            continue

        index = 0
        current: list[str] = []
        current_len = 0

        def flush():
            nonlocal index
            if not current:
                return
            chunks.append(
                Chunk(
                    text="\n\n".join(current),
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )
            index += 1
            current.clear()

        for para in paragraphs:
            over_size = current and current_len + len(para) + 2 > chunk_size
            if over_size and current_len >= MIN_CHUNK_SIZE:
                flush()
                current_len = 0
            current.append(para)
            current_len += len(para) + 2
        flush()

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
