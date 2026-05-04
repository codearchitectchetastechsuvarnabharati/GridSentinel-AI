# GridSentinel AI
### Explainable Smart Meter Intelligence for Power Distribution Utilities

---

## Overview

**GridSentinel AI** is an explainable, decision‑support analytics platform designed for electricity distribution utilities such as **BESCOM**.  
The platform analyzes smart meter data to help engineers forecast localized electricity demand, identify grid stress, and detect abnormal consumption patterns using transparent and auditable machine‑learning techniques.

The system operates strictly as a **read‑only analytics layer**. It does **not** modify, control, or automate any existing utility infrastructure. All outputs are advisory, explainable, and intended to support human decision‑making in regulated public‑utility environments.

---

## Problem Statement

Electricity distribution utilities generate large volumes of smart meter data, but often lack localized, explainable analytics to proactively forecast demand and identify abnormal consumption without increasing false positives or disrupting existing operational systems.

---

## Solution Summary

GridSentinel AI transforms raw smart meter data into actionable insights by combining:

- Zone‑level demand forecasting  
- Grid stress assessment  
- Explainable anomaly detection  
- Peer‑group comparison  
- Composite, transparent risk scoring  

The platform helps utilities prioritize inspections, anticipate peak load conditions, and improve planning efficiency while maintaining full human oversight.

---

## Key Objectives

- Forecast short‑term electricity demand at zone level  
- Identify high‑risk zones for peak load and grid stress  
- Detect abnormal meter behavior using explainable ML  
- Reduce false positives through peer‑group comparison  
- Provide audit‑ready, decision‑support dashboards  
- Restrict access to authorized users only  

---

## Solution Architecture

### 1. Data Ingestion Layer
- Input: CSV extracts from smart meter systems  
- Read‑only processing  
- No changes to upstream BESCOM systems  

### 2. Analytics & AI Layer

**Part A – Localized Demand Forecasting**
- Rolling statistics and EWMA‑based forecasting  
- Zone‑level stress ratio computation  
- Risk classification: LOW / MEDIUM / HIGH  

**Part B – Anomaly & Peer Analysis**
- Unsupervised anomaly detection (Isolation Forest)  
- Peer‑group deviation analysis to minimize false positives  
- Composite risk scoring with transparent weights  

### 3. Explainability & Governance
- Human‑readable reasons for every flagged meter  
- Explicit confidence and stress indicators  
- Complete audit trail of user actions  
- Decision‑support only (no automated enforcement)  

### 4. Web Interface
- Engineer dashboard with KPIs and tables  
- Charts with confidence bands  
- Profile and admin pages  
- Role‑based access and audit visibility  

---

## Non‑Negotiables (Design Constraints)

- No automated grid control or enforcement  
- No modification of existing billing or control systems  
- No personal customer data exposed  
- All outputs are advisory and explainable  
- Human approval required for all actions  

---

## Technology Stack

- **Backend:** Python, Flask  
- **AI / ML:** Pandas, scikit‑learn  
- **Visualization:** Chart.js, Bootstrap  
- **Data Storage:** CSV / Excel (lightweight, audit‑friendly)  
- **Deployment:** Local / On‑premise compatible  

---

## Project Structure
'''
GridSentinel-AI/
│
├── backend/
│   ├── app.py
│   ├── smart_meter_ai.py
│   ├── constants.py
│   ├── auth_utils.py
│   ├── local_llm_stub.py
│   │
│   └── ai/
│       ├── demand_forecasting.py
│       └── peer_analysis.py
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── charts.html
│   ├── profile.html
│   └── admin.html
│
├── data/
│   └── csv_inputs/
│
├── .gitignore
└── README.md
---

## How the System Works (High‑Level Flow)

1. Smart meter data is ingested from CSV files  
2. Zone‑level demand forecasts are generated  
3. Meter‑level anomalies are detected  
4. Peer‑group analysis reduces false positives  
5. A composite, explainable risk score is calculated  
6. Engineers review insights and take informed actions  

---

## User Roles

### Engineer
- View dashboards and analytics  
- Review AI‑generated recommendations  
- Read‑only access  

### Admin
- View registered users  
- Access audit logs  
- Governance and oversight  

---

## Disclaimer

> GridSentinel AI is a **decision‑support platform only**.  
> All operational actions must be reviewed and approved by authorized utility personnel as per internal utility policies.

---

## Author

**Developed by:**  
**Chetas Swaroop Karnam**

> Note: This repository was temporarily pushed using a shared family laptop and GitHub account for submission purposes.  
> Authorship, design, and implementation ownership belong to the above individual.

---

## Usage

This project is intended for:
- Academic evaluation  
- Hackathon and innovation challenges  
- Demonstration of smart grid analytics concepts  

---

## License

For demonstration and academic submission purposes only.