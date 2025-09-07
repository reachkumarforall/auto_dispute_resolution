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

# --- Assume agent runner functions exist in these modules ---
# These would contain the logic to initialize and run each specific agent.
# You will need to implement these based on your agent setup.
from src.agents.rag_agent import run_rag_query
from src.agents.db_agent import run_db_query
from src.agents.llm_agent import run_llm_decision

# --- Environment Setup ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "config/.env")

def resolve_dispute(user_dispute_prompt: str) -> dict:
    """
    Orchestrates the entire dispute resolution workflow.

    Args:
        user_dispute_prompt: The full text of the user's dispute.

    Returns:
        A dictionary containing the final decision from the LLM agent.
    """
    print("--- Starting Dispute Resolution Workflow ---")

    # 1. Call RAG agent to get terms and conditions for refunds
    print("\n[Step 1/4] Calling RAG Agent for Terms & Conditions...")
    t_and_c_query = "What are the terms and conditions for refunds and cancellations?"
    terms_and_conditions = run_rag_query(t_and_c_query)
    print("   > RAG Agent Response Received.")

    # 2. Call DB agent to get transaction and usage data
    print("\n[Step 2/4] Calling DB Agent for Customer Data...")
    # The prompt for the DB agent should be specific to the user's dispute
    db_query = f"Find transaction and usage history for the customer dispute: '{user_dispute_prompt}'"
    transaction_data = run_db_query(db_query)
    print("   > DB Agent Response Received.")

    # 3. Create a structured dispute object for the LLM
    print("\n[Step 3/4] Compiling data for LLM analysis...")
    dispute_context = {
        "user_dispute": user_dispute_prompt,
        "terms_and_conditions": terms_and_conditions,
        "customer_data": transaction_data
    }
    dispute_json = json.dumps(dispute_context, indent=2)
    print("   > Compiled JSON created.")
    # print(dispute_json) # Uncomment to see the full JSON

    # 4. Call LLM agent for a final decision
    print("\n[Step 4/4] Calling LLM Agent for Final Decision...")
    llm_prompt = f"""
    Analyze the following customer dispute based on the provided context.
    Determine if the dispute is valid according to the terms and conditions and customer data.

    Your response must be a JSON object with three keys:
    1. "dispute_status": "Accepted" or "Rejected".
    2. "reason": A brief, clear explanation for your decision.
    3. "recommended_action": A specific next step (e.g., "Process full refund", "Deny refund due to policy violation", "Escalate to human agent").

    Context:
    {dispute_json}
    """
    final_decision_str = run_llm_decision(llm_prompt)
    print("   > LLM Agent Response Received.")

    try:
        final_decision = json.loads(final_decision_str)
    except json.JSONDecodeError:
        print("Error: LLM did not return valid JSON. Returning raw response.")
        final_decision = {"raw_response": final_decision_str}

    return final_decision


if __name__ == "__main__":
    # Example user dispute from your CSV file
    sample_dispute = """
    This is an unauthorized transaction for a service I never signed up for.
    I already had an account through a reseller but was charged for a duplicate one.
    Please process an immediate refund as this is a fraudulent charge.
    The reference transaction number: P-1234567890 Account Number: 5931479520
    """

    # Run the workflow
    decision = resolve_dispute(sample_dispute)

    # Print the final result
    print("\n--- Dispute Resolution Complete ---")
    print(f"Final Decision: {json.dumps(decision, indent=2)}")