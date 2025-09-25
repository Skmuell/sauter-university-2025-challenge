# Multi-Agent System – Sauter & ONS

## Overview
This project implements a **multi-agent system** designed to provide real-time and reliable answers about the company **Sauter** and the **ONS (Operador Nacional do Sistema Elétrico)**.  
The architecture uses **Gemini models**, **Google Search**, and **BigQuery** to integrate structured and unstructured data into a single interface.

---

## Agents

### Sauter Agent (`sauter_expert`)
- **Model:** `gemini-2.0-flash`
- **Purpose:** Acts as an expert on the **Sauter company**.
- **Tool:** `google_search`
- **Description:**
  Retrieves official information from the website [`sauter.digital`](https://sauter.digital) and other indexed sources.
- **Answers questions about:**
  - Contact details and institutional info.
  - Services and solutions.
  - Portfolio and projects.
- **Instruction:**
  > Always use the official Sauter website or reliable indexed sources to provide accurate answers.

---

### ONS Agent (`ons_expert`)
- **Model:** `gemini-2.0-flash`
- **Purpose:** Specialist in the **Brazilian electrical system**.
- **Tool:** **BigQuery**
- **Description:**
  Queries structured datasets from **ONS** to provide up-to-date and official answers.
- **Answers questions about:**
  - Energy demand and historical data.
  - Generation by source (hydro, thermal, wind, solar).
  - Official reports and real-time data.
- **Instruction:**
  > Use BigQuery to query ONS datasets and always provide official and data-driven responses.

---

### Root Agent (`root_agent`)
- **Model:** `gemini-2.0-flash`
- **Purpose:** Orchestrator agent that routes questions to the correct specialized agent.
- **Tools:**
  - `AgentTool(sauter_expert)`
  - `AgentTool(ons_expert)`
- **Description:**
  - Routes **Sauter-related** questions to the `sauter_expert`.
  - Routes **energy/ONS-related** questions to the `ons_expert`.
  - Can combine answers when needed.

---

## Interaction Flow

```mermaid
flowchart TD
    User([User]) --> RootAgent
    RootAgent -->|Sauter questions| SauterAgent
    RootAgent -->|Energy/ONS questions| ONSAgent
    SauterAgent -->|Google Search + Official Website| FonteSauter
    ONSAgent -->|BigQuery (ONS datasets)| FonteONS
    FonteSauter --> RootAgent
    FonteONS --> RootAgent
    RootAgent --> User
````

---

## Design Decisions

* Only **one built-in tool** per root agent (ADK limitation).
* **ONS Agent** directly queries **BigQuery** → ensures fresh and official data.
* **Sauter Agent** uses **Google Search** as a dynamic connector to the website.
* **Root Agent** orchestrates all requests, giving the user a single point of access.

---

## Current Limitations

* Sauter Agent depends on **Google Search** indexing quality.
* ONS Agent only retrieves data from the configured **BigQuery dataset**.
* Built-in tool restrictions require careful orchestration.

---

## Next Steps

1. Extend ONS datasets in BigQuery (include predictions and newer reports).
2. Implement a **cache layer** for repeated queries.
3. Expand Sauter Agent with institutional PDFs and documents.
4. Add **usage dashboards** for monitoring and metrics.
