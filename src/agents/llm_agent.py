import os
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from oci.addons.adk import Agent, AgentClient

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "config/.env")

OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE")          # e.g. ~/.oci/config
OCI_PROFILE     = os.getenv("OCI_PROFILE", "DEFAULT")
AGENT_REGION    = os.getenv("AGENT_REGION")             # e.g. us-chicago-1
LLM_AGNET_EP_ID     = os.getenv("LLM_AGNET_EP_ID")  # supply a dedicated endpoint if desired

def build_agent():
    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )
    # Instructions guide the LLM behavior
    instructions = (
        "You are a concise assistant. Answer clearly. "
        "If the user asks for unsupported tasks, politely decline."
    )
    agent = Agent(
        client=client,
        agent_endpoint_id=LLM_AGNET_EP_ID,
        instructions=instructions,
        tools=[]  # no tools -> pure LLM
    )
    return agent

def run_llm_decision(query: str) -> str:
    """
    Initializes and runs the LLM agent for a given query.
    Handles asyncio event loop for Streamlit compatibility.
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
    final_message = response.data["message"]["content"]["text"]
    return final_message

if __name__ == "__main__":
    test_query = "Is the sky blue?"
    print("--- Testing LLM Agent ---")
    response_text = run_llm_decision(test_query)
    print("\n--- LLM Agent Response ---")
    print(response_text)