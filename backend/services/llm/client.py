from groq import AuthenticationError

try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None


def get_messages(chat_messages):
    return [
        {"role": getattr(m.role, "value", m.role), "content": m.content}
        for m in chat_messages
    ]


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
        response = ChatGroq(model="openai/gpt-oss-20b", temperature=0).invoke(messages)
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
        response = ChatGroq(model="openai/gpt-oss-20b", temperature=0).invoke(messages)
        return (response.content or "YES").strip().upper().startswith("YES")
    except Exception:
        return True


def llm_response(messages):
    if ChatGroq is None:
        return "I'm currently unable to generate a response."

    try:
        response = ChatGroq(model="openai/gpt-oss-20b", temperature=0).invoke(messages)
        return response.content or ""
    except AuthenticationError:
        return "I'm currently unable to generate a response due to an authentication error."
    except Exception:
        return "I'm currently unable to generate a response right now. Please try again shortly."
