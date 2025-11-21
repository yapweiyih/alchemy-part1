#!/usr/bin/env python3
"""
GCP Cloud Logging Download Script

This script downloads logs from GCP Cloud Logging for a specific Reasoning Engine
and extracts the textPayload fields.

Usage:
    python download_logs.py
    python download_logs.py --minutes 600
    python download_logs.py --reasoning-engine-id 7957944104447377408
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from google.cloud import logging


def download_logs(
    project_id: str,
    reasoning_engine_id: str,
    location: str = "us-central1",
    minutes: int = 5,
) -> List[Dict[str, Any]]:
    """
    Download logs from GCP Cloud Logging.

    Args:
        project_id: GCP project ID
        reasoning_engine_id: Reasoning Engine ID to filter logs
        location: GCP location (default: us-central1)
        minutes: Number of minutes to look back (default: 5)

    Returns:
        List of log entries as dictionaries
    """
    # Initialize the Cloud Logging client
    client = logging.Client(project=project_id)

    # Calculate time range (last N minutes)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=minutes)

    # Build the filter query
    filter_str = f"""
    resource.type="aiplatform.googleapis.com/ReasoningEngine"
    resource.labels.location="{location}"
    resource.labels.reasoning_engine_id="{reasoning_engine_id}"
    timestamp>="{start_time.isoformat()}"
    timestamp<="{end_time.isoformat()}"
    """.strip()

    print(f"Querying logs from {start_time.isoformat()} to {end_time.isoformat()}")
    print(f"Filter: {filter_str}\n")

    # Fetch logs
    entries = client.list_entries(filter_=filter_str, order_by=logging.ASCENDING)

    # Convert to list of dictionaries
    log_entries = []
    for entry in entries:
        log_dict = {
            "textPayload": entry.payload if isinstance(entry.payload, str) else None,
            # "insertId": entry.insert_id,
            # "resource": {
            #     "type": entry.resource.type,
            #     "labels": dict(entry.resource.labels) if entry.resource.labels else {},
            # },
            # "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
            # "logName": entry.log_name,
            # "receiveTimestamp": (
            #     entry.received_timestamp.isoformat()
            #     if entry.received_timestamp
            #     else None
            # ),
        }
        log_entries.append(log_dict)

    return log_entries


def extract_text_payloads(log_entries: List[Dict[str, Any]]) -> List[str]:
    """
    Extract textPayload values from log entries.

    Args:
        log_entries: List of log entry dictionaries

    Returns:
        List of textPayload strings
    """
    text_payloads = []
    for entry in log_entries:
        if entry.get("textPayload"):
            text_payloads.append(entry["textPayload"])
    return text_payloads


def save_to_json(
    log_entries: List[Dict[str, Any]], text_payloads: List[str], output_dir: str = "."
) -> str:
    """
    Save logs to JSON file with timestamp.

    Args:
        log_entries: Full log entries
        text_payloads: Extracted textPayload values
        output_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{output_dir}/downloaded-logs-{timestamp}.json"

    output_data = {
        "metadata": {
            "download_time": datetime.now(timezone.utc).isoformat(),
            "total_entries": len(log_entries),
            "entries_with_text_payload": len(text_payloads),
        },
        # "log_entries": log_entries,
        "text_payloads": text_payloads,
    }

    with open(filename, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved {len(log_entries)} log entries to: {filename}")
    return filename


def print_text_payloads(text_payloads: List[str]) -> None:
    """
    Print textPayload values line by line to stdout.

    Args:
        text_payloads: List of textPayload strings
    """
    print("\n" + "=" * 80)
    print("TEXT PAYLOADS (line by line)")
    print("=" * 80 + "\n")

    for i, payload in enumerate(text_payloads, 1):
        print(f"{i:4d}: {payload}")

    print("\n" + "=" * 80)
    print(f"Total: {len(text_payloads)} text payloads")
    print("=" * 80)


def main():
    """Main function to orchestrate log downloading and processing."""
    parser = argparse.ArgumentParser(
        description="Download GCP Cloud Logging logs and extract textPayload fields"
    )
    parser.add_argument(
        "--project-id",
        default="hello-world-418507",
        help="GCP project ID (default: hello-world-418507)",
    )
    parser.add_argument(
        "--reasoning-engine-id",
        default="8904095850381180928",
        help="Reasoning Engine ID (default: 8904095850381180928)",
    )
    parser.add_argument(
        "--location", default="us-central1", help="GCP location (default: us-central1)"
    )
    parser.add_argument(
        "--minutes",
        type=int,
        default=360,
        help="Number of minutes to look back (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        default="logs",
        help="Output directory for JSON file (default: current directory)",
    )

    args = parser.parse_args()

    try:
        # Download logs
        print(f"Downloading logs for Reasoning Engine: {args.reasoning_engine_id}")
        log_entries = download_logs(
            project_id=args.project_id,
            reasoning_engine_id=args.reasoning_engine_id,
            location=args.location,
            minutes=args.minutes,
        )

        if not log_entries:
            print("\nNo log entries found matching the criteria.")
            return

        # Extract textPayload values
        text_payloads = extract_text_payloads(log_entries)

        # Save to JSON file
        save_to_json(log_entries, text_payloads, args.output_dir)

        # Print to stdout
        print_text_payloads(text_payloads)

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
