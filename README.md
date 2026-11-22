# ☀️ SolarOptima: A Smart Decision Support System for Solar Panel Cleaning 

An interactive dashboard that turns dust, weather, and solar production data into a **clear financial decision** for solar plant owners. It answers one question:

> **Will cleaning my solar panels today save me more money than the cleaning itself costs?**

---

## 🎯 The Problem

Dust accumulation in Iraq can reduce solar panel output by **20% – 40%**. Plant owners lose money, but they don't know the optimal time to clean, because cleaning itself is costly (labor + water).

## 💡 The Solution

A Decision Support System that does three things:

1. **Calculates** current performance and lost production.
2. **Forecasts** losses over the coming days.
3. **Recommends** an economic action: clean now or wait, with the **cleaning payback period** in days and dollars.

The core idea: we don't show users complex technical data (irradiance, voltage). We translate it directly into **profit and loss figures**.

---

## 🖥️ Dashboard Sections

| Section | Description |
|---|---|
| **1. Control Panel** | System capacity, electricity tariff ($/kWh), cleaning cost, last cleaning date |
| **2. Financial Executive Cards** | Recommendation (🟢 Clean / 🔴 Postpone), payback period, daily loss, 7-day projected loss |
| **3. Performance & Forensics** | Root cause breakdown (dust vs. temperature), 14-day loss forecast curve, soiling index |
| **4. What-If Scenarios & Report** | Comparison (clean today vs. ignore for 30 days) and a downloadable feasibility PDF report |

All figures update instantly when any input changes.

---

## 🧮 Economic Model

| Symbol | Meaning |
|---|---|
| **P** | Plant capacity (kW) |
| **PSH** | Peak sun hours per day |
| **PR** | Performance ratio |
| **r** | Soiling rate (% loss per day) |
| **d** | Days since last cleaning |
| **T** | Electricity tariff ($/kWh) |
| **C** | Cleaning cost ($) |

```
Daily output if clean (E)   = P × PSH × PR
Dust loss percentage        = r × d   (capped at a reasonable maximum)
Daily loss ($)              = E × (r × d) × T
Payback period (days)       = C ÷ daily loss
Recommendation              = 🟢 Clean if payback is below the threshold, else 🔴 Postpone
```

---

## 🗂️ Data Sources

| Source | Use |
|---|---|
| **NASA POWER** | Solar irradiance and temperature for Baghdad |
| **Kaggle (Solar Panel Soiling)** | Estimating the soiling rate |
| **Kaggle (Solar Power Generation)** | Real production data from an actual plant |

> ⚠️ **Note:** The soiling rate is based on non-Iraqi data, so it is a **preliminary estimate** that can be calibrated with a client's own plant data. Electricity prices and cleaning costs are also **assumptions** adjustable from the control panel.

---

## 💰 Business Model

| Stream | Description |
|---|---|
| **Subscription (SaaS)** | Monthly/annual fee based on plant size, for ongoing alerts and analytics |
| **Pay-Per-Report** | One-time analytical report, ideal for investors before building a plant |
| **API Licensing** | Selling recommendation algorithms to maintenance and installation companies |

**Target segments:** Factories and companies (B2B), installation and maintenance firms, large home system owners, investors and developers.

**Competitive advantage:** Built for Iraq's climate (heavy dust, extreme heat) and focused on the **financial decision**, not just technical metrics.

---

## 🚀 Running Locally

**Requirements:** Python 3.9 or newer.

```bash
# 1. Clone the project
git clone https://github.com/USERNAME/REPO-NAME.git
cd REPO-NAME

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

The dashboard opens automatically in your browser at a local address (localhost).

---

## 📁 Project Structure

```
├── app.py              # Main dashboard (Streamlit)
├── data/
│   └── data.json       # Climate, soiling, and default parameters
├── requirements.txt    # Python dependencies
├── AGENTS.md           # Project context for the AI coding assistant
└── README.md           # This file
```

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** for the interactive UI
- **Plotly** for charts
- **Pandas** for data handling
- **Google Colab** for data analysis and generating `data.json`

---

## 👥 Team

| Name | Role |
|---|---|
| Tabark | Data Lead |
| Sarah | Dashboard Builder |
| Amna | Business & Numbers Lead |
| Zahraa | Design & UX |
