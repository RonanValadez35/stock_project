from unittest.mock import Mock, patch

from backend.summarizer import formatDoc, getResponse


@patch("backend.summarizer.Client")
def test_get_response(mock_client):
    fake_response = {"message": "This is a fake response"}
    fake_client_instance = Mock()
    mock_client.return_value = fake_client_instance

    fake_client_instance.chat.return_value = fake_response

    actual = getResponse("Hello")

    assert actual == fake_response
    mock_client.assert_called_once_with(host="http://127.0.0.1:11434")

    messages = [
        {
            'role': 'user',
            'content': "Hello",
        },
    ]

    fake_client_instance.chat.assert_called_once_with(
        "llama3:8b",
        messages=messages,
        options={"temperature": 0.0},
    )


def test_format_doc_returns_formatted_text():
    response = "Ticker Symbol: NVDA\n\nSummary.\n\nKeypoints: * One. * Two."

    actual = formatDoc(response)

    assert actual == (
        "Ticker Symbol: NVDA\n\n"
        "Summary.\n\n"
        "Keypoints:\n"
        "* One.\n"
        "* Two.\n"
    )
    
