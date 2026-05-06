from __future__ import annotations

import os
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from langgraph_rag.retriever import RetrievedDocument, retrieve_documents


load_dotenv()


class AgenticRagState(TypedDict, total=False):
    question: str
    rewritten_question: str
    answer: str
    documents: list[dict]
    retrieval_needed: bool
    documents_relevant: bool
    steps: list[str]
    iterations: int


RAG_KEYWORDS = {
    "langgraph",
    "graphe",
    "graph",
    "rag",
    "agent",
    "agentic",
    "retrieval",
    "studio",
    "streamlit",
    "noeud",
    "node",
    "arete",
    "edge",
}


def _append_step(state: AgenticRagState, step: str) -> list[str]:
    return [*state.get("steps", []), step]


def _doc_to_dict(doc: RetrievedDocument) -> dict:
    return {"title": doc.title, "content": doc.content, "score": round(doc.score, 3)}


def _get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0,
        api_key=api_key,
    )


def route_question(state: AgenticRagState) -> dict:
    question = state["question"]
    lowered = question.lower()
    retrieval_needed = any(keyword in lowered for keyword in RAG_KEYWORDS)
    if len(question.split()) > 5:
        retrieval_needed = True
    return {
        "retrieval_needed": retrieval_needed,
        "steps": _append_step(state, f"route_question: retrieval_needed={retrieval_needed}"),
    }


def decide_route(state: AgenticRagState) -> Literal["retrieve", "direct_answer"]:
    if state.get("retrieval_needed", True):
        return "retrieve"
    return "direct_answer"


def retrieve(state: AgenticRagState) -> dict:
    query = state.get("rewritten_question") or state["question"]
    documents = [_doc_to_dict(doc) for doc in retrieve_documents(query)]
    return {
        "documents": documents,
        "iterations": state.get("iterations", 0) + 1,
        "steps": _append_step(state, f"retrieve: {len(documents)} document(s)"),
    }


def grade_documents(state: AgenticRagState) -> dict:
    documents = state.get("documents", [])
    best_score = max((doc["score"] for doc in documents), default=0)
    relevant = best_score >= 0.12
    return {
        "documents_relevant": relevant,
        "steps": _append_step(state, f"grade_documents: relevant={relevant}, score={best_score}"),
    }


def decide_after_grading(state: AgenticRagState) -> Literal["generate_answer", "rewrite_question"]:
    if state.get("documents_relevant") or state.get("iterations", 0) >= 2:
        return "generate_answer"
    return "rewrite_question"


def rewrite_question(state: AgenticRagState) -> dict:
    rewritten = (
        f"{state['question']} LangGraph StateGraph noeuds aretes conditionnelles "
        "Agentic RAG Studio Streamlit"
    )
    return {
        "rewritten_question": rewritten,
        "steps": _append_step(state, "rewrite_question: question enrichie avec mots-cles"),
    }


def direct_answer(state: AgenticRagState) -> dict:
    return {
        "answer": (
            "Bonjour. Posez-moi une question sur LangGraph, Agentic RAG, "
            "LangGraph Studio ou l'interface Streamlit du projet."
        ),
        "documents": [],
        "steps": _append_step(state, "direct_answer: reponse sans recuperation"),
    }


def _extractive_answer(question: str, documents: list[dict]) -> str:
    if not documents:
        return (
            "Je n'ai pas trouve de passage pertinent dans la base de connaissances. "
            "Reformulez la question ou ajoutez des documents au projet."
        )

    bullets = []
    for index, doc in enumerate(documents, start=1):
        first_sentence = doc["content"].split(". ")[0].strip()
        bullets.append(f"{index}. {first_sentence}. Source: {doc['title']}")

    return "Voici une reponse fondee sur les documents recuperes :\n\n" + "\n".join(bullets)


def generate_answer(state: AgenticRagState) -> dict:
    documents = state.get("documents", [])
    context = "\n\n".join(
        f"Source: {doc['title']}\nScore: {doc['score']}\n{doc['content']}" for doc in documents
    )
    llm = _get_llm()

    if llm and documents:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "Tu es un assistant RAG. Reponds en francais, uniquement avec le "
                        "contexte fourni. Cite les titres des sources utilisees. Si le "
                        "contexte est insuffisant, dis-le clairement."
                    )
                ),
                HumanMessage(content=f"Question: {state['question']}\n\nContexte:\n{context}"),
            ]
        )
        answer = response.content
    else:
        answer = _extractive_answer(state["question"], documents)

    return {
        "answer": answer,
        "steps": _append_step(state, "generate_answer: reponse produite"),
    }


builder = StateGraph(AgenticRagState)
builder.add_node("route_question", route_question)
builder.add_node("retrieve", retrieve)
builder.add_node("grade_documents", grade_documents)
builder.add_node("rewrite_question", rewrite_question)
builder.add_node("generate_answer", generate_answer)
builder.add_node("direct_answer", direct_answer)

builder.add_edge(START, "route_question")
builder.add_conditional_edges("route_question", decide_route)
builder.add_edge("retrieve", "grade_documents")
builder.add_conditional_edges("grade_documents", decide_after_grading)
builder.add_edge("rewrite_question", "retrieve")
builder.add_edge("generate_answer", END)
builder.add_edge("direct_answer", END)

graph = builder.compile()


def ask(question: str) -> AgenticRagState:
    return graph.invoke({"question": question, "steps": [], "iterations": 0})


if __name__ == "__main__":
    result = ask("Comment fonctionne un Agentic RAG avec LangGraph ?")
    print(result["answer"])
    print(result["steps"])
