import os
import json
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# We use LlamaIndex ONLY for the stable LLM connection.
# We are bypassing their broken Agent classes entirely!
from llama_index.llms.google_genai import GoogleGenAI

# Import your real tools
from tools import notify_slack, quarantine_branch, analyze_blast_radius, execute_github_rollback

load_dotenv()
console = Console()

# 1. Map our tools so the custom engine can call them securely
tool_map = {
    "quarantine_branch": quarantine_branch,
    "notify_slack": notify_slack,
    "analyze_blast_radius": analyze_blast_radius,
    "execute_github_rollback": execute_github_rollback
}

# 2. Initialize the Brain: Gemini 2.5 Flash
llm = GoogleGenAI(
    model="gemini-2.5-flash", 
    api_key=os.getenv("GEMINI_API_KEY")
)

def run_sentinel_core(incident_text: str):
    """Our Custom Zero-Trust Execution Engine."""
    
    system_prompt = """
    You are Sentinel, a Zero-Trust Autonomous SRE.
    You must resolve the incident by deciding which tool to call next based on the history.
    
    Available Tools:
    - quarantine_branch(repo_name="auth-service-demo")
    - notify_slack(message="...")
    - analyze_blast_radius(repo_name="auth-service-demo", commit_hash="a1b2c3d4")
    - execute_github_rollback(repo_name="auth-service-demo", commit_hash="a1b2c3d4", risk_summary="...")

    Security Protocol Order:
    1. Quarantine
    2. Notify
    3. Analyze
    4. Rollback (Using the analysis output as the risk_summary)

    Output ONLY a valid JSON object representing your next move. No markdown formatting.
    {
        "thought": "your reasoning for this step",
        "tool_name": "name of the tool to call",
        "args": {"arg_name": "arg_value"}
    }
    
    If all 4 steps are complete, output:
    {
        "thought": "Incident completely resolved.",
        "tool_name": "DONE",
        "args": {}
    }
    """
    
    # The memory context for the AI
    history = f"INCIDENT DETECTED: {incident_text}\n"
    
    for step in range(5):  # Max 5 iterations to prevent infinite loops
        # 1. Ask Gemini for the next move
        prompt = f"{system_prompt}\n\nCURRENT HISTORY:\n{history}\n\nNEXT ACTION JSON:"
        response = llm.complete(prompt).text.strip()
        
        # Strip markdown if Gemini tries to be helpful
        if response.startswith("```json"):
            response = response[7:-3].strip()
        elif response.startswith("```"):
            response = response[3:-3].strip()
            
        try:
            decision = json.loads(response)
        except json.JSONDecodeError:
            console.print(f"[bold red]AI Communication Error:[/bold red] Invalid JSON received.\n{response}")
            break
            
        thought = decision.get("thought", "")
        tool_name = decision.get("tool_name", "")
        args = decision.get("args", {})
        
        console.print(f"[bold magenta]Thought:[/bold magenta] {thought}")
        
        if tool_name == "DONE":
            break
            
        console.print(f"[bold yellow]Action:[/bold yellow] Executing {tool_name}...")
        
        # 2. Execute the chosen tool
        if tool_name in tool_map:
            try:
                # This unpacks the arguments and runs the function in tools.py
                tool_result = tool_map[tool_name](**args)
                console.print(f"[bold cyan]Observation:[/bold cyan] {tool_result}\n")
                
                # Add the result to history so Gemini knows what happened
                history += f"Action executed: {tool_name}\nObservation: {tool_result}\n"
            except Exception as e:
                console.print(f"[bold red]Execution Failed:[/bold red] {e}\n")
                history += f"Action {tool_name} failed: {e}\n"
        else:
            console.print(f"[bold red]Security Block:[/bold red] Unknown tool requested '{tool_name}'\n")
            history += f"Action blocked: Tool '{tool_name}' does not exist.\n"

if __name__ == "__main__":
    console.clear()
    console.print(Panel.fit(
        "SENTINEL-AI: ZERO-TRUST AUTONOMOUS SRE\n[Engine: Custom Sentinel Core] [Brain: Gemini 2.5 Flash]", 
        style="bold green"
    ))

    incident_report = (
        "CRITICAL: Latency spike in 'auth-service-demo' repo on branch 'main'. "
        "The bad commit is 'a1b2c3d4'. Solve the incident immediately."
    )

    console.print(f"[bold red]>>> INCOMING ALERT:[/bold red] {incident_report}\n")
    
    # Start the custom engine
    run_sentinel_core(incident_report)
    
    console.print("\n" + "="*50)
    console.print("[bold green]INCIDENT RESOLVED. RETURNING TO STANDBY.[/bold green]")