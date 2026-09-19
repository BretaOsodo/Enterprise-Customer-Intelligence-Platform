from __future__ import annotations 

import logging 
from dataclasses import dataclass, field
from os import path
from pathlib import Path
from typing import Dict, List

#paths 
PROJECT_ROOT:Path = Path(__file__).resolve().parent.parent
DATA_ROOT: Path = PROJECT_ROOT/"data" /"raw"
REPORT_PATH:Path=DATA_ROOT/ "data_quality_report.json"

DEFAULT_SEED:int = 42

#Row Counts

@dataclass
class Counts:
    customers: int =10_000
    mobile_usage:int= 10_000
    financial_transactions: int = 10_000
    credit_accounts: int =20_000
    fiber_subscriptions: int =5_000
    fiber_usage: int = 200_000
    device_purchases: int =30_000
    enterprise_services:int = 5_000
    digital_services: int = 100_000


#dirty data ratios per datasets 

@dataclass
class DirtyRates:
    customers: float = 0.08
    mobile : float = 0.05
    financial: float = 0.05
    credit: float = 0.07
    fiber: float= 0.05
    fiber_usage: float = 0.04
    devices: float = 0.05
    enterprise: float = 0.04
    digital_services:float=0.05

#Orphan-record rate applied to downstream fact tables 
ORPHAN_RATES: float = 0.015

#Kenyan reference data 
COUNTIES: List[str] = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Kiambu", "Machakos",
    "Kajiado", "Uasin Gishu", "Kakamega", "Meru", "Nyeri", "Kilifi",
    "Bungoma", "Kisii", "Homa Bay", "Siaya", "Migori", "Kitui",
    "Embu", "Murang'a",
]

COUNTY_TOWNS: Dict[str, List[str]] = {
    "Nairobi": ["Westlands", "Karen", "Kasarani", "Embakasi", "Langata", "CBD"],
    "Mombasa": ["Nyali", "Bamburi", "Likoni", "Mvita", "Kisauni"],
    "Kisumu": ["Milimani", "Kondele", "Nyalenda", "Mamboleo"],
    "Nakuru": ["Milimani", "Lanet", "Njoro", "Naivasha"],
    "Kiambu": ["Thika", "Ruiru", "Kikuyu", "Limuru", "Juja"],
    "Machakos": ["Machakos Town", "Athi River", "Mlolongo", "Kangundo"],
    "Kajiado": ["Kitengela", "Ngong", "Ongata Rongai", "Rongai"],
    "Uasin Gishu": ["Eldoret", "Burnt Forest", "Turbo"],
    "Kakamega": ["Kakamega Town", "Mumias", "Butere"],
    "Meru": ["Meru Town", "Maua", "Nkubu"],
    "Nyeri": ["Nyeri Town", "Karatina", "Othaya"],
    "Kilifi": ["Malindi", "Watamu", "Kilifi Town"],
    "Bungoma": ["Bungoma Town", "Webuye", "Kimilili"],
    "Kisii": ["Kisii Town", "Ogembo", "Keroka"],
    "Homa Bay": ["Homa Bay Town", "Mbita", "Oyugis"],
    "Siaya": ["Siaya Town", "Bondo", "Ugunja"],
    "Migori": ["Migori Town", "Kehancha", "Awendo"],
    "Kitui": ["Kitui Town", "Mwingi", "Mutomo"],
    "Embu": ["Embu Town", "Runyenjes", "Siakago"],
    "Murang'a": ["Murang'a Town", "Kenol", "Kangema"],
}

# Inconsistent representations used to simulate multi-system integration
COUNTY_VARIANTS: Dict[str, List[str]] = {
    "Nairobi": ["Nairobi", "nairobi", "NAIROBI", "Nairobi County", " Nairobi"],
    "Mombasa": ["Mombasa", "mombasa", "MOMBASA", "Mombasa County"],
    "Kisumu": ["Kisumu", "kisumu", "KISUMU", "Kisumu County"],
    "Nakuru":["Nakuru","nakuru","NAKURU"," Nakuru County"],
    "Kiambu": ["Kiambu","kiambu","KIAMBU","Kiambu County"],
    "Machakos":["MAchakos", "machakos", "MACHAKOS","Machakos County"],
    "Kajiado":["Kajiado","kajiado", "KAJIADO","Kajiado County"],
    "Uasin Gishu":["Uasin Gishu","uasin gishu","Uasin Gishu County","UASIN GISHU"],
    "Kakamega":["Kakamega","kakamega","Kakamega County","KAKAMEGA COUNTY"],
    "Meru":["Meru","meru","Meru County","MERU"],
    "Nyeri":["Nyeri","nyeri","Nyeri County","NYERI"],
    "Kilifi":["Kilifi","kilifi","Kilifi County", "KILIFI"],
    "Bungoma":["Bungoma","Bungoma County","bungoma","BUNGOMA"],
    "Kisii":["kISII","Kisii","Kisii County","kisii"],
    'Homa bay':["HomaBay","Homa Bay","HOMABAY","HOMA BAY COUNTY", "homa bay "],
    "Siaya":["Siaya", "SIAYA", "Siaya County","siaya"],
    "Migori":["Migori","migori","MIGORI","Migori COunty"],
    "Kitui":["Kitui","kitui","Kitui County","KITUI"],
    "Embu":["Embu","embu","EMBU","Embu County"],
    "Murang'a":["Murang'a","murang'a","Murang'a County", "MURANG'A"]
}

