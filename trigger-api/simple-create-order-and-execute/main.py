import os
import requests
import base58
import base64

from dotenv import load_dotenv
from solders.solders import Keypair, VersionedTransaction

# Load .env file and read environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

if not PRIVATE_KEY:
    print("Error: PRIVATE_KEY must be set in your .env file")
    exit()

# Create a keypair wallet from your private key
private_key_bytes = base58.b58decode(PRIVATE_KEY)
wallet = Keypair.from_bytes(private_key_bytes)

# Create an order to swap WSOL (Wrapped SOL) to USDC tokens
order_request = {
    "inputMint": "So11111111111111111111111111111111111111112",  # WSOL
    "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "maker": str(wallet.pubkey()),
    "payer": str(wallet.pubkey()),
    "params": {
        "makingAmount": "100000000",  # 0.1 WSOL
        "takingAmount": "100000000",  # 100 USDC
    }
}

order_response = requests.post("https://api.jup.ag/trigger/v1/createOrder", json=order_request)

if order_response.status_code != 200:
    print(f"Error creating order: {order_response.json()}")
    exit()

order_data = order_response.json()

print("Create order response:", order_data)

# Get Raw Transaction
swap_transaction_base64 = order_data["transaction"]
swap_transaction_bytes = base64.b64decode(swap_transaction_base64)
raw_transaction = VersionedTransaction.from_bytes(swap_transaction_bytes)

# Sign Transaction
account_keys = raw_transaction.message.account_keys
wallet_index = account_keys.index(wallet.pubkey())

signers = list(raw_transaction.signatures)
signers[wallet_index] = wallet

signed_transaction = VersionedTransaction(raw_transaction.message, signers)
serialized_signed_transaction = base64.b64encode(bytes(signed_transaction)).decode("utf-8")

# Execute the order transaction
execute_request = {
    "signedTransaction": serialized_signed_transaction,
    "requestId": order_data["requestId"],
}

execute_response = requests.post("https://api.jup.ag/trigger/v1/execute", json=execute_request)

if execute_response.status_code == 200:
    execute_response = execute_response.json()
    signature = execute_response["signature"]

    if execute_response["status"] == "Success":
        print(f"Transaction sent successfully! Signature: {signature}")
        print(f"View transaction on Solscan: https://solscan.io/tx/{signature}")
    else:
        print("Transaction failed! Signature: {signature}")
        print(f"View transaction on Solscan: https://solscan.io/tx/{signature}")
else:
    print(f"Error executing order: {execute_response.json()}")
