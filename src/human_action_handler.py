import sys
import json
import logging
from datetime import datetime

# Configure basic logging to print to the terminal
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - HUMAN ACTION - %(levelname)s - %(message)s'
)

def process_human_action(action, details_json):
    """
    Processes the human action and logs it.
    In a real application, this could trigger other workflows,
    update a database, or call an external API.
    """
    try:
        details = json.loads(details_json)
        logging.info(f"Decision: {action.upper()}")
        logging.info(f"Original Reason: {details.get('reason')}")
        logging.info(f"Dispute Amount: {details.get('dispute_amount')}")
        
        # This is where you would add logic to interact with other systems.
        # For now, we just confirm it was processed.
        print(f"Action '{action}' processed successfully.")

    except json.JSONDecodeError:
        logging.error("Failed to parse details JSON.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        action_arg = sys.argv[1]
        details_arg = sys.argv[2]
        process_human_action(action_arg, details_arg)
    else:
        logging.error("Insufficient arguments. Usage: python human_action_handler.py <action> <details_json>")
        sys.exit(1)