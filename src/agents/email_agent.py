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

# Load these securely in production (e.g., from environment variables or a config file)
SMTP_HOST = "smtp.email.us-ashburn-1.oraclecloud.com"  # Example endpoint
SMTP_PORT = 587
SMTP_USERNAME = "ocid1.emailsender.oc1.us-chicago-1.amaaaaaayanwdzaal2rabqthpxzvapzltxfwjjhpynhhk67osha77b35kj5q"  # Your SMTP username
SMTP_PASSWORD = "your_smtp_password"  # Your SMTP password
APPROVED_SENDER = "malkitbhasin@kpmg.com"

def send_email_via_oci(recipient, subject, body):
    """
    Sends an email using OCI Email Delivery via SMTP.
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = APPROVED_SENDER
    msg['To'] = recipient

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()  # Enable TLS
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return f"Email sent successfully to {recipient}"
    except Exception as e:
        return f"Failed to send email: {e}"

if __name__ == "__main__":
    # Example usage
    recipient = "mbhasin@gmail.com"
    subject = "Test Email from OCI Email Delivery"
    body = "Hello, this is a test email sent using OCI Email Delivery."
    print(send_email_via_oci(recipient, subject, body))