from dotenv import load_dotenv
from jup_ag_sdk.clients.swap_api_client import SwapApiClient
from jup_ag_sdk.models.swap_api.quote_request_model import QuoteRequest
from jup_ag_sdk.models.swap_api.swap_request_model import SwapRequest

load_dotenv()
client = SwapApiClient()

quote_request = QuoteRequest(
    input_mint="So11111111111111111111111111111111111111112",  # WSOL
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    amount=10000000,  # 0.01 WSOL
)

try:
    quote_response = client.quote(quote_request)
    print("Quote response:", quote_response)

    swap_request = SwapRequest(
        user_public_key=client._get_public_key(),
        quote_response=quote_response,
    )

    rpc_response = client.swap_and_execute(swap_request)
    signature = str(rpc_response.value)
    assert signature is not None, "Transaction signature is missing or invalid."
    print(f"Transaction sent successfully! View transaction on Solscan: https://solscan.io/tx/{signature}")
except Exception as e:
    print("Error occurred while processing the swap:", str(e))
finally:
    client.close()