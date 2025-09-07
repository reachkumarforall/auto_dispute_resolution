import streamlit as st
import sys
from pathlib import Path
import json
import time
import pandas as pd

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

# --- Define Agent Steps for the Visual Flow ---
# --- MODIFIED: Reordered steps to match the new workflow ---
AGENT_STEPS = {
    "Classification Agent: Issue Type": "1. Classify Issue",
    "DB Agent: Customer Data": "2. Get Account Data",
    "RAG Agent: Terms & Conditions": "3. Fetch Policies",
    "LLM Agent: Final Decision": "4. Generate Decision"
}
AGENT_STEP_NAMES = list(AGENT_STEPS.keys())

if st.button("Analyze Dispute"):
    if not user_prompt.strip():
        st.error("Please enter a dispute prompt.")
    else:
        # --- Create placeholders for progress boxes and agent output ---
        st.subheader("Workflow Progress")
        progress_cols = st.columns(len(AGENT_STEPS))
        progress_boxes = {}

        # --- NEW: Create placeholders for the data tables ---
        st.subheader("Live Data Feed")
        table_cols = st.columns(3)
        with table_cols[0]:
            st.markdown("##### User Info")
            st.divider()
            user_info_placeholder = st.empty()
            user_info_placeholder.markdown("*Waiting for data...*")
        with table_cols[1]:
            st.markdown("##### Account Usage")
            st.divider()
            usage_placeholder = st.empty()
            usage_placeholder.markdown("*Waiting for data...*")
        with table_cols[2]:
            st.markdown("##### Transactions")
            st.divider()
            transactions_placeholder = st.empty()
            transactions_placeholder.markdown("*Waiting for data...*")

        # --- MODIFIED: Initialize progress boxes with placeholders for status text ---
        for i, (step_name, label) in enumerate(AGENT_STEPS.items()):
            with progress_cols[i]:
                box_container = st.container(border=True)
                box_container.markdown(f"**{label}**")
                status_placeholder = box_container.empty() # Create a placeholder for the status
                status_placeholder.markdown("⚪ Pending")
                progress_boxes[step_name] = status_placeholder # Store the placeholder itself

        st.subheader("Agent Output Log")
        output_container = st.container()
        final_decision = {}
        
        try:
            # --- Iterate through the workflow and update the UI ---
            for i, result in enumerate(resolve_dispute(user_prompt)):
                current_step_name = result["step_name"]
                data = result["data"]
                is_final = result["is_final"]

                # --- MODIFIED: Update the placeholder's content directly ---
                # Update current step to "In Progress" (Yellow)
                progress_boxes[current_step_name].markdown("🟡 In Progress...")

                # Update previous step to "Completed" (Green)
                if i > 0:
                    previous_step_name = AGENT_STEP_NAMES[i-1]
                    progress_boxes[previous_step_name].markdown("✅ Completed")
                
                # --- Populate tables when DB Agent finishes ---
                if current_step_name == "DB Agent: Customer Data":
                    try:
                        # Find the start and end of the JSON block
                        json_start = data.find('{')
                        json_end = data.rfind('}') + 1
                        
                        if json_start != -1 and json_end != 0:
                            cleaned_json_str = data[json_start:json_end]
                            db_data = json.loads(cleaned_json_str)

                            # --- MODIFIED: Clear placeholders and display data as tables ---
                            user_info_placeholder.empty()
                            usage_placeholder.empty()
                            transactions_placeholder.empty()

                            # Display User Info
                            user_info = db_data.get("user_info")
                            if user_info:
                                user_df = pd.DataFrame([user_info])
                                user_info_placeholder.dataframe(user_df, use_container_width=True, hide_index=True)
                            else:
                                user_info_placeholder.markdown("*Not found.*")
                            
                            # Display Account Usage
                            account_usage = db_data.get("account_usage")
                            if account_usage:
                                usage_df = pd.DataFrame([account_usage])
                                usage_placeholder.dataframe(usage_df, use_container_width=True, hide_index=True)
                            else:
                                usage_placeholder.markdown("*Not found.*")

                            # Display Transactions
                            transactions = db_data.get("transactions")
                            if transactions:
                                # Ensure transactions is a list for DataFrame compatibility
                                trans_list = transactions if isinstance(transactions, list) else [transactions]
                                trans_df = pd.DataFrame(trans_list)
                                transactions_placeholder.dataframe(trans_df, use_container_width=True, hide_index=True)
                            else:
                                transactions_placeholder.markdown("*Not found.*")
                        else:
                            raise json.JSONDecodeError("No JSON object found in string", data, 0)

                    except (json.JSONDecodeError, AttributeError, TypeError):
                        # Fallback if the agent doesn't return clean JSON
                        user_info_placeholder.markdown("*Could not parse DB Agent output.*")
                        usage_placeholder.empty()
                        transactions_placeholder.empty()


                # Display agent output log
                with output_container:
                    with st.expander(f"Output from: **{current_step_name}**", expanded=True):
                        st.text(data) # Display raw text output here
                
                time.sleep(1) # Visual delay

                if is_final:
                    # Mark the final step as "Completed"
                    progress_boxes[current_step_name].markdown("✅ Completed")
                    final_decision = json.loads(data) if isinstance(data, str) else data
                    break
        
        except Exception as e:
            st.error(f"An error occurred during the workflow: {e}")
            st.exception(e)

        # --- Display the final, summarized decision ---
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
    "2. **Click Analyze:** Watch the workflow progress and see live data populate.\n\n"
    "3. **Review the output:** The final decision is summarized at the end."
)