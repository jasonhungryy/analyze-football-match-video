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
REVIEW_SUBSTRATES = {"direct_playback", "extracted_stills"}
CATEGORY_RESCANS = {
    "ball_arrival_reception",
    "defensive_responsibility",
    "post_action",
}
CANDIDATE_DISPOSITIONS = {
    "retained",
    "merged",
    "rejected_other_player",
    "rejected_ordinary_visibility",
    "unresolved",
}
UNDERCOUNT_CHECKS = {
    "identity_and_side_direction",
    "ball_arrivals_and_receptions",
    "no_touch_defending",
    "restarts_and_aerials",
    "transitions_and_weak_side",
    "post_action_continuations",
}
IDENTITY_ANCHOR_RESULTS = {"confirmed_positive", "rejected_wrong_player"}
REBUILD_STATES = {"not_required", REVIEWED}


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
    block_seconds: int = 30,
    marker_values: Iterable[str] = (),
) -> dict[str, Any]:
    if block_seconds < 10 or block_seconds > 30:
        raise ValueError("block_seconds must be between 10 and 30")

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
                    "coverage_dispositions": [],
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
        "schema_version": 2,
        "block_seconds": block_seconds,
        "review_mode": "two_pass_continuous",
        "review_substrate": {
            "mode": "pending",
            "baseline_step_seconds": None,
            "candidate_step_seconds": None,
            "source_resolution_checks": "pending",
            "notes": "",
        },
        "category_rescans": {
            name: {"status": "pending", "notes": ""}
            for name in sorted(CATEGORY_RESCANS)
        },
        "candidate_generation_used": False,
        "candidate_dispositions": [],
        "identity_reference_audit": {
            "status": "pending",
            "appearance_matching_used": False,
            "anchors": [],
            "negative_confusers": [],
            "downstream_rebuild": "not_required",
            "notes": "",
        },
        "revision_audit": {
            "prior_report_challenged": False,
            "status": "not_required",
            "superseded_report": "",
            "full_interval_rebuild": "not_required",
            "old_event_dispositions_completed": "not_required",
            "notes": "",
        },
        "undercount_audit": {
            "status": "pending",
            "checks": {name: "pending" for name in sorted(UNDERCOUNT_CHECKS)},
            "notes": "",
        },
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

    substrate = payload.get("review_substrate")
    if not isinstance(substrate, dict):
        errors.append("review_substrate must be an object")
        substrate = {}
    substrate_mode = substrate.get("mode")
    if substrate_mode not in REVIEW_SUBSTRATES:
        errors.append(
            "review_substrate.mode must be direct_playback or extracted_stills"
        )
    if substrate_mode == "extracted_stills":
        baseline_step = substrate.get("baseline_step_seconds")
        candidate_step = substrate.get("candidate_step_seconds")
        if not isinstance(baseline_step, (int, float)) or baseline_step > 0.5:
            errors.append(
                "extracted_stills requires baseline_step_seconds no greater than 0.5"
            )
        if not isinstance(candidate_step, (int, float)) or candidate_step > 0.25:
            errors.append(
                "extracted_stills requires candidate_step_seconds no greater than 0.25"
            )
    if substrate.get("source_resolution_checks") != REVIEWED:
        errors.append("source_resolution_checks is not reviewed")

    category_rescans = payload.get("category_rescans")
    if not isinstance(category_rescans, dict):
        errors.append("category_rescans must be an object")
        category_rescans = {}
    for name in sorted(CATEGORY_RESCANS):
        rescan = category_rescans.get(name)
        if not isinstance(rescan, dict) or rescan.get("status") != REVIEWED:
            errors.append(f"category rescan {name} is not reviewed")

    candidates = payload.get("candidate_dispositions")
    if not isinstance(candidates, list):
        errors.append("candidate_dispositions must be a list")
        candidates = []
    if payload.get("candidate_generation_used") is True and not candidates:
        errors.append(
            "candidate_generation_used is true but candidate_dispositions is empty"
        )
    if candidates and payload.get("candidate_generation_used") is not True:
        errors.append(
            "candidate_dispositions is non-empty but candidate_generation_used is not true"
        )
    unresolved_candidates: list[str] = []
    candidate_ids: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("Every candidate_disposition must be an object")
            continue
        candidate_id = str(candidate.get("id", "")).strip()
        if not candidate_id:
            errors.append("Candidate disposition is missing id")
        elif candidate_id in candidate_ids:
            errors.append(f"Duplicate candidate id {candidate_id}")
        else:
            candidate_ids.add(candidate_id)
        disposition = candidate.get("disposition")
        if disposition not in CANDIDATE_DISPOSITIONS:
            errors.append(
                f"{candidate_id or '<candidate>'}: invalid or pending disposition"
            )
        elif disposition == "unresolved":
            unresolved_candidates.append(candidate_id or "<candidate>")
        if not candidate.get("timestamp") and not (
            candidate.get("start") and candidate.get("end")
        ):
            errors.append(
                f"{candidate_id or '<candidate>'}: timestamp or start/end is required"
            )

    identity_audit = payload.get("identity_reference_audit")
    if not isinstance(identity_audit, dict):
        errors.append("identity_reference_audit must be an object")
        identity_audit = {}
    if identity_audit.get("status") != REVIEWED:
        errors.append("identity_reference_audit is not reviewed")
    if identity_audit.get("status") == REVIEWED and not str(
        identity_audit.get("notes", "")
    ).strip():
        errors.append("identity_reference_audit needs concrete notes")
    appearance_matching_used = identity_audit.get("appearance_matching_used")
    if not isinstance(appearance_matching_used, bool):
        errors.append("identity_reference_audit.appearance_matching_used must be boolean")
        appearance_matching_used = False
    anchors = identity_audit.get("anchors")
    if not isinstance(anchors, list):
        errors.append("identity_reference_audit.anchors must be a list")
        anchors = []
    anchor_ids: set[str] = set()
    rejected_anchor_ids: list[str] = []
    confirmed_anchor_count = 0
    for anchor in anchors:
        if not isinstance(anchor, dict):
            errors.append("Every identity anchor must be an object")
            continue
        anchor_id = str(anchor.get("id", "")).strip()
        if not anchor_id:
            errors.append("Identity anchor is missing id")
        elif anchor_id in anchor_ids:
            errors.append(f"Duplicate identity anchor id {anchor_id}")
        else:
            anchor_ids.add(anchor_id)
        if not anchor.get("timestamp"):
            errors.append(f"{anchor_id or '<anchor>'}: timestamp is required")
        result = anchor.get("result")
        if result not in IDENTITY_ANCHOR_RESULTS:
            errors.append(f"{anchor_id or '<anchor>'}: invalid identity anchor result")
        elif result == "confirmed_positive":
            confirmed_anchor_count += 1
            cues = anchor.get("cues")
            if not isinstance(cues, list) or len([cue for cue in cues if str(cue).strip()]) < 2:
                errors.append(
                    f"{anchor_id or '<anchor>'}: confirmed anchor needs at least two cues"
                )
        else:
            rejected_anchor_ids.append(anchor_id or "<anchor>")
            if not str(anchor.get("notes", "")).strip():
                errors.append(f"{anchor_id or '<anchor>'}: rejected anchor needs notes")
    if appearance_matching_used:
        if payload.get("candidate_generation_used") is not True:
            errors.append("appearance matching requires candidate_generation_used true")
        if confirmed_anchor_count < 2:
            errors.append("appearance matching needs at least two confirmed identity anchors")
    negative_confusers = identity_audit.get("negative_confusers")
    if not isinstance(negative_confusers, list):
        errors.append("identity_reference_audit.negative_confusers must be a list")
        negative_confusers = []
    for confuser in negative_confusers:
        if not isinstance(confuser, dict) or not str(confuser.get("id", "")).strip():
            errors.append("Every negative confuser needs an id")
            continue
        if not confuser.get("timestamp") or not str(confuser.get("reason", "")).strip():
            errors.append(f"{confuser.get('id')}: negative confuser needs timestamp and reason")
    downstream_rebuild = identity_audit.get("downstream_rebuild")
    if downstream_rebuild not in REBUILD_STATES:
        errors.append("identity_reference_audit.downstream_rebuild is invalid")
    if rejected_anchor_ids and downstream_rebuild != REVIEWED:
        errors.append(
            "Rejected identity anchors require a reviewed downstream full-interval rebuild"
        )

    revision_audit = payload.get("revision_audit")
    if not isinstance(revision_audit, dict):
        errors.append("revision_audit must be an object")
        revision_audit = {}
    prior_report_challenged = revision_audit.get("prior_report_challenged")
    if not isinstance(prior_report_challenged, bool):
        errors.append("revision_audit.prior_report_challenged must be boolean")
    elif prior_report_challenged:
        if revision_audit.get("status") != REVIEWED:
            errors.append("challenged prior report revision audit is not reviewed")
        if revision_audit.get("full_interval_rebuild") != REVIEWED:
            errors.append("challenged prior report requires a full-interval rebuild")
        if revision_audit.get("old_event_dispositions_completed") != REVIEWED:
            errors.append("challenged prior report requires old event dispositions")
        if not str(revision_audit.get("superseded_report", "")).strip():
            errors.append("challenged prior report must name the superseded report")
        if not str(revision_audit.get("notes", "")).strip():
            errors.append("challenged prior report revision audit needs concrete notes")
    else:
        for field in ("status", "full_interval_rebuild", "old_event_dispositions_completed"):
            if revision_audit.get(field) != "not_required":
                errors.append(f"revision_audit.{field} must be not_required when unchallenged")

    undercount = payload.get("undercount_audit")
    if not isinstance(undercount, dict):
        errors.append("undercount_audit must be an object")
        undercount = {}
    if undercount.get("status") != REVIEWED:
        errors.append("undercount_audit is not reviewed")
    checks = undercount.get("checks")
    if not isinstance(checks, dict):
        errors.append("undercount_audit.checks must be an object")
        checks = {}
    for name in sorted(UNDERCOUNT_CHECKS):
        if checks.get(name) != REVIEWED:
            errors.append(f"undercount audit check {name} is not reviewed")
    if undercount.get("status") == REVIEWED and not str(
        undercount.get("notes", "")
    ).strip():
        errors.append("undercount_audit needs a concrete notes summary")

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

        dispositions = block.get("coverage_dispositions")
        allowed_dispositions = {
            "confirmed_direct_action",
            "meaningful_off_ball",
            "visible_no_material_involvement",
            "not_visible_or_occluded",
            "identity_ambiguous",
            "confirmed_confuser",
            "dead_ball_or_stoppage",
        }
        if not isinstance(dispositions, list) or not dispositions:
            errors.append(f"{block_id}: coverage_dispositions needs at least one status")
        else:
            unknown_dispositions = sorted(set(dispositions) - allowed_dispositions)
            if unknown_dispositions:
                errors.append(
                    f"{block_id}: unknown coverage_dispositions {unknown_dispositions}"
                )

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

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        candidate_id = str(candidate.get("id", "<candidate>"))
        disposition = candidate.get("disposition")
        if disposition == "retained":
            linked_ids = candidate.get("ledger_event_ids")
            if not isinstance(linked_ids, list) or not linked_ids:
                errors.append(f"{candidate_id}: retained candidate needs ledger_event_ids")
            else:
                missing_ids = sorted(set(linked_ids) - event_ids)
                if missing_ids:
                    errors.append(
                        f"{candidate_id}: unknown linked event ids {missing_ids}"
                    )
        elif disposition == "merged":
            merged_into = str(candidate.get("merged_into", "")).strip()
            if not merged_into or merged_into == candidate_id or merged_into not in candidate_ids:
                errors.append(
                    f"{candidate_id}: merged candidate needs another valid candidate id"
                )
        elif disposition in {
            "rejected_other_player",
            "rejected_ordinary_visibility",
            "unresolved",
        } and not str(candidate.get("notes", "")).strip():
            errors.append(f"{candidate_id}: disposition needs a concrete notes reason")

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
    if unresolved_candidates:
        warnings.append(
            "Unresolved identity/action candidates prevent a completeness claim: "
            + ", ".join(unresolved_candidates)
        )

    return {
        "valid": not errors,
        "complete_eligible": not errors
        and not limited_ranges
        and not unresolved_candidates,
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
    init_parser.add_argument("--block-seconds", type=int, default=30)
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
