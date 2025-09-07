import streamlit as st
import sys
from pathlib import Path
import json
import time

# --- Add project root to path to allow imports ---
PROJECT_ROOT = str(Path(__file__).resolve().parent)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.workflows.dispute_resolution_workflow import resolve_dispute

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Auto Dispute Resolution", layout="wide")
st.title("🤖 Automated Dispute Resolution System")
st.markdown("Enter a customer dispute below to begin the analysis workflow. The system will use multiple AI agents to gather context and recommend a decision.")

# --- UI Elements ---
default_prompt = """
This is an unauthorized transaction for a service I never signed up for.
I already had an account through a reseller but was charged for a duplicate one.
Please process an immediate refund as this is a fraudulent charge.
The reference transaction number: P-1234567890 Account Number: 5931479520
"""

user_prompt = st.text_area("Customer Dispute Prompt:", value=default_prompt, height=250)

if st.button("Analyze Dispute"):
    if not user_prompt.strip():
        st.error("Please enter a dispute prompt.")
    else:
        final_decision = {}
        # Use st.status to show the sequential workflow progress
        with st.status("Starting dispute resolution workflow...", expanded=True) as status:
            try:
                # --- FIX: Iterate through the generator from resolve_dispute ---
                for result in resolve_dispute(user_prompt):
                    step_name = result["step_name"]
                    data = result["data"]
                    is_final = result["is_final"]

                    status.write(f"**{step_name}** completed.")
                    
                    # Display the data from the current step
                    if isinstance(data, dict):
                        st.json(data)
                    else:
                        st.text(data)
                    
                    time.sleep(0.5) # Small delay for better visual flow

                    if is_final:
                        status.update(label="Workflow Complete!", state="complete", expanded=False)
                        final_decision = data # Store the final data
                        break
                    else:
                        # Update status for the next step
                        # --- MODIFIED: Add the new classification step ---
                        next_step_map = {
                            "Classification Agent: Issue Type": "Calling RAG Agent...",
                            "RAG Agent: Terms & Conditions": "Calling DB Agent...",
                            "DB Agent: Customer Data": "Calling LLM Agent for decision...",
                        }
                        next_status_text = next_step_map.get(step_name, "Processing next step...")
                        status.update(label=next_status_text)

            except Exception as e:
                status.update(label="Workflow Failed", state="error")
                st.error(f"An error occurred during the workflow: {e}")
                st.exception(e)

        # --- Display the final, summarized decision outside the status box ---
        if final_decision:
            st.subheader("Final Decision Summary")
            status_val = final_decision.get("dispute_status", "N/A")
            reason = final_decision.get("reason", "N/A")
            action = final_decision.get("recommended_action", "N/A")

            if status_val.lower() == "accepted":
                st.success(f"**Status:** {status_val}")
            else:
                st.error(f"**Status:** {status_val}")

            st.info(f"**Reason:** {reason}")
            st.warning(f"**Recommended Action:** {action}")

# --- Instructions in Sidebar ---
st.sidebar.title("How to Use")
st.sidebar.info(
    "1. **Enter the dispute:** Paste the full text of the customer's complaint.\n\n"
    "2. **Click Analyze:** Watch as each AI agent is called in sequence.\n\n"
    "3. **Review the output:** The final decision is summarized at the end."
)