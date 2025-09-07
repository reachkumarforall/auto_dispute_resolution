"""
Author: Malkit Bhasin
Date: 2025-09-06
==========================
==Tax Auditor Assistant==
==========================
This agent is for intration with database

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
DB_AGENT_EP_ID = os.getenv("DB_AGENT_EP_ID")


INLINE_DATABASE_SCHEMA = '''
                        CREATE TABLE "ADMIN"."FLIGHTS"
                        (   "FLIGHT_ID" NUMBER,
                            "AIRLINE" VARCHAR2(4000 BYTE) COLLATE "USING_NLS_COMP",
                            "FROM_LOCATION" VARCHAR2(4000 BYTE) COLLATE "USING_NLS_COMP",
                            "TO_LOCATION" VARCHAR2(4000 BYTE) COLLATE "USING_NLS_COMP",
                            "Date" TIMESTAMP (6),
                            "TIME_DEPARTURE" TIMESTAMP (6),
                            "TIME_ARRIVAL" TIMESTAMP (6),
                            "PRICE" NUMBER
                        )  DEFAULT COLLATION "USING_NLS_COMP" ;
                        '''
 
INLINE_TABLE_COLUMN_DESCRIPTION = '''
                        FLIGHTS table
                        - Each row in this table represents a flight
 
                        Columns:
                        "FLIGHT_ID" - The ID of the flight
                        "AIRLINE" - The airline company of the flight
                       "FROM_LOCATION" - The location where the flight is coming from in format City, Country (AIRPORT). i.e " New York, USA (JFK)"
                        "TO_LOCATION"- The destination of the flight in format City, Country (AIRPORT). i.e " New York, USA (JFK)"
                        "Date" - the date of the flight
                        "TIME_DEPARTURE" - the time the flight departs
                        "TIME_ARRIVAL" - the time the flight arrives
                        "PRICE"- the price of the flight
                         '''




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

    instructions = (f"You are an agent that retrieves answers from the flight data. " # Assign the right topic
                    f"For city use like clause in generated sql " 
                    f"and not use equality for matching. For example: "
                    f"SELECT * FROM FLIGHTS WHERE FROM_LOCATION LIKE 'New York%' AND TO_LOCATION LIKE 'Los Angeles%'")

    custom_instructions = (f"DB contains data about the flights and conenction to the database is already established. "
                           f"When user asks about flight data, generate SQL query to get the data from the database. "
                           f"Use the SQL tool to run the query and get the data.") 
    # Instantiate a SQL Tool
    sql_tool_with_inline_schema = AgenticSqlTool(
        name="Flight SQL Tool - Inline Schema",
        description="A NL2SQL tool that retrieves flight data",
        database_schema=InlineInputLocation(content=INLINE_DATABASE_SCHEMA),
        model_size=ModelSize.LARGE,
        dialect=SqlDialect.ORACLE_SQL,
        db_tool_connection_id="ocid1.databasetoolsconnection.oc1.us-chicago-1.amaaaaaayanwdzaauwk7ghmrkwojxspv2tcodt43geihocpe4yrendkxtyja",
        enable_sql_execution=True,
        enable_self_correction=True,
        # icl_examples=ObjectStorageInputLocation(namespace_name="namespace", bucket_name="bucket", prefix="_sql.icl_examples.txt"),
        table_and_column_description=InlineInputLocation(content=INLINE_TABLE_COLUMN_DESCRIPTION),
        custom_instructions=custom_instructions
    )

    agent = Agent(
        client=client,
        agent_endpoint_id=DB_AGENT_EP_ID,
        instructions=instructions,
        tools=[
            sql_tool_with_inline_schema
        ]
    )

    return agent


def setup_agent():

    agent = agent_flow()
    agent.setup()

    # This is a context your existing code is best at producing (e.g., fetching the authenticated user id)
    client_provided_context = "[Context: The logged in user ID is: user_123] "

    # Run the agent with a user message
    # input = "Find me flights from New York to Los Angeles"
    input = "Find me flights from New York to Los Angeles"
    response = agent.run(input)
    response.pretty_print()
 
    # Print Response Traces
    response.pretty_print_traces()

if __name__ == "__main__":
    setup_agent()