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
