# kara_dagster_pipeline/repo.py

import subprocess
from dagster import job, op, repository, ScheduleDefinition
import os

# Helper function to run shell commands and log their output
def run_command(command, project_dir=None):
    """Helper function to run shell commands from a specific directory."""
    # If a project_dir is specified for dbt, construct the full command
    if project_dir:
        full_command = f"cd {project_dir} && {command}"
    else:
        full_command = command

    # Start the subprocess
    process = subprocess.Popen(
        full_command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        executable='/bin/bash' # Explicitly use bash
    )

    # Stream stdout and stderr
    for line in process.stdout:
        print(line, end='')
    for line in process.stderr:
        print(line, end='')

    # Wait for the process to complete and get the return code
    return_code = process.wait()
    if return_code != 0:
        raise Exception(f"Command failed with return code {return_code}: {full_command}")
    return "Command executed successfully"


@op(name="scrape_telegram_data")
def scrape_telegram_op(context):
    """Dagster op to run the Telegram scraper."""
    context.log.info("Starting Telegram scraping.")
    result = run_command("python src/scraping/scraper.py")
    context.log.info(result)
    return result

@op(name="load_raw_to_postgres")
def load_to_raw_op(context, scrape_result: str):
    """Dagster op to load raw data into PostgreSQL."""
    context.log.info("Loading raw data to PostgreSQL.")
    result = run_command("python src/loading/load_to_raw.py")
    context.log.info(result)
    return result

@op(name="run_dbt_transformations")
def run_dbt_op(context, load_result: str):
    """Dagster op to run dbt build."""
    context.log.info("Running dbt transformations.")
    # dbt commands must be run from within the dbt project directory
    result = run_command("dbt run", project_dir="kara_dbt_project")
    context.log.info(result)
    # Also run tests
    test_result = run_command("dbt test", project_dir="kara_dbt_project")
    context.log.info(test_result)
    return test_result

@op(name="run_yolo_enrichment")
def run_yolo_op(context, dbt_result: str):
    """Dagster op to run YOLO enrichment."""
    context.log.info("Running YOLO enrichment.")
    result = run_command("python src/enrichment/run_yolo.py")
    context.log.info(result)
    return result

@job(name="end_to_end_telegram_pipeline")
def full_pipeline_job():
    """Defines the full data pipeline as a Dagster job."""
    scrape_result = scrape_telegram_op()
    load_result = load_to_raw_op(scrape_result)
    dbt_result = run_dbt_op(load_result)
    run_yolo_op(dbt_result)

# Define a schedule to run the job daily at midnight
daily_schedule = ScheduleDefinition(
    job=full_pipeline_job,
    cron_schedule="0 0 * * *",  # every day at midnight UTC
    execution_timezone="UTC",
)

@repository
def kara_solutions_repo():
    """A repository to hold all jobs and schedules."""
    return [full_pipeline_job, daily_schedule]