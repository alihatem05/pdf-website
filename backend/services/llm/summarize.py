from backend.celery_app import celery_app
from backend.models.chat import Chat
from backend.models.chat_message import ChatMessage
from backend.config import CELERY_DATABASE_URL, SUMMARY_LIMIT

sync_engine = create_engine(CELERY_DATABASE_URL)
SyncSession = sessionmaker(bind=sync_engine)
llm_client = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

def build_summary_prompt(old_summary, new_messages):
    conversation = "\n".join(f"{m.role.value}: {m.content}" for m in new_messages)
    if old_summary:
        return (
            f"Here is a summary of the conversation so far:\n{old_summary}\n\n"
            f"Here are new messages to fold into that summary:\n{conversation}\n\n"
            f"Produce an updated, concise summary that captures the key points of the "
            f"entire conversation, including what's new."
        )
    return (
        f"Summarize the key points of this conversation concisely, in a way that "
        f"preserves context needed to continue answering related questions:\n\n{conversation}"
    )

@celery_app.task
def update_chat_summary(chat_id):
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
        new_summary = response.content or ""

        chat.summary = new_summary
        chat.summarized_up_to = chat.message_count
        session.commit()
