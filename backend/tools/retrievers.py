import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder


# =====================================================
# CONFIG
# =====================================================

DENSE_WEIGHT = 0.5
BM25_WEIGHT = 0.5

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


# =====================================================
# BM25 INDEX SAVE
# =====================================================

def save_bm25_index(
    company_id,
    chunks
):

    Path("./data/bm25").mkdir(
        parents=True,
        exist_ok=True
    )

    index_path = (
        f"./data/bm25/{company_id}.pkl"
    )

    # Load existing docs
    existing_docs = []

    if Path(index_path).exists():

        with open(
            index_path,
            "rb"
        ) as f:

            existing = pickle.load(f)

            existing_docs = existing[
                "documents"
            ]

    # Merge old + new docs
    all_docs = (
        existing_docs +
        chunks
    )

    corpus = [
        doc.page_content
        for doc in all_docs
    ]

    tokenized = [
        text.lower().split()
        for text in corpus
    ]

    bm25 = BM25Okapi(tokenized)

    with open(
        index_path,
        "wb"
    ) as f:

        pickle.dump(
            {
                "bm25": bm25,
                "documents": all_docs
            },
            f
        )


# =====================================================
# LOAD INDEX
# =====================================================

def load_bm25_index(
    company_id
):

    path = (
        f"./data/bm25/{company_id}.pkl"
    )

    if not Path(path).exists():
        return None

    with open(
        path,
        "rb"
    ) as f:

        return pickle.load(f)


#Hybrid retrival
def weighted_hybrid_search(
    company_id,
    question,
    dense_docs,
    top_k=20
):

    data = load_bm25_index(
        company_id
    )

    if not data:
        return dense_docs[:top_k]

    bm25 = data["bm25"]

    all_docs = data["documents"]

    bm25_scores = bm25.get_scores(
        question.lower().split()
    )

    bm25_max = (
        max(bm25_scores)
        if len(bm25_scores) > 0
        else 1
    )

    score_map = {}

    # ------------------------
    # Dense Scores
    # ------------------------

    for rank, doc in enumerate(
        dense_docs
    ):

        dense_score = (
            1 -
            (
                rank /
                max(
                    len(dense_docs),
                    1
                )
            )
        )

        score_map[
            doc.page_content
        ] = {
            "doc": doc,
            "dense": dense_score,
            "bm25": 0.0
        }


    # BM25 Scores

    for idx, doc in enumerate(
        all_docs
    ):

        bm25_score = (
            bm25_scores[idx] /
            bm25_max
            if bm25_max > 0
            else 0
        )

        key = doc.page_content

        if key not in score_map:

            score_map[key] = {
                "doc": doc,
                "dense": 0.0,
                "bm25": bm25_score
            }

        else:

            score_map[key][
                "bm25"
            ] = bm25_score


    # Weighted Score


    scored_docs = []

    for item in score_map.values():

        final_score = (
            DENSE_WEIGHT *
            item["dense"]
            +
            BM25_WEIGHT *
            item["bm25"]
        )

        scored_docs.append(
            (
                item["doc"],
                final_score
            )
        )

    scored_docs.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return [
        doc
        for doc, _
        in scored_docs[:top_k]
    ]



# CROSS ENCODER RERANK

def rerank_documents(
    question,
    docs,
    top_k=4
):

    if not docs:
        return []

    pairs = [
        (
            question,
            doc.page_content
        )
        for doc in docs
    ]

    scores = reranker.predict(
        pairs
    )

    ranked = sorted(
        zip(docs, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        doc
        for doc, _
        in ranked[:top_k]
    ]