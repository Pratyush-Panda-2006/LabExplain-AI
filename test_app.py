from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from config import settings
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /health returns operational status and active model tag."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"] == settings.MODEL_NAME
    assert data["service"] == "LabExplain"


def test_serve_root_spa():
    """Verify GET / returns the frontend single-page application."""
    response = client.get("/")
    assert response.status_code == 200
    assert "LabExplain" in response.text
    assert "<!DOCTYPE html>" in response.text


def test_explain_invalid_pin():
    """Verify POST /api/explain rejects wrong PIN with HTTP 401."""
    payload = {
        "pin": "wrong-pin-000000",
        "code": "print('hello')",
        "language": "python",
    }
    response = client.post("/api/explain", json=payload)
    assert response.status_code == 401
    assert "Invalid session PIN" in response.json()["detail"]


def test_explain_empty_code():
    """Verify POST /api/explain rejects empty code with HTTP 422."""
    payload = {
        "pin": settings.SESSION_PIN,
        "code": "   ",
        "language": "python",
    }
    response = client.post("/api/explain", json=payload)
    assert response.status_code == 422


def test_explain_code_too_long():
    """Verify POST /api/explain rejects code exceeding 4000 characters."""
    payload = {
        "pin": settings.SESSION_PIN,
        "code": "x = 1\n" * 1500,
        "language": "python",
    }
    response = client.post("/api/explain", json=payload)
    assert response.status_code == 422


def test_explain_successful_inference():
    """Verify POST /api/explain returns line-by-line explanation."""
    mock_explanation = (
        "### 📝 Overview\n"
        "Reads a file safely.\n\n"
        "### 🔍 Line-by-Line Breakdown\n"
        "- **Line**: `with open('data.txt') as f:`\n"
        "- **What it does**: Opens file with context manager.\n"
        "- **Why it matters / Gotchas**: Guarantees file descriptor closure."
    )

    with patch("services.llm_service.get_groq_client") as mock_get_client:
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = mock_explanation
        mock_res = MagicMock()
        mock_res.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_res
        mock_get_client.return_value = mock_client

        payload = {
            "pin": settings.SESSION_PIN,
            "code": "with open('data.txt') as f:\n    data = f.read()",
            "language": "python",
        }
        response = client.post("/api/explain", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "Guarantees file descriptor closure" in data["explanation"]


def test_decommissioned_model_fallback():
    """Verify that a decommissioned model error triggers fallback to llama-3.1-8b-instant."""
    import httpx
    from groq import APIStatusError
    from services.llm_service import explain_snippet

    dummy_request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    dummy_response = httpx.Response(400, request=dummy_request)
    decommissioned_err = APIStatusError(
        message="The model `gemma2-9b-it` has been decommissioned.",
        response=dummy_response,
        body={"error": {"code": "model_decommissioned"}},
    )

    with patch("services.llm_service.get_groq_client") as mock_get_client:
        mock_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Fallback explanation success"
        mock_res = MagicMock()
        mock_res.choices = [mock_choice]

        # First call fails with decommissioned error, second call succeeds with llama-3.1-8b-instant
        mock_client.chat.completions.create.side_effect = [decommissioned_err, mock_res]
        mock_get_client.return_value = mock_client

        with patch.object(settings, "MODEL_NAME", "gemma2-9b-it"):
            result = explain_snippet("print('hello')", "python")
            assert result == "Fallback explanation success"
            assert mock_client.chat.completions.create.call_count == 2
