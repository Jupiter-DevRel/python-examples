import os
import requests
import base58
import base64

from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Load .env file and read environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")

if not PRIVATE_KEY or not RPC_URL:
    print("Error: PRIVATE_KEY and RPC_URL must be set in your .env file")
    exit()


# Create a keypair wallet from the private key in the .env file
private_key_bytes = base58.b58decode(PRIVATE_KEY)
wallet = Keypair.from_bytes(private_key_bytes)

# Build Quote: Fetch a quote to swap WSOL (Wrapped SOL) to USDC tokens
quote_params = {
    "inputMint": "So11111111111111111111111111111111111111112",  # WSOL
    "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "amount": 10000000,  # 0.01 WSOL
}

quote_response = requests.get("https://api.jup.ag/swap/v1/quote", params=quote_params)

if quote_response.status_code != 200:
    print(f"Error fetching quote: {quote_response.json()}")
    exit()

quote_data = quote_response.json()

print("Quote response:", quote_data)

# Building Swap
swap_request = {
    "userPublicKey": str(wallet.pubkey()),
    "quoteResponse": quote_data,
}

swap_response = requests.post("https://api.jup.ag/swap/v1/swap", json=swap_request)

if swap_response.status_code != 200:
    print(f"Error performing swap: {swap_response.json()}")
    exit()

swap_data = swap_response.json()

print("Swap response:", swap_data)

# Get Raw Transaction
swap_transaction_base64 = swap_data["swapTransaction"]
swap_transaction_bytes = base64.b64decode(swap_transaction_base64)
raw_transaction = VersionedTransaction.from_bytes(swap_transaction_bytes)

# Sign Transaction
account_keys = raw_transaction.message.account_keys
wallet_index = account_keys.index(wallet.pubkey())

signers = list(raw_transaction.signatures)
signers[wallet_index] = wallet

raw_signed_transaction = VersionedTransaction(raw_transaction.message, signers)
signed_transaction = base64.b64encode(bytes(raw_signed_transaction)).decode("utf-8")

# Send transaction to an RPC
rpc_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "sendTransaction",
    "params": [
        signed_transaction,
        {"encoding": "base64"},
    ],
}

rpc_response = requests.post(RPC_URL, json=rpc_request)
rpc_data = rpc_response.json()

print("RPC Response Status:", rpc_response.status_code)
print("RPC Response:", rpc_data)
print(f"View transaction on Solscan: https://solscan.io/tx/{rpc_data['result']}")
