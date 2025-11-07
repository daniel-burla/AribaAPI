# Ariba API Authentication Client

A Python client for authenticating with SAP Ariba API and obtaining OAuth bearer tokens using Basic Authentication.

## Features

- OAuth 2.0 client credentials authentication with Basic Auth
- Automatic token caching and refresh
- Environment variable configuration
- Token expiration management
- Clean and simple API

## Prerequisites

- Python 3.7+
- Ariba API credentials (username and password)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd AribaAPI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your credentials:
```bash
cp .env.example .env
# Edit .env with your actual Ariba API credentials
```

## Configuration

Create a `.env` file in the project root with your Ariba API credentials:

```env
ARIBA_USERNAME=your_username_here
ARIBA_PASSWORD=your_password_here
```

## Usage

### Quick Start

Run the example script:

```bash
python ariba_auth.py
```

### Using in Your Code

```python
from ariba_auth import AribaAuthClient

# Initialize the client (reads from .env file)
client = AribaAuthClient()

# Get bearer token
token = client.get_bearer_token()
print(f"Bearer Token: {token}")

# Use the token in API requests
import requests
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
response = requests.get('https://api.ariba.com/api/endpoint', headers=headers)
```

### Advanced Usage

```python
from ariba_auth import AribaAuthClient

# Initialize with explicit credentials
client = AribaAuthClient(
    username='your_username',
    password='your_password'
)

# Get token (cached if still valid)
token = client.get_bearer_token()

# Force refresh token
new_token = client.get_bearer_token(force_refresh=True)

# Check token status
token_info = client.get_token_info()
print(f"Token valid: {token_info['is_valid']}")
print(f"Expires in: {token_info['expires_in']} seconds")

# Clear cached token
client.clear_token()
```

## API Reference

### AribaAuthClient

#### `__init__(username, password, base_url)`

Initialize the authentication client.

**Parameters:**
- `username` (str, optional): Ariba API username. Defaults to `ARIBA_USERNAME` env var.
- `password` (str, optional): Ariba API password. Defaults to `ARIBA_PASSWORD` env var.
- `base_url` (str, optional): Base URL for Ariba API. Defaults to `https://api.ariba.com`

#### `get_bearer_token(force_refresh=False)`

Get a valid bearer token.

**Parameters:**
- `force_refresh` (bool): Force fetching a new token even if cached token is valid.

**Returns:** Bearer token string

#### `get_token_info()`

Get information about the current token.

**Returns:** Dictionary with token information:
- `has_token`: Whether a token is cached
- `is_valid`: Whether the cached token is valid
- `expires_at`: Expiration timestamp
- `expires_in`: Seconds until expiration

#### `clear_token()`

Clear the cached token.

## OAuth Endpoint

This client uses the Ariba OAuth 2.0 endpoint:
```
https://api.ariba.com/v2/oauth/token
```

The authentication follows the OAuth 2.0 client credentials flow with Basic Authentication. The username and password are BASE64 encoded and sent in the Authorization header.

## Error Handling

The client raises exceptions for authentication failures:

```python
try:
    client = AribaAuthClient()
    token = client.get_bearer_token()
except ValueError as e:
    print(f"Configuration error: {e}")
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
```

## Security

- Never commit your `.env` file or expose your credentials
- The `.gitignore` file is configured to exclude `.env`
- Store credentials securely using environment variables or secret management systems
- Tokens are cached in memory only and not persisted to disk

## License

MIT License

## Support

For issues related to Ariba API credentials or API access, contact SAP Ariba support.
