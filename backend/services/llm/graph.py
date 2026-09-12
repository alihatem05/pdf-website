from typing import TypedDict
from uuid import UUID
from langgraph.graph import END, START, StateGraph
from backend.config import LLM_TOP_K
from backend.services.llm.client import classify_rag_need, contextualize_question, llm_response
from backend.services.llm.prompt import build_general_messages, build_messages
from backend.services.llm.retrieval import RetrievedChunk, retrieve


class InputState(TypedDict):
    chat_id: UUID
    question: str
    history: list[dict[str, str]]
    summary: str | None


class OverallState(InputState, total=False):
    contextualized_question: str
    needs_rag: bool
    chunks: list[RetrievedChunk]
    messages: list[dict[str, str]]


class OutputState(TypedDict):
    answer: str


def contextualize(state: OverallState):
    return {"contextualized_question": contextualize_question(
        state.get("history", []), state["question"], state.get("summary")
    )}


def classify_rag(state: OverallState):
    question = state.get("contextualized_question", state["question"])
    return {"needs_rag": classify_rag_need(question)}


def route_question(state: OverallState):
    return "retrieve" if state.get("needs_rag", True) else "answer_directly"


def retrieve_context(state: OverallState):
    search_question = state.get("contextualized_question", state["question"])
    chunks = retrieve(state["chat_id"], search_question, top_k=LLM_TOP_K)
    return {
        "chunks": chunks,
        "messages": build_messages(chunks, state.get("history", []), state["question"]),
    }


def answer_directly(state: OverallState):
    return {
        "messages": build_general_messages(
            state.get("history", []), state["question"]
        )
    }


def generate_answer(state: OverallState):
    messages = state["messages"]
    return {"answer": llm_response(messages)}


def build_rag_graph():
    workflow = StateGraph(
        OverallState,
        input_schema=InputState,
        output_schema=OutputState,
    )
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("answer_directly", answer_directly)
    workflow.add_node("generate", generate_answer)
    workflow.add_node("contextualize", contextualize)
    workflow.add_node("classify_rag", classify_rag)
    workflow.add_edge(START, "contextualize")
    workflow.add_edge("contextualize", "classify_rag")
    workflow.add_conditional_edges(
        "classify_rag",
        route_question,
        {"retrieve": "retrieve", "answer_directly": "answer_directly"},
    )
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("answer_directly", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()


rag_graph = build_rag_graph()