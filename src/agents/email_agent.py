"""
email_agent.py
Author: Malkit Bhasin
Date: 2025-09-06
==========================
==Email Sender Assistant==
==========================
This module demonstrates sending an email using OCI Email Delivery via SMTP.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv

THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE")

# Load these securely in production (e.g., from environment variables or a config file)
SMTP_HOST = os.getenv("SMTP_HOST")  # Example endpoint
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")  # Your SMTP username
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Your SMTP password
APPROVED_SENDER = os.getenv("APPROVED_SENDER")

def send_email_via_oci(recipient, subject, body):
    """
    Sends an email using OCI Email Delivery via SMTP.
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = APPROVED_SENDER
    msg['To'] = recipient
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:
            server.ehlo()
            server.starttls()  # Enable TLS
            server.ehlo()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            result = server.sendmail(APPROVED_SENDER, [recipient], msg.as_string())
            print("SMTP sendmail result:", result)
        return f"Email sent successfully to {recipient}"
    except Exception as e:
        return f"Failed to send email: {e}"

if __name__ == "__main__":
    # Example usage
    recipient = "malkitbhasin@kpmg.com"
    # recipient = "mbhasin@gmail.com"
    subject = "Test Email from OCI Email Delivery"
    body = "Hello, this is a test email sent using OCI Email Delivery."
    print(send_email_via_oci(recipient, subject, body))