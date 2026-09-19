from __future__ import annotations

import logging
from datetime import datetime , timedelta
from pathlib import Path
from sys import base_prefix

from airflow.sdk import dag, task
from airflow.models import Variable

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'data-eng',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

@dag(
    dag_id='synthetic_data_generator_to_s3',
    description="Generate synthetic dirty customer 360 data and load it to s3",
    default_args=default_args,
    schedule= timedelta(minutes=55),
    start_date= datetime(2026,1,1),
    catchup=False,
    tags=['data-generator','s3','synthetic-data']
)

def synthetic_data_generator_to_s3():

    @task.python(task_id="generate_data")
    def generate_data()-> dict:

        from data_generator import config
        from data_generator.utils import QualityReport, get_faker, reseed, save_csv
        from data_generator.generators.customers import generate_customers,assign_segments
        from data_generator.generators.mobile import generate_mobile_usage
        from data_generator.generators.financials import generate_financial_transactions
        from data_generator.generators.credit import generate_credit_accounts
        from data_generator.generators.fiber import generate_fiber_subscriptions, generate_fiber_usage
        from data_generator.generators.devices import generate_device_purchases
        from data_generator.generators.enterprise import generate_enterprise_services
        from data_generator.generators.digital_services import generate_digital_services

        seed = int(Variable.get("data_generator_seed", default_var="42"))
        n_customers=int(Variable.get("data_generator_customers", default_var="0")) or config.Counts.customers

        config.configure_logging()
        config.ensure_directories()
        reseed(seed)
        get_faker(seed)

        logger.info("Starting synthetic data generation", seed , n_customers)

        report= QualityReport()

        customers = generate_customers(n_customers)
        customers= assign_segments(customers)
        save_csv(customers, config.DATA_ROOT/"customers"/"customers.csv")
        report.add("customers", customers)

        mobile = generate_mobile_usage(config.Counts.mobile_usage, customers)
        save_csv(mobile, config.DATA_ROOT / "mobile" / "mobile_usage.csv")
        report.add("mobile_usage", mobile)

        financial = generate_financial_transactions(config.Counts.financial_transactions, customers)
        save_csv(financial, config.DATA_ROOT / "financial" / "financial_transactions.csv")
        report.add("financial_transactions", financial)

        credit = generate_credit_accounts(config.Counts.credit_accounts, customers)
        save_csv(credit, config.DATA_ROOT / "credit" / "credit_accounts.csv")
        report.add("credit_accounts", credit)

        fiber_subs = generate_fiber_subscriptions(config.Counts.fiber_subscriptions, customers)
        save_csv(fiber_subs, config.DATA_ROOT / "fiber" / "fiber_subscriptions.csv")
        report.add("fiber_subscriptions", fiber_subs)

        fiber_usage = generate_fiber_usage(config.Counts.fiber_usage, fiber_subs)
        save_csv(fiber_usage, config.DATA_ROOT / "fiber" / "fiber_usage.csv")
        report.add("fiber_usage", fiber_usage)

        devices = generate_device_purchases(config.Counts.device_purchases, customers)
        save_csv(devices, config.DATA_ROOT / "devices" / "device_purchases.csv")
        report.add("device_purchases", devices)

        enterprise = generate_enterprise_services(config.Counts.enterprise_services, customers)
        save_csv(enterprise, config.DATA_ROOT / "enterprise" / "enterprise_services.csv")
        report.add("enterprise_services", enterprise)

        digital = generate_digital_services(config.Counts.digital_services, customers)
        save_csv(digital, config.DATA_ROOT / "digital" / "digital_services.csv")
        report.add("digital_services", digital)

        report.write(config.REPORT_PATH)

        logger.info("Generation complete. Data written to %s", config.DATA_ROOT)

        # Returned dict is auto-pushed to XCom and passed to the next task.
        return {
            "data_root": str(config.DATA_ROOT),
            "report_path": str(config.REPORT_PATH),
        }

    @task.python(task_id="upload_to_s3")
    def upload_to_s3(paths: dict)-> None:

        from airflow.providers.amazon.aws.hooks.s3 import S3Hook
        from airflow.operators.python import get_current_context

        bucket = Variable.get("data_generator_s3_bucket")
        prefix = Variable.get("data_generator_s3_prefix", default_var="").strip("/")
        aws_conn_id = Variable.get("data_generator_aws_conn_id", default_var="aws_default")

        data_root= Path(paths["data_root"])
        report_path= Path(paths["report_path"])

        hook= S3Hook(aws_conn_id=aws_conn_id)

        run_date = get_current_context()["ds"]

        base_prefix=f"{prefix}/{run_date}" if prefix else run_date

        files = sorted(p for p in data_root.rglob("*") if p.is_file())

        if report_path.exists():
            files.append(report_path)

        if not files:
            raise FileNotFoundError(f"{report_path} does not exist")

        logger.info("Uploading %d files to s3://%s/%s", len(files), bucket, base_prefix)

        for path in files:
            if path == report_path:
                key=f"{base_prefix}/{path.name}"

            else:
                rel=path.relative_to(data_root)
                key=f"{base_prefix}/{rel.as_posix()}"

            hook.load_file(
                filename=str(path),
                key=key,
                bucket_name=bucket,
                replace=True
            )
            logger.info(f"Uploaded {key} to s3://%s/%s", path,bucket, key)

        logger.info("Upload complete:", len(files),bucket, base_prefix)


    upload_to_s3(generate_data())

synthetic_data_generator_to_s3()