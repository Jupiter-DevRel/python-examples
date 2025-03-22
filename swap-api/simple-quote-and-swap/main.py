import os
import requests
import base58
import base64

from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.rpc.core import RPCException
from solders.solders import Keypair, VersionedTransaction

# Load .env file and read environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")

if not PRIVATE_KEY or not RPC_URL:
    print("Error: PRIVATE_KEY and RPC_URL must be set in your .env file")
    exit()

# Initialize the Solana RPC client
rpc = Client(RPC_URL)

# Create a keypair wallet from your private key
private_key_bytes = base58.b58decode(PRIVATE_KEY)
wallet = Keypair.from_bytes(private_key_bytes)

# Fetch a quote to swap WSOL (Wrapped SOL) to USDC tokens
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

# Fetch the swap transaction for the quote
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

signed_transaction = VersionedTransaction(raw_transaction.message, signers)

# Send the signed transaction to the RPC client
try:
    rpc_response = rpc.send_transaction(signed_transaction)

    signature = str(rpc_response.value)
    print(f"Transaction sent successfully! Signature: {signature}")
    print(f"View transaction on Solscan: https://solscan.io/tx/{signature}")
except RPCException as e:
    error_message = e.args[0]
    print("Transaction failed!")
    print(f"Custom Program Error Code: {error_message.data.err.err.code}")
    print(f"Message: {error_message.message}")
