from typing import Any, TypedDict
from uuid import UUID
from langgraph.graph import END, START, StateGraph
from backend.config import LLM_TOP_K
from backend.services.client import contextualize_question, llm_response
from backend.services.llm.prompt import build_messages
from backend.services.llm.retrieval import RetrievedChunk, retrieve


class RagState(TypedDict, total=False):
    chat_id: UUID
    question: str
    contextualized_question: str
    history: list[dict[str, str]]
    has_document: bool
    chunks: list[RetrievedChunk]
    messages: list[dict[str, str]]
    answer: str


def contextualize(state: RagState):
    return {"contextualized_question": contextualize_question(
        state.get("history", []), state["question"]
    )}


def route_question(state: RagState):
    return "retrieve" if state.get("has_document", False) else "generate"


def retrieve_context(state: RagState):
    search_question = state.get("contextualized_question", state["question"])
    chunks = retrieve(state["chat_id"], search_question, top_k=LLM_TOP_K)
    return {
        "chunks": chunks,
        "messages": build_messages(chunks, state.get("history", []), state["question"]),
    }


def generate_answer(state: RagState):
    messages = state.get("messages") or build_messages(
        [], state.get("history", []), state["question"]
    )
    return {"answer": llm_response(messages)}


def prepare_messages(state: RagState):
    contextualized_question = contextualize_question(
        state.get("history", []), state["question"]
    )
    chunks = []
    if state.get("has_document", False):
        chunks = retrieve(state["chat_id"], contextualized_question, top_k=LLM_TOP_K)
    return build_messages(chunks, state.get("history", []), state["question"])


def build_rag_graph():
    workflow = StateGraph(RagState)
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("contextualize", contextualize)
    workflow.add_edge(START, "contextualize")
    workflow.add_conditional_edges(
        "contextualize",
        route_question,
        {"retrieve": "retrieve", "generate": "generate"},
    )
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()


rag_graph = build_rag_graph()