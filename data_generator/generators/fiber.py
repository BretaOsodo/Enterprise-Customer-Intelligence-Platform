"""Fiber (home internet) subscriptions and usage generator."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta

import pandas as pd

from .. import config
from ..quality import corruptions as qc
from ..utils import get_faker, log_section, random_date_between

logger = logging.getLogger(__name__)


def generate_fiber_subscriptions(
    count: int, customers: pd.DataFrame
) -> pd.DataFrame:
    """Generate fiber subscriptions for eligible customers."""
    log_section("Generating fiber subscriptions")
    get_faker()

    eligible = customers[customers["segment"].str.contains("fiber", na=False)]
    if eligible.empty:
        eligible = customers
    cust_ids = eligible["customer_id"].dropna().astype(str).tolist()

    records = []
    for i in range(count):
        cid = random.choice(cust_ids)
        plan = random.choice(list(config.FIBER_PLANS.keys()))
        meta = config.FIBER_PLANS[plan]
        install = random_date_between(date(2021, 1, 1), date.today())
        contract_end = install + timedelta(days=365)

        records.append({
            "subscription_id": f"FIB{i:07d}",
            "customer_id": cid,
            "plan_id": plan,
            "plan_name": plan.replace("_", " ").title(),
            "installation_date": install,
            "monthly_fee": meta["fee"],
            "speed_mbps": meta["speed"],
            "status": random.choices(
                config.FIBER_STATUSES, weights=[0.85, 0.1, 0.05]
            )[0],
            "contract_end_date": contract_end,
            "created_at": install,
            "updated_at": install + timedelta(days=random.randint(1, 365)),
        })

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s fiber subscriptions", len(df))

    rate = config.DirtyRates.fiber
    df = qc.duplicate_rows_exact(df, rate * 0.4)
    df = qc.duplicate_rows_key(
        df, "subscription_id", rate * 0.3,
        mutate={"updated_at": lambda v: v + timedelta(days=2)},
    )
    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)
    df = qc.set_missing(df, ["customer_id", "monthly_fee", "speed_mbps"], rate)
    df = qc.negative_values(df, "monthly_fee", rate * 0.2)
    df = qc.negative_values(df, "speed_mbps", rate * 0.2)
    df = qc.future_dates(df, "installation_date", rate * 0.2, days_ahead=180)
    df = qc.corrupt_column(
        df, "plan_id", rate * 0.3,
        lambda _: random.choice(["UNKNOWN_PLAN", "HOME_999", "INVALID"]),
    )
    df = qc.corrupt_column(df, "status", rate * 0.3, qc.whitespace_or_case)

    return df


def generate_fiber_usage(
    count: int, subscriptions: pd.DataFrame
) -> pd.DataFrame:
    """Generate fiber usage records tied to subscriptions."""
    log_section("Generating fiber usage")
    get_faker()

    sub_ids = subscriptions["subscription_id"].dropna().astype(str).tolist()
    cust_map = dict(zip(
        subscriptions["subscription_id"], subscriptions["customer_id"]
    ))

    records = []
    for i in range(count):
        sid = random.choice(sub_ids)
        usage_date = random_date_between(date(2023, 1, 1), date.today())
        data_gb = round(random.uniform(0.1, 500), 2)
        sessions = random.randint(1, 200)
        uptime = round(random.uniform(0.1, 24), 2)

        records.append({
            "usage_id": f"FUS{i:08d}",
            "customer_id": cust_map.get(sid),
            "subscription_id": sid,
            "usage_date": usage_date,
            "data_used_gb": data_gb,
            "session_count": sessions,
            "uptime_hours": uptime,
            "created_at": usage_date,
        })

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s fiber usage records", len(df))

    rate = config.DirtyRates.fiber_usage
    df = qc.duplicate_rows_exact(df, rate * 0.5)
    df = qc.duplicate_rows_key(
        df, "usage_id", rate * 0.3,
        mutate={"created_at": lambda v: v + timedelta(hours=1)},
    )
    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)
    df = qc.set_missing(df, ["customer_id", "data_used_gb"], rate)
    df = qc.negative_values(df, "data_used_gb", rate * 0.3)
    df = qc.negative_values(df, "uptime_hours", rate * 0.2)
    df = qc.corrupt_column(
        df, "subscription_id", rate * 0.3,
        lambda _: random.choice(["FIB999999", "INVALID_SUB", ""]),
    )
    df = qc.future_dates(df, "usage_date", rate * 0.15, days_ahead=90)

    return df