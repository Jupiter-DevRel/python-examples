import os
import requests
import base58
import base64

from dotenv import load_dotenv
from requests import JSONDecodeError
from solders.solders import Keypair, VersionedTransaction

# Load .env file and read environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
API_KEY = os.getenv("API_KEY")

# Free tier users should use lite-api.jup.ag. api.jup.ag is for paid plans and requires an API key
API_BASE_URL = "https://api.jup.ag" if API_KEY else "https://lite-api.jup.ag"

# Set up headers for API requests (include x-api-key if API_KEY is available)
headers = {"x-api-key": API_KEY} if API_KEY else {}

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

order_endpoint = f"{API_BASE_URL}/trigger/v1/createOrder"
order_response = requests.post(order_endpoint, json=order_request)

if order_response.status_code != 200:
    try:
        print(f"Error creating order: {order_response.json()}")
    except JSONDecodeError as e:
        print(f"Error creating order: {order_response.json()}")
    finally:
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

execute_endpoint = f"{API_BASE_URL}/trigger/v1/execute"
execute_response = requests.post(execute_endpoint, json=execute_request)

if execute_response.status_code == 200:
    error_data = execute_response.json()
    signature = error_data["signature"]

    if error_data["status"] == "Success":
        print(f"Transaction sent successfully! Signature: {signature}")
        print(f"View transaction on Solscan: https://solscan.io/tx/{signature}")
    else:
        print(f"Transaction failed! Signature: {signature}")
        print(f"View transaction on Solscan: https://solscan.io/tx/{signature}")
else:
    error_data = execute_response.json()
    signature = error_data["signature"]
    error_code = error_data["code"]
    error_message = error_data["error"]

    print(f"Transaction failed! Signature: {signature}")
    print(f"Custom Program Error Code: {error_code}")
    print(f"Message: {error_message}")
    print(f"View transaction on Solscan: https://solscan.io/tx/{signature}")
