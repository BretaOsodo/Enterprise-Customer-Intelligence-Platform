"""Mobile usage generator (voice, SMS, data)."""

from __future__ import annotations

import logging
import random
from datetime import date, datetime, timedelta
from typing import List

import numpy as np
import pandas as pd

from .. import config
from ..quality import corruptions as qc
from ..utils import (
    fake_kenyan_msisdn,
    get_faker,
    log_section,
    random_date_between,
    save_csv,
)

logger = logging.getLogger(__name__)


def _row(idx: int, cust_id: str, msisdn: str) -> dict:
    """Build one realistic mobile usage record."""
    usage_type = random.choices(
        config.USAGE_TYPES, weights=[0.4, 0.2, 0.4]
    )[0]
    start = datetime.combine(
        random_date_between(date(2023, 1, 1), date.today()),
        datetime.min.time(),
    ) + timedelta(seconds=random.randint(0, 86_399))
    plan = random.choice(config.PLAN_TYPES)
    network = random.choice(config.NETWORK_TYPES)

    duration = 0
    data_mb = 0.0
    sms = 0
    amount = 0.0

    if usage_type == "VOICE":
        duration = random.randint(10, 3_600)
        amount = round(duration / 60 * random.uniform(1.5, 4.0), 2)
    elif usage_type == "SMS":
        sms = random.randint(1, 50)
        amount = round(sms * random.uniform(0.5, 1.5), 2)
    else:  # DATA
        data_mb = round(random.uniform(1, 5_000), 2)
        amount = round(data_mb * random.uniform(0.05, 0.4), 2)

    return {
        "usage_id": f"USG{idx:08d}",
        "customer_id": cust_id,
        "msisdn": msisdn,
        "usage_type": usage_type,
        "usage_date": start.date(),
        "start_time": start.strftime("%H:%M:%S"),
        "duration_seconds": duration,
        "data_mb": data_mb,
        "sms_count": sms,
        "amount": amount,
        "plan_type": plan,
        "network_type": network,
        "cell_tower_id": f"TWR{random.randint(1, 5000):05d}",
        "created_at": start + timedelta(minutes=random.randint(1, 120)),
    }


def generate_mobile_usage(
    count: int, customers: pd.DataFrame
) -> pd.DataFrame:
    """Generate mobile usage records for a subset of customers."""
    log_section("Generating mobile usage")
    faker = get_faker()

    eligible = customers[customers["segment"].str.startswith("mobile", na=False)]
    if eligible.empty:
        eligible = customers
    cust_ids = eligible["customer_id"].dropna().astype(str).tolist()

    msisdn_cache = {cid: fake_kenyan_msisdn(faker) for cid in cust_ids}

    records = []
    for i in range(count):
        cid = random.choice(cust_ids)
        records.append(_row(i, cid, msisdn_cache[cid]))

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s mobile usage records", len(df))

    rate = config.DirtyRates.mobile

    # Exact + key duplicates
    df = qc.duplicate_rows_exact(df, rate * 0.5)
    df = qc.duplicate_rows_key(
        df, "usage_id", rate * 0.5,
        mutate={"created_at": lambda v: v + timedelta(seconds=random.randint(1, 300))},
    )

    # Nulls / orphans
    df = qc.set_missing(df, ["customer_id", "amount", "msisdn", "network_type"], rate)
    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)

    # Negative / zero metrics
    df = qc.negative_values(df, "duration_seconds", rate * 0.3)
    df = qc.negative_values(df, "amount", rate * 0.3)

    # Future dates
    df = qc.future_dates(df, "usage_date", rate * 0.2, days_ahead=180)

    # Categorical corruption
    df = qc.corrupt_column(
        df, "network_type", rate * 0.5,
        lambda _: random.choice(config.INVALID_NETWORK_TYPES),
    )
    df = qc.corrupt_column(
        df, "usage_type", rate * 0.3,
        lambda v: qc.categorical_corrupt(v, config.USAGE_TYPES),
    )

    # Invalid MSISDN formats
    df = qc.corrupt_column(
        df, "msisdn", rate * 0.4,
        lambda _: random.choice(["0000000000", "+254-ABC-DEFG", "N/A", ""]),
    )

    # Whitespace
    df = qc.corrupt_column(df, "plan_type", rate * 0.3, qc.whitespace_or_case)

    return df