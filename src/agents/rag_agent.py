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
AGENT_REGION = os.getenv("AGENT_REGION")
AGENT_SERVICE_EP = os.getenv("AGENT_SERVICE_EP")
RAG_AGENT_EP_ID = os.getenv("RAG_AGENT_EP_ID")
RAG_AGENT_KB_TERMS_AND_CONDITIONS = os.getenv("RAG_AGENT_KB_TERMS_AND_CONDITIONS")


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
    instructions = (f"You are an agent that retrieves answers from the policy documents. " 
                    f"Also try to answer the question the policy documents only") # Assign the right topic
    custom_instructions = (f"Use the tools to execute RAG search")
    
    agent = Agent(
        client=client,
        agent_endpoint_id=RAG_AGENT_EP_ID,
        instructions=instructions,
        tools=[
            AgenticRagTool(knowledge_base_ids=[RAG_AGENT_KB_TERMS_AND_CONDITIONS], description=custom_instructions),
        ]
    )

    return agent

# NEW function that can be imported by the workflow
def run_rag_query(query: str) -> str:
    """
    Initializes and runs the RAG agent for a given query.
    """
    agent = agent_flow()
    agent.setup()
    response = agent.run(query)
    # Assuming the response structure is consistent
    final_message = response.data["message"]["content"]["text"]
    return final_message

# MODIFIED main block for standalone testing
if __name__ == "__main__":
    # This part now calls the new function
    test_query = "give me policies on terms and conditions"
    print("--- Testing RAG Agent ---")
    response_text = run_rag_query(test_query)
    print("\n--- RAG Agent Response ---")
    print(response_text)