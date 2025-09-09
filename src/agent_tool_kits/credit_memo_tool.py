import requests
import os
import json
from oci.addons.adk import Toolkit, tool
from pathlib import Path
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP


load_dotenv("./config/.env")  # expects OCI_ vars in .env
# Set up the OCI GenAI Agents endpoint configuration
API_USER = os.getenv("FUSION_API_USER")
API_PASS = os.getenv("FUSION_API_PASS")
API_URL = os.getenv("FUSION_API_URL", "https://fa-edtc-dev80-saasfaprod1.fa.ocs.oraclecloud.com")

class Credit_Memo_Tool(Toolkit):
	"""
	Agent tool for creating Oracle Receivables Credit Memos via REST API.
	"""
	def __init__(self, api_user=API_USER, api_pass=API_PASS, api_url=API_URL):
		super().__init__()

	@tool
	def create_credit_memo(self, payload):
		if not API_USER or not API_PASS:
			raise ValueError("FUSION_API_USER and FUSION_API_PASS must be set in the environment or provided to Credit_Memo_Tool.")
		url = str(API_URL).rstrip("/") + "/fscmRestApi/resources/latest/receivablesCreditMemos"
		headers = {
			"Content-Type": "application/json"
		}
		print("Creating Credit Memo at URL:", url)  # Debug statement
		try:
			response = requests.post(
				url,
				auth=(str(API_USER), str(API_PASS)),
				headers=headers,
				data=json.dumps(payload)
			)
			response.raise_for_status()
			return response.json()
		except requests.RequestException as e:
			return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}

	@tool
	def get_credit_memo(self, customer_transaction_id):
		"""
		Retrieve a credit memo by CustomerTransactionId using Oracle Fusion Receivables API.
		Args:
			customer_transaction_id (str): The CustomerTransactionId to fetch.
		Returns:
			dict: API response.
		"""
		if not API_USER or not API_PASS:
			raise ValueError("FUSION_API_USER and FUSION_API_PASS must be set in the environment or provided to Credit_Memo_Tool.")
		url = str(API_URL).rstrip("/") + f"/fscmRestApi/resources/latest/receivablesCreditMemos/{customer_transaction_id}"
		headers = {
			"Accept": "application/json"
		}
		print("Fetching Credit Memo from URL:", url)  # Debug statement
		try:
			response = requests.get(
				url,
				auth=(str(API_USER), str(API_PASS)),
				headers=headers
			)
			response.raise_for_status()
			return response.json()
		except requests.RequestException as e:
			return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}

# Example payload for credit memo creation
example_payload = {
   "BusinessUnit": "Powered US",
   "TransactionSource": "Manual",
   "TransactionType": "Credit Memo",
   "TransactionDate": "2025-09-09",
   "CreditMemoCurrency": "USD",
   "BillToCustomerName": "Acme Corp",
   "BillToCustomerNumber": "10008",
   "ShipToCustomerName": "Acme Corp",
   "ShipToCustomerNumber": "132009",
   "ShipToCustomerSite": "80008",
   "CreditMemoComments": "Account credit for Service Interruption - 2 Devices",
   "receivablesCreditMemoLines": [
       {
           "LineDescription": "Refund to Customer for item1",
           "LineNumber": 1,
           "LineQuantityCredit": 1,
           "UnitSellingPrice": -50.00
      
       }
     ]
     
}


def test_create_credit_memo():
	tool = Credit_Memo_Tool()
	result = tool.create_credit_memo(example_payload)
	print("Credit Memo API Result:", result)

def test_get_credit_memo():
	tool = Credit_Memo_Tool()
	# Replace with a valid CustomerTransactionId for your environment
	customer_transaction_id = "300000058290502"
	result = tool.get_credit_memo(customer_transaction_id)
	print("Get Credit Memo API Result:", result)

if __name__ == "__main__":
	test_create_credit_memo()
	# Uncomment below to test get_credit_memo
	#test_get_credit_memo()
