from sentence_transformers import CrossEncoder


compressor = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def compress_context(
    question: str,
    docs: list,
    top_sentences: int = 10
) -> str:

    candidates = []

    for doc in docs:

        text = doc.page_content.strip()

        if not text:
            continue

        sentences = [
            sentence.strip()
            for sentence in text.split(".")
            if sentence.strip()
        ]

        candidates.extend(sentences)

    if not candidates:
        return ""

    pairs = [
        (question, sentence)
        for sentence in candidates
    ]

    scores = compressor.predict(
        pairs
    )

    ranked = sorted(
        zip(candidates, scores),
        key=lambda x: x[1],
        reverse=True
    )

    selected_sentences = [
        sentence
        for sentence, _
        in ranked[:top_sentences]
    ]

    return ". ".join(
        selected_sentences
    )