from __future__ import annotations

import streamlit as st

from langgraph_rag.agent import ask


st.set_page_config(page_title="Chatbot Agentic RAG", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --surface: #ffffff;
            --surface-soft: #f6f8fb;
            --line: #d9e1ea;
            --text: #18212f;
            --muted: #64748b;
            --accent: #0f766e;
            --accent-soft: #e6f4f1;
            --warn-soft: #fff7ed;
        }

        .stApp {
            background:
                linear-gradient(180deg, #f7fafc 0%, #eef4f8 46%, #f8fafc 100%);
            color: var(--text);
        }

        [data-testid="stHeader"] {
            background: rgba(247, 250, 252, 0.86);
            backdrop-filter: blur(12px);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 7rem;
        }

        .app-title {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            border-bottom: 1px solid var(--line);
            padding-bottom: 1rem;
            margin-bottom: 1.25rem;
        }

        .app-title h1 {
            font-size: 2rem;
            line-height: 1.12;
            margin: 0;
            letter-spacing: 0;
        }

        .app-title p {
            color: var(--muted);
            margin: 0.35rem 0 0;
            font-size: 0.98rem;
        }

        .status-pill {
            border: 1px solid #99d5cd;
            background: var(--accent-soft);
            color: #115e59;
            border-radius: 999px;
            padding: 0.42rem 0.72rem;
            font-size: 0.86rem;
            white-space: nowrap;
        }

        [data-testid="stSidebar"] {
            background: #fbfdff;
            border-right: 1px solid var(--line);
        }

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            letter-spacing: 0;
        }

        .metric-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0 0 1.2rem;
        }

        .metric-box {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.8rem;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.78rem;
            margin-bottom: 0.18rem;
        }

        .metric-value {
            color: var(--text);
            font-size: 1.05rem;
            font-weight: 700;
        }

        .empty-state {
            border: 1px dashed #a8b6c7;
            background: rgba(255, 255, 255, 0.72);
            border-radius: 8px;
            padding: 1.2rem;
            color: var(--muted);
            margin-top: 0.5rem;
        }

        .source-item {
            border-left: 3px solid var(--accent);
            background: var(--surface);
            padding: 0.75rem 0.85rem;
            margin-bottom: 0.7rem;
            border-radius: 0 8px 8px 0;
            border-top: 1px solid var(--line);
            border-right: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
        }

        .source-title {
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .source-score {
            color: var(--muted);
            font-size: 0.84rem;
            margin-bottom: 0.45rem;
        }

        .step-row {
            display: flex;
            gap: 0.65rem;
            align-items: flex-start;
            padding: 0.46rem 0;
            border-bottom: 1px solid #edf2f7;
        }

        .step-index {
            background: #0f172a;
            color: white;
            width: 1.55rem;
            height: 1.55rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            font-size: 0.78rem;
            flex: 0 0 auto;
            margin-top: 0.05rem;
        }

        .step-text {
            color: var(--text);
            font-size: 0.92rem;
        }

        div[data-testid="stChatMessage"] {
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.82);
            padding: 0.9rem 1rem;
            margin-bottom: 0.85rem;
        }

        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #f8fbff;
        }

        .stChatInput {
            border-top: 1px solid var(--line);
            background: rgba(248, 250, 252, 0.92);
            backdrop-filter: blur(10px);
        }

        .stButton > button {
            width: 100%;
            border-radius: 8px;
            border: 1px solid var(--line);
            background: var(--surface);
            color: var(--text);
            min-height: 2.5rem;
        }

        .stButton > button:hover {
            border-color: #0f766e;
            color: #0f766e;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 1rem;
            }

            .app-title {
                align-items: flex-start;
                flex-direction: column;
            }

            .metric-strip {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_chat(question: str) -> dict:
    result = ask(question)
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "steps": result.get("steps", []),
            "documents": result.get("documents", []),
        }
    )
    st.session_state.last_result = result
    return result


def render_steps(steps: list[str]) -> None:
    if not steps:
        st.caption("Aucune etape disponible.")
        return

    for index, step in enumerate(steps, start=1):
        st.markdown(
            f"""
            <div class="step-row">
                <span class="step-index">{index}</span>
                <span class="step-text">{step}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sources(documents: list[dict]) -> None:
    if not documents:
        st.caption("Aucune source recuperee.")
        return

    for doc in documents:
        st.markdown(
            f"""
            <div class="source-item">
                <div class="source-title">{doc["title"]}</div>
                <div class="source-score">Score de pertinence: {doc["score"]}</div>
                <div>{doc["content"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("steps") is not None:
            with st.expander("Trace LangGraph", expanded=False):
                render_steps(message.get("steps", []))
            with st.expander("Sources", expanded=False):
                render_sources(message.get("documents", []))


inject_styles()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_result" not in st.session_state:
    st.session_state.last_result = {}

last_result = st.session_state.last_result
last_docs = last_result.get("documents", [])
last_steps = last_result.get("steps", [])

with st.sidebar:
    st.subheader("Session")
    st.markdown(
        f"""
        <div class="metric-strip">
            <div class="metric-box">
                <div class="metric-label">Messages</div>
                <div class="metric-value">{len(st.session_state.messages)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Sources</div>
                <div class="metric-value">{len(last_docs)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Etapes</div>
                <div class="metric-value">{len(last_steps)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_result = {}
        st.rerun()

    st.divider()
    st.subheader("Questions rapides")

    sample_questions = [
        "Comment fonctionne un Agentic RAG avec LangGraph ?",
        "A quoi sert LangGraph Studio ?",
        "Comment Streamlit utilise le graphe du chatbot ?",
    ]

    for sample in sample_questions:
        if st.button(sample, key=f"sample-{sample}", use_container_width=True):
            with st.spinner("Execution du graphe LangGraph..."):
                run_chat(sample)
            st.rerun()

    st.divider()
    st.subheader("Derniere trace")
    render_steps(last_steps)

st.markdown(
    """
    <div class="app-title">
        <div>
            <h1>Chatbot Agentic RAG avec LangGraph</h1>
            <p>Questions, recuperation, verification et generation dans un graphe inspectable.</p>
        </div>
        <div class="status-pill">Mode local pret</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown(
        """
        <div class="empty-state">
            Lancez une question depuis le champ de chat ou choisissez une question rapide dans le panneau lateral.
        </div>
        """,
        unsafe_allow_html=True,
    )

for chat_message in st.session_state.messages:
    render_message(chat_message)

question = st.chat_input("Posez une question sur LangGraph, RAG, Studio ou Streamlit")

if question:
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Execution du graphe LangGraph..."):
            result = run_chat(question)
        st.markdown(result["answer"])

        with st.expander("Trace LangGraph", expanded=True):
            render_steps(result.get("steps", []))
        with st.expander("Sources", expanded=True):
            render_sources(result.get("documents", []))

    st.rerun()
