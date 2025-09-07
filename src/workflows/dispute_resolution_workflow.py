"""
dispute_resolution_workflow.py

This script orchestrates the dispute resolution process by coordinating multiple agents.
Workflow:
1. Receives a user's dispute prompt.
2. Calls the RAG agent to fetch relevant terms and conditions.
3. Calls the DB agent to retrieve user transaction and usage data.
4. Compiles the collected information into a structured JSON object.
5. Calls the LLM agent with the compiled data to get a final decision.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

# --- MODIFIED: Import the new classification agent ---
from src.agents.classification_agent import run_classification_query
from src.agents.rag_agent import run_rag_query
from src.agents.db_agent import run_db_query
from src.agents.llm_agent import run_llm_decision

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "config/.env")

def resolve_dispute(user_dispute_prompt: str):
    """
    Orchestrates the dispute resolution workflow, yielding updates at each step.
    """
    # --- NEW: Step 1 - Classify the issue type ---
    classification = run_classification_query(user_dispute_prompt)
    yield {
        "step_name": "Classification Agent: Issue Type",
        "data": classification,
        "is_final": False
    }

    # Step 2: Call RAG agent
    t_and_c_query = "What are the terms and conditions for refunds and cancellations?"
    terms_and_conditions = run_rag_query(t_and_c_query)
    yield {
        "step_name": "RAG Agent: Terms & Conditions",
        "data": terms_and_conditions,
        "is_final": False
    }

    # Step 3: Call DB agent
    # --- MODIFIED: Pass both the user prompt and the classification to the DB agent ---
    transaction_data = run_db_query(user_dispute_prompt, classification)
    yield {
        "step_name": "DB Agent: Customer Data",
        "data": transaction_data,
        "is_final": False
    }

    # Step 4: Compile data and call LLM agent
    dispute_context = {
        "user_dispute": user_dispute_prompt,
        "issue_classification": classification, # Include the classification
        "terms_and_conditions": terms_and_conditions,
        "customer_data": transaction_data
    }
    dispute_json = json.dumps(dispute_context, indent=2)
    
    llm_prompt = f"""
    Analyze the following customer dispute based on the provided context.
    Your response must be a JSON object with three keys:
    1. "dispute_status": "Accepted" or "Rejected".
    2. "reason": A brief, clear explanation for your decision.
    3. "recommended_action": A specific next step.

    Context:
    {dispute_json}
    """
    final_decision_str = run_llm_decision(llm_prompt)
    
    cleaned_json_str = final_decision_str.strip()
    if cleaned_json_str.startswith("```json"):
        cleaned_json_str = cleaned_json_str[7:]
    if cleaned_json_str.endswith("```"):
        cleaned_json_str = cleaned_json_str[:-3]
    cleaned_json_str = cleaned_json_str.strip()

    try:
        final_decision = json.loads(cleaned_json_str)
    except json.JSONDecodeError:
        final_decision = {"raw_response": final_decision_str}

    # Step 5: Yield the final decision
    yield {
        "step_name": "LLM Agent: Final Decision",
        "data": final_decision,
        "is_final": True
    }


if __name__ == "__main__":
    # Example user dispute from your CSV file
    sample_dispute = """
    This is an unauthorized transaction for a service I never signed up for.
    I already had an account through a reseller but was charged for a duplicate one.
    Please process an immediate refund as this is a fraudulent charge.
    The reference transaction number: P-1234567890 Account Number: 5931479520
    """

    # Run the workflow
    for update in resolve_dispute(sample_dispute):
        print(f"\n--- {update['step_name']} ---")
        print(json.dumps(update, indent=2))

    print("\n--- Dispute Resolution Complete ---")