"""
Example usage of the Ariba Authentication Client
This script demonstrates various ways to use the AribaAuthClient.
"""

from ariba_auth import AribaAuthClient
import requests


def example_basic_usage():
    """Basic usage example."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)

    try:
        # Initialize client (reads from .env)
        client = AribaAuthClient()

        # Get bearer token
        token = client.get_bearer_token()
        print(f"✓ Token obtained: {token[:20]}...{token[-20:]}")

        # Get token again (uses cache)
        token2 = client.get_bearer_token()
        print(f"✓ Token from cache: Same token = {token == token2}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_token_info():
    """Example showing how to get token information."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Token Information")
    print("=" * 60)

    try:
        client = AribaAuthClient()
        token = client.get_bearer_token()

        # Get token information
        info = client.get_token_info()
        print(f"Has token: {info['has_token']}")
        print(f"Is valid: {info['is_valid']}")
        print(f"Expires in: {info['expires_in']} seconds")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_api_request():
    """Example showing how to use the token in an API request."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Using Token in API Request")
    print("=" * 60)

    try:
        # Get token
        client = AribaAuthClient()
        token = client.get_bearer_token()

        # Prepare headers with bearer token
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        print("✓ Headers prepared with bearer token")
        print(f"  Authorization: Bearer {token[:20]}...")

        # Example: Making an API request (uncomment and adjust endpoint as needed)
        # response = requests.get(
        #     'https://api.ariba.com/api/analytics/v1/prod/...',
        #     headers=headers
        # )
        # print(f"Response status: {response.status_code}")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_explicit_credentials():
    """Example using explicit credentials instead of environment variables."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Explicit Credentials (for reference)")
    print("=" * 60)

    # Note: In production, always use environment variables
    # This is just to show the option exists
    print("Initialize with explicit credentials:")
    print("""
    client = AribaAuthClient(
        username='your_username',
        password='your_password'
    )
    token = client.get_bearer_token()
    """)


def example_force_refresh():
    """Example showing how to force refresh a token."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Force Token Refresh")
    print("=" * 60)

    try:
        client = AribaAuthClient()

        # Get initial token
        token1 = client.get_bearer_token()
        print(f"✓ Initial token: {token1[:20]}...")

        # Force refresh (gets new token even if cached one is valid)
        token2 = client.get_bearer_token(force_refresh=True)
        print(f"✓ Refreshed token: {token2[:20]}...")
        print(f"  Tokens are different: {token1 != token2}")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "ARIBA API AUTHENTICATION EXAMPLES" + " " * 12 + "║")
    print("╚" + "=" * 58 + "╝")

    example_basic_usage()
    example_token_info()
    example_api_request()
    example_explicit_credentials()
    example_force_refresh()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
