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
    * **Technical Layer:** Uses **Python (Faker)** to attach realistic technical indicators (Malicious IPs, Phishing Domains).
* **Advanced Campaign Orchestration:**
    * **Campaign Management:** Messages are not isolated but grouped into coherent STIX 2.1 `Campaign` objects (e.g., "Operation Blackout"), allowing analysts to track strategic movements.
    * **Attribution:** Automatically links simulated Bots (`Identity`) to Campaigns and Indicators.
* **Cyber Arsenal Simulation:**
    * **Malware Injection:** The engine randomly injects weaponized payloads (Ransomware, Spyware) into social media posts.
    * **STIX Patterning:** Creates the full kill-chain graph: `Threat Actor` -> `uses` -> `Malware` -> `indicated-by` -> `File Hash (SHA256)`.
* **Autonomous Daemon:** Runs as a background service (Dockerized) simulating continuous activity with "human-like" pause intervals.
* **Live Monitoring:** Integrated directly with OpenCTI dashboards. Provides clear visualization via pie charts (distribution of narratives) and knowledge graphs to analyze correlations.
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

### Quick Start

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/Elbayly-Amir/cognitive-warfare-range.git](https://github.com/Elbayly-Amir/cognitive-warfare-range.git)
    cd cognitive-warfare-range
    ```

2.  **Configure Environment**
    Duplicate the sample file.
    ```bash
    cp .env.sample .env
    ```
    
    **Important:** You must generate a unique ID for the connector.
    Run the following command in your terminal:
    ```bash
    uuidgen
    ```
    Copy the output (e.g., `550e8400-e29b...`) and replace `CHANGEME_UUID` in your `.env` file.
    *Note: If you do not have `uuidgen`, you can use any online UUID generator.*

    Edit `OPENCTI_TOKEN` in the `.env` file with your OpenCTI admin token.

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

The simulator is data-driven. You can control narratives, personas, and available malware by editing `scenarios.json`.

**Example Configuration:**
```json
{
  "personas": [
    {
      "id": "patriot_bot_ru",
      "description": "Influence agent spreading political propaganda.",
      "origin_country": "RU",
      "weight": 0.5
    }
  ],
  "scenarios": [
    {
      "name": "Energy Grid Disinformation",
      "category": "DISINFORMATION",
      "weight": 0.4,
      "ai_topic": "Government hiding massive blackouts for next winter.",
      "campaign": "Operation Winter Blackout"
    }
  ],
  "malwares": [
    {
      "name": "WannaCry 2.0",
      "type": "Ransomware",
      "hash": "24d004a104d45d21699126d5d932172a80f074d18646b241d112348392749001"
    }
  ]
}