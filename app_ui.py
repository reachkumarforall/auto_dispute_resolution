import streamlit as st
import sys
from pathlib import Path
import json
import pandas as pd
import subprocess # --- NEW: Import subprocess

# --- Add project root to path to allow imports ---
PROJECT_ROOT = str(Path(__file__).resolve().parent)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.workflows.dispute_resolution_workflow import resolve_dispute

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Auto Dispute Resolution", layout="wide")

# --- State Management for Page Views ---
if 'page_view' not in st.session_state:
    st.session_state.page_view = 'main'
    st.session_state.final_outcome = None
    st.session_state.original_prompt = None
    # --- NEW: State to track if the workflow is active ---
    st.session_state.analysis_running = False

def reset_to_main_view():
    """Resets the view to the main analysis page."""
    st.session_state.page_view = 'main'
    st.session_state.final_outcome = None
    st.session_state.original_prompt = None
    # --- NEW: Reset the analysis state ---
    st.session_state.analysis_running = False

# --- Custom CSS for colored status boxes and layout adjustments ---
st.markdown("""
<style>
    /* Adjust top padding to prevent logo clipping */
    .block-container {
        padding-top: 2rem !important;
    }
    /* Target the title to reduce space between it and the logo */
    h1 {
        padding-top: 0rem !important;
    }
    /* --- MODIFIED: Reduce space around subheaders --- */
    h3 { /* st.subheader */
        margin-bottom: 0rem !important;
    }
    h5 { /* st.markdown("##### ...") */
        margin-top: 0.5rem !important;
        margin-bottom: 0rem !important;
    }
    /* Base style for the status box */
    .status-box {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
        color: black !important; /* Ensure text is black */
    }
    /* Colors for each status */
    .status-pending { background-color: #f0f2f6; } /* Light Grey */
    .status-in-progress { background-color: #ffecb3; } /* Darker Yellow */
    .status-completed { background-color: #c8e6c9; } /* Darker Green */
    .status-action-required { background-color: #ffcdd2; } /* Darker Red */
</style>
""", unsafe_allow_html=True)

# --- NEW: Function to render the confirmation page ---
def render_confirmation_page():
    """Displays the final outcome after a human approval decision."""
    outcome = st.session_state.final_outcome
    prompt = st.session_state.original_prompt
    status = outcome.get("dispute_status", "")

    st.image("ds-logo-on-white.png", width=200)
    if st.session_state.page_view == 'approved':
        st.success(f"## ✅ {status}")
    else:
        st.error(f"## ❌ {status}")

    st.markdown("---")
    st.subheader("Original Dispute")
    st.text_area("", value=prompt, height=150, disabled=True)
    
    st.subheader("Final Outcome")
    decision_df = pd.DataFrame({
        "Metric": ["Reason", "Recommended Action"],
        "Value": [outcome.get('reason'), outcome.get('recommended_action')]
    })
    st.table(decision_df.set_index("Metric"))

