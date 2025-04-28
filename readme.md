<div align="center">
 
![logo](https://github.com/yaswanthkumargothi/daily_real_estate_insights/blob/main/real_estate_agent_logo.png)

<h1 align="center"><strong> Real-Estate Daily Investment Insights Agent :<h6 align="center">AI-powered agentic system for investing in new Real estate </h6></strong></h1>

![Python - Version](https://img.shields.io/badge/PYTHON-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI - Version](https://img.shields.io/badge/FastAPI-0.104+-teal?style=for-the-badge&logo=fastapi)
![Pydantic - Version](https://img.shields.io/badge/Pydantic-2.0+-red?style=for-the-badge&logo=pydantic)
![Streamlit - Version](https://img.shields.io/badge/Streamlit-latest-orange?style=for-the-badge&logo=streamlit)
![Pandas - Version](https://img.shields.io/badge/Pandas-latest-blue?style=for-the-badge&logo=pandas)
![OpenAI - Version](https://img.shields.io/badge/OpenAI-1.0+-grey?style=for-the-badge&logo=openai)
![Playwright - Version](https://img.shields.io/badge/Playwright-1.39+-brightgreen?style=for-the-badge&logo=playwright)
![Prefect - Version](https://img.shields.io/badge/Prefect-2.0+-blue?style=for-the-badge&logo=prefect)
[![GitHub Issues](https://img.shields.io/github/issues/souvikmajumder26/Multi-Agent-Medical-Assistant.svg?style=for-the-badge)](https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg?style=for-the-badge)

</div>


# Real Estate Property Analysis Agent

## Introduction

The Real Estate Property Analysis System is an automated data pipeline designed to collect, process, and analyze property listings from popular Indian real estate websites. This project combines web crawling, data extraction, and AI-powered analysis to provide valuable insights for property investors and buyers.

### Key Features
- **Automated Data Collection**: Daily crawling of Housing.com and MagicBricks.com
- **Intelligent Data Extraction**: Structured property data extraction using AI
- **Interactive Dashboard**: Visual exploration of property trends and statistics
- **Investment Analysis**: AI-powered recommendations for property investment
- **API Access**: RESTful API endpoints for programmatic data access
- **Scheduled Execution**: Fully automated workflow with Prefect orchestration

The system is designed to be maintainable, extensible, and robust, with proper error handling and monitoring capabilities.

## System Architecture Overview

This flowchart provides a visual overview of the real estate property analysis system architecture, showing how data flows from web crawling to analysis and presentation.

```mermaid
flowchart TD
    %% Define the main components
    Scheduler["Scheduler (scheduler.py)"]
    Prefect["Prefect Workflow Engine"]
    
    %% Data Collection
    subgraph "Data Collection"
        Housing["Housing.com Crawler\n(app.py)"]
        MagicBricks["MagicBricks Crawler\n(magicbricks_app.py)"]
        HousingHooks["Housing Hooks\n(crawlers/housing.py)"]
        MBHooks["MagicBricks Hooks\n(crawlers/magicbricks.py)"]
    end
    
    %% Data Processing
    subgraph "Data Processing"
        Extraction["Property Data Extraction\n(agents/extract_properties.py)"]
        PropertySchema["Property Schema\n(models/property_schema.py)"]
        LocationProcessor["Location Processor\n(utils/location_processor.py)"]
        Cache["Cache System\n(/cache)"]
    end
    
    %% Data Storage
    subgraph "Data Storage"
        RawData["Raw Data (Markdown)\n/data/*.md"]
        ProcessedData["Processed Data (JSON)\n/data/*.json"]
    end
    
    %% Data Analysis & Visualization
    subgraph "Analysis & Visualization"
        Dashboard["Streamlit Dashboard\n(app/streamlit_dashboard.py)"]
        DashboardUI["Dashboard UI Components\n(ui/dashboard_ui.py)"]
        Analysis["Property Analysis Agent\n(agents/property_analysis_agent.py)"]
    end
    
    %% API Layer
    subgraph "API Layer"
        APIServer["FastAPI Server\n(api/main.py)"]
        APIEndpoints{{"API Endpoints:\n- /properties\n- /stats\n- /health"}}
    end
    
    %% External Dependencies
    subgraph "External Services"
        OpenAI["OpenAI API"]
        PlayWright["Playwright Browser"]
    end
    
    %% Define the connections and data flow
    Scheduler -->|"Deploys & Schedules"| Prefect
    Prefect -->|"Triggers Daily at 1AM"| Housing
    Prefect -->|"Triggers Daily"| MagicBricks
    Prefect -->|"Triggers Daily"| Extraction
    Prefect -->|"Starts"| APIServer
    
    Housing -->|"Uses"| HousingHooks
    MagicBricks -->|"Uses"| MBHooks
    Housing -->|"Uses"| PlayWright
    MagicBricks -->|"Uses"| PlayWright
    
    Housing -->|"Outputs"| RawData
    MagicBricks -->|"Outputs"| RawData
    
    Extraction -->|"Reads"| RawData
    Extraction -->|"Uses"| PropertySchema
    Extraction -->|"Uses"| OpenAI
    Extraction -->|"Saves to"| Cache
    Extraction -->|"Outputs"| ProcessedData
    
    APIServer -->|"Serves"| APIEndpoints
    APIServer -->|"Reads"| ProcessedData
    
    Dashboard -->|"Reads"| ProcessedData
    Dashboard -->|"Uses"| LocationProcessor
    Dashboard -->|"Uses"| DashboardUI
    DashboardUI -->|"Uses"| Analysis
    
    Analysis -->|"Uses"| OpenAI
    Analysis -->|"Analyzes"| ProcessedData
    
    %% User access
    User(["User"])
    User -->|"Views"| Dashboard
    User -->|"Accesses"| APIEndpoints
```

## System Architecture

### 1. Orchestration
The scheduler.py file controls the entire workflow using Prefect for robust task scheduling and management. Tasks run daily at 1 AM in sequence.

### 2. Data Collection
- Web crawlers for Housing.com and MagicBricks.com
- Uses Playwright for browser automation
- Site-specific interaction hooks handle navigation and filtering

### 3. Data Processing
- Extracts structured property data from raw markdown
- Normalizes and standardizes data (locations, prices, areas)
- Caches processed data to improve efficiency

### 4. Data Storage
- Raw scraped data stored as markdown files
- Processed data stored in JSON format for easy consumption

### 5. API Layer
- FastAPI server provides programmatic access to property data
- Endpoints for property listings, statistics, and system health

### 6. Analysis & Visualization
- Streamlit dashboard for interactive data exploration
- Location-based analysis with map visualization
- AI-powered investment analysis using OpenAI

### 7. External Dependencies
- OpenAI API for data extraction and analysis
- Playwright for web automation

This architecture provides a complete end-to-end pipeline from data collection to analysis and presentation, with both UI and API access to the processed data.