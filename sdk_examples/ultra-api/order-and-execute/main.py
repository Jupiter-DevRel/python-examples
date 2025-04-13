from dotenv import load_dotenv
from jup_ag_sdk.clients.ultra_api_client import UltraApiClient
from jup_ag_sdk.models.ultra_api.ultra_order_request_model import UltraOrderRequest

load_dotenv()
client = UltraApiClient()

order_request = UltraOrderRequest(
    input_mint="So11111111111111111111111111111111111111112",  # WSOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=10000000,  # 0.01 WSOL
    taker=client._get_public_key()
)

try:
    rpc_response = client.order_and_execute(order_request)
    signature = str(rpc_response["signature"])
    assert signature is not None, "Transaction signature is missing or invalid."
    print(f"Transaction sent successfully! View transaction on Solscan: https://solscan.io/tx/{signature}")
except Exception as e:
    print("Error occurred while processing the swap:", str(e))
finally:
    client.close()