# PharmaPulse-ET: End-to-End Telegram Data Analytics Platform

![Project Status](https://img.shields.io/badge/status-completed-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Tech Stack](https://img.shields.io/badge/Tech-Docker%20%7C%20dbt%20%7C%20Dagster%20%7C%20FastAPI-informational)

An end-to-end data pipeline for the Ethiopian medical sector, leveraging public Telegram data. This project extracts raw data, processes it through a modern ELT framework with dbt and Dagster, enriches it with YOLOv8, and serves insights via a FastAPI application.

## 1. Overview

In Ethiopia's digital marketplace, public Telegram channels are a primary source for information on medical products. This project, **PharmaPulse-ET**, tackles the challenge of transforming this chaotic, unstructured data into a structured, queryable, and valuable asset. It builds a robust data platform to ingest, process, enrich, and serve insights, enabling analysts to answer critical business questions like:

- What are the most frequently mentioned medical products?
- How does product availability vary across channels?
- What are the daily and weekly trends in posting volume?

## 2. System Architecture

The platform is built on a modern, layered data architecture that ensures scalability, reliability, and reproducibility. The data flows through several distinct stages, from raw ingestion in a data lake to a final, analytics-ready star schema.


**The data pipeline consists of five key stages:**

1.  **Extract & Load (to Data Lake):** Python scripts using **Telethon** scrape raw messages and images from public Telegram channels into a local file system, which serves as our data lake.
2.  **Load (to Data Warehouse):** A loading script takes the raw JSON files and populates a `raw` schema in our **PostgreSQL** data warehouse.
3.  **Transform & Model:** **dbt** connects to the warehouse, transforming the raw data into clean `staging` models and then building a final, analytics-ready **Star Schema** in a `marts` schema.
4.  **Enrich:** A Python script using a pre-trained **YOLOv8** model performs object detection on scraped images and writes the results back to the warehouse.
5.  **Serve & Orchestrate:** A **FastAPI** application exposes analytical endpoints, while **Dagster** orchestrates the entire workflow, managing dependencies, schedules, and monitoring.

## 3. Key Features

- **Automated Data Scraping:** Continuously extracts new messages and images from specified Telegram channels.
- **Modern ELT Pipeline:** Leverages the power of a data warehouse for transformations using dbt.
- **Dimensional Data Model:** Implements a Star Schema optimized for fast and efficient analytical queries.
- **AI-Powered Data Enrichment:** Uses a YOLOv8 object detection model to extract insights from visual content.
- **Analytical API:** Serves cleaned, structured data through a high-performance REST API with automated documentation.
- **Robust Orchestration:** Manages the entire pipeline with Dagster, providing scheduling, monitoring, and a clear user interface.
- **Reproducible Environment:** Fully containerized with **Docker** for a consistent development and deployment experience.

## 4. Tech Stack

| Component            | Technology                                                                             |
| -------------------- | -------------------------------------------------------------------------------------- |
| **Containerization** | [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/)  |
| **Data Extraction**  | [Python](https://www.python.org/), [Telethon](https://docs.telethon.dev/en/stable/)    |
| **Data Warehouse**   | [PostgreSQL](https://www.postgresql.org/)                                              |
| **Transformation**   | [dbt (Data Build Tool)](https://www.getdbt.com/)                                       |
| **Data Enrichment**  | [PyTorch](https://pytorch.org/), [YOLOv8 (Ultralytics)](https://docs.ultralytics.com/) |
| **API Server**       | [FastAPI](https://fastapi.tiangolo.com/)                                               |
| **Orchestration**    | [Dagster](https://dagster.io/)                                                         |

## 5. Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Setup and Configuration

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Miheret-Girmachew/PharmaPulse-ET.git
    cd PharmaPulse-ET
    ```

2.  **Configure your environment variables:**
    Create a `.env` file by copying the example. This file will store your secret keys and configurations. **It is already included in `.gitignore` to prevent accidental commits.**

    ```bash
    # For Windows (Git Bash / MINGW64) or Linux/macOS
    cp .env.example .env
    ```

3.  **Edit the `.env` file** and add your credentials:
    - `TELEGRAM_API_ID` & `TELEGRAM_API_HASH`: Get these from [my.telegram.org](https://my.telegram.org).
    - `POSTGRES_*`: These are pre-configured for the Docker setup. You can change them if you wish.

### Running the Application

Build the Docker images and start all services (PostgreSQL, Dagster UI) in detached mode.

```bash
docker-compose up --build -d
```

The first build will take several minutes as it downloads all dependencies. Subsequent builds will be much faster due to Docker's caching.

## 6. How to Use the Pipeline

Once the containers are running, you can interact with the different components of the system.

### Orchestration with Dagster

Open the Dagster UI in your browser:

    http://localhost:3000

You will see the end_to_end_telegram_pipeline job.
To run the entire pipeline manually, click on the job, go to the "Launchpad" tab, and click "Launch Run". You can monitor the progress of each step in the "Runs" tab.

[//]: # "Take a screenshot of your pipeline graph in the Dagster UI, save it as 'assets/dagster-ui.png', and replace this line with:
![alt text](assets/dagster-ui.png"

)

### Running Individual Scripts

You can also run any script manually from your terminal. For example, to run the scraper:

```bash
docker-compose exec app python src/scraping/scraper.py
```

The first time you run the scraper, you will be prompted to enter your phone number, a login code from Telegram, and your 2FA password (if enabled).

### Accessing the Analytical API

To run the API server for development, execute the following command in a new terminal:

```bash
docker-compose exec app uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the interactive API documentation in your browser:

    http://localhost:8000/docs

From here, you can test all the available endpoints directly.

Example curl request:

```bash
curl -X GET "http://localhost:8000/api/channels/CheMed123/activity"
```

[//]: # "Take a screenshot of a successful API request in Postman or the FastAPI docs, save it as 'assets/api-demo.png', and replace this line with:
![alt text](assets/api-demo.png"

)

## 7. Project Structure

```
.
├── api/                  # FastAPI application code (main.py, crud.py, etc.)
├── data/                 # Data Lake for raw scraped data (ignored by Git)
├── kara_dagster_pipeline/  # Dagster definitions (ops, jobs, schedules)
├── kara_dbt_project/     # dbt project for data transformation and modeling
│   ├── models/
│   │   ├── staging/      # Staging models (1-to-1 with sources, light cleaning)
│   │   └── marts/        # Final data mart models (star schema)
│   ├── packages.yml      # dbt package dependencies (e.g., dbt_utils)
│   └── dbt_project.yml   # dbt project configuration
├── src/                  # Python source code for pipeline scripts
│   ├── enrichment/       # YOLOv8 enrichment script
│   ├── loading/          # Script to load raw data from data lake to warehouse
│   └── scraping/         # Telethon scraping script
├── tests/                # Placeholder for Python unit/integration tests
├── .env.example          # Example environment file
├── .gitignore            # Files and directories to ignore in version control
├── docker-compose.yml    # Defines and orchestrates the multi-container application
├── Dockerfile            # Defines the Python application container
└── requirements.txt      # Python dependencies
```

## 8. License

This project is licensed under the MIT License. See the LICENSE file for details.