CUSTOMER_TYPES: List[str] = ["INDIVIDUAL", "BUSINESS", "SME", "CORPORATE"]
CUSTOMER_STATUSES: List[str] = ["ACTIVE", "INACTIVE", "SUSPENDED", "CLOSED"]

GENDERS: List[str] = ["Male", "Female"]
GENDER_VARIANTS: List[str] = ["Male", "male", "M", "MALE",
                              "Female", "female", "F", "FEMALE"]

USAGE_TYPES: List[str] = ["VOICE", "SMS", "DATA"]
PLAN_TYPES: List[str] = ["PREPAID", "POSTPAID"]
NETWORK_TYPES: List[str] = ["3G", "4G", "5G"]
INVALID_NETWORK_TYPES: List[str] = ["2G", "LTE", "WIFI", "UNKNOWN", "5g "]

TXN_TYPES: List[str] = ["P2P_TRANSFER", "MERCHANT_PAYMENT", "DEPOSIT", "WITHDRAWAL"]
TXN_CHANNELS: List[str] = ["USSD", "APP", "AGENT", "STK_PUSH", "WEB"]
TXN_STATUSES: List[str] = ["SUCCESS", "FAILED", "REVERSED", "PENDING"]

CREDIT_PRODUCTS: List[str] = ["OVERDRAFT", "PERSONAL_LOAN", "BUSINESS_CREDIT"]
CREDIT_STATUSES: List[str] = ["ACTIVE", "CLOSED", "DEFAULTED", "SUSPENDED"]

FIBER_PLANS: Dict[str, Dict[str, int]] = {
    "HOME_10_MBPS":  {"speed": 10,  "fee": 2_500},
    "HOME_20_MBPS":  {"speed": 20,  "fee": 3_500},
    "HOME_40_MBPS":  {"speed": 40,  "fee": 4_500},
    "HOME_60_MBPS":  {"speed": 60,  "fee": 5_500},
    "HOME_100_MBPS": {"speed": 100, "fee": 7_500},
    "HOME_200_MBPS": {"speed": 200, "fee": 12_000},
}
FIBER_STATUSES: List[str] = ["ACTIVE", "SUSPENDED", "TERMINATED"]

DEVICE_TYPES: List[str] = ["SMARTPHONE", "ROUTER", "TABLET", "ACCESSORY"]
DEVICE_MANUFACTURERS: List[str] = [
    "Samsung", "Apple", "Tecno", "Infinix", "Xiaomi", "Nokia", "Huawei",
]
PAYMENT_METHODS: List[str] = ["CASH", "CARD", "MOBILE_MONEY", "FINANCING"]
FINANCING_STATUSES: List[str] = ["NONE", "ACTIVE", "COMPLETED", "DEFAULTED"]

ENTERPRISE_SERVICES: Dict[str, Dict[str, int]] = {
    "DEDICATED_INTERNET": {"fee": 45_000},
    "CLOUD":              {"fee": 30_000},
    "WEB_HOSTING":        {"fee": 12_000},
    "CYBERSECURITY":      {"fee": 80_000},
    "BULK_MESSAGING":     {"fee": 25_000},
}
ENTERPRISE_STATUSES: List[str] = ["ACTIVE", "SUSPENDED", "TERMINATED"]

DIGITAL_SERVICES: Dict[str, Dict[str, int]] = {
    "MUSIC":               {"fee": 300},
    "SUPER_APP":           {"fee": 200},
    "DIGITAL_AGRICULTURE": {"fee": 500},
}
DIGITAL_STATUSES: List[str] = ["ACTIVE", "INACTIVE", "CANCELLED"]

# Customer-segment probabilities (used to keep product ownership realistic)
SEGMENT_PROBS: Dict[str, float] = {
    "mobile_only": 0.40,
    "mobile_financial": 0.20,
    "mobile_financial_credit": 0.12,
    "mobile_fiber": 0.08,
    "mobile_financial_fiber": 0.06,
    "mobile_device": 0.06,
    "mobile_financial_device_fiber": 0.04,
    "business_enterprise": 0.03,
    "business_financial": 0.01,
}

ORPHAN_IDS: List[str] = [
    "CUST999999", "CUST888888", "INVALID001", "UNKNOWN_CUSTOMER",
    "CUST000000", "ORPHAN-XYZ",
]

#Logging
LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_LEVEL: int = logging.INFO

def ensure_directories() -> None:
    """Create the raw data output tree if it does not exst"""
    subdirs = [
        "customers", "mobile", "financial", "credit", "fiber",
        "devices", "enterprise", "digital"
    ]

    DATA_ROOT.mkdir(parents=True, exist_ok= True)
    for sub in subdirs:
        (DATA_ROOT/sub).mkdir(parents=True, exist_ok=True)

def configure_logging()-> None:
    """Configure root logger ones for te whole run."""
    logging.basicConfig(level= LOG_LEVEL,format=LOG_FORMAT)