# src/analytics/rag_engine.py
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment")

# Vector store path
VECTOR_STORE_PATH = Path("data/processed/vector_store")

# System prompt + examples
SYSTEM_PROMPT = """
You are an AI FinOps assistant. Answer questions using ONLY the provided context.
Always cite sources.
<context>
{context}
</context>
"""
FEW_SHOT_EXAMPLES = """
### Examples ###
Question: What was my monthly cost by service for May 2023?
Answer: Use `kpis.monthly_cost_by_service(month='2023-05')`.
Question: Which resources are idle and how much can I save?
Answer: Use `recommendations.find_idle_resources(month)`.
Question: What is tagging and why is it important?
Answer: Tagging categorizes resources by team/project/environment for cost visibility.
"""
PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=SYSTEM_PROMPT + FEW_SHOT_EXAMPLES + "\nQuestion: {question}\nAnswer:"
)

def get_answer(question: str):
    """Retrieve docs from vector store and generate answer using LLM"""
    try:
        vector_db = Chroma(
            embedding_function=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY),
            persist_directory=str(VECTOR_STORE_PATH)
        )
        retriever = vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 10})

        retrieved_docs = retriever.invoke(question)
        if not retrieved_docs:
            return "No relevant information found.", []

        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        parser = StrOutputParser()
        llm = ChatOpenAI(model_name="gpt-4", temperature=0.0, openai_api_key=OPENAI_API_KEY)
        chain = PROMPT | llm | parser

        try:
            answer = chain.invoke({"context": context_text, "question": question})
        except Exception as e:
            logger.exception("LLM failed")
            return "Error generating answer.", retrieved_docs

        return answer, retrieved_docs

    except Exception as e:
        logger.exception("RAG pipeline failed")
        return "Internal RAG error.", []
