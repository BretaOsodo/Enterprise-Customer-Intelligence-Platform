"""Device purchase generator."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta

import pandas as pd

from .. import config
from ..quality import corruptions as qc
from ..utils import get_faker, log_section, random_date_between

logger = logging.getLogger(__name__)

_MODELS = {
    "Samsung": ["Galaxy A14", "Galaxy A54", "Galaxy S23"],
    "Apple": ["iPhone 12", "iPhone 13", "iPhone 14"],
    "Tecno": ["Spark 10", "Camon 20", "Pop 7"],
    "Infinix": ["Hot 30", "Note 30", "Zero 5G"],
    "Xiaomi": ["Redmi 12", "Redmi Note 12", "Poco X5"],
    "Nokia": ["G21", "C32", "X30"],
    "Huawei": ["Nova 11i", "P60", "Y90"],
}


def generate_device_purchases(
    count: int, customers: pd.DataFrame
) -> pd.DataFrame:
    """Generate device purchases."""
    log_section("Generating device purchases")
    get_faker()

    eligible = customers[customers["segment"].str.contains("device", na=False)]
    if eligible.empty:
        eligible = customers
    cust_ids = eligible["customer_id"].dropna().astype(str).tolist()

    records = []
    for i in range(count):
        cid = random.choice(cust_ids)
        dtype = random.choices(
            config.DEVICE_TYPES, weights=[0.6, 0.15, 0.15, 0.1]
        )[0]
        manu = random.choice(config.DEVICE_MANUFACTURERS)
        model = random.choice(_MODELS.get(manu, ["Generic"]))
        purchase_date = random_date_between(date(2022, 1, 1), date.today())

        if dtype == "SMARTPHONE":
            amount = round(random.uniform(8_000, 120_000), 2)
        elif dtype == "ROUTER":
            amount = round(random.uniform(3_000, 20_000), 2)
        elif dtype == "TABLET":
            amount = round(random.uniform(15_000, 80_000), 2)
        else:
            amount = round(random.uniform(500, 5_000), 2)

        pay = random.choices(
            config.PAYMENT_METHODS, weights=[0.3, 0.1, 0.4, 0.2]
        )[0]
        fin = (
            random.choice(config.FINANCING_STATUSES)
            if pay == "FINANCING" else "NONE"
        )

        records.append({
            "purchase_id": f"DEV{i:07d}",
            "customer_id": cid,
            "device_id": f"MDL{random.randint(1, 99999):05d}",
            "device_type": dtype,
            "manufacturer": manu,
            "model": model,
            "purchase_date": purchase_date,
            "purchase_amount": amount,
            "payment_method": pay,
            "financing_status": fin,
            "created_at": purchase_date,
        })

    df = pd.DataFrame.from_records(records)
    logger.info("Generated %s device purchases", len(df))

    rate = config.DirtyRates.devices
    df = qc.duplicate_rows_exact(df, rate * 0.4)
    df = qc.duplicate_rows_key(
        df, "purchase_id", rate * 0.3,
        mutate={"created_at": lambda v: v + timedelta(hours=2)},
    )
    df = qc.inject_orphans(df, rate=config.ORPHAN_RATES)
    df = qc.set_missing(df, ["customer_id", "purchase_amount"], rate)
    df = qc.negative_values(df, "purchase_amount", rate * 0.3)
    df = qc.future_dates(df, "purchase_date", rate * 0.2, days_ahead=120)
    df = qc.corrupt_column(
        df, "device_type", rate * 0.4,
        lambda v: qc.categorical_corrupt(v, config.DEVICE_TYPES),
    )
    df = qc.corrupt_column(
        df, "manufacturer", rate * 0.3,
        lambda _: random.choice(["SAMSUNG", "samsung", "Unknown", "Nokia "]),
    )
    df = qc.corrupt_column(df, "payment_method", rate * 0.3, qc.whitespace_or_case)

    return df