# Cognitive Warfare Range (Social Engineering Simulator)

**An automated, hybrid threat simulator designed to train SOC analysts and fight against information manipulation (Cognitive Warfare).**

---

## Project Overview

In the modern cyber landscape, Security Operations Centers (SOCs) are well-equipped to detect technical malware but often struggle against **Cognitive Warfare** (disinformation campaigns) and **Social Engineering** (targeted phishing).

**The Problem:** Analysts lack realistic, safe, and dynamic datasets to train on detecting "grey zone" attacks that mix psychological manipulation with technical indicators.

**The Solution:** A fully automated "Cyber Range" that generates hybrid threats (Semantic + Technical) using local AI and injects them into a CTI platform (OpenCTI) using the STIX 2.1 standard.

---

## Key Features

* **Hybrid Generation Engine:**
    * **Semantic Layer:** Uses a local LLM (**Ollama/Mistral**) to generate unique, credible, and context-aware narratives (e.g., "Urgent bank alert", "Political scandal cover-up").
    * **Technical Layer:** Uses **Python (Faker)** to attach realistic technical indicators (Malicious IPs, Phishing Domains, File Hashes).
* **STIX 2.1 Structured Data:** Unlike simple log generators, this tool creates a complex graph of objects: `Identity` (Bot) -> `related-to` -> `Note` (Content) -> `related-to` -> `Indicator` (Technical IOC).
* **Autonomous Daemon:** Runs as a background service (Dockerized) simulating continuous activity with "human-like" pause intervals.
* **Live Monitoring:** Integrated directly with OpenCTI dashboards to visualize threat distribution and campaign intensity in real-time.
* **Secure by Design:** Local execution (no data leakage), environment variable management, and strict separation of configuration vs. code.

---

## Technical Architecture

| Component | Technology | Role |
|-----------|------------|------|
| **AI Brain** | **Ollama** (Mistral/Llama3) | Generates the psychological vector (Disinformation/Phishing text) via Prompt Engineering. |
| **Tech Generator** | **Python** (Faker) | Generates the technical vector (IPs, URLs, SHA256 Hashes). |
| **Connector** | **Python** (pycti) | Orchestrates the simulation and pushes STIX objects to the platform. |
| **CTI Platform** | **OpenCTI** (Docker) | Knowledge base for analysis, visualization, and correlation. |

---

## Installation & Setup

### Prerequisites
* **Docker** & **Docker Compose**
* **Ollama** installed on the host machine (Mac/Linux/Windows)
* **Python 3.13** (optional, for local dev)

### Quick Start

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Elbayly-Amir/cognitive-warfare-range.git
    cd cognitive-warfare-range
    ```

2.  **Configure Environment**
    Duplicate the sample file and set your credentials.
    ```bash
    cp .env.sample .env
    # Edit .env if you changed OpenCTI default credentials
    ```

3.  **Start the AI Model (Local Host)**
    Ensure Ollama is running and has the model pulled.
    ```bash
    ollama pull mistral
    ```

4.  **Launch the Stack**
    ```bash
    docker compose up -d --build
    ```

5.  **Access the Platform**
    * URL: `http://localhost:8080`
    * Default Credentials: `admin@opencti.io` / `Password1234!`

---

## Scenario Configuration

The simulator is data-driven. You can control the narratives by editing `scenarios.json`.
The engine uses the `ai_topic` to prompt the LLM and the `category` to tag the data.

**Example Configuration:**
```json
{
  "scenarios": [
    {
      "name": "Banking Phishing Campaign",
      "category": "PHISHING",
      "weight": 0.5,
      "ai_topic": "Urgent account suspension notice due to suspicious activity",
      "templates": [] 
    },
    {
      "name": "Political Disinformation",
      "category": "DISINFORMATION",
      "weight": 0.5,
      "ai_topic": "Government hiding a sanitary scandal regarding tap water"
    }
  ]
}