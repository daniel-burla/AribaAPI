"""
Ariba API OAuth Authentication Client
This module handles authentication with Ariba API and retrieves bearer tokens.
"""

import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import time
import base64


class AribaAuthClient:
    """Client for handling Ariba API OAuth authentication using Basic Auth."""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: str = "https://api.ariba.com"
    ):
        """
        Initialize the Ariba Authentication Client.

        Args:
            username: Ariba API username. If not provided, reads from ARIBA_USERNAME env var.
            password: Ariba API password. If not provided, reads from ARIBA_PASSWORD env var.
            base_url: Base URL for Ariba API. Defaults to https://api.ariba.com
        """
        # Load environment variables
        load_dotenv()

        self.username = username or os.getenv('ARIBA_USERNAME')
        self.password = password or os.getenv('ARIBA_PASSWORD')
        self.base_url = base_url
        self.token_url = f"{base_url}/v2/oauth/token"

        # Token storage
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

        # Validate required credentials
        if not self.username:
            raise ValueError("Username is required. Set ARIBA_USERNAME environment variable or pass username parameter.")
        if not self.password:
            raise ValueError("Password is required. Set ARIBA_PASSWORD environment variable or pass password parameter.")

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
        Fetch a new bearer token from Ariba API using Basic Authentication.

        Returns:
            Bearer token string

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        # Prepare request payload with grant_type
        payload = {
            'grant_type': 'client_credentials'
        }

        # Create Basic Auth header (BASE64 encoded username:password)
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded_credentials}'
        }

        try:
            print(f"Requesting bearer token from {self.token_url}...")
            print(f"Using Basic Auth with username: {self.username}")

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
