import json
import logging

from groq import AuthenticationError
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

def get_messages(chat_messages):
    return [
        {"role": getattr(m.role, "value", m.role), "content": m.content}
        for m in chat_messages
    ]

def create_client(max_tokens=None):
    return ChatGroq(model="openai/gpt-oss-20b", temperature=0, max_tokens=max_tokens)


def contextualize_question(history, question, summary=None):
    if not history and not summary:
        return question

    system_content = (
        "Rewrite the user's latest question as a standalone question using the conversation history. "
        "Resolve references such as 'it', 'that', or 'page 2'. Do not answer the question. "
        "Return only the rewritten question."
    )
    if summary:
        system_content += f"\n\nSummary of earlier conversation:\n{summary}"

    messages = [
        {"role": "system", "content": system_content},
        *[
            {"role": str(message["role"]), "content": message["content"]}
            for message in history
        ],
        {"role": "user", "content": question},
    ]

    try:
        if ChatGroq is None:
            return question
        ai = create_client()
        response = ai.invoke(messages)
        return (response.content or question).strip()
    except AuthenticationError:
        return question


def classify_rag_need(question):
    if ChatGroq is None:
        return True

    messages = [
        {
            "role": "system",
            "content": (
                "Decide whether the user's standalone question requires information "
                "from the uploaded PDF. Reply with exactly YES or NO. Reply YES for "
                "questions about the document, its contents, pages, figures, or facts "
                "that must be verified in it. Reply NO for greetings, casual conversation, "
                "writing help, or general knowledge unrelated to the document."
            ),
        },
        {"role": "user", "content": question},
    ]

    try:
        ai = create_client()
        response = ai.invoke(messages)
        return (response.content or "YES").strip().upper().startswith("YES")
    except Exception:
        return True


def plan_retrieval(question, documents, max_chunks_per_document):
    document_ids = [str(document["id"]) for document in documents]
    fallback = {document_id: max_chunks_per_document for document_id in document_ids}
    if not document_ids or max_chunks_per_document < 1 or ChatGroq is None:
        return fallback

    messages = [
        {
            "role": "system",
            "content": (
                "Plan retrieval for a question about uploaded PDFs. Choose how many "
                "chunks to retrieve from each PDF, between 1 and the supplied maximum. "
                "Use more chunks for detailed comparisons and fewer for narrow questions. "
                "Include every PDF so answers can compare them individually. Return only "
                'a JSON object mapping each exact document ID to an integer, like {"id": 3}.'
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question": question,
                    "maximum_chunks_per_document": max_chunks_per_document,
                    "documents": documents,
                }
            ),
        },
    ]

    try:
        response = create_client().invoke(messages)
        content = (response.content or "").strip()
        if content.startswith("```"):
            content = content.removeprefix("```json").removeprefix("```")
            content = content.removesuffix("```").strip()
        requested = json.loads(content)
        if not isinstance(requested, dict):
            return fallback
        budgets = {}
        for document_id in document_ids:
            value = requested.get(document_id, max_chunks_per_document)
            if isinstance(value, bool) or not isinstance(value, int):
                value = max_chunks_per_document
            budgets[document_id] = max(1, min(value, max_chunks_per_document))
        return budgets
    except Exception:
        return fallback


def llm_response(messages):
    if ChatGroq is None:
        return "I'm currently unable to generate a response."

    try:
        ai = create_client(max_tokens=4096)
        response = ai.invoke(messages)
        content = response.content
        if isinstance(content, str) and content.strip():
            return content.strip()

        logger.warning(
            "LLM returned an empty answer; response metadata: %s",
            getattr(response, "response_metadata", {}),
        )
        return "I couldn't generate an answer this time. Please try again."
    except AuthenticationError:
        return "I'm currently unable to generate a response due to an authentication error."
    except Exception:
        logger.exception("LLM answer generation failed")
        return "I'm currently unable to generate a response right now. Please try again shortly."
