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

def resolve_dispute(user_dispute_prompt: str, approval_threshold: float = 500.0):
    """
    Orchestrates the dispute resolution workflow, yielding updates at each step.
    """
    # --- Step 1 - Classify the issue type ---
    classification = run_classification_query(user_dispute_prompt)
    yield {
        "step_name": "Classification Agent: Issue Type",
        "data": classification,
        "is_final": False
    }

    # --- Step 2 - Get all customer data from DB ---
    # We now pass the classification to the DB agent
    transaction_data_str = run_db_query(user_dispute_prompt, classification)
    yield {
        "step_name": "DB Agent: Customer Data",
        "data": transaction_data_str,
        "is_final": False
    }

    # --- Step 3 - Call RAG agent ---
    t_and_c_query = "What are the terms and conditions for refunds and cancellations?"
    terms_and_conditions = run_rag_query(t_and_c_query)
    yield {
        "step_name": "RAG Agent: Terms & Conditions",
        "data": terms_and_conditions,
        "is_final": False
    }

    # Step 4: Compile data and call LLM agent
    dispute_context = {
        "user_dispute": user_dispute_prompt,
        "issue_classification": classification, # Include the classification
        "terms_and_conditions": terms_and_conditions,
        "customer_data": transaction_data_str
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

    # --- Step 5: Check for Human-in-the-Loop condition ---
    dispute_amount = 0
    try:
        # Attempt to parse the transaction data to find the amount
        json_start = transaction_data_str.find('{')
        json_end = transaction_data_str.rfind('}') + 1
        if json_start != -1 and json_end != 0:
            db_data = json.loads(transaction_data_str[json_start:json_end])
            transactions = db_data.get("transactions", [])
            
            # --- MODIFIED: Handle both list and dict for transactions ---
            if transactions:
                # If it's a dictionary, treat it as a single transaction in a list
                if isinstance(transactions, dict):
                    transactions = [transactions]
                
                # Now safely access the first transaction
                if transactions: # Check again in case it was an empty dict originally
                    dispute_amount = float(transactions[0].get("amount", 0))

    except (json.JSONDecodeError, ValueError, TypeError):
        dispute_amount = 0 # Default to 0 if parsing fails

    # --- DEBUG: Print values before the human-in-the-loop check ---
    print("\n--- HUMAN-IN-THE-LOOP CHECK ---")
    print(f"Dispute Amount: {dispute_amount}")
    print(f"Approval Threshold: {approval_threshold}")
    print(f"AI Decision Status: {final_decision.get('dispute_status')}")
    print("---------------------------------\n")

    # If AI accepts a refund over the threshold, ask for human approval
    if final_decision.get("dispute_status") == "Accepted" and dispute_amount > approval_threshold:
        # --- MODIFIED: Add dispute amount to the data payload for the UI ---
        approval_data = final_decision.copy()
        approval_data['dispute_amount'] = dispute_amount
        
        yield {
            "step_name": "Human Approval Required",
            "data": approval_data, # Pass the AI recommendation and the amount
            "is_final": False # Not final until a human decides
        }
    else:
        # Otherwise, yield the final decision directly
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

    # Run the workflow with a sample threshold
    for update in resolve_dispute(sample_dispute, approval_threshold=400.0):
        print(f"\n--- {update['step_name']} ---")
        print(json.dumps(update, indent=2))

    print("\n--- Dispute Resolution Complete ---")