"""ETL pipeline for processing scan jobs."""

import asyncio
import logging
import os
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from apps.api.app.fees.calc import compute_breakdown
from apps.api.app.fees.interfaces import Dimensions, FeeBreakdown, FeeInputs
from apps.api.app.persistence.db import get_session_local
from apps.api.app.persistence.scan_repo import (
    get_scan,
    load_selleramp_rows,
    save_results,
    update_scan_status,
)
from apps.api.app.rules.engine import apply_rules
from apps.api.app.rules.types import RuleSet

logger = logging.getLogger(__name__)

# Rate limiting via semaphore
MAX_CONCURRENCY_RAW = os.getenv("SCAN_MAX_CONCURRENCY", "10")
try:
    parsed = int(MAX_CONCURRENCY_RAW)
    # If <= 0 or missing, default to 10
    MAX_CONCURRENCY = 10 if parsed <= 0 else parsed
except (ValueError, TypeError):
    MAX_CONCURRENCY = 10  # Safe default if parsing fails
_semaphore = asyncio.Semaphore(MAX_CONCURRENCY)


class ETLCounts(BaseModel):
    """ETL processing counts."""

    extracted: int
    transformed: int
    loaded: int
    skipped: int = 0
    errors: int = 0


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize SellerAmp row to internal product structure.

    Args:
        row: Raw SellerAmp row dict

    Returns:
        Normalized product dict
    """
    # Extract common fields with defaults
    normalized: dict[str, Any] = {
        "asin": row.get("asin", "").strip(),
        "title": row.get("title") or row.get("name", "").strip(),
        "brand": row.get("brand", "").strip() or None,
        "buy_cost": _parse_decimal(row.get("buy_cost") or row.get("cost")),
        "sell_price": _parse_decimal(row.get("sell_price") or row.get("price")),
        "notes": row.get("notes"),
    }

    # Copy over any other fields
    for key, value in row.items():
        if key not in normalized and value is not None:
            normalized[key.lower()] = value

    return normalized


def _parse_decimal(value: Any) -> Decimal | None:
    """Parse value to Decimal, returning None if invalid."""
    if value is None:
        return None
    try:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, str):
            # Remove currency symbols and commas
            cleaned = value.replace("$", "").replace(",", "").strip()
            return Decimal(cleaned) if cleaned else None
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def warn_deprecated_weight() -> None:
    """Emit structured warning when legacy dimensions.weight is consumed."""
    logger.warning(
        '{"event":"deprecated_weight_field","action":"use_weight_kg",'
        '"source":"Dimensions","level":"warning"}'
    )


def build_dimensions(raw: Any) -> Dimensions | None:
    """
    Construct a Dimensions object from raw payload, handling legacy fields.

    Args:
        raw: Raw dimensions mapping from SellerAmp payload.

    Returns:
        Dimensions instance or None if insufficient data.
    """
    if not isinstance(raw, dict):
        return None

    length = _parse_decimal(raw.get("length_cm")) or Decimal("0")
    width = _parse_decimal(raw.get("width_cm")) or Decimal("0")
    height = _parse_decimal(raw.get("height_cm")) or Decimal("0")

    weight_kg = _parse_decimal(raw.get("weight_kg"))
    if weight_kg is None:
        legacy_weight = raw.get("weight")
        legacy_value = _parse_decimal(legacy_weight) if legacy_weight is not None else None
        if legacy_value is not None:
            warn_deprecated_weight()
            weight_kg = legacy_value

    return Dimensions(
        length_cm=length,
        width_cm=width,
        height_cm=height,
        weight_kg=weight_kg,
    )


def serialize_fee_breakdown(breakdown: FeeBreakdown) -> dict[str, float]:
    """Serialize FeeBreakdown dataclass to JSON-safe primitives."""
    serialized: dict[str, float] = {}
    for key, value in asdict(breakdown).items():
        if isinstance(value, Decimal):
            serialized[key] = float(value)
        else:
            serialized[key] = value
    return serialized


async def process_item(
    item: dict[str, Any],
    ruleset: RuleSet | None = None,
    max_retries: int = 3,
) -> dict[str, Any]:
    """
    Process a single item: compute fees, apply rules, return result.

    Retries only on transient errors (network, I/O, timeouts).
    Non-transient errors (validation, data errors) fail immediately.

    Args:
        item: Normalized product item
        ruleset: Optional rule set to apply
        max_retries: Maximum retry attempts on transient errors

    Returns:
        Item dict with computed fees and rule evaluation

    Raises:
        Exception: On non-transient errors or after max retries
    """
    attempt = 0
    last_error: Exception | None = None

    # Transient exceptions that should be retried
    TRANSIENT_EXCEPTIONS = (
        TimeoutError,
        ConnectionError,
        asyncio.CancelledError,
        OSError,
    )

    while attempt < max_retries:
        try:
            # Compute fees if we have required fields
            if item.get("sell_price") and item.get("buy_cost"):
                # Build Dimensions if we have dimension/weight data
                dimensions_obj = build_dimensions(item.get("dimensions"))

                fee_inputs = FeeInputs(
                    category=item.get("category") or "Unknown",
                    sell_price=_parse_decimal(item["sell_price"]) or Decimal("0"),
                    buy_cost=_parse_decimal(item["buy_cost"]) or Decimal("0"),
                    dimensions=dimensions_obj,
                )
                breakdown = compute_breakdown(fee_inputs)
                # Convert dataclass to dict
                item["fee_breakdown"] = serialize_fee_breakdown(breakdown)
                item["net_profit"] = float(breakdown.net_profit)
                item["roi"] = float(breakdown.roi)
            else:
                item["fee_breakdown"] = None
                item["net_profit"] = None
                item["roi"] = None

            # Apply rules if provided
            if ruleset:
                evaluation = apply_rules(item, ruleset)
                item["rule_evaluation"] = evaluation.model_dump()
                item["passed_rules"] = evaluation.passed
            else:
                item["rule_evaluation"] = None
                item["passed_rules"] = None

            return item

        except TRANSIENT_EXCEPTIONS as e:
            # Retry transient errors (network, I/O, timeouts)
            last_error = e
            attempt += 1
            if attempt < max_retries:
                # Exponential backoff
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))
                continue
            # Re-raise after max retries
            raise
        except Exception:
            # Non-transient errors (validation, data errors) - no retry
            raise

    # Should never reach here
    raise last_error or Exception("Unexpected error in process_item")


async def run_scan(scan_id: UUID, ruleset: RuleSet | None = None) -> ETLCounts:
    """
    Run ETL pipeline for a scan.

    Args:
        scan_id: Scan UUID
        ruleset: Optional rule set to apply during transform

    Returns:
        ETL counts summary
    """
    counts = ETLCounts(extracted=0, transformed=0, loaded=0, skipped=0, errors=0)

    # Get async DB session (creates own session, not using Depends)
    session_factory = get_session_local()
    async with session_factory() as db:
        try:
            # Idempotency check: early exit if scan is not pending
            scan = await get_scan(db, scan_id)
            if not scan:
                logger.error(f"Scan {scan_id} not found")
                raise ValueError(f"Scan {scan_id} not found")
            if scan.status != "pending":
                logger.info(f"Skip: scan {scan_id} already {scan.status}")
                return counts  # Return zeros for idempotent re-runs

            # Mark scan as running
            start_time = datetime.utcnow()
            await update_scan_status(db, scan_id, "running", started_at=start_time)

            # Extract: Load SellerAmp rows
            rows = await load_selleramp_rows(db, scan_id)
            counts.extracted = len(rows)

            # Transform: Normalize and process items
            processed_items: list[dict[str, Any]] = []
            tasks = []

            async def process_with_limit(row: dict[str, Any]) -> dict[str, Any] | None:
                """Process item with semaphore-based rate limiting."""
                async with _semaphore:
                    try:
                        normalized = normalize_row(row)
                        processed = await process_item(normalized, ruleset)
                        return processed
                    except Exception as e:
                        logger.error(f"Error processing item {row.get('asin', 'unknown')}: {e}")
                        return None

            # Create tasks for all items
            for row in rows:
                tasks.append(process_with_limit(row))

            # Process in parallel (with concurrency limit via semaphore)
            # Handle cancellation gracefully
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError:
                # Set status to failed with cancellation note
                await update_scan_status(
                    db,
                    scan_id,
                    "failed",
                    error="cancelled",
                    finished_at=datetime.utcnow(),
                )
                logger.warning(f"Scan {scan_id} cancelled")
                raise

            for result in results:
                if isinstance(result, Exception):
                    counts.errors += 1
                elif result is None:
                    counts.errors += 1
                else:
                    counts.transformed += 1
                    processed_items.append(result)

            # Load: Save results
            passed_items = [
                item for item in processed_items if item.get("passed_rules") is not False
            ]
            skipped_items = [item for item in processed_items if item.get("passed_rules") is False]

            counts.loaded = len(passed_items)
            counts.skipped = len(skipped_items)

            await save_results(db, scan_id, passed_items)

            # Mark scan as done
            finished_time = datetime.utcnow()
            await update_scan_status(db, scan_id, "done", finished_at=finished_time)

            # Calculate duration
            duration_ms = int((finished_time - start_time).total_seconds() * 1000)

            # Log ETL summary (single line, after all awaits complete)
            logger.info(
                f"SCAN {scan_id} ETL extracted={counts.extracted} "
                f"transformed={counts.transformed} loaded={counts.loaded} "
                f"skipped={counts.skipped} errors={counts.errors} "
                f"scan_duration_ms={duration_ms}"
            )

        except asyncio.CancelledError:
            # Handle cancellation explicitly
            try:
                await update_scan_status(
                    db,
                    scan_id,
                    "failed",
                    error="cancelled",
                    finished_at=datetime.utcnow(),
                )
            except Exception as update_err:
                logger.error(f"Failed to update scan {scan_id} status to cancelled: {update_err}")
            logger.warning(f"Scan {scan_id} cancelled")
            raise
        except Exception as e:
            # Mark scan as failed
            error_msg = str(e)
            error_trace = f"{type(e).__name__}: {error_msg}"

            try:
                await update_scan_status(
                    db, scan_id, "failed", error=error_trace, finished_at=datetime.utcnow()
                )
            except Exception as update_err:
                # If we can't update status, log it
                logger.error(f"Failed to update scan {scan_id} status to failed: {update_err}")

            logger.error(f"Scan {scan_id} failed: {error_trace}", exc_info=True)
            raise

    return counts
