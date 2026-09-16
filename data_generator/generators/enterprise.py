"""Enterprise service generator."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta

import pandas as pd

from .. import config
from ..quality import corruptions as qc
from ..utils import get_faker, log_section, random_date_between

logger = logging.getLogger(__name__)


def generate_enterprise_services(
    count: int, customers: pd.DataFrame
) -> pd.DataFrame:
    """Generate enterprise service contracts."""
    log_section("Generating enterprise services")
    get_faker()

    eligible = customers[
        customers["segment"].str.contains("enterprise", na=False)
    ]
    if eligible.empty:
        eligible = customers
    cust_ids = eligible["customer_id"].dropna().astype(str).tolist()

    records = []
    for i in range(count):
        cid = random.choice(cust_ids)
        service = random.choice(list(config.ENTERPRISE_SERVICES.keys()))
        fee = config.ENTERPRISE_SERVICES[service]["fee"]
        start = random_date_between(date(2020, 1, 1), date.today())
        end = start + timedelta(days=random.choice([365, 730, 1095]))

        # Billing usually equals monthly fee, occasionally discounted
        billing = round(fee * random.choice([1.0, 0.95, 0.9, 0.85]), 2)

        records.append({
            "service_id": f"ENT{i:06d}",
            "customer_id": cid,
            "business_id": f"BIZ{random.randint(1, 5000):05d}",
            "service_type": service,
            "start_date": start,
            "monthly_fee": fee,
            "billing_amount": billing,
            "status": random.choices(
                config.ENTERPRISE_STATUSES, weights=[0.85, 0.1, 0.05]
            )[0],
            "contract_end_date": end,
            "created_at": start,
        })

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s enterprise service records", len(df))

    rate = config.DirtyRates.enterprise
    df = qc.duplicate_rows_exact(df, rate * 0.3)
    df = qc.duplicate_rows_key(
        df, "service_id", rate * 0.3,
        mutate={"created_at": lambda v: v + timedelta(days=1)},
    )
    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)
    df = qc.set_missing(df, ["customer_id", "billing_amount"], rate)
    df = qc.negative_values(df, "monthly_fee", rate * 0.2)
    df = qc.negative_values(df, "billing_amount", rate * 0.2)
    df = qc.future_dates(df, "start_date", rate * 0.15, days_ahead=180)
    df = qc.corrupt_column(
        df, "service_type", rate * 0.4,
        lambda v: qc.categorical_corrupt(v, list(config.ENTERPRISE_SERVICES)),
    )
    df = qc.corrupt_column(df, "status", rate * 0.3, qc.whitespace_or_case)

    return df