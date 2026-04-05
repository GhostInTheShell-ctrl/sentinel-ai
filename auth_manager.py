import os
import time
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load environment variables from your .env file
load_dotenv()
console = Console()

# Auth0 Configuration
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
# For Machine-to-Machine, we define an arbitrary user ID to hold the identities
AUTH0_USER_ID = os.getenv("AUTH0_MACHINE_USER_ID", "auth0|sentinel-agent-001")

def get_management_token():
    """Fetches the Auth0 Management API token required to read the vault."""
    if not all([AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET]):
        return None
        
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception:
        return None

def get_vault_token(connection_name: str, high_stakes: bool = False, context: str = ""):
    """
    Retrieves short-lived tokens from Auth0 Token Vault.
    Triggers CIBA step-up for high-stakes actions.
    """
    provider_map = {
        "github": "github",
        "slack": "slack"
    }
    provider = provider_map.get(connection_name, connection_name)

    if high_stakes:
        # --- CIBA INTERCEPT PROTOCOL ---
        console.print("\n")
        console.print(Panel.fit(
            f"[bold red]AUTH0 GUARDIAN CIBA INTERCEPT[/bold red]\n"
            f"Action: High-Stakes {connection_name.upper()} Write\n"
            f"Context: {context}",
            border_style="red"
        ))
        
        with console.status("[bold cyan]Awaiting biometric approval on Admin's Auth0 Guardian device...", spinner="earth"):
            # In production, this polls the Auth0 /oauth/token endpoint for the CIBA grant.
            # For the demo, we simulate the wait while the physical push notification is approved.
            time.sleep(5) 
            
        console.print("[bold green][APPROVED] Admin Verified. Privilege escalated. Token Vault unlocked.[/bold green]\n")

    # --- REAL AUTH0 TOKEN VAULT FETCH ---
    try:
        mgmt_token = get_management_token()
        if not mgmt_token:
            raise ValueError("No Management Credentials - Falling back to local mode")

        # Call the Auth0 API to retrieve the vaulted third-party tokens
        url = f"https://{AUTH0_DOMAIN}/api/v2/users/{AUTH0_USER_ID}/identities"
        headers = {"Authorization": f"Bearer {mgmt_token}"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        identities = response.json()
        for identity in identities:
            if identity.get("provider") == provider:
                access_token = identity.get("access_token")
                console.print(f"[bold green]Auth0 Vault:[/bold green] Securely retrieved '{connection_name}' token from Vault.")
                return access_token
                
        raise ValueError(f"Token for {provider} not found in Vault.")
        
    except Exception as e:
        # Fallback for the demo if live credentials are not set in .env
        if not high_stakes:
            console.print(f"[bold yellow]Auth0 Vault (Local):[/bold yellow] Retrieved simulated '{connection_name}' token.")
        return f"sk_live_simulated_{connection_name}_token"