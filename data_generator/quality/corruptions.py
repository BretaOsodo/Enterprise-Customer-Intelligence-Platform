from __future__ import annotations

import logging 
import random 
from datetime import date, timedelta
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np
import pandas as pd 

from .. import config

logger = logging.getLogger(__name__)

#Row-level Helpers 
def duplicate_rows_exact(df: pd.DataFrame, rate: float)-> pd.DataFrame:
    if df.empty:
        return df
    n= max(1, int(len(df)* rate))
    sample = df.sample(n=min(n, len(df)), random_state=random.randint(0,10**6))

    logger.info("Introduced %s exact duplicates rows", len(sample))
    return pd.concat([df,sample], ignore_index=True)

def duplicate_rows_key(
        df: pd.DataFrame,
        key: str,
        rate: float,
        mutate: Optional[Dict[str, Callable[[Any], Any]]] = None
) -> pd.DataFrame:
    if df.empty:
        return df
    n= max(1, int(len(df)* rate))
    sample = df.sample(n=min(n, len(df)), random_state=random.randint(0,10**6))

    if mutate:
        for col, func in mutate.items():
            if col in sample.columns:
                sample[col] = sample[col].apply(func)

    logger.info("Introduced %s key-duplicate rows", len(sample))
    return pd.concat([df,sample], ignore_index=True)

def corrupt_column(
        df: pd.DataFrame,
        column: str,
        rate: float,
        corruptor: Callable[[Any], Any]
) -> pd.DataFrame:

    if column not in df.columns or df.empty:
        return df
    df = df.copy()
    n= max(1, int(len(df)* rate))
    idx= np.random.choice(df.index, size=min(n,len(df)),replace= False)
    for i in idx:
        df.at[i,column] = corruptor(df.at[i,column])
    logger.info("Corrupted %s values in column %s", len(idx), column)
    return df

def set_missing(df: pd.DataFrame, columns: Sequence[str], rate: float) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    n= max(1, int(len(df)* rate))
    idx= np.random.choice(df.index, size=min(n,len(df)),replace= False)
    for i in idx:
        col= random.choice(columns)
        df.at[i, col]= None

    logger.info("Introduced nulls into %s rows", len(idx))
    return df

def inject_orphans(
        df: pd.DataFrame,
        customer_col : str ="customer_id",
        rate: float = config.ORPHAN_RATES
)-> pd.DataFrame:
    """Replace a fraction of customer ids with non-existent ones"""

    if customer_col not in df.columns or df.empty:
        return df
    df = df.copy()
    n=max(1, int(len(df)*rate))
    idx= np.random.choice(df.index, size=min(n, len(df)), replace=False)
    for i in idx:
        df.at[i, customer_col]=random.choice(config.ORPHAN_IDS)

    logger.info("Injected %s orphan customer ids", len(idx))
    return df

def future_dates(
        df:pd.DataFrame, column: str, rate: float, days_ahead: int=365
)-> pd.DataFrame:
    if column not in df.columns or df.empty:
        return df
    df = df.copy()
    n= max(1, int(len(df)* rate))
    idx = np.random.choice(df.index, size= min(n, len(df)), replace= False)
    future= date.today() + timedelta(days = days_ahead)
    for i in idx:
        df.at[i,column]=future
    logger.info("Set %s future dates in %s", len(idx), column)
    return df

def negative_values(df: pd.DataFrame, column: str, rate: float) -> pd.DataFrame:
    """Flip a fraction of numeric values to their negative counterpart."""
    if column not in df.columns or df.empty:
        return df
    df = df.copy()
    n = max(1, int(len(df) * rate))
    idx = np.random.choice(df.index, size=min(n, len(df)), replace=False)
    for i in idx:
        try:
            df.at[i, column] = -abs(float(df.at[i, column]))
        except (TypeError, ValueError):
            df.at[i, column] = -1.0
    logger.info("Negated %s values in '%s'", len(idx), column)
    return df



# Categorical string corruption

def categorical_corrupt(value: Any, valid: Sequence[str]) -> Any:
    """Return a plausible but invalid categorical variant of ``value``."""
    if pd.isna(value):
        return value
    kind = random.choice(["case", "space", "invalid"])
    if kind == "case":
        return random.choice([str(value).lower(), str(value).upper()])
    if kind == "space":
        return f" {value} "
    invalids = ["UNKNOWN", "N/A", "", "???", "NONE", "INVALID"]
    return random.choice(invalids)


def whitespace_or_case(value: Any) -> Any:
    """Return a whitespace/case-mutated version of ``value``."""
    if pd.isna(value):
        return value
    return random.choice([
        str(value).strip().lower(),
        str(value).strip().upper(),
        f" {value}",
        f"{value} ",
        f"  {value}  ",
    ])