from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class DemoState(TypedDict):
    sujet: str
    score: int
    decision: str
    explication: str


def analyser_sujet(state: DemoState) -> dict:
    sujet = state["sujet"].strip()
    score = 0
    for mot in ("langgraph", "graphe", "agent", "rag", "streamlit"):
        if mot in sujet.lower():
            score += 1
    return {"score": score}


def choisir_branche(state: DemoState) -> Literal["expliquer_langgraph", "reponse_generale"]:
    if state["score"] >= 1:
        return "expliquer_langgraph"
    return "reponse_generale"


def expliquer_langgraph(state: DemoState) -> dict:
    return {
        "decision": "branche_langgraph",
        "explication": (
            "Le sujet semble lie a LangGraph. Le graphe a utilise un noeud "
            "d'analyse puis une arete conditionnelle pour choisir cette branche."
        ),
    }


def reponse_generale(state: DemoState) -> dict:
    return {
        "decision": "branche_generale",
        "explication": (
            "Le sujet ne contient pas de mot-cle LangGraph. Le graphe termine "
            "donc avec une reponse generale."
        ),
    }


builder = StateGraph(DemoState)
builder.add_node("analyser_sujet", analyser_sujet)
builder.add_node("expliquer_langgraph", expliquer_langgraph)
builder.add_node("reponse_generale", reponse_generale)
builder.add_edge(START, "analyser_sujet")
builder.add_conditional_edges("analyser_sujet", choisir_branche)
builder.add_edge("expliquer_langgraph", END)
builder.add_edge("reponse_generale", END)

graph = builder.compile()


if __name__ == "__main__":
    resultat = graph.invoke(
        {
            "sujet": "Construire un agent RAG avec LangGraph",
            "score": 0,
            "decision": "",
            "explication": "",
        }
    )
    print(resultat)
