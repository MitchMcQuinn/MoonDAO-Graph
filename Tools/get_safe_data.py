import requests
import logging
import json
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add file handler for logging
def setup_file_logging(address):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"safe_data_{address}_{timestamp}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    return log_filename

def get_safe_data(address):
    """
    Fetches data from the Safe.Global API for a given address, including all transaction data, the signing threshold, owners, and assets.

    Args:
        address (str): The wallet address.

    Returns:
        dict: The JSON response from the API, or None if an error occurs.
    """
    safe_url = f'https://safe-transaction-mainnet.safe.global/api/v1/safes/{address}/'
    transactions_url = f'https://safe-transaction-mainnet.safe.global/api/v1/safes/{address}/all-transactions/'
    assets_url = f'https://safe-transaction-mainnet.safe.global/api/v1/safes/{address}/balances/'
    
    try:
        # Get the safe data
        safe_response = requests.get(safe_url, timeout=10)
        
        # Get all transactions data with pagination
        all_transactions = []
        next_url = transactions_url
        while next_url:
            transactions_response = requests.get(next_url, timeout=10)
            if transactions_response.status_code == 200:
                data = transactions_response.json()
                all_transactions.extend(data['results'])
                next_url = data['next']
                logger.info(f"Fetched {len(data['results'])} more transactions. Total: {len(all_transactions)}")
            else:
                logger.error(f"Failed to fetch transactions. Status: {transactions_response.status_code}")
                break
        
        # Get assets data
        assets_response = requests.get(assets_url, timeout=10)
        
        # Check if the responses are successful
        if safe_response.status_code == 200 and all_transactions and assets_response.status_code == 200:
            safe_data = safe_response.json()
            assets_data = assets_response.json()
            
            # Log the number of transactions and assets
            logger.info(f"Fetched a total of {len(all_transactions)} transactions for Safe {address}")
            logger.info(f"Fetched {len(assets_data)} assets for Safe {address}")
            
            # Log sample data
            logger.info(f"Sample transaction data: {json.dumps(all_transactions[0] if all_transactions else {}, indent=2)}")
            logger.info(f"Sample asset data: {json.dumps(assets_data[0] if assets_data else {}, indent=2)}")
            
            # Extract signing threshold and owners
            threshold = safe_data.get('threshold')
            owners = safe_data.get('owners', [])
            
            logger.info(f"Signing threshold: {threshold}")
            logger.info(f"Number of owners: {len(owners)}")
            
            # Include all transactions, threshold, owners, and assets in the result
            safe_data['transactions'] = all_transactions
            safe_data['threshold'] = threshold
            safe_data['owners'] = owners
            safe_data['assets'] = assets_data
            
            logger.info(f"Processed {len(all_transactions)} transactions and {len(assets_data)} assets for Safe {address}")
            return safe_data
        else:
            # Log the error if the responses are not successful
            logger.error(f"Failed to fetch data. Safe status: {safe_response.status_code}, Transactions fetched: {len(all_transactions)}, Assets status: {assets_response.status_code}")
    except requests.exceptions.RequestException as e:
        # Log the error if there is an exception
        logger.error(f"Error fetching Safe data for {address}: {str(e)}")
    except Exception as e:
        # Log the error if there is an unexpected error
        logger.error(f"Unexpected error processing Safe data for {address}: {str(e)}")
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = "0xFFe1bcF92156f50c78F0B6dE4B5fAa3fAA6AdB52"  # Default address
    
    log_filename = setup_file_logging(address)
    logger.info(f"Logging output to file: {log_filename}")
    
    logger.info(f"Fetching data for Safe address: {address}")
    safe_data = get_safe_data(address)
    
    if safe_data:
        logger.info(f"Successfully fetched data for Safe {address}")
        logger.info(f"Number of transactions: {len(safe_data.get('transactions', []))}")
        
        # Log the complete safe_data to the file
        logger.info(f"Complete Safe data:\n{json.dumps(safe_data, indent=2)}")
    else:
        logger.error(f"Failed to fetch data for Safe {address}")
