from __future__ import annotations

import logging
from datetime import datetime, timedelta
from pathlib import Path

from airflow.sdk import dag, task
from airflow.models import Variable

logger = logging.getLogger(__name__)

default_args = {
    "owner": "data-eng",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="load_s3_data_to_bronze",
    default_args=default_args,
    description="Load data from S3 into Bronze",
    schedule=timedelta(minutes=10),
    start_date=datetime(2026, 1, 1),
    catchup=False,  # True here would backfill every 10-min interval since Jan 2026
    tags=["data-generator", "s3", "postgres", "bronze", "dbt"],
)
def load_s3_data_to_bronze():

    @task.python(task_id="load_data_to_bronze")
    def load_data_to_bronze() -> None:
        """Find the latest S3 partition and load every CSV in it into the bronze schema.

        Rows are parsed and inserted individually (not via COPY) because
        this dataset is deliberately "dirty": some rows have more or fewer
        fields than the header. COPY aborts the entire file on the first
        malformed row; this loader instead reconciles each row to the
        expected column count and keeps going, since the bronze layer's job
        is to land the data as-is for dbt to clean downstream, not to
        reject it before it even arrives.
        """
        import csv
        import io
        import re

        from psycopg2.extras import execute_values
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from airflow.providers.amazon.aws.hooks.s3 import S3Hook

        bucket = Variable.get("data_generator_s3_bucket").strip()
        prefix = Variable.get("data_generator_s3_prefix", default_var="").strip().strip("/")
        aws_conn_id = Variable.get("data_generator_aws_conn_id", default_var="aws_default")
        postgres_conn_id = Variable.get("data_generator_postgres_conn_id", default_var="postgres_warehouse")
        schema = Variable.get("data_generator_postgres_schema", default_var="bronze").strip()

        s3_hook = S3Hook(aws_conn_id=aws_conn_id)
        pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)

        base_prefix = f"{prefix}/" if prefix else ""

        date_prefixes = s3_hook.list_prefixes(bucket_name=bucket, prefix=base_prefix, delimiter="/") or []
        if not date_prefixes:
            raise FileNotFoundError(f"No date-partitioned folders found under s3://{bucket}/{prefix}")

        # Folder names sort correctly as strings because they are YYYY-MM-DD.
        latest_prefix = sorted(date_prefixes)[-1]
        logger.info("Latest data-partitioned folder: %s", latest_prefix)

        keys = s3_hook.list_keys(bucket_name=bucket, prefix=latest_prefix) or []
        csv_keys = sorted(k for k in keys if k.lower().endswith(".csv"))
        if not csv_keys:
            raise FileNotFoundError(f"No CSV files found under s3://{bucket}/{latest_prefix}")

        def sanitize(name: str) -> str:
            """Make a string a safe, lowercase Postgres identifier."""
            name = re.sub(r"[^0-9a-zA-Z_]", "_", name.strip().lower())
            if name and name[0].isdigit():
                name = f"_{name}"
            return name or "col"

        def reconcile_row(row: list, n_cols: int) -> list:
            """Force a parsed CSV row to exactly n_cols fields without losing data.

            Too many fields (a dirty/malformed row): merge the overflow
            back into the last column, comma-joined, so nothing is
            silently dropped -- dbt/silver decides how to clean it later.
            Too few fields: pad with NULL.
            """
            if len(row) == n_cols:
                return row
            if len(row) > n_cols:
                head = row[: n_cols - 1]
                tail = ",".join(row[n_cols - 1:])
                return head + [tail]
            return row + [None] * (n_cols - len(row))

        conn = pg_hook.get_conn()
        conn.autocommit = False
        cur = conn.cursor()

        try:
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}";')
            conn.commit()

            for key in csv_keys:
                table = sanitize(Path(key).stem)
                logger.info("Loading s3://%s/%s -> %s.%s", bucket, key, schema, table)

                raw_text = s3_hook.read_key(key=key, bucket_name=bucket)
                if not raw_text.strip():
                    logger.warning("Skipping empty file: %s", key)
                    continue

                reader = csv.reader(io.StringIO(raw_text))
                header = next(reader)
                columns = [sanitize(c) for c in header]

                # De-duplicate any column names that collide after sanitizing.
                seen: dict[str, int] = {}
                deduped = []
                for c in columns:
                    if c in seen:
                        seen[c] += 1
                        c = f"{c}_{seen[c]}"
                    else:
                        seen[c] = 0
                    deduped.append(c)
                columns = deduped
                n_cols = len(columns)

                col_defs = ", ".join(f'"{c}" TEXT' for c in columns)
                cur.execute(f'CREATE TABLE IF NOT EXISTS "{schema}"."{table}" ({col_defs});')
                cur.execute(f'TRUNCATE TABLE "{schema}"."{table}";')

                rows = [tuple(reconcile_row(row, n_cols)) for row in reader if row]

                if rows:
                    col_list = ", ".join(f'"{c}"' for c in columns)
                    execute_values(
                        cur,
                        f'INSERT INTO "{schema}"."{table}" ({col_list}) VALUES %s',
                        rows,
                        page_size=1000,
                    )
                conn.commit()
                logger.info("Loaded %d rows -> %s.%s", len(rows), schema, table)

        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            conn.close()

        logger.info(
            "Postgres load complete: %d tables loaded into schema '%s' from %s",
            len(csv_keys), schema, latest_prefix,
        )

    load_data_to_bronze()


load_s3_data_to_bronze()