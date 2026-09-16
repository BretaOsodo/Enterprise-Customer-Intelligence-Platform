
import json
import logging 
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional 

import numpy as np  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
from faker import Faker 

from . import config 

logger =  logging.getLogger(__name__)

_FAKER: Optional[Faker] = None

def get_faker(seed: int = config.DEFAULT_SEED) -> Faker:
    """Get a singleton instance of Faker with a specific seed."""
    global _FAKER
    if _FAKER is None:
        try:
            _FAKER = Faker("en_KE")
        except Exception:
            _FAKER = Faker()
        Faker.seed(seed)
        random.seed(seed)
        np.random.seed(seed)
    return _FAKER


def reseed(seed: int)-> None:
    """Reset all RNGs to a dterministic state"""
    random.seed(seed)
    np.random.seed(seed)
    Faker.seed(seed)

#Kenya Phone Number / Identification fabrication 

def kenyan_phone_formats(local:str)-> List[str]:

    national=  local[1:] # drop leading 0 -> 0797626066
    return [
        local,
        f"+254{national}",
        f"254{national}",
        f"+254 {national[:3]} {national[3:6]} {national[6:]}",
        f"0{national[:3]} {national[3:6]} {national[6:]}",
        f"254-{national[:3]}-{national[3:]}",
    ]

def fake_kenyan_msisdn(faker:Faker, dirty:bool = False)-> str:
    """generate a Kenyan-styl;e phone numer, optionally in a dirty formart"""

    prefix= random.choice(["70", "71", "72", "74", "75", "76", "79", "11", "10"])

    local = f"0{prefix}{random.randint(1000000,9999999)}"
    if dirty:
        return random.choice(kenyan_phone_formats(local))
    return local

def invalid_phone_samples()-> List[str]:
    return [
         "0000000000", "12345", "+254-ABC-DEFG", "N/A", "", "0700",
        "+254 700 000", "phone_missing",
    ]

def fake_email(faker:Faker, first: str, last:str)-> str:
    domain= random.choice(["gmail.com", "yahoo.com"])
    sep= random.choice([".", "_", ""])
    local= f"{first.lower()}{sep}{last.lower()}{random.randint(1, 999)}"

    return f"{local}@{domain}"

def corrupt_email(email:str)->str:
    """Introducew a realistic email corruption"""
    kind= random.choice([
        "upper", "space_before_at", "no_tld", "double_at", "trailing_dot",
    ])

    if kind == "upper":
        return email.upper()
    if kind == "space_before_at":
        return email.replace("@"," @")
    if kind == "no_tld":
        return email.rsplit(".",1)[0]
    if kind == 'double_at':
        return email.replace("@","@@")
    return email + "."

#Dates 
def random_date_between(start:date,end:date, rng:Optional[np.random.Generator] = None) -> date:
    """return a random date in start and end """

    rng= rng or np.random.default_rng()
    delta = (end-start).days
    return start + timedelta(days = int(rng.integers(0,max(delta,1))))

def iso(dt: Any)-> str:
    if isinstance (dt,(datetime, pd.Timestamp)):
        return dt.isoformat(sep=" ")
    if isinstance(dt, date):
        return dt.isoformat()
    return str(dt)

#Text corruption 
def random_case (text: str)-> str:
    if not text:
        return text 
    choice = random.random()

    if choice < 0.4:
        return text

    if choice < 0.6:
        return text.lower()

    if choice < 0.8:
        return text.upper()

    return text.title()

def pad_whitespace(text: str)->str:
    """Add leading / trailing whitespace"""
    return random.choice([" ", "  ", "\t"]) + str(text) + random.choice([" ", "  "])

def inject_dirty_rows(
        df: pd.DataFrame,
        columns: Iterable[str],
        rate: float,
        corruptor
) -> pd.DataFrame:

    df = df.copy()
    n = max(1,int(len(df)* rate))
    idx= np.random.choice(df.index, size=min(n,len(df)),replace= False)
    cols= list(columns)
    for i in idx:
        col= random.choice(cols)
        df.at[i, col]=corruptor(df.at[i, col])
    return df

#Io + reporting 

def save_csv(df: pd.DataFrame, path: Path, log: bool = True) -> Path:
    """Persist ``df`` to CSV, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    if log:
        logger.info("Saved %s rows to %s", len(df), path)
    return path


def save_parquet(df: pd.DataFrame, path: Path) -> Path:
    """Optional Parquet writer (requires pyarrow)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.info("Saved %s rows to %s", len(df), path)
    return path


def quality_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute dirty-data descriptive stats for the report."""
    return {
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "duplicate_count": int(df.duplicated().sum()),
        "null_counts": {c: int(df[c].isna().sum()) for c in df.columns},
        "unique_counts": {c: int(df[c].nunique(dropna=True)) for c in df.columns},
    }

class QualityReport:

    def __init__(self)-> None:
        self.datasets: Dict[str, Dict[str, Any]]= {}

    def add(self,name:str, df:pd.DataFrame)-> None:
        self.datasets[name]= quality_stats(df)

    def write(self, path: Path = config.REPORT_PATH)-> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding ="utf-8") as fh:
            json.dump(self.datasets, fh, indent=2, default = str)
        logger.info('Wrote Quality report to %s',path)
def log_section(title: str) -> None:
    """Log a visible section header."""
    logger.info("%s", title)

