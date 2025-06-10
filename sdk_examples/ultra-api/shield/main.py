from jup_python_sdk.clients.ultra_api_client import UltraApiClient

client = UltraApiClient()

# WSOL and USDC mints
wsol_mint = "So11111111111111111111111111111111111111112"
usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

try:
    shield_response = client.shield(mints=[wsol_mint, usdc_mint])

    print("Shield API Response:")
    if shield_response["warnings"]:
        for mint, warnings in shield_response["warnings"].items():
            print(f"Mint: {mint}")
            for warning in warnings:
                print(f"  - Type: {warning.get('type')}")
                print(f"    Message: {warning.get('message')}")
    else:
        print("No warnings returned for provided mints")

except Exception as e:
    print("Error occurred while fetching shield information:", str(e))
finally:
    client.close()
