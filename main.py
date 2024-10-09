import requests
import time
import logging
import multiprocessing
from datetime import datetime, timedelta
from tqdm import tqdm  # For the progress bar

# Constants
API_URL = 'https://matchscan.io/api'
AIRDROP_CONTRACT_ADDRESS = '0xD5B3BC210352D71f9c7fe7d94cb86FC49B42209a'
TIME_WINDOW_HOURS = 48  # Define 'recently funded' as within the last 48 hours

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed output
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("airdrop_analysis.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_claim_transactions(contract_address):
    """Retrieve all transactions involving the airdrop contract."""
    transactions = []
    page = 1
    offset = 1000  # Number of transactions per page
    logger.info(f"Starting to fetch transactions for contract: {contract_address}")

    with tqdm(desc="Fetching contract transactions", unit="tx") as pbar:
        while True:
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': contract_address,
                'startblock': 0,
                'endblock': 99999999,
                'page': page,
                'offset': offset,
                'sort': 'asc'
            }
            try:
                response = requests.get(API_URL, params=params)
                data = response.json()
                if data['status'] != '1':
                    logger.error(f"Error fetching transactions: {data.get('message', 'Unknown error')}")
                    break
                result = data.get('result', [])
                if not result:
                    logger.info("No more transactions found.")
                    break
                transactions.extend(result)
                pbar.update(len(result))
                if len(result) < offset:
                    logger.info("Reached the last page of transactions.")
                    break  # No more pages
                page += 1
                time.sleep(0.2)  # Sleep to respect API rate limits
            except Exception as e:
                logger.exception(f"Exception occurred while fetching transactions: {e}")
                break
    logger.info(f"Total transactions fetched: {len(transactions)}")
    return transactions

def extract_claimant_addresses(transactions):
    """Extract unique claimant addresses from the transactions."""
    addresses = set(tx['from'].lower() for tx in transactions)
    logger.info(f"Extracted {len(addresses)} unique claimant addresses.")
    return addresses

def analyze_address(args):
    """Analyze an address to determine if it meets the bot criteria."""
    address, contract_address, cutoff_time = args
    # Fetch all transactions for the address
    page = 1
    offset = 1000
    all_transactions = []

    try:
        while True:
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'page': page,
                'offset': offset,
                'sort': 'asc'
            }
            response = requests.get(API_URL, params=params)
            data = response.json()
            if data['status'] != '1':
                logger.error(f"Error fetching data for address {address}: {data.get('message', 'Unknown error')}")
                return False, address
            result = data.get('result', [])
            if not result:
                break
            all_transactions.extend(result)
            if len(result) < offset:
                break
            page += 1
            time.sleep(0.2)
    except Exception as e:
        logger.exception(f"Exception occurred while fetching transactions for address {address}: {e}")
        return False, address

    # Separate incoming and outgoing transactions
    incoming_txs = [tx for tx in all_transactions if tx['to'].lower() == address.lower()]
    outgoing_txs = [tx for tx in all_transactions if tx['from'].lower() == address.lower()]

    # Check if only outgoing transaction is the airdrop claim
    if len(outgoing_txs) != 1:
        logger.debug(f"Address {address}: Has {len(outgoing_txs)} outgoing transactions, not a bot.")
        return False, address  # More than one outgoing transaction

    # Check if the only outgoing transaction is to the airdrop contract
    if outgoing_txs[0]['to'].lower() != contract_address.lower():
        logger.debug(f"Address {address}: Outgoing transaction is not to the airdrop contract.")
        return False, address  # Outgoing transaction to a different address

    # Check if the address was recently funded by another wallet
    if not incoming_txs:
        logger.debug(f"Address {address}: No incoming transactions.")
        return False, address  # No incoming transactions

    # Check if the first incoming transaction was within the cutoff time
    first_incoming_tx = incoming_txs[0]
    funding_time = datetime.utcfromtimestamp(int(first_incoming_tx['timeStamp']))
    if funding_time < cutoff_time:
        logger.debug(f"Address {address}: Funding occurred before cutoff time.")
        return False, address  # Funding occurred before the cutoff time

    logger.info(f"Address {address}: Identified as likely bot.")
    return True, address  # Address meets the criteria

def main():
    contract_address = AIRDROP_CONTRACT_ADDRESS
    logger.info(f"Starting analysis for contract: {contract_address}")
    transactions = get_claim_transactions(contract_address)
    if not transactions:
        logger.warning("No transactions found for the airdrop contract.")
        return
    addresses = extract_claimant_addresses(transactions)
    logger.info(f"Total unique claimants to analyze: {len(addresses)}")

    bot_addresses = []
    total_addresses = len(addresses)
    now = datetime.utcnow()
    cutoff_time = now - timedelta(hours=TIME_WINDOW_HOURS)

    # Prepare arguments for multiprocessing
    args_list = [(address, contract_address, cutoff_time) for address in addresses]

    # Use multiprocessing pool
    pool_size = multiprocessing.cpu_count()
    logger.info(f"Using multiprocessing with pool size: {pool_size}")
    with multiprocessing.Pool(pool_size) as pool:
        results = []
        # Use tqdm progress bar
        for result in tqdm(pool.imap_unordered(analyze_address, args_list), total=total_addresses, desc="Analyzing addresses"):
            is_bot, address = result
            if is_bot:
                bot_addresses.append(address)

    logger.info("Analysis Complete.")
    logger.info(f"Total claimants: {total_addresses}")
    logger.info(f"Likely bots: {len(bot_addresses)}")
    logger.info(f"Percentage of bots: {len(bot_addresses)/total_addresses*100:.2f}%")

    # Optionally, save bot addresses to a file
    with open('bot_addresses.txt', 'w') as f:
        for address in bot_addresses:
            f.write(f"{address}\n")
    logger.info("Bot addresses have been saved to 'bot_addresses.txt'.")

if __name__ == '__main__':
    main()
