import os
import tempfile
from typing import List
import nest_asyncio
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.sitemap import SitemapLoader
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langsmith import traceable, trace

# --- Config ---
MODEL_NAME = "models/gemini-2.5-flash"   # Gemini LLM for chat
MODEL_PROVIDER = "google"
APP_VERSION = 1.0
RAG_SYSTEM_PROMPT = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the latest question in the conversation. 
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise.
"""

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", os.getenv("GEMINI_API_KEY", "")))


# --- Retriever setup ---
def get_vector_db_retriever():
    persist_path = os.path.join(tempfile.gettempdir(), "union.parquet")

    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "Missing API key: set GOOGLE_API_KEY or GEMINI_API_KEY to use GoogleGenerativeAIEmbeddings."
        )

    # Use Google embeddings
    embd = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    # If vector store already exists
    if os.path.exists(persist_path):
        vectorstore = SKLearnVectorStore(
            embedding=embd,
            persist_path=persist_path,
            serializer="parquet"
        )
        return vectorstore.as_retriever(lambda_mult=0)

    # Otherwise, build from sitemap
    ls_docs_sitemap_loader = SitemapLoader(
        web_path="https://docs.smith.langchain.com/sitemap.xml",
        continue_on_failure=True
    )
    ls_docs = ls_docs_sitemap_loader.load()

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(ls_docs)

    vectorstore = SKLearnVectorStore.from_documents(
        documents=doc_splits,
        embedding=embd,
        persist_path=persist_path,
        serializer="parquet"
    )
    vectorstore.persist()
    return vectorstore.as_retriever(lambda_mult=0)


nest_asyncio.apply()
retriever = get_vector_db_retriever()


"""
retrieve_documents
- Returns documents fetched from a vectorstore based on the user's question
"""
@traceable(run_type="chain")
def retrieve_documents(question: str):
    return retriever.invoke(question)


"""
call_gemini
- Returns the chat completion output from Gemini
"""
@traceable(
    run_type="llm",
    metadata={
        "ls_provider": MODEL_PROVIDER,
        "ls_model_name": MODEL_NAME
    }
)
def call_gemini(messages: List[dict], model: str = MODEL_NAME, temperature: float = 0.0):
    prompt = "\n\n".join([m["content"] for m in messages])
    gmodel = genai.GenerativeModel(model)
    resp = gmodel.generate_content(prompt, generation_config={"temperature": temperature})

    # Adapter: mimic OpenAI response structure
    class Msg:
        def __init__(self, content): self.content = content

    class Choice:
        def __init__(self, content): self.message = Msg(content)

    class Resp:
        def __init__(self, content): self.choices = [Choice(content)]

    return Resp(getattr(resp, "text", ""))


"""
generate_response
- Calls `call_gemini` to generate a model response after formatting inputs
"""
@traceable(run_type="chain")
def generate_response(question: str, documents):
    formatted_docs = "\n\n".join(doc.page_content for doc in documents)
    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": f"Context: {formatted_docs} \n\n Question: {question}"}
    ]
    return call_gemini(messages)


"""
langsmith_rag
- Retrieves documents and generates response
"""
@traceable(run_type="chain")
def langsmith_rag(question: str):
    documents = retrieve_documents(question)
    response = generate_response(question, documents)
    return response.choices[0].message.content
