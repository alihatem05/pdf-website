from langchain_groq import ChatGroq
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from celery_app import celery_app
from config import CELERY_DATABASE_URL, SUMMARY_LIMIT
from models.chat import Chat
from models.chat_message import ChatMessage
from services.llm.client import create_client

sync_engine = create_engine(CELERY_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)
llm_client = create_client()


def build_summary_prompt(old_summary, new_messages):
    conversation = "\n".join(f"{message.role.value}: {message.content}" for message in new_messages)
    if old_summary:
        return (
            f"Here is a summary of the conversation so far:\n{old_summary}\n\n"
            f"Here are new messages to fold into that summary:\n{conversation}\n\n"
            "Produce an updated, concise summary that captures the key points of the "
            "entire conversation, including what's new."
        )
    return (
        "Summarize the key points of this conversation concisely, in a way that "
        "preserves context needed to continue answering related questions:\n\n"
        f"{conversation}"
    )


@celery_app.task
def update_chat_summary(chat_id: str):
    with SyncSession() as session:
        chat = session.get(Chat, chat_id)
        if chat is None:
            return

        new_messages = session.scalars(
            select(ChatMessage)
            .where(ChatMessage.chat_id == chat.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(SUMMARY_LIMIT)
        ).all()
        new_messages.reverse()

        if not new_messages:
            return

        prompt = build_summary_prompt(chat.summary, new_messages)
        response = llm_client.invoke(prompt)
        chat.summary = response.content
        chat.summarized_up_to = chat.message_count
        session.commit()
