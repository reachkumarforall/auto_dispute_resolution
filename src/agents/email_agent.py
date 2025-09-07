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
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv

THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")

# Load credentials from environment variables
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
APPROVED_SENDER = os.getenv("APPROVED_SENDER")

def send_email_via_oci(recipient, subject, body):
    """
    Sends an email using OCI Email Delivery via SMTP with verbose debugging.
    """
    # --- Credential Check ---
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, APPROVED_SENDER]):
        return "Error: One or more SMTP environment variables are missing. Please check your .env file."

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = APPROVED_SENDER
    msg['To'] = recipient
    msg.set_content(body)

    try:
        print("--- Attempting to connect to OCI SMTP server ---")
        with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:
            # --- ADDED: Enable verbose debug output ---
            server.set_debuglevel(1)
            
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg) # Using send_message is slightly more modern for EmailMessage objects
            
        return f"Email sent successfully to {recipient}"
    except Exception as e:
        return f"Failed to send email: {e}"

if __name__ == "__main__":
    # Example usage
    recipient = "malkitbhasin@kpmg.com"
    subject = "Test Email from OCI (Debug Mode)"
    body = "Hello, this is a test email sent using OCI Email Delivery with debugging enabled."
    
    print(send_email_via_oci(recipient, subject, body))