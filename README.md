# 🛡️ Sentinel-AI: Zero-Trust Autonomous SRE

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Brain-Gemini_2.5_Flash-orange.svg)](https://deepmind.google/technologies/gemini/)
[![Auth0 Secured](https://img.shields.io/badge/Security-Auth0_CIBA-black.svg)](https://auth0.com/)

**Sentinel-AI** is an autonomous incident response agent built on strict Zero-Trust security principles. It detects latency spikes, quarantines repositories, analyzes the blast radius of bad commits, and requests biometric Admin approval via Auth0 before executing destructive rollbacks.

[👉 Watch the Demo Video Here](#) [https://drive.google.com/file/d/1OTOFnO5vTD9XF4wFb9yc0epL4vpgjAxb/view?usp=sharing]

---

## 🛑 The Problem
Site Reliability Engineers (SREs) are forced into a dangerous trade-off: 
1. Leave production environments open with "standing privileges" so incidents can be fixed quickly (High Security Risk).
2. Lock down environments completely, turning a 5-minute fix into a 45-minute bureaucratic nightmare of hunting down access tokens (High Downtime Risk).

## 💡 The Solution
Sentinel-AI bridges the gap. By utilizing a custom LLM reasoning engine, Sentinel acts as a first responder that can instantly halt damage, but it is strictly gated by **Auth0's Client-Initiated Backchannel Authentication (CIBA)** for any destructive or high-stakes actions.

### 🔒 The "Triple-Lock" Protocol
When a critical incident is triggered, Sentinel autonomously executes this workflow:
1. **Quarantine:** Immediately locks the affected GitHub branch to stop the "bleeding" (Safe Action).
2. **Notify:** Alerts the engineering team via Slack (Safe Action).
3. **Analyze:** Scans the problematic commit to determine the impact radius (Safe Action).
4. **CIBA Intercept & Rollback:** Formulates a risk summary and sends a push notification to the Admin's Auth0 Guardian app. **The AI cannot revert the code until the human provides biometric approval.**

---

## Architecture: The Custom Execution Engine

Many AI agents rely on bloated, generic frameworks that break easily under edge cases. To ensure absolute reliability for critical infrastructure, **we bypassed standard agent frameworks and built a custom Execution Engine.**

* **The Brain:** Google's `gemini-2.5-flash` processes the incident state and outputs deterministic JSON routing decisions.
* **The Engine:** A custom Python loop that safely unpacks AI intentions, maps them to local Python tools, and manages the operational history to prevent hallucination loops.
* **The Vault:** All API calls are brokered through our `auth_manager.py` which issues short-lived, scoped tokens.

---

## ⚙️ Local Setup & Installation

### 1. Clone & Environment Setup
Ensure you have Python 3.12+ installed. 
```bash
git clone https://github.com/yourusername/sentinel-ai.git
cd sentinel-ai

# Create and activate a virtual environment
python3 -m venv venv_real
source venv_real/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `google-genai`, `llama-index-llms-google-genai`, `python-dotenv`, `rich`)*

### 3. Environment Variables
Create a `.env` file in the root directory and add your keys:
```env
# AI Engine
GEMINI_API_KEY=your_gemini_api_key_here

# Auth0 Vault (CIBA Integration)
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
```

---

## Usage

To trigger an incident simulation and watch Sentinel-AI's reasoning loop in real-time, run:

```bash
python main.py
```

### What to expect:
1. The terminal will initialize the **Custom Sentinel Core**.
2. An alert regarding `auth-service-demo` will be ingested.
3. You will see the AI's internal **Thought/Action** loop as it quarantines the branch and notifies Slack.
4. **The Intercept:** The terminal will pause with a spinner, awaiting your approval on the Auth0 Guardian mobile app before issuing the GitHub rollback token.
