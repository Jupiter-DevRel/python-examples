import os
import requests
import base58
import base64

from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.rpc.core import RPCException
from solders.solders import Keypair, VersionedTransaction, Instruction, Pubkey, AccountMeta, AddressLookupTableAccount, \
    MessageV0

# Load .env file and read environment variables
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")

if not PRIVATE_KEY or not RPC_URL:
    print("Error: PRIVATE_KEY and RPC_URL must be set in your .env file")
    exit()

def deserialize_instruction(instruction):
    return Instruction(
        accounts=[
            AccountMeta(
                is_signer=account["isSigner"],
                is_writable=account["isWritable"],
                pubkey=Pubkey.from_string(account["pubkey"]),
            )
            for account in instruction["accounts"]
        ],
        data=base64.b64decode(instruction["data"]),
        program_id=Pubkey.from_string(instruction["programId"]),
    )

def fetch_alt_accounts(keys):
    alt_accounts = []
    address_lookup_table_accounts = []
    for key in keys:
        address_lookup_table_accounts.append(
            AddressLookupTableAccount(
                key=Pubkey.from_string(key),
                addresses=[
                    Pubkey.from_string(address)
                    for address in rpc.get_account_info_json_parsed(Pubkey.from_string(key)).value.data.parsed["info"]["addresses"]
                ]
            )
        )

    return alt_accounts

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

# Fetch the swap instructions for the quote
swap_instructions_request = {
    "userPublicKey": str(wallet.pubkey()),
    "quoteResponse": quote_data,
}

swap_instructions_response = requests.post("https://api.jup.ag/swap/v1/swap-instructions", json=swap_instructions_request)

if swap_instructions_response.status_code != 200:
    print(f"Error performing swap instructions: {swap_instructions_response.json()}")
    exit()

swap_instructions_data = swap_instructions_response.json()

print("Swap instructions response:", swap_instructions_data)

# Build instructions
instructions = []

# Compute budget Instructions
instructions.extend(
    deserialize_instruction(instr) for instr in swap_instructions_data["computeBudgetInstructions"]
)

# Setup Instructions
instructions.extend(
    deserialize_instruction(instr) for instr in swap_instructions_data["setupInstructions"]
)

# Swap Instructions
instructions.append(deserialize_instruction(swap_instructions_data["swapInstruction"]))

# Cleanup Instructions
cleanup_instruction = swap_instructions_data.get("cleanupInstruction")
if cleanup_instruction:
    instructions.append(deserialize_instruction(cleanup_instruction))

# Get address lookup table accounts
address_lookup_table_accounts = []
if "addressLookupTableAddresses" in swap_instructions_data:
    address_lookup_table_accounts = fetch_alt_accounts(swap_instructions_data["addressLookupTableAddresses"])

# Fetch the latest blockhash
blockhash = rpc.get_latest_blockhash().value.blockhash

# Compile the versioned transaction
raw_transaction = VersionedTransaction(
    message=MessageV0.try_compile(
        wallet.pubkey(),
        instructions,
        address_lookup_table_accounts,
        blockhash,
    ),
    keypairs=[wallet]
)

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