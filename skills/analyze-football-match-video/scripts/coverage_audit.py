#!/usr/bin/env python3
"""Build and validate a two-pass coverage manifest for full-match reviews."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable


TIME_RE = re.compile(r"^(?:(\d+):)?(\d+):(\d+)$")
REVIEWED = "reviewed"
VISIBLE_STATES = {"visible", "partly_visible"}
LIMITED_IDENTITY_STATES = {"partly_lost", "not_visible"}
MARKER_RESULTS = {
    "supported",
    "partly_supported",
    "contradicted",
    "not_judgeable",
}
EVENT_TYPES = {
    "on_ball",
    "defending",
    "attacking_transition",
    "defensive_transition",
    "restart",
    "attacking_off_ball",
    "defensive_positioning",
    "aerial",
}


def parse_time(value: str) -> int:
    match = TIME_RE.fullmatch(value.strip())
    if not match:
        raise ValueError(f"Invalid timestamp: {value!r}")
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    if seconds >= 60 or (match.group(1) and minutes >= 60):
        raise ValueError(f"Invalid timestamp: {value!r}")
    return hours * 3600 + minutes * 60 + seconds


def format_time(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def parse_interval(value: str) -> tuple[int, int]:
    try:
        start_text, end_text = value.split("-", 1)
    except ValueError as exc:
        raise ValueError(f"Invalid interval: {value!r}") from exc
    start = parse_time(start_text)
    end = parse_time(end_text)
    if end <= start:
        raise ValueError(f"Interval must end after it starts: {value!r}")
    return start, end


def parse_marker(value: str) -> dict[str, Any]:
    timestamp_text, separator, claim = value.partition("|")
    timestamp = parse_time(timestamp_text)
    return {
        "id": "",
        "timestamp": format_time(timestamp),
        "timestamp_seconds": timestamp,
        "claim": claim.strip() if separator else "",
        "result": "pending",
        "ledger_event_ids": [],
        "notes": "",
    }


def build_manifest(
    interval_values: Iterable[str],
    block_seconds: int = 60,
    marker_values: Iterable[str] = (),
) -> dict[str, Any]:
    if block_seconds < 15 or block_seconds > 90:
        raise ValueError("block_seconds must be between 15 and 90")

    intervals = [parse_interval(value) for value in interval_values]
    if not intervals:
        raise ValueError("At least one playing interval is required")
    intervals.sort()
    for previous, current in zip(intervals, intervals[1:]):
        if current[0] < previous[1]:
            raise ValueError("Playing intervals must not overlap")

    blocks: list[dict[str, Any]] = []
    interval_payload: list[dict[str, Any]] = []
    for stint_index, (start, end) in enumerate(intervals, start=1):
        interval_payload.append(
            {
                "id": f"S{stint_index:02d}",
                "start": format_time(start),
                "end": format_time(end),
                "start_seconds": start,
                "end_seconds": end,
            }
        )
        cursor = start
        block_index = 1
        while cursor < end:
            block_end = min(cursor + block_seconds, end)
            blocks.append(
                {
                    "id": f"S{stint_index:02d}-B{block_index:03d}",
                    "stint_id": f"S{stint_index:02d}",
                    "start": format_time(cursor),
                    "end": format_time(block_end),
                    "start_seconds": cursor,
                    "end_seconds": block_end,
                    "tracking_pass": "pending",
                    "action_pass": "pending",
                    "identity_status": "pending",
                    "player_visibility": "pending",
                    "events": [],
                    "quiet_reason": "",
                    "notes": "",
                }
            )
            cursor = block_end
            block_index += 1

    markers = [parse_marker(value) for value in marker_values]
    for marker_index, marker in enumerate(markers, start=1):
        marker["id"] = f"M{marker_index:03d}"
        containing = [
            block["id"]
            for block in blocks
            if block["start_seconds"] <= marker["timestamp_seconds"] < block["end_seconds"]
        ]
        marker["block_id"] = containing[0] if containing else "outside-playing-intervals"

    return {
        "schema_version": 1,
        "block_seconds": block_seconds,
        "review_mode": "two_pass_continuous",
        "intervals": interval_payload,
        "blocks": blocks,
        "user_markers": markers,
        "miss_root_cause_audits": [],
    }


def audit_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    blocks = payload.get("blocks")
    intervals = payload.get("intervals")
    if not isinstance(blocks, list) or not isinstance(intervals, list):
        return {
            "valid": False,
            "complete_eligible": False,
            "errors": ["Manifest must contain interval and block lists"],
            "warnings": [],
        }

    blocks_by_stint: dict[str, list[dict[str, Any]]] = {}
    event_ids: set[str] = set()
    limited_ranges: list[str] = []
    for block in blocks:
        block_id = str(block.get("id", "<missing-id>"))
        blocks_by_stint.setdefault(str(block.get("stint_id", "")), []).append(block)
        for pass_name in ("tracking_pass", "action_pass"):
            if block.get(pass_name) != REVIEWED:
                errors.append(f"{block_id}: {pass_name} is not reviewed")
        if block.get("identity_status") == "pending":
            errors.append(f"{block_id}: identity_status is pending")
        if block.get("player_visibility") == "pending":
            errors.append(f"{block_id}: player_visibility is pending")

        events = block.get("events")
        if not isinstance(events, list):
            errors.append(f"{block_id}: events must be a list")
            events = []
        if block.get("player_visibility") in VISIBLE_STATES and not events and not str(
            block.get("quiet_reason", "")
        ).strip():
            errors.append(
                f"{block_id}: visible block needs at least one event or a quiet_reason"
            )
        for event in events:
            if not isinstance(event, dict):
                errors.append(f"{block_id}: every event must be an object")
                continue
            event_id = str(event.get("id", "")).strip()
            if not event_id:
                errors.append(f"{block_id}: event is missing id")
            elif event_id in event_ids:
                errors.append(f"{block_id}: duplicate event id {event_id}")
            else:
                event_ids.add(event_id)
            labels = event.get("labels", [])
            if not isinstance(labels, list) or not labels:
                errors.append(f"{block_id}/{event_id or '<event>'}: labels are required")
            else:
                unknown = sorted(set(labels) - EVENT_TYPES)
                if unknown:
                    errors.append(
                        f"{block_id}/{event_id or '<event>'}: unknown labels {unknown}"
                    )
            if event.get("source") not in {"blind_scan", "user_marker", "both"}:
                errors.append(
                    f"{block_id}/{event_id or '<event>'}: source must be blind_scan, user_marker, or both"
                )

        if block.get("identity_status") in LIMITED_IDENTITY_STATES or block.get(
            "player_visibility"
        ) == "not_visible":
            limited_ranges.append(f"{block.get('start')}–{block.get('end')}")

    for interval in intervals:
        stint_id = str(interval.get("id", ""))
        stint_blocks = sorted(
            blocks_by_stint.get(stint_id, []), key=lambda item: item.get("start_seconds", -1)
        )
        expected = interval.get("start_seconds")
        for block in stint_blocks:
            if block.get("start_seconds") != expected:
                errors.append(f"{stint_id}: coverage gap or overlap before {block.get('id')}")
            expected = block.get("end_seconds")
        if expected != interval.get("end_seconds"):
            errors.append(f"{stint_id}: blocks do not cover the full playing interval")

    markers = payload.get("user_markers", [])
    if not isinstance(markers, list):
        errors.append("user_markers must be a list")
        markers = []
    for marker in markers:
        marker_id = str(marker.get("id", "<missing-marker-id>"))
        if marker.get("result") not in MARKER_RESULTS:
            errors.append(f"{marker_id}: user marker has not been reconciled")
        linked_ids = marker.get("ledger_event_ids", [])
        if not isinstance(linked_ids, list):
            errors.append(f"{marker_id}: ledger_event_ids must be a list")
        else:
            missing_ids = sorted(set(linked_ids) - event_ids)
            if missing_ids:
                errors.append(f"{marker_id}: unknown linked event ids {missing_ids}")

    root_cause_audits = payload.get("miss_root_cause_audits", [])
    if not isinstance(root_cause_audits, list):
        errors.append("miss_root_cause_audits must be a list")
    else:
        for audit in root_cause_audits:
            if not isinstance(audit, dict) or not audit.get("missed_event_id"):
                errors.append("Every miss_root_cause_audit needs a missed_event_id")
                continue
            if audit.get("same_type_rescan") != "reviewed":
                errors.append(
                    f"{audit.get('missed_event_id')}: same-type full-match rescan is not reviewed"
                )

    if limited_ranges:
        warnings.append(
            "Identity or visibility limitations prevent a zero-gap completeness claim in: "
            + ", ".join(limited_ranges)
        )

    return {
        "valid": not errors,
        "complete_eligible": not errors and not limited_ranges,
        "errors": errors,
        "warnings": warnings,
        "reviewed_blocks": sum(
            1
            for block in blocks
            if block.get("tracking_pass") == REVIEWED
            and block.get("action_pass") == REVIEWED
        ),
        "total_blocks": len(blocks),
        "event_count": len(event_ids),
        "marker_count": len(markers),
    }


def write_json(path: Path, payload: dict[str, Any], overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a pending coverage manifest")
    init_parser.add_argument("--interval", action="append", required=True)
    init_parser.add_argument("--block-seconds", type=int, default=60)
    init_parser.add_argument(
        "--marker",
        action="append",
        default=[],
        help='User marker as "MM:SS|claim"',
    )
    init_parser.add_argument("--output", type=Path, required=True)
    init_parser.add_argument("--force", action="store_true")

    validate_parser = subparsers.add_parser("validate", help="Audit a completed manifest")
    validate_parser.add_argument("manifest", type=Path)

    args = parser.parse_args()
    if args.command == "init":
        payload = build_manifest(args.interval, args.block_seconds, args.marker)
        write_json(args.output, payload, overwrite=args.force)
        print(json.dumps({"output": str(args.output), "blocks": len(payload["blocks"])}))
        return 0

    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = audit_manifest(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
