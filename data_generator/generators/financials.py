"""Financial (M-PESA-style) transaction generator."""

from __future__ import annotations

import logging
import random
from datetime import date, datetime, timedelta
from typing import Dict

import numpy as np
import pandas as pd

from .. import config
from ..quality import corruptions as qc
from ..utils import get_faker, log_section, random_date_between

logger = logging.getLogger(__name__)


def _amount_for(txn_type: str) -> float:
    if txn_type in ("P2P_TRANSFER", "MERCHANT_PAYMENT"):
        return round(random.uniform(10, 50_000), 2)
    if txn_type == "DEPOSIT":
        return round(random.uniform(50, 100_000), 2)
    return round(random.uniform(100, 40_000), 2)  # WITHDRAWAL


def _fee_for(txn_type: str, amount: float) -> float:
    if txn_type in ("P2P_TRANSFER", "WITHDRAWAL"):
        return round(min(amount * 0.015, 110), 2)
    return 0.0


def generate_financial_transactions(
    count: int, customers: pd.DataFrame
) -> pd.DataFrame:
    """Generate financial transactions with realistic balance relationships."""
    log_section("Generating financial transactions")
    faker = get_faker()

    eligible = customers[
        customers["segment"].str.contains("financial", na=False)
        & customers["segment"].str.startswith("mobile", na=False)
    ]
    if eligible.empty:
        eligible = customers
    cust_ids = eligible["customer_id"].dropna().astype(str).tolist()

    # Track a rolling balance per customer for plausible before/after pairs
    balances: Dict[str, float] = {
        cid: round(random.uniform(500, 200_000), 2) for cid in cust_ids
    }

    records = []
    for i in range(count):
        cid = random.choice(cust_ids)
        txn_type = random.choices(
            config.TXN_TYPES, weights=[0.4, 0.35, 0.15, 0.1]
        )[0]
        amount = _amount_for(txn_type)
        fee = _fee_for(txn_type, amount)
        before = balances[cid]

        if txn_type in ("P2P_TRANSFER", "WITHDRAWAL", "MERCHANT_PAYMENT"):
            after = max(0.0, before - amount - fee)
        else:  # DEPOSIT
            after = before + amount

        balances[cid] = after

        ts = datetime.combine(
            random_date_between(date(2023, 1, 1), date.today()),
            datetime.min.time(),
        ) + timedelta(seconds=random.randint(0, 86_399))

        records.append({
            "transaction_id": f"TXN{i:010d}",
            "customer_id": cid,
            "transaction_type": txn_type,
            "transaction_date": ts.date(),
            "amount": amount,
            "fee": fee,
            "balance_before": round(before, 2),
            "balance_after": round(after, 2),
            "counterparty_id": (
                f"CUST{random.randint(1, 10_000):06d}" if txn_type == "P2P_TRANSFER" else None
            ),
            "merchant_id": (
                f"MERCH{random.randint(1, 5_000):05d}"
                if txn_type == "MERCHANT_PAYMENT" else None
            ),
            "channel": random.choice(config.TXN_CHANNELS),
            "transaction_status": random.choices(
                config.TXN_STATUSES, weights=[0.88, 0.06, 0.03, 0.03]
            )[0],
            "location": faker.city(),
            "created_at": ts + timedelta(seconds=random.randint(1, 60)),
        })

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s financial transactions", len(df))

    rate = config.DirtyRates.financial

    # Duplicates: exact + key (different timestamp)
    df = qc.duplicate_rows_exact(df, rate * 0.4)
    df = qc.duplicate_rows_key(
        df, "transaction_id", rate * 0.4,
        mutate={"created_at": lambda v: v + timedelta(seconds=random.randint(5, 600))},
    )

    # Orphans and nulls
    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)
    df = qc.set_missing(df, ["customer_id", "amount", "fee"], rate)

    # Negative amounts / fees
    df = qc.negative_values(df, "amount", rate * 0.3)
    df = qc.negative_values(df, "fee", rate * 0.2)

    # Future transaction dates
    df = qc.future_dates(df, "transaction_date", rate * 0.2, days_ahead=90)

    # Categorical corruption
    df = qc.corrupt_column(
        df, "transaction_status", rate * 0.4,
        lambda v: qc.categorical_corrupt(v, config.TXN_STATUSES),
    )
    df = qc.corrupt_column(
        df, "transaction_type", rate * 0.3,
        lambda v: qc.categorical_corrupt(v, config.TXN_TYPES),
    )
    df = qc.corrupt_column(df, "channel", rate * 0.3, qc.whitespace_or_case)

    return df