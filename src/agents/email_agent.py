"""
email_agent.py
Author: Malkit Bhasin
Date: 2025-09-06
==========================
==Email Sender Assistant==
==========================
This module demonstrates sending an email using OCI Email Delivery via SMTP or REST.
"""

import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
import requests

THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")

# Load credentials from environment variables
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
APPROVED_SENDER = os.getenv("APPROVED_SENDER")
OIC_EMAIL_ENDPOINT = os.getenv("OIC_EMAIL_ENDPOINT")  # e.g., https://oic.example.com/sendEmail

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

def send_email_via_oic_rest(email_id, subject, body):
    """
    Sends an email using a REST endpoint exposed by OIC.
    The endpoint expects a JSON payload: { "email_id": ..., "subject": ..., "body": ... }
    """
    if not OIC_EMAIL_ENDPOINT:
        return "Error: OIC_EMAIL_ENDPOINT environment variable is not set."

    payload = {
        "email_id": email_id,
        "subject": subject,
        "body": body
    }

    try:
        response = requests.post(OIC_EMAIL_ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
        return f"Email sent successfully via OIC REST endpoint. Status: {response.status_code}"
    except requests.RequestException as e:
        return f"Error sending email via OIC REST endpoint: {str(e)}"

if __name__ == "__main__":
    # Example usage
    recipient = "malkitbhasin@kpmg.com"
    subject = "Test Email from OCI (Debug Mode)"
    body = "Hello, this is a test email sent using OCI Email Delivery with debugging enabled."
    
    print(send_email_via_oci(recipient, subject, body))
    # Uncomment below to test OIC REST email sending
    # print(send_email_via_oic_rest("recipient@example.com", subject, body))