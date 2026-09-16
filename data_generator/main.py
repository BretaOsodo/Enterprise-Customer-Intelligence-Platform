"""Entry point for the synthetic dirty data generator.

Usage examples
--------------
    python -m data_generator.main
    python -m data_generator.main --customers 50000
    python -m data_generator.main --seed 42
    python -m data_generator.main --customers 2000 --skip-financial
"""

from __future__ import annotations

import argparse
import logging
import time
from dataclasses import asdict
from pathlib import Path

from data_generator import config
from .utils import QualityReport, get_faker, log_section, reseed, save_csv

from .generators.customers import generate_customers, assign_segments
from .generators.mobile import generate_mobile_usage
from .generators.financials import generate_financial_transactions
from .generators.credit import generate_credit_accounts
from .generators.fiber import generate_fiber_subscriptions, generate_fiber_usage
from .generators.devices import generate_device_purchases
from .generators.enterprise import generate_enterprise_services
from .generators.digital_services import generate_digital_services

logger = logging.getLogger("data_generator")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    p = argparse.ArgumentParser(
        description="Generate synthetic dirty data for a Kenyan fintech/telecom Customer 360 platform."
    )
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED,
                   help="Random seed for reproducibility.")
    p.add_argument("--customers", type=int, default=config.Counts.customers,
                   help="Number of customers to generate.")
    p.add_argument("--mobile", type=int, default=config.Counts.mobile_usage,
                   help="Number of mobile usage records.")
    p.add_argument("--financial", type=int, default=config.Counts.financial_transactions,
                   help="Number of financial transactions.")
    p.add_argument("--credit", type=int, default=config.Counts.credit_accounts,
                   help="Number of credit accounts.")
    p.add_argument("--fiber-subs", type=int, default=config.Counts.fiber_subscriptions,
                   help="Number of fiber subscriptions.")
    p.add_argument("--fiber-usage", type=int, default=config.Counts.fiber_usage,
                   help="Number of fiber usage records.")
    p.add_argument("--devices", type=int, default=config.Counts.device_purchases,
                   help="Number of device purchases.")
    p.add_argument("--enterprise", type=int, default=config.Counts.enterprise_services,
                   help="Number of enterprise service records.")
    p.add_argument("--digital", type=int, default=config.Counts.digital_services,
                   help="Number of digital service records.")
    p.add_argument("--skip-financial", action="store_true",
                   help="Skip the (slow) financial transaction generator.")
    return p.parse_args()


def main() -> None:
    """Run the full generation pipeline."""
    args = parse_args()

    config.configure_logging()
    config.ensure_directories()
    reseed(args.seed)
    get_faker(args.seed)

    start = time.time()
    logger.info("=" * 70)
    logger.info("Synthetic dirty data generation starting (seed=%s)", args.seed)
    logger.info("=" * 70)

    report = QualityReport()

    # ------------------------------------------------------------------
    # Customers (foundation)
    # ------------------------------------------------------------------
    customers = generate_customers(args.customers)
    customers = assign_segments(customers)
    save_csv(customers, config.DATA_ROOT / "customers" / "customers.csv")
    report.add("customers", customers)

    # ------------------------------------------------------------------
    # Mobile
    # ------------------------------------------------------------------
    mobile = generate_mobile_usage(args.mobile, customers)
    save_csv(mobile, config.DATA_ROOT / "mobile" / "mobile_usage.csv")
    report.add("mobile_usage", mobile)

    # ------------------------------------------------------------------
    # Financial
    # ------------------------------------------------------------------
    if not args.skip_financial:
        financial = generate_financial_transactions(args.financial, customers)
        save_csv(financial, config.DATA_ROOT / "financial" / "financial_transactions.csv")
        report.add("financial_transactions", financial)
    else:
        logger.info("Skipping financial transactions (--skip-financial)")

    # ------------------------------------------------------------------
    # Credit
    # ------------------------------------------------------------------
    credit = generate_credit_accounts(args.credit, customers)
    save_csv(credit, config.DATA_ROOT / "credit" / "credit_accounts.csv")
    report.add("credit_accounts", credit)

    # ------------------------------------------------------------------
    # Fiber
    # ------------------------------------------------------------------
    fiber_subs = generate_fiber_subscriptions(args.fiber_subs, customers)
    save_csv(fiber_subs, config.DATA_ROOT / "fiber" / "fiber_subscriptions.csv")
    report.add("fiber_subscriptions", fiber_subs)

    fiber_usage = generate_fiber_usage(args.fiber_usage, fiber_subs)
    save_csv(fiber_usage, config.DATA_ROOT / "fiber" / "fiber_usage.csv")
    report.add("fiber_usage", fiber_usage)

    # ------------------------------------------------------------------
    # Devices
    # ------------------------------------------------------------------
    devices = generate_device_purchases(args.devices, customers)
    save_csv(devices, config.DATA_ROOT / "devices" / "device_purchases.csv")
    report.add("device_purchases", devices)

    # ------------------------------------------------------------------
    # Enterprise
    # ------------------------------------------------------------------
    enterprise = generate_enterprise_services(args.enterprise, customers)
    save_csv(enterprise, config.DATA_ROOT / "enterprise" / "enterprise_services.csv")
    report.add("enterprise_services", enterprise)

    # ------------------------------------------------------------------
    # Digital
    # ------------------------------------------------------------------
    digital = generate_digital_services(args.digital, customers)
    save_csv(digital, config.DATA_ROOT / "digital" / "digital_services.csv")
    report.add("digital_services", digital)

    # ------------------------------------------------------------------
    # Quality report + summary
    # ------------------------------------------------------------------
    report.write(config.REPORT_PATH)

    elapsed = time.time() - start
    log_section("Generation complete")
    logger.info("Total elapsed time: %.1f seconds", elapsed)
    logger.info("Data written to: %s", config.DATA_ROOT)
    logger.info("Quality report:  %s", config.REPORT_PATH)


if __name__ == "__main__":
    main()