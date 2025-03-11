import requests
import base58
import base64

from solders.keypair import Keypair
from solders.solders import NullSigner
from solders.transaction import VersionedTransaction

private_key_base58 = ""
private_key_bytes = base58.b58decode(private_key_base58)

keypair = Keypair.from_bytes(private_key_bytes)
print("Public Key:", keypair.pubkey())

jup_order_api = "https://api.jup.ag/ultra/v1/order"
jup_execute_api = "https://api.jup.ag/ultra/v1/execute"

IN = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
OUT = "So11111111111111111111111111111111111111112"

params = {
    "inputMint": IN,
    "outputMint": OUT,
    "amount": 10000000,
    "taker": str(keypair.pubkey())
}

print("Order request:", jup_order_api, params)
order_response = requests.get(jup_order_api, params=params)
order_data = order_response.json()

print("Order:", order_data)

if not order_data:
    print("Failed to get order!")
    exit()

# Get raw transaction
transaction_base64 = order_data["transaction"]
transaction_buffer = base64.b64decode(transaction_base64)
raw_transaction = VersionedTransaction.from_bytes(transaction_buffer)

print("Signing transaction...")

# Sign transaction
account_keys = raw_transaction.message.account_keys
user_index = account_keys.index(keypair.pubkey())

signers = list(raw_transaction.signatures)
signers[user_index] = keypair
if len(signers) > 1:
    signers[len(signers) - 1 - user_index] = NullSigner(raw_transaction.message.account_keys[0])

signed_tx = VersionedTransaction(raw_transaction.message, signers)
serialized_tx = base64.b64encode(bytes(signed_tx)).decode("utf-8")
print("Transaction Base64 Length:", len(serialized_tx))


print("Sending signed transaction...")



execute_request = {
    "signedTransaction": serialized_tx,
    "requestId": order_data["requestId"]
}

# Send swap request
print("Execute request:", execute_request)
execute_response = requests.post(jup_execute_api, json=execute_request)
execute_data = execute_response.json()

# Print response from RPC
print("Execute response status:", execute_response.status_code)
print("Send Response:", execute_data)
print(f"https://solscan.io/tx/{execute_data['signature']}")
