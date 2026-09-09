import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from backend.core.storage import upload_file
from backend.services.client import contextualize_question
from backend.services.llm.prompt import build_messages
from backend.services.llm.retrieval import RetrievedChunk


def test_prompt_contains_retrieved_context():
    messages = build_messages(
        [RetrievedChunk("important PDF text", {"page": 1})],
        [],
        "What does it say?",
    )

    assert messages[0]["role"] == "system"
    assert "important PDF text" in messages[0]["content"]
    assert messages[-1]["content"] == "What does it say?"


def test_follow_up_question_is_contextualized():
    response = SimpleNamespace(content="What does page 2 say about the training plan?", response_metadata={})
    with patch("backend.services.client.ChatGroq") as model:
        model.return_value.invoke.return_value = response
        result = contextualize_question(
            [{"role": "user", "content": "Tell me about the training plan."}],
            "What about page 2?",
        )

    assert result == "What does page 2 say about the training plan?"


def test_upload_limit_is_enforced(tmp_path):
    file = SimpleNamespace(read=lambda size: asyncio.sleep(0, result=b"12345"))

    async def run():
        with patch("backend.core.storage.UPLOAD_ROOT", tmp_path):
            try:
                await upload_file(file, "document-id", 4)
            except ValueError as error:
                return str(error)
        return ""

    assert "upload limit" in asyncio.run(run())
