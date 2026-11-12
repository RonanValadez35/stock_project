from unittest.mock import patch

from backend.email_sender import sendEmail


@patch("backend.email_sender.smtplib.SMTP")
def test_send_email_attaches_summary_from_memory(mock_smtp):
    sendEmail(
        "sender@example.com",
        "password",
        "receiver@example.com",
        "Ticker Symbol: NVDA\n",
    )

    message = mock_smtp.return_value.__enter__.return_value.send_message.call_args.args[0]
    attachment = list(message.iter_attachments())[0]
    assert attachment.get_filename() == "response.txt"
    assert attachment.get_content() == "Ticker Symbol: NVDA\n"

