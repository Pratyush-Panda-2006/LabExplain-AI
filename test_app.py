from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /health returns operational status and Gemma 2 model tag."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"] == "gemma2-9b-it"
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
        "pin": "999999",
        "code": "print('hello')",
        "language": "python",
    }
    response = client.post("/api/explain", json=payload)
    assert response.status_code == 401
    assert "Invalid session PIN" in response.json()["detail"]


def test_explain_empty_code():
    """Verify POST /api/explain rejects empty code with HTTP 422."""
    payload = {
        "pin": "482910",
        "code": "   ",
        "language": "python",
    }
    response = client.post("/api/explain", json=payload)
    assert response.status_code == 422


def test_explain_code_too_long():
    """Verify POST /api/explain rejects code exceeding 4000 characters."""
    payload = {
        "pin": "482910",
        "code": "x = 1\n" * 1500,
        "language": "python",
    }
    response = client.post("/api/explain", json=payload)
    assert response.status_code == 422


def test_explain_successful_inference():
    """Verify POST /api/explain returns Gemma 2 line-by-line explanation."""
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
            "pin": "482910",
            "code": "with open('data.txt') as f:\n    data = f.read()",
            "language": "python",
        }
        response = client.post("/api/explain", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "Guarantees file descriptor closure" in data["explanation"]
