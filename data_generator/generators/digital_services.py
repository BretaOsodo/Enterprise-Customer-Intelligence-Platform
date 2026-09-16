"""Digital services generator."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta

import pandas as pd

from .. import config
from ..quality import corruptions as qc
from ..utils import get_faker, log_section, random_date_between

logger = logging.getLogger(__name__)


def generate_digital_services(
    count: int, customers: pd.DataFrame
) -> pd.DataFrame:
    """Generate digital service subscriptions."""
    log_section("Generating digital services")
    get_faker()

    cust_ids = customers["customer_id"].dropna().astype(str).tolist()

    records = []
    for i in range(count):
        cid = random.choice(cust_ids)
        service = random.choice(list(config.DIGITAL_SERVICES.keys()))
        fee = config.DIGITAL_SERVICES[service]["fee"]
        sub_date = random_date_between(date(2022, 6, 1), date.today())
        usage_count = random.randint(0, 500)
        last_active = sub_date + timedelta(days=random.randint(0, 365))

        records.append({
            "subscription_id": f"DIG{i:07d}",
            "customer_id": cid,
            "service_type": service,
            "subscription_date": sub_date,
            "monthly_fee": fee,
            "usage_count": usage_count,
            "status": random.choices(
                config.DIGITAL_STATUSES, weights=[0.7, 0.2, 0.1]
            )[0],
            "last_activity_date": last_active,
            "created_at": sub_date,
            "updated_at": last_active,
        })

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s digital service records", len(df))

    rate = config.DirtyRates.digital_services
    df = qc.duplicate_rows_exact(df, rate * 0.4)
    df = qc.duplicate_rows_key(
        df, "subscription_id", rate * 0.3,
        mutate={"updated_at": lambda v: v + timedelta(days=1)},
    )
    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)
    df = qc.set_missing(df, ["customer_id", "monthly_fee", "usage_count"], rate)
    df = qc.negative_values(df, "monthly_fee", rate * 0.2)
    df = qc.negative_values(df, "usage_count", rate * 0.3)
    df = qc.future_dates(df, "subscription_date", rate * 0.15, days_ahead=120)
    df = qc.corrupt_column(
        df, "service_type", rate * 0.4,
        lambda v: qc.categorical_corrupt(v, list(config.DIGITAL_SERVICES)),
    )
    df = qc.corrupt_column(df, "status", rate * 0.3, qc.whitespace_or_case)

    return df