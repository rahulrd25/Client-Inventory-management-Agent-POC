import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='/Users/rd/Downloads/800 pharmacy docs/.env', override=True) # Load environment variables from .env file

def send_results_email(recipient_email, subject, body, attachment_paths):
    """
    Sends an email with the replenishment results as attachments.
    SMTP server details and credentials are read from environment variables.
    """
    sender_email = os.getenv("EMAIL_USERNAME")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587)) # Default to 587 for TLS

    if not all([sender_email, sender_password, smtp_host]):
        print("Email credentials (EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_HOST) not set as environment variables.")
        return False, "Email credentials not configured."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    for file_path in attachment_paths:
        if os.path.exists(file_path):
            try:
                part = MIMEBase('application', 'octet-stream')
                with open(file_path, 'rb') as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(file_path)}")
                msg.attach(part)
            except Exception as e:
                print(f"Could not attach file {file_path}: {e}")
                return False, f"Could not attach file {file_path}: {e}"
        else:
            print(f"Attachment file not found: {file_path}")
            # Decide if this should be a fatal error or just a warning
            # For now, we'll continue but log it.

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True, "Email sent successfully!"
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, f"Error sending email: {e}"
