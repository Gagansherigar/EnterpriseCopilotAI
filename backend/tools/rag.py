from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_groq import ChatGroq


llm = ChatGroq(model="llama-3.1-8b-instant")

# ✅ Embeddings
embeddings = FastEmbedEmbeddings()


# ✅ Get vector DB per company (multi-tenant)
def get_vectordb(company_id: str):
    return Chroma(
        collection_name=f"docs_{company_id}",
        embedding_function=embeddings,
        persist_directory="/data"
    )


# ✅ Ingest PDF (company-specific)
def ingest_pdf(file_path: str, company_id: str):
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(docs)

        vectordb = get_vectordb(company_id)
        vectordb.add_documents(chunks)


        return {"status": "success", "chunks": len(chunks)}

    except Exception as e:
        return {"error": str(e)}


# ✅ RAG node for agent graph
async def rag_node(state):
    try:
        question = state.get("question", "")
        company_id = state.get("company_id", "default")

        vectordb = get_vectordb(company_id)
        retriever = vectordb.as_retriever(search_kwargs={"k": 4})

        docs = retriever.invoke(question)

        # ✅ If nothing found → escalate
        if not docs:
            state["route"] = "escalate"
            state["answer"] = "I don't have that information. Connecting you to human support."
            return state

        context = "\n".join([d.page_content for d in docs])

        # ✅ STRICT PROMPT (very important)
        prompt = f"""
        You are an internal company assistant.

        Use previous conversation if relevant.

        Chat History:
        {state.get("history", "")}

        Context:
        {context}

        Question:
        {question}

        Rules:
        - Answer ONLY from context
        - If not found → say "Not found in knowledge base"
        """

        response = await llm.ainvoke(prompt)

        answer = response.content.strip()

        # ✅ Extra safety (guardrail)
        if "I don't have that information" in answer:
            state["route"] = "escalate"

        state["answer"] = answer
        return state

    except Exception as e:
        state["route"] = "escalate"
        state["answer"] = f"RAG Error: {str(e)}"
        return state