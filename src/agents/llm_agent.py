import os
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

def run_llm(query: str):
    agent = build_agent()
    agent.setup()
    resp = agent.run(query)
    text = resp.data["message"]["content"]["text"]
    print("=== LLM Response ===")
    print(text)
    # Optional: resp.pretty_print_traces()
    return text

if __name__ == "__main__":
    user_query = "Summarize why email soft bounces happen."
    run_llm(user_query)