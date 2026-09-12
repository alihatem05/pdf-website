from groq import AuthenticationError
from langchain_groq import ChatGroq

def get_messages(chat_messages):
    return [{"role": m.role, "content": m.content} for m in chat_messages]

def llm_response(messages):
    model = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
    )

    try:
        response = model.invoke(messages)
        return response.content
    
    except AuthenticationError as exc:
        print("SKIPPED: GROQ_API_KEY was rejected by the Groq service.")
        print(f"Details: {exc}")
        return



