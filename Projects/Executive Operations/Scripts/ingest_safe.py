# ingest_safe.py 
# This script ingests a Safe address, its owners, assets, transactions and transfers into the graph.

import sys
import os
import requests
from dotenv import load_dotenv
from neo4j import GraphDatabase
import logging
import argparse

# Add the parent directory of 'Projects' to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Add the Tools directory to the Python path
tools_dir = os.path.abspath(os.path.join(project_root, 'Tools'))
sys.path.insert(0, tools_dir)

try:
    from Tools.get_safe_data import get_safe_data
except ImportError as e:
    print(f"Error importing get_safe_data: {e}")
    sys.exit(1)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
ETHERSCAN_API_URL = 'https://api.etherscan.io/api'

# Add these lines to define Neo4j connection variables
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# Default address (replace with your default Safe address)
DEFAULT_ADDRESS = '0xFFe1bcF92156f50c78F0B6dE4B5fAa3fAA6AdB52'

class SafeIngester:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def ingest_safe(self, safe_address):
        with self.driver.session() as session:
            safe_data = get_safe_data(safe_address)
            
            if not safe_data:
                logging.error(f"Failed to fetch data for Safe address: {safe_address}")
                return

            self.ingest_main_safe_node(session, safe_data)
            self.ingest_multisig_owners(session, safe_address, safe_data['owners'])
            self.ingest_transactions(session, safe_address, safe_data['transactions'])

    def ingest_main_safe_node(self, session, safe_data):
        query = """
        MERGE (s:Address:Safe {address: $address})
        SET s.threshold = $threshold,
            s.owners = $owners
        """
        session.run(query, address=safe_data['address'], threshold=safe_data['threshold'], owners=safe_data['owners'])

    def ingest_multisig_owners(self, session, safe_address, owners):
        query = """
        MATCH (s:Safe {address: $safe_address})
        UNWIND $owners as owner
        MERGE (o:Address {address: owner})
        MERGE (s)-[:HAS_SIGNER]->(o)
        """
        session.run(query, safe_address=safe_address, owners=owners)

    def ingest_transactions(self, session, safe_address, transactions):
        for tx in transactions:
            self.ingest_transaction(session, safe_address, tx)

    def ingest_transaction(self, session, safe_address, tx):
        query = """
        MATCH (s:Safe {address: $safe_address})
        MERGE (t:Transaction {txHash: $txHash})
        SET t.submissionDate = $submissionDate,
            t.executionDate = $executionDate,
            t.transactionHash = $transactionHash,
            t.safeTxHash = $safeTxHash,
            t.nonce = $nonce,
            t.isExecuted = $isExecuted,
            t.isSuccessful = $isSuccessful,
            t.ethGasPrice = $ethGasPrice,
            t.maxFeePerGas = $maxFeePerGas,
            t.maxPriorityFeePerGas = $maxPriorityFeePerGas,
            t.gasUsed = $gasUsed,
            t.fee = $fee,
            t.origin = $origin,
            t.method = $method
        MERGE (s)-[:HAS_TRANSACTION]->(t)
        """
        # Extract the method from dataDecoded if it exists
        data_decoded = tx.get('dataDecoded', {})
        method = data_decoded.get('method') if isinstance(data_decoded, dict) else None

        # Use safeTxHash if available, otherwise use transactionHash
        tx_hash = tx.get('safeTxHash') or tx.get('transactionHash')
        if not tx_hash:
            logging.warning(f"Transaction without hash encountered: {tx}")
            return

        # Check if the transaction already exists
        check_query = """
        MATCH (t:Transaction {txHash: $txHash})
        RETURN COUNT(t) as count
        """
        result = session.run(check_query, txHash=tx_hash).single()
        if result and result['count'] > 0:
            logging.warning(f"Transaction {tx_hash} already exists in the database.")
            return

        session.run(query, 
                    safe_address=safe_address,
                    txHash=tx_hash,
                    safeTxHash=tx.get('safeTxHash'),
                    transactionHash=tx.get('transactionHash'),
                    submissionDate=tx.get('submissionDate'),
                    executionDate=tx.get('executionDate'),
                    nonce=tx.get('nonce'),
                    isExecuted=tx.get('isExecuted'),
                    isSuccessful=tx.get('isSuccessful'),
                    ethGasPrice=tx.get('ethGasPrice'),
                    maxFeePerGas=tx.get('maxFeePerGas'),
                    maxPriorityFeePerGas=tx.get('maxPriorityFeePerGas'),
                    gasUsed=tx.get('gasUsed'),
                    fee=tx.get('fee'),
                    origin=tx.get('origin'),
                    method=method)

        for transfer in tx.get('transfers', []):
            self.ingest_transfer(session, tx_hash, transfer)

    def ingest_transfer(self, session, tx_hash, transfer):
        query = """
        MATCH (t:Transaction {txHash: $tx_hash})
        MERGE (tr:Transfer {transactionHash: $transactionHash})
        SET tr.type = $type,
            tr.value = $value,
            tr.tokenSymbol = $tokenSymbol,
            tr.tokenDecimals = $tokenDecimals
        MERGE (t)-[:HAS_TRANSFER]->(tr)
        """
        token_info = transfer.get('tokenInfo') or {}
        session.run(query,
                    tx_hash=tx_hash,
                    transactionHash=transfer['transactionHash'],
                    type=transfer['type'],
                    value=transfer['value'],
                    tokenSymbol=token_info.get('symbol'),
                    tokenDecimals=token_info.get('decimals'))

        # Create relationships only if the addresses are not null
        if transfer.get('from'):
            query_from = """
            MATCH (tr:Transfer {transactionHash: $transactionHash})
            MERGE (from:Address {address: $from_address})
            MERGE (tr)-[:IS_FROM]->(from)
            """
            session.run(query_from, transactionHash=transfer['transactionHash'], from_address=transfer['from'])

        if transfer.get('to'):
            query_to = """
            MATCH (tr:Transfer {transactionHash: $transactionHash})
            MERGE (to:Address {address: $to_address})
            MERGE (tr)-[:SENT_TO]->(to)
            """
            session.run(query_to, transactionHash=transfer['transactionHash'], to_address=transfer['to'])

        # Remove the proposer relationship as it's not part of the transfer data

def main():
    parser = argparse.ArgumentParser(description="Ingest Safe data into Neo4j.")
    parser.add_argument('--safe', help='Safe address to ingest.')
    args = parser.parse_args()

    safe_address = args.safe or DEFAULT_ADDRESS

    ingester = SafeIngester()
    try:
        ingester.ingest_safe(safe_address)
    finally:
        ingester.close()

if __name__ == '__main__':
    main()
