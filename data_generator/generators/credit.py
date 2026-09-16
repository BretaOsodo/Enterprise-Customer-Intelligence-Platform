"""Credit account generator."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta

import pandas as pd

from .. import config
from ..quality import corruptions as qc
from ..utils import get_faker, log_section, random_date_between

logger = logging.getLogger(__name__)


def generate_credit_accounts(
    count: int, customers: pd.DataFrame
) -> pd.DataFrame:
    """Generate credit accounts for customers in credit segments."""
    log_section("Generating credit accounts")
    get_faker()

    eligible = customers[customers["segment"].str.contains("credit", na=False)]
    if eligible.empty:
        eligible = customers
    cust_ids = eligible["customer_id"].dropna().astype(str).tolist()

    records = []
    for i in range(count):
        cid = random.choice(cust_ids)
        product = random.choice(config.CREDIT_PRODUCTS)
        limit = round(random.uniform(1_000, 500_000), 2)
        borrowed = round(random.uniform(0, limit), 2)
        repaid = round(random.uniform(0, borrowed), 2)
        outstanding = round(borrowed - repaid, 2)
        opened = random_date_between(date(2020, 1, 1), date.today())
        due = opened + timedelta(days=random.randint(30, 730))

        records.append({
            "credit_account_id": f"CRD{i:07d}",
            "customer_id": cid,
            "product_type": product,
            "credit_limit": limit,
            "amount_borrowed": borrowed,
            "amount_repaid": repaid,
            "outstanding_balance": outstanding,
            "interest_rate": round(random.uniform(5.0, 24.0), 2),
            "opened_date": opened,
            "due_date": due,
            "status": random.choices(
                config.CREDIT_STATUSES, weights=[0.7, 0.2, 0.05, 0.05]
            )[0],
            "created_at": opened,
            "updated_at": opened + timedelta(days=random.randint(1, 365)),
        })

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s credit accounts", len(df))

    rate = config.DirtyRates.credit

    # Duplicates
    df = qc.duplicate_rows_exact(df, rate * 0.3)
    df = qc.duplicate_rows_key(
        df, "credit_account_id", rate * 0.3,
        mutate={"updated_at": lambda v: v + timedelta(days=1)},
    )

    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)
    df = qc.set_missing(df, ["customer_id", "outstanding_balance", "credit_limit"], rate)

    # Impossible values
    df = qc.negative_values(df, "credit_limit", rate * 0.2)
    df = qc.negative_values(df, "amount_borrowed", rate * 0.2)

    # Break outstanding_balance relationship
    def _break_balance(row):
        return row["outstanding_balance"] * random.choice([-1, 2, 0.5])

    if not df.empty:
        idx = df.sample(frac=rate * 0.2, random_state=7).index
        for i in idx:
            try:
                df.at[i, "outstanding_balance"] = _break_balance(df.loc[i])
            except Exception:
                df.at[i, "outstanding_balance"] = -1

    # Due before opened
    if not df.empty:
        idx = df.sample(frac=rate * 0.2, random_state=11).index
        for i in idx:
            df.at[i, "due_date"] = df.at[i, "opened_date"] - timedelta(days=30)

    df = qc.future_dates(df, "opened_date", rate * 0.15, days_ahead=180)

    df = qc.corrupt_column(
        df, "status", rate * 0.4,
        lambda v: qc.categorical_corrupt(v, config.CREDIT_STATUSES),
    )
    df = qc.corrupt_column(
        df, "product_type", rate * 0.3,
        lambda v: qc.categorical_corrupt(v, config.CREDIT_PRODUCTS),
    )

    return df