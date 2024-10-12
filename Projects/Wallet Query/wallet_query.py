# This function reads a contract through etherscan.io API and returns the the locked value.
# This is the contract 0xCc71C80d803381FD6Ee984FAff408f8501DB1740
# ETHERSCAN_API_KEY is already defined in the .env file

import os
import json
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
INFURA_URL = os.getenv("INFURA_URL")  # Make sure to add this to your .env file

def get_locked_value(contract_address):
    # Etherscan API endpoint
    url = "https://api.etherscan.io/api"
    
    # Parameters for the API request
    params = {
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": ETHERSCAN_API_KEY
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()
    
    if data["status"] == "1":
        # ABI retrieved successfully
        abi = json.loads(data["result"])
        
        # Connect to Ethereum network
        w3 = Web3(Web3.HTTPProvider(INFURA_URL))
        
        # Create contract instance
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Get total supply (locked value)
        total_supply = contract.functions.totalSupply().call()
        
        # Convert from wei to ether
        total_supply_ether = w3.from_wei(total_supply, 'ether')
        
        return f"Total locked value: {total_supply_ether} ETH"
    else:
        return f"Error: {data.get('message', 'Unknown error')}"

# Print API key for debugging (be careful not to share this in public!)
print(f"API Key: {ETHERSCAN_API_KEY}")

# Example usage
contract_address = "0xCc71C80d803381FD6Ee984FAff408f8501DB1740"
result = get_locked_value(contract_address)
print(result)
