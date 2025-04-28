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

The Real Estate Property Analysis System is an automated data pipeline designed to collect, process, and analyze property listings from popular Indian real estate websites. This project combines web crawling, data extraction, and AI-powered analysis to provide valuable insights for property investors and buyers.

### Key Features
- **Automated Data Collection**: Daily crawling of real estate sites for new properties
- **Intelligent Data Extraction**: Structured property data extraction using AI
- **Interactive Dashboard**: Visual exploration of property trends and statistics
- **Investment Analysis**: AI-powered recommendations for property investment
- **API Access**: RESTful API endpoints for programmatic data access
- **Scheduled Execution**: Fully automated workflow with Prefect orchestration

The system is designed to be maintainable, extensible, and robust, with proper error handling and monitoring capabilities.

## System Architecture Overview

This flowchart provides a visual overview of the real estate property analysis system architecture, showing how data flows from web crawling to analysis and presentation.

```mermaid
---
config:
  layout: fixed
  look: neo
  theme: neo
---
flowchart TD
    Start["Start: Daily Data Update"] --> CloudWatchEvent["CloudWatch Event (Schedule)"]
    CloudWatchEvent --> AWSLambda["AWS Lambda (Data Scraping & Processing)"]
    AWSLambda --> AWSS3["AWS S3 (JSON Data Storage)"]
    AWSLambda -- Optional --> AWSRDS["AWS RDS/DynamoDB (Database)"]
    AWSS3 -- Data --> FastAPIApp["FastAPI App (on Lambda/EC2/ECS)"]
    AWSRDS -- Data --> FastAPIApp
    FastAPIApp --> AWSAPIGateway["AWS API Gateway (REST API)"]
    AWSAPIGateway --> StreamlitDashboard["Streamlit Dashboard (S3 + CloudFront)"]
    StreamlitDashboard --> User["User"] & AWSAPIGateway
    User --> StreamlitDashboard

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

## Streamlit Dashboard
[![Streamlit UI](http://img.youtube.com/vi/sbQWHOb1ndg/0.jpg)](https://www.youtube.com/watch?v=sbQWHOb1ndg)
