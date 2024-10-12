import os
import requests
from dotenv import load_dotenv

load_dotenv()

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
ETHERSCAN_API_URL = 'https://api.etherscan.io/api'
# Get transaction data from etherscan
def get_transaction_data(tx_hash):
    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionByHash',
        'txhash': tx_hash,
        'apikey': ETHERSCAN_API_KEY
    }
    response = requests.get(ETHERSCAN_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Add this line at the end of the file
__all__ = ['get_transaction_data']
