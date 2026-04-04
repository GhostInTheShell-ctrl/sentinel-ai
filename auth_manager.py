import time
from rich.console import Console
from rich.panel import Panel

console = Console()

def get_vault_token(connection_name: str, high_stakes: bool = False, context: str = ""):
    """
    Retrieves short-lived tokens from Auth0 Vault.
    Triggers CIBA step-up for high-stakes actions.
    """
    if not high_stakes:
        console.print(f"[bold green]🔐 Auth0 Vault:[/bold green] Retrieved standard '{connection_name}' token.")
        return f"sk_live_std_{connection_name}_token"

    # --- CIBA INTERCEPT PROTOCOL ---
    console.print("\n")
    console.print(Panel.fit(
        f"[bold red]🚨 AUTH0 GUARDIAN CIBA INTERCEPT[/bold red]\n"
        f"Action: High-Stakes {connection_name.upper()} Write\n"
        f"Context: {context}",
        border_style="red"
    ))
    
    with console.status("[bold cyan]📲 Awaiting biometric approval on Admin's Auth0 Guardian device...", spinner="earth"):
        # Real-world: This polls the Auth0 /oauth/token endpoint for the CIBA grant
        # For the hackathon demo, we simulate the 5-second wait while you tap your phone
        time.sleep(5) 
        
    console.print("[bold green][✅] Admin Approved. Privilege escalated. Token released to Sentinel.[/bold green]\n")
    return f"sk_live_critical_{connection_name}_token"