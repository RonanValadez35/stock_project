from unittest.mock import Mock, patch
from summarizer import getResponse

@patch("os.environ.get")
@patch("summarizer.Client")
def test_get_response(mock_client, mock_getenv):
    fake_response = {"message": "This is a fake response"}
    mock_getenv.return_value = "Fake_Token"
    fake_client_instance = Mock()
    mock_client.return_value = fake_client_instance

    fake_client_instance.chat.return_value = fake_response

    actual = getResponse("Hello")

    assert actual == fake_response

    messages = [
        {
            'role': 'user',
            'content': "Hello",
        },
    ]

    fake_client_instance.chat.assert_called_once_with('gemma4:31b-cloud', messages=messages)
    
