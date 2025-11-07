"""
Ariba API OAuth Authentication Client
This module handles authentication with Ariba API and retrieves bearer tokens.
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import time


class AribaAuthClient:
    """Client for handling Ariba API OAuth authentication."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        client_secret: Optional[str] = None,
        realm: Optional[str] = None,
        base_url: str = "https://api.ariba.com"
    ):
        """
        Initialize the Ariba Authentication Client.

        Args:
            api_key: Ariba API key (client_id). If not provided, reads from ARIBA_API_KEY env var.
            client_secret: Ariba client secret. If not provided, reads from ARIBA_CLIENT_SECRET env var.
            realm: Ariba realm. If not provided, reads from ARIBA_REALM env var.
            base_url: Base URL for Ariba API. Defaults to https://api.ariba.com
        """
        # Load environment variables
        load_dotenv()

        self.api_key = api_key or os.getenv('ARIBA_API_KEY')
        self.client_secret = client_secret or os.getenv('ARIBA_CLIENT_SECRET')
        self.realm = realm or os.getenv('ARIBA_REALM')
        self.base_url = base_url
        self.token_url = f"{base_url}/v2/oauth/token"

        # Token storage
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

        # Validate required credentials
        if not self.api_key:
            raise ValueError("API key is required. Set ARIBA_API_KEY environment variable or pass api_key parameter.")
        if not self.client_secret:
            raise ValueError("Client secret is required. Set ARIBA_CLIENT_SECRET environment variable or pass client_secret parameter.")

    def get_bearer_token(self, force_refresh: bool = False) -> str:
        """
        Get a valid bearer token. Returns cached token if still valid.

        Args:
            force_refresh: If True, forces fetching a new token even if cached token is valid.

        Returns:
            Bearer token string

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        # Return cached token if valid
        if not force_refresh and self._is_token_valid():
            return self._access_token

        # Fetch new token
        return self._fetch_new_token()

    def _is_token_valid(self) -> bool:
        """Check if the current token is valid and not expired."""
        if not self._access_token or not self._token_expires_at:
            return False

        # Add 60 second buffer before expiration
        return time.time() < (self._token_expires_at - 60)

    def _fetch_new_token(self) -> str:
        """
        Fetch a new bearer token from Ariba API.

        Returns:
            Bearer token string

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        # Prepare request payload
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.api_key,
            'client_secret': self.client_secret
        }

        # Add realm if provided
        if self.realm:
            payload['realm'] = self.realm

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            print(f"Requesting bearer token from {self.token_url}...")
            response = requests.post(
                self.token_url,
                data=payload,
                headers=headers,
                timeout=30
            )

            # Raise exception for bad status codes
            response.raise_for_status()

            # Parse response
            token_data = response.json()

            # Extract token and expiration
            self._access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)  # Default to 1 hour
            self._token_expires_at = time.time() + expires_in

            print(f"✓ Bearer token obtained successfully (expires in {expires_in} seconds)")

            return self._access_token

        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to obtain bearer token: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response status: {e.response.status_code}")
                print(f"  Response body: {e.response.text}")
            raise

    def get_token_info(self) -> Dict[str, any]:
        """
        Get information about the current token.

        Returns:
            Dictionary with token information including:
            - has_token: Whether a token is cached
            - is_valid: Whether the cached token is valid
            - expires_at: Expiration timestamp (if available)
            - expires_in: Seconds until expiration (if available)
        """
        info = {
            'has_token': self._access_token is not None,
            'is_valid': self._is_token_valid(),
            'expires_at': self._token_expires_at,
            'expires_in': None
        }

        if self._token_expires_at:
            info['expires_in'] = max(0, int(self._token_expires_at - time.time()))

        return info

    def clear_token(self):
        """Clear the cached token."""
        self._access_token = None
        self._token_expires_at = None
        print("Token cache cleared")


def main():
    """Example usage of the Ariba Authentication Client."""
    try:
        # Initialize the client
        client = AribaAuthClient()

        # Get bearer token
        token = client.get_bearer_token()

        print("\n" + "="*60)
        print("BEARER TOKEN")
        print("="*60)
        print(f"{token}")
        print("="*60)

        # Display token info
        token_info = client.get_token_info()
        print("\nToken Information:")
        print(f"  Valid: {token_info['is_valid']}")
        print(f"  Expires in: {token_info['expires_in']} seconds")

        # Example: Get token again (should use cached version)
        print("\nGetting token again (should use cache)...")
        token2 = client.get_bearer_token()
        print(f"Same token: {token == token2}")

    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
