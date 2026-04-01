import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv 


def sendEmail(sender: str, password: str, receiver: str, file_name: str) -> None:
    if not sender:
        raise ValueError("Sender email address missing")
    if not password:
        raise ValueError("Sender password missing")
    if not receiver:
        raise ValueError("Recipient password missing")
    
    msg = EmailMessage()
    with open(file_name, "rb") as f:
        file_data = f.read()
        attatchment_name = f.name

    msg.set_content("Here is the email with the stock summary file")
    msg['Subject'] = "Stock Summary file"
    msg['From'] = sender
    msg['To'] = receiver
    msg.add_attachment(file_data,
                       maintype="text",
                       subtype="plain",
                       filename=attatchment_name)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)

    print("Email sent successfully!")


# load_dotenv()
# sender = os.getenv("EMAIL_USER")
# password = os.getenv("EMAIL_PASSWORD")
# receiver = os.getenv("RECIPIENT_EMAIL")

# sendEmail(sender, password, receiver, "response.txt")