# --- NEW: Function to render the main analysis page ---
def render_main_page(approval_threshold):
    """Displays the main analysis workflow UI."""
    st.image("ds-logo-on-white.png", width=200)
    st.title("Automated Dispute Resolution System")
    st.markdown("Enter a customer dispute below to begin the analysis workflow. The system will use multiple AI agents to gather context and recommend a decision.")

    default_prompt = """
This is an unauthorized transaction for a service I never signed up for.
I already had an account through a reseller but was charged for a duplicate one.
Please process an immediate refund as this is a fraudulent charge.
The reference transaction number: P-1234567890 Account Number: 5931479520
"""
    user_prompt = st.text_area("Customer Dispute Prompt:", value=default_prompt, height=250)

    AGENT_STEPS = {
        "Classification Agent: Issue Type": "1. Classify Issue",
        "DB Agent: Customer Data": "2. Get Account Data",
        "RAG Agent: Terms & Conditions": "3. Fetch Policies",
        "LLM Agent: Final Decision": "4. Generate Decision",
        "Human Approval Required": "5. Human Approval"
    }
    AGENT_STEP_NAMES = list(AGENT_STEPS.keys())

    # --- MODIFIED: Set the analysis_running state on button click ---
    if st.button("Analyze Dispute"):
        if not user_prompt.strip():
            st.error("Please enter a dispute prompt.")
        else:
            st.session_state.analysis_running = True
            st.session_state.original_prompt = user_prompt # Store prompt
            st.rerun() # Rerun to start the analysis flow

    # --- MODIFIED: The workflow now runs if the state is set, not just on button click ---
    if st.session_state.analysis_running:
        # Use the stored prompt for the analysis
        prompt_for_analysis = st.session_state.original_prompt

        st.subheader("Workflow Progress")
        progress_cols = st.columns(len(AGENT_STEPS))
        progress_boxes = {}
        for i, (step_name, label) in enumerate(AGENT_STEPS.items()):
            with progress_cols[i]:
                progress_boxes[step_name] = st.empty()
                progress_boxes[step_name].markdown(
                    f'<div class="status-box status-pending"><b>{label}</b></div>',
                    unsafe_allow_html=True
                )

        st.subheader("Live Data Feed")
        table_cols = st.columns([0.25, 0.30, 0.45])
        placeholders = {}
        data_labels = ["User Info", "Account Usage", "Transactions"]
        for i, label in enumerate(data_labels):
            with table_cols[i]:
                st.markdown(f"##### {label}")
                placeholders[label] = st.empty()
                placeholders[label].markdown("*Waiting for data...*")
        
        user_info_placeholder = placeholders["User Info"]
        usage_placeholder = placeholders["Account Usage"]
        transactions_placeholder = placeholders["Transactions"]

        st.subheader("Agent Output Log")
        output_container = st.container()
        final_decision_placeholder = st.empty()
        final_decision = {}
        
        with st.spinner("Analyzing dispute..."):
            try:
                # --- MODIFIED: Use the stored prompt ---
                for i, result in enumerate(resolve_dispute(prompt_for_analysis, approval_threshold)):
                    current_step_name = result["step_name"]
                    data = result["data"]
                    is_final = result["is_final"]
                    current_label = AGENT_STEPS.get(current_step_name, "")

                    if current_step_name in progress_boxes:
                        progress_boxes[current_step_name].markdown(
                            f'<div class="status-box status-in-progress"><b>{current_label} ⏳</b></div>',
                            unsafe_allow_html=True
                        )

                    if i > 0:
                        previous_step_name = AGENT_STEP_NAMES[i-1]
                        previous_label = AGENT_STEPS.get(previous_step_name, "")
                        if previous_step_name in progress_boxes:
                            progress_boxes[previous_step_name].markdown(
                                f'<div class="status-box status-completed"><b>{previous_label} ✅</b></div>',
                                unsafe_allow_html=True
                            )
                    
                    if current_step_name == "DB Agent: Customer Data":
                        try:
                            json_start = data.find('{')
                            json_end = data.rfind('}') + 1
                            if json_start != -1:
                                db_data = json.loads(data[json_start:json_end])
                                user_info_placeholder.dataframe(pd.DataFrame([db_data.get("user_info")]), hide_index=True, use_container_width=True)
                                usage_placeholder.dataframe(pd.DataFrame([db_data.get("account_usage")]), hide_index=True, use_container_width=True)
                                trans_list = db_data.get("transactions", [])
                                transactions_placeholder.dataframe(pd.DataFrame(trans_list if isinstance(trans_list, list) else [trans_list]), hide_index=True, use_container_width=True)
                            else:
                                user_info_placeholder.markdown("*Could not parse DB Agent output.*")
                        except (json.JSONDecodeError, AttributeError):
                            user_info_placeholder.markdown("*Error displaying DB data.*")
                    
                    # --- MODIFIED: Moved output log rendering before the break logic ---
                    with output_container:
                        with st.expander(f"Output from: **{current_step_name}**", expanded=False):
                            if current_step_name == "Classification Agent: Issue Type":
                                st.write(data)
                            elif current_step_name == "RAG Agent: Terms & Conditions":
                                st.write(data)
                            elif current_step_name == "DB Agent: Customer Data":
                                try:
                                    json_start = data.find('{')
                                    json_end = data.rfind('}') + 1
                                    if json_start != -1:
                                        db_data = json.loads(data[json_start:json_end])
                                        user_info = db_data.get("user_info")
                                        if user_info:
                                            st.write("**User Info**")
                                            st.dataframe(pd.DataFrame([user_info]), hide_index=True, use_container_width=True)
                                        account_usage = db_data.get("account_usage")
                                        if account_usage:
                                            st.write("**Account Usage**")
                                            st.dataframe(pd.DataFrame([account_usage]), hide_index=True, use_container_width=True)
                                        transactions = db_data.get("transactions")
                                        if transactions:
                                            st.write("**Transactions**")
                                            trans_list = transactions if isinstance(transactions, list) else [transactions]
                                            st.dataframe(pd.DataFrame(trans_list), hide_index=True, use_container_width=True)
                                    else:
                                        st.text(data)
                                except (json.JSONDecodeError, AttributeError):
                                    st.text(data)
                            elif current_step_name == "Human Approval Required":
                                amount = data.get('dispute_amount', 'N/A')
                                amount_str = f"${amount:,.2f}" if isinstance(amount, (int, float)) else str(amount)
                                approval_df = pd.DataFrame({
                                    "Metric": ["Refund Amount", "AI Recommendation", "Reason", "Suggested Action"],
                                    "Value": [amount_str, data.get('dispute_status'), data.get('reason'), data.get('recommended_action')]
                                })
                                st.table(approval_df.set_index("Metric"))
                            else:
                                st.json(data)

                    if current_step_name == "Human Approval Required":
                        progress_boxes[current_step_name].markdown(
                            f'<div class="status-box status-action-required"><b>{current_label} ⚠️</b></div>',
                            unsafe_allow_html=True
                        )
                        with final_decision_placeholder.container():
                            st.warning("Human approval required for high-value refund.")
                            amount = data.get('dispute_amount', 'N/A')
                            amount_str = f"${amount:,.2f}" if isinstance(amount, (int, float)) else str(amount)
                            approval_df = pd.DataFrame({
                                "Metric": ["Refund Amount", "AI Recommendation", "Reason", "Suggested Action"],
                                "Value": [amount_str, data.get('dispute_status'), data.get('reason'), data.get('recommended_action')]
                            })
                            st.table(approval_df.set_index("Metric"))
                            btn_cols = st.columns(2)
                            
                            if btn_cols[0].button("✅ Approve Refund", use_container_width=True):
                                subprocess.run([sys.executable, "src/human_action_handler.py", "approve", json.dumps(data)])
                                st.session_state.final_outcome = {"dispute_status": "Accepted (Human Approved)", "reason": "Refund approved by operator.", "recommended_action": "Refund has been processed."}
                                st.session_state.page_view = 'approved'
                                st.session_state.analysis_running = False
                                break
                            
                            if btn_cols[1].button("❌ Reject Refund", use_container_width=True):
                                subprocess.run([sys.executable, "src/human_action_handler.py", "reject", json.dumps(data)])
                                st.session_state.final_outcome = {"dispute_status": "Rejected (Human Override)", "reason": "Refund rejected by operator.", "recommended_action": "No further action required."}
                                st.session_state.page_view = 'rejected'
                                st.session_state.analysis_running = False
                                break
                    
                    if is_final:
                        final_decision = data
                        final_label = AGENT_STEPS.get("LLM Agent: Final Decision", "")

            except Exception as e:
                st.error(f"An error occurred during the workflow: {e}")
                st.exception(e)
                st.session_state.analysis_running = False # Reset on error

# --- Main App Router ---
st.sidebar.title("Configuration")
approval_threshold = st.sidebar.number_input(
    "Human Approval Threshold ($)",
    min_value=0,
    value=100,
    step=50,
    help="Refunds recommended by the AI above this value will require manual approval."
)
st.sidebar.button("Reset Page", on_click=reset_to_main_view, use_container_width=True, type="primary")

if st.session_state.page_view == 'main':
    render_main_page(approval_threshold)
else:
    render_confirmation_page()