import asyncio
import json
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from backend.services.chat.storage import upload_file
from backend.services.llm.client import contextualize_question, llm_response, plan_retrieval
from backend.services.llm.prompt import build_messages
from backend.services.llm.retrieval import RetrievedChunk, retrieve


def test_prompt_contains_retrieved_context():
    messages = build_messages(
        [RetrievedChunk("important PDF text", {"page": 1, "filename": "resume.pdf"})],
        [],
        "What does it say?",
    )

    assert messages[0]["role"] == "system"
    assert "important PDF text" in messages[0]["content"]
    assert "resume.pdf, page 2" in messages[0]["content"]
    assert "compare them directly" in messages[0]["content"]
    assert messages[-1]["content"] == "What does it say?"


def test_retrieval_plan_uses_model_selected_budget_per_document():
    first_id = str(uuid4())
    second_id = str(uuid4())
    documents = [
        {"id": first_id, "filename": "engineer.pdf"},
        {"id": second_id, "filename": "designer.pdf"},
    ]
    response = SimpleNamespace(content=json.dumps({first_id: 3, second_id: 7}))

    with patch("backend.services.llm.client.ChatGroq"), patch(
        "backend.services.llm.client.create_client"
    ) as create_client:
        create_client.return_value.invoke.return_value = response
        budgets = plan_retrieval("Compare their experience", documents, 8)

    assert budgets == {first_id: 3, second_id: 7}


def test_retrieval_applies_budget_and_filename_to_each_document():
    first_id = str(uuid4())
    second_id = str(uuid4())
    calls = []

    def search(question, **kwargs):
        calls.append(kwargs)
        return [SimpleNamespace(page_content="CV details", metadata={"page": 0})]

    vector_store = SimpleNamespace(max_marginal_relevance_search=search)
    with patch("backend.services.llm.retrieval.get_chat_vector_store", return_value=vector_store):
        chunks = retrieve(
            uuid4(),
            "Compare experience",
            [first_id, second_id],
            top_k_by_document={first_id: 2, second_id: 6},
            document_names={first_id: "engineer.pdf", second_id: "designer.pdf"},
        )

    assert [call["k"] for call in calls] == [2, 6]
    assert [call["filter"]["document_id"] for call in calls] == [first_id, second_id]
    assert [chunk.metadata["filename"] for chunk in chunks] == ["engineer.pdf", "designer.pdf"]


def test_follow_up_question_is_contextualized():
    response = SimpleNamespace(content="What does page 2 say about the training plan?", response_metadata={})
    with patch("backend.services.llm.client.ChatGroq") as model:
        model.return_value.invoke.return_value = response
        result = contextualize_question(
            [{"role": "user", "content": "Tell me about the training plan."}],
            "What about page 2?",
        )

    assert result == "What does page 2 say about the training plan?"


def test_empty_llm_completion_returns_visible_fallback():
    response = SimpleNamespace(content="", response_metadata={"finish_reason": "length"})
    with patch("backend.services.llm.client.ChatGroq"), patch(
        "backend.services.llm.client.create_client"
    ) as create_client:
        create_client.return_value.invoke.return_value = response
        result = llm_response([{"role": "user", "content": "Compare these CVs"}])

    assert result == "I couldn't generate an answer this time. Please try again."
    create_client.assert_called_once_with(max_tokens=4096)


def test_llm_response_returns_nonempty_completion():
    response = SimpleNamespace(content="  CV A has more experience.  ")
    with patch("backend.services.llm.client.ChatGroq"), patch(
        "backend.services.llm.client.create_client"
    ) as create_client:
        create_client.return_value.invoke.return_value = response
        result = llm_response([{"role": "user", "content": "Compare these CVs"}])

    assert result == "CV A has more experience."


def test_upload_limit_is_enforced(tmp_path):
    file = SimpleNamespace(read=lambda size: asyncio.sleep(0, result=b"12345"))

    async def run():
        with patch("backend.services.chat.storage.UPLOAD_ROOT", tmp_path):
            try:
                await upload_file(file, "document-id", 4)
            except ValueError as error:
                return str(error)
        return ""

    assert "upload limit" in asyncio.run(run())
