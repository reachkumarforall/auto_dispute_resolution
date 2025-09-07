"""
classification_agent.py
Author: Malkit Bhasin
Date: 2025-09-06
================================
==Dispute Classification Agent==
================================
This agent classifies a user's dispute prompt into a predefined category.
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from oci.addons.adk import Agent, AgentClient

# --- Bootstrap paths and environment ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "config/.env")

OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE")
OCI_PROFILE = os.getenv("OCI_PROFILE", "DEFAULT")
AGENT_REGION = os.getenv("AGENT_REGION")
# Assumes a new endpoint ID for this specific agent
CLASSIFICATION_AGENT_EP_ID = os.getenv("LLM_AGNET_EP_ID")

# --- Predefined Classification Categories ---
CLASSIFICATION_CATEGORIES = [
    "Unauthorized Charge",
    "Issues with Subscription Cancellation",
    "Double Billing",
    "Failure to Refund within Policy Window",
    "Service Not Received",
    "Misleading Charges and Lack of Support",
    "Ineffective Cancellation Process",
    "Billing Despite Suspension",
    "Lack of Communication",
    "Auto-Renewal without Consent"
]

def build_agent():
    """Builds the classification agent with specific instructions."""
    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )
    
    # Instructions are highly specific to the classification task
    instructions = (
        "You are an expert at classifying customer support issues. "
        "Analyze the user's prompt and classify it into one of the following categories:\n"
        f"{', '.join(CLASSIFICATION_CATEGORIES)}\n"
        "Your response MUST be only the category name and nothing else."
    )
    
    agent = Agent(
        client=client,
        agent_endpoint_id=CLASSIFICATION_AGENT_EP_ID,
        instructions=instructions,
        tools=[]  # No tools needed for this agent
    )
    return agent

def run_classification_query(query: str) -> str:
    """
    Initializes and runs the classification agent for a given query.
    """
    # --- FIX for Streamlit's threading ---
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    # ------------------------------------

    agent = build_agent()
    agent.setup()
    response = agent.run(query)
    # The response should be just the category name
    classification = response.data["message"]["content"]["text"].strip()
    return classification

if __name__ == "__main__":
    test_query = "I was charged twice this month for the same subscription! This is unacceptable."
    print("--- Testing Classification Agent ---")
    response_text = run_classification_query(test_query)
    print(f"\nUser Prompt: '{test_query}'")
    print(f"Classification: {response_text}")