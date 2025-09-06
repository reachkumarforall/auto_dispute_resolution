"""
taxagent.py
Author: Malkit Bhasin
Date: 2025-09-06
==========================
==Tax Auditor Assistant==
==========================
This module is a specialized assistant to search and retrieve information from terms and conditions documents
Workflow Overview:
1. Load config and credentials from .env
2. Register tools with the agent - AgenticRagTool, SQL Tool
3. Run the agent with user input and print response
"""
import os
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv
import logging

from oci.addons.adk import Agent, AgentClient
from oci.addons.adk.run.types import InlineInputLocation, ObjectStorageInputLocation
from oci.addons.adk.tool.prebuilt.agentic_sql_tool import AgenticSqlTool, SqlDialect, ModelSize
from oci.addons.adk import Agent, AgentClient, tool
from oci.addons.adk.tool.prebuilt import AgenticRagTool

from src.prompts.prompts import prompt_Agent_Auditor
# ────────────────────────────────────────────────────────
# 1) bootstrap paths + env + llm
# ────────────────────────────────────────────────────────
logging.getLogger('adk').setLevel(logging.DEBUG)

THIS_DIR     = Path(__file__).resolve()
PROJECT_ROOT = THIS_DIR.parent.parent.parent

load_dotenv(PROJECT_ROOT / "config/.env")  # expects OCI_ vars in .env

# Set up the OCI GenAI Agents endpoint configuration
OCI_CONFIG_FILE = os.getenv("OCI_CONFIG_FILE")
OCI_PROFILE = os.getenv("OCI_PROFILE")
AGENT_EP_ID = os.getenv("AGENT_EP_ID")
AGENT_SERVICE_EP = os.getenv("AGENT_SERVICE_EP")
TAX_AGENT_KB_ME_ID = os.getenv("TAX_AGENT_KB_ME_ID")
TAX_AGENT_KB_BUS_ID = os.getenv("TAX_AGENT_KB_BUS_ID")
AGENT_REGION = os.getenv("AGENT_REGION")


# ────────────────────────────────────────────────────────
# 2) Logic
# ────────────────────────────────────────────────────────
def agent_flow():

    client = AgentClient(
        auth_type="api_key",
        config=OCI_CONFIG_FILE,
        profile=OCI_PROFILE,
        region=AGENT_REGION
    )

    # instructions = prompt_Agent_Auditor # Assign the right topic
    instructions = "You are an agent that retrieves answers from the policy documents and flight data. Also try to get answers from the policy document" # Assign the right topic
    custom_instructions = (f"Use the tools to execute RAG search")
    # custom_instructions = (
    #     f"response with not more than 10 words. Hide any PHI information from sending back to the user")

    agent = Agent(
        client=client,
        agent_endpoint_id=AGENT_EP_ID,
        instructions=instructions,
        tools=[
            AgenticRagTool(knowledge_base_ids=[TAX_AGENT_KB_ME_ID], description=custom_instructions),
        ]
    )

    return agent


def setup_agent():

    agent = agent_flow()
    agent.setup()

    # This is a context your existing code is best at producing (e.g., fetching the authenticated user id)
    client_provided_context = "[Context: The logged in user ID is: user_123] "

    # Call the RAG Service
    input = "“give me policies on terms and conditions”"
    response = agent.run(input)
    final_message = response.data["message"]["content"]["text"]
    print(final_message)
 
    # Print Response Traces
    response.pretty_print_traces()

if __name__ == "__main__":
    setup_agent()