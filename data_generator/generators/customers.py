from __future__ import annotations
import logging 
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd 
from faker import Faker 

from .. import config
from ..quality import corruptions as qc
from ..utils import (
    fake_email,
    fake_kenyan_msisdn,
    get_faker,
    log_section,
    random_date_between,
    save_csv
)

logger =  logging.getLogger(__name__)


def _gender_variant(gender: str)-> str:
    mapping ={
        "Male":["Male", "male", "M", "MALE"],
        "Female": ["Female", "female", "F", "FEMALE"],
    }

    return random.choice(mapping.get(gender, [gender]))

def _county_variant(county: str)-> str:
    variants = config.COUNTY_VARIANTS.get(county)

    if variants  and random.random()< 0.7:
        return random.choice(variants)

    return county

def generate_customers(counts: int)-> pd.DataFrame:
    faker: Faker = get_faker()

    records=[]
    for i in range(counts):
        customer_id=f"CUST{i + 1:06d}"
        gender = random.choice(config.GENDERS)
        first= faker.first_name_male() if gender == "Male" else faker.first_name_female()
        last = faker.last_name()
        county= random.choice(config.COUNTIES)
        town = random.choice(config.COUNTY_TOWNS.get(county,["Unknown"]))
        customer_type= random.choices(
            config.CUSTOMER_TYPES, weights=[0.7,0.15,0.1,0.05]
        )[0]
        status = random.choices(
            config.CUSTOMER_STATUSES, weights=[0.75,0.1,0.1,0.05]
        )[0]
        reg_date = random_date_between(date(2018, 1, 1), date.today())
        created= reg_date 
        updated= reg_date + timedelta(days= random.randint(0,365))

        records.append({
            "customer_id": customer_id,
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}",
            "gender": gender,
            "date_of_birth": random_date_between(date(1955, 1, 1), date(2005, 12, 31)),
            "phone_number": fake_kenyan_msisdn(faker),
            "email": fake_email(faker, first, last),
            "county": county,
            "town": town,
            "customer_type": customer_type,
            "registration_date": reg_date,
            "customer_status": status,
            "created_at": created,
            "updated_at": updated,
        })

    df = pd.DataFrame.from_records(records)
    logger.info('genrated %s customers')

    #Dirty-data injection 
    rate= config.DirtyRates.customers

    #Near-duplicated customers: Same person, different formattinf 
    dupes = df.sample(n=max(1, int(len(df)* rate*0.5)), random_state=1).copy()

    for i in range( len(dupes)):
        dupes.iloc[i, dupes.columns.get_loc("full_name")]=random.choice([
            dupes.iloc[i]["full_name"].lower(),
            dupes.iloc[i]["full_name"].upper(),
            dupes.iloc[i]["full_name"].replace(" ", "  ")
        ])
        dupes.iloc[i, dupes.columns.get_loc("phone_number")]= random.choice(
            ["0712 345 678", "+254 712 345 678", "254712345678", "0712-345-678"]
        )

    df = pd.concat([df,dupes], ignore_index=True)

    #Inconsistent gender formatting 
    df= qc.corrupt_column(df,"gender", rate, _gender_variant)

    # Inconsistent county representations
    df = qc.corrupt_column(df, "county", rate, _county_variant)

    # Whitespace / case on names
    df = qc.corrupt_column(df, "first_name", rate * 0.5, qc.whitespace_or_case)
    df = qc.corrupt_column(df, "last_name", rate * 0.5, qc.whitespace_or_case)

    # Invalid phone numbers
    df = qc.corrupt_column(
        df, "phone_number", rate * 0.4, lambda _: random.choice(
            ["0000000000", "12345", "+254-ABC-DEFG", "N/A", ""]
        )
    )

    # Invalid emails
    def _bad_email(value):
        return random.choice([
            str(value).upper(),
            str(value).replace("@", " @"),
            str(value).rsplit(".", 1)[0],
            "not-an-email",
        ])

    df = qc.corrupt_column(df, "email", rate * 0.4, _bad_email)

    # Nulls across a few columns
    df = qc.set_missing(
        df, ["email", "town", "county", "phone_number", "date_of_birth"], rate * 0.6
    )

    # Corrupt customer_status / customer_type
    df = qc.corrupt_column(
        df, "customer_status", rate * 0.3,
        lambda v: qc.categorical_corrupt(v, config.CUSTOMER_STATUSES),
    )
    df = qc.corrupt_column(
        df, "customer_type", rate * 0.3,
        lambda v: qc.categorical_corrupt(v, config.CUSTOMER_TYPES),
    )

    # Invalid customer_id (malformed) on a tiny slice
    def _bad_id(value):
        return random.choice(["CUST999999", "INVALID001", "", "UNKNOWN_CUSTOMER"])

    df = qc.corrupt_column(df, "customer_id", rate * 0.2, _bad_id)

    logger.info("Customers dirty: %s rows, %s cols", df.shape[0], df.shape[1])
    return df

def assign_segments(customers: pd.DataFrame) -> pd.DataFrame:
    """Assign each customer a product segment used to drive downstream tables."""
    rng = np.random.default_rng(config.DEFAULT_SEED)
    segments = list(config.SEGMENT_PROBS.keys())
    probs = list(config.SEGMENT_PROBS.values())

    customer_ids = customers["customer_id"].dropna().unique()
    seg = rng.choice(segments, size=len(customer_ids), p=probs)
    seg_df = pd.DataFrame({"customer_id": customer_ids, "segment": seg})
    return customers.merge(seg_df, on="customer_id", how="left")