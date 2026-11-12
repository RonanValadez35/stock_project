import smtplib
from email.message import EmailMessage


def sendEmail(
    sender: str,
    password: str,
    receiver: str,
    summary: str,
    file_name: str = "response.txt",
) -> None:
    """Send summary text as an in-memory plain-text attachment."""
    if not sender:
        raise ValueError("Sender email address missing")
    if not password:
        raise ValueError("Sender password missing")
    if not receiver:
        raise ValueError("Recipient email address missing")

    msg = EmailMessage()
    msg.set_content("Here is the email with the stock summary file")
    msg['Subject'] = "Stock Summary file"
    msg['From'] = sender
    msg['To'] = receiver
    msg.add_attachment(summary, subtype="plain", filename=file_name)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)
