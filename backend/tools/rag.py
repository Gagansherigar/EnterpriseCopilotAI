import os

from pathlib import Path
from backend.tools.context_compression import (
    compress_context
)
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

from langchain_community.embeddings import (
    FastEmbedEmbeddings
)

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)

from langchain_experimental.text_splitter import (
    SemanticChunker
)

from backend.state import AgentState

from backend.tools.retrievers import (
    save_bm25_index,
    weighted_hybrid_search,
    rerank_documents
)


# =====================================================
# LLM
# =====================================================

llm = ChatGroq(
    model=os.getenv(
        "GROQ_MODEL",
        "llama-3.1-8b-instant"
    )
)


# =====================================================
# EMBEDDINGS
# =====================================================

embeddings = FastEmbedEmbeddings()


# =====================================================
# VECTOR DB
# =====================================================

def get_vectordb(
    company_id: str
):

    return Chroma(
        collection_name=f"docs_{company_id}",
        embedding_function=embeddings,
        persist_directory="./data/chroma"
    )


# =====================================================
# DOCUMENT INGESTION
# =====================================================

def ingest_document(
    file_path: str,
    company_id: str
):

    try:

        extension = (
            Path(file_path)
            .suffix
            .lower()
        )

        # -------------------------
        # Loader Selection
        # -------------------------

        if extension == ".pdf":

            loader = PyPDFLoader(
                file_path
            )

        elif extension in [
            ".txt",
            ".md"
        ]:

            loader = TextLoader(
                file_path,
                encoding="utf-8"
            )

        else:

            return {
                "status": "error",
                "message": (
                    f"Unsupported file type: "
                    f"{extension}"
                )
            }

        docs = loader.load()

        # ==================================================
        # SEMANTIC CHUNKING
        # ==================================================

        splitter = SemanticChunker(
            embeddings,
            breakpoint_threshold_type="standard_deviation",
            breakpoint_threshold_amount=1.0
        )

        chunks = splitter.split_documents(
            docs
        )

        # ==================================================
        # REMOVE TINY CHUNKS
        # ==================================================

        chunks = [
            chunk
            for chunk in chunks
            if len(
                chunk.page_content.strip()
            ) > 100
        ]

        # ==================================================
        # CHROMA INDEX
        # ==================================================

        vectordb = get_vectordb(
            company_id
        )

        vectordb.add_documents(
            chunks
        )

        # ==================================================
        # BM25 INDEX
        # ==================================================

        save_bm25_index(
            company_id,
            chunks
        )

        return {
            "status": "success",
            "chunks": len(chunks)
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# HYBRID RETRIEVAL


def hybrid_retrieve(
    question,
    company_id,
    vectordb
):

    dense_retriever = (
        vectordb.as_retriever(
            search_kwargs={"k": 10}
        )
    )

    dense_docs = (
        dense_retriever.invoke(
            question
        )
    )

    hybrid_docs = (
        weighted_hybrid_search(
            company_id,
            question,
            dense_docs,
            top_k=20
        )
    )

    final_docs = (
        rerank_documents(
            question,
            hybrid_docs,
            top_k=4
        )
    )

    return final_docs



# RAG NODE

async def rag_node(
    state: AgentState
):

    try:

        question = state["question"]

        company_id = state.get(
            "company_id",
            "default"
        )

        vectordb = get_vectordb(
            company_id
        )

        docs = hybrid_retrieve(
            question,
            company_id,
            vectordb
        )

        if not docs:

            state["rag_result"] = {
                "success": False,
                "error":
                "No relevant documents found"
            }

            return state

        context = compress_context(
            question=question,
            docs=docs,
            top_sentences=10
        )
        prompt = f"""
You are an enterprise AI assistant.

Answer ONLY from the provided context.

Question:
{question}

Context:
{context}

Rules:
- Do not hallucinate
- If answer is not found, say:
  "Not found in knowledge base"
- Be concise
"""

        response = await llm.ainvoke(
            prompt
        )

        answer = (
            response.content.strip()
        )

        citations = []

        for doc in docs:

            citations.append(
                {
                    "source":
                    doc.metadata.get(
                        "source",
                        "unknown"
                    ),

                    "page":
                    doc.metadata.get(
                        "page",
                        "unknown"
                    )
                }
            )

        state["rag_result"] = {
            "success": True,
            "answer": answer,
            "citations": citations
        }

        return state

    except Exception as e:

        state["rag_result"] = {
            "success": False,
            "error": str(e)
        }

        state["error"] = str(e)

        return state