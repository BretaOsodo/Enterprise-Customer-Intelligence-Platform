# Business Requirements

## 1. Purpose

This document defines the business requirements for the KenyaFintech Customer 360
Data Platform.

The platform must provide a unified view of customers across the company's
telecommunications, financial, internet, device, enterprise, and digital
services.

---

# 2. Business Objective

The primary objective is to create a reliable centralized data platform that
allows KenyaFintech to understand its customers across multiple products and
services.

The platform should allow analysts and applications to answer questions such
as:

- Who is this customer?
- Which products does the customer use?
- How active is the customer?
- How much does the customer spend?
- How much financial activity does the customer have?
- Does the customer use home internet?
- Which devices does the customer own?
- Which digital services does the customer use?
- What is the customer's overall value to the business?

---

# 3. Functional Requirements

## BR-001: Unified Customer Identity

The system must maintain a unique `customer_id` that can be used to connect
records across business domains.

The same customer should be identifiable across:

- Mobile services
- Financial services
- Credit
- Fiber
- Devices
- Digital services
- Enterprise services

---

## BR-002: Customer Profile

The platform must maintain a centralized customer profile.

The profile should contain:

- Customer ID
- Customer name
- Customer type
- Location
- Registration date
- Customer status

---

## BR-003: Product Ownership

The platform must identify the products and services associated with each
customer.

Examples:

- Mobile line
- Mobile data package
- Fiber subscription
- Credit product
- Digital subscription
- Device
- Enterprise service

---

## BR-004: Mobile Usage

The platform must provide customer-level mobile usage metrics.

Required metrics include:

- Voice usage
- SMS usage
- Mobile data usage
- Number of usage events
- Last mobile activity

---

## BR-005: Financial Activity

The platform must provide a consolidated view of customer financial activity.

Required metrics include:

- Total transaction count
- Total transaction value
- P2P transaction value
- Merchant payment value
- Average transaction value
- Last transaction date

---

## BR-006: Credit Activity

The platform must provide visibility into customer credit products.

Required information includes:

- Credit account
- Credit limit
- Amount borrowed
- Amount repaid
- Outstanding balance
- Credit status

---

## BR-007: Fiber and Home Internet

The platform must provide customer-level information about home internet
services.

Required information includes:

- Fiber plan
- Subscription status
- Subscription start date
- Monthly fee
- Usage
- Last activity

---

## BR-008: Device Ownership

The platform must identify devices purchased by customers.

Required information includes:

- Device ID
- Device type
- Device model
- Purchase date
- Purchase value
- Financing status

---

## BR-009: Enterprise Services

The platform must support business customers using enterprise services.

Examples include:

- Dedicated internet
- Cloud services
- Web hosting
- Cybersecurity
- Bulk messaging

---

## BR-010: Digital Services

The platform must capture customer engagement with digital services.

Examples include:

- Music
- Super-app services
- Digital agriculture
- Other digital subscriptions

---

# 4. Customer-Level Metrics

The Customer 360 model should calculate useful customer-level metrics.

Examples:

```text
product_count
total_mobile_usage
total_transaction_value
transaction_count
credit_balance
fiber_monthly_value
device_spend
digital_service_count
total_customer_value
last_activity_date