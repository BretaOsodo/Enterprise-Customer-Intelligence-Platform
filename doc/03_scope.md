# Project Scope

## 1. Purpose

This document defines what is included in and excluded from the KenyaFintech
Customer 360 Data Platform.

The scope is intentionally designed to produce a realistic but manageable
data engineering project.

---

# 2. In Scope

## 2.1 Synthetic Data Generation

The project will generate synthetic data representing KenyaFintech's business
domains.

The data will include:

- Customers
- Mobile usage
- Financial transactions
- Credit
- Fiber
- Devices
- Enterprise services
- Digital services

No real customer information will be used.

---

# 2.2 Amazon S3 Data Lake

Amazon S3 will be used to store raw customer-domain data.

Example structure:

```text
customer360-data/
│
├── raw/
│   ├── customers/
│   ├── mobile/
│   ├── mpesa/
│   ├── credit/
│   ├── fiber/
│   ├── devices/
│   ├── enterprise/
│   └── digital_services/
│
└── airflow-logs/