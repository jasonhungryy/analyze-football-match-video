from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "analyze-football-match-video" / "scripts"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


normalize = load_module("normalize_timestamps")
profile = load_module("init_player_profile")
coverage = load_module("coverage_audit")


class TimestampTests(unittest.TestCase):
    def test_accepts_dotted_and_hour_timestamps(self):
        self.assertEqual(normalize.parse_time("39.24"), 2364)
        self.assertEqual(normalize.parse_time("1:02:03"), 3723)

    def test_calculates_total_playing_time(self):
        payload = normalize.build_payload(
            ["10:00-25:30", "40:00-52:15"], [], None
        )
        self.assertEqual(payload["total_playing_time"], "27:45")

    def test_resolves_end_from_video_duration(self):
        payload = normalize.build_payload(["52:00-end"], [], "1:10:00")
        self.assertEqual(payload["stints"][0]["duration"], "18:00")

    def test_rejects_reversed_interval(self):
        with self.assertRaises(ValueError):
            normalize.parse_interval("20:00-10:00")


class ProfileTests(unittest.TestCase):
    def test_creates_profile_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "template.md"
            destination = root / "references" / "player-profile.md"
            template.write_text("private template\n", encoding="utf-8")
            profile.initialize_profile(template, destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), "private template\n")
            with self.assertRaises(FileExistsError):
                profile.initialize_profile(template, destination)


class CoverageAuditTests(unittest.TestCase):
    def complete_required_audits(self, payload, mode="direct_playback"):
        payload["review_substrate"].update(
            {
                "mode": mode,
                "source_resolution_checks": "reviewed",
            }
        )
        if mode == "extracted_stills":
            payload["review_substrate"].update(
                {
                    "baseline_step_seconds": 0.5,
                    "candidate_step_seconds": 0.25,
                }
            )
        for rescan in payload["category_rescans"].values():
            rescan["status"] = "reviewed"
        payload["undercount_audit"]["status"] = "reviewed"
        payload["undercount_audit"]["notes"] = (
            "Identity, both flanks, all arrivals, defending, restarts, and continuations rechecked."
        )
        for check in payload["undercount_audit"]["checks"]:
            payload["undercount_audit"]["checks"][check] = "reviewed"
        payload["identity_reference_audit"].update(
            {
                "status": "reviewed",
                "appearance_matching_used": False,
                "notes": "Manual full-frame continuity used; no crop similarity or tracker gallery.",
            }
        )
        for block in payload["blocks"]:
            block.setdefault("coverage_dispositions", [])
            if not block["coverage_dispositions"]:
                block["coverage_dispositions"] = ["visible_no_material_involvement"]

    def test_builds_gapless_blocks_and_places_markers(self):
        payload = coverage.build_manifest(
            ["10:00-11:10"], block_seconds=30, marker_values=["10:45|missed header"]
        )
        self.assertEqual(len(payload["blocks"]), 3)
        self.assertEqual(payload["blocks"][0]["start"], "10:00")
        self.assertEqual(payload["blocks"][-1]["end"], "11:10")
        self.assertEqual(payload["user_markers"][0]["block_id"], "S01-B002")

    def test_rejects_blocks_longer_than_thirty_seconds(self):
        with self.assertRaises(ValueError):
            coverage.build_manifest(["10:00-12:10"], block_seconds=31)

    def test_rejects_pending_or_unexplained_visible_blocks(self):
        payload = coverage.build_manifest(["10:00-10:30"])
        payload["blocks"][0]["player_visibility"] = "visible"
        result = coverage.audit_manifest(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("tracking_pass" in error for error in result["errors"]))
        self.assertTrue(any("quiet_reason" in error for error in result["errors"]))
        self.assertTrue(
            any("coverage_dispositions" in error for error in result["errors"])
        )

    def test_validates_two_pass_review_and_marker_reconciliation(self):
        payload = coverage.build_manifest(
            ["10:00-10:50"], block_seconds=30, marker_values=["10:15|recovery run"]
        )
        first, second = payload["blocks"]
        for block in payload["blocks"]:
            block["tracking_pass"] = "reviewed"
            block["action_pass"] = "reviewed"
            block["identity_status"] = "confirmed"
            block["player_visibility"] = "visible"
        first["events"] = [
            {
                "id": "E001",
                "labels": ["defending", "defensive_transition"],
                "source": "both",
            }
        ]
        second["quiet_reason"] = "Phase stayed on the opposite side outside the player's responsibility."
        marker = payload["user_markers"][0]
        marker["result"] = "supported"
        marker["ledger_event_ids"] = ["E001"]
        self.complete_required_audits(payload)

        result = coverage.audit_manifest(payload)
        self.assertTrue(result["valid"])
        self.assertTrue(result["complete_eligible"])

    def test_rejects_sparse_still_frame_review_metadata(self):
        payload = coverage.build_manifest(["10:00-10:30"])
        block = payload["blocks"][0]
        block.update(
            {
                "tracking_pass": "reviewed",
                "action_pass": "reviewed",
                "identity_status": "confirmed",
                "player_visibility": "visible",
                "quiet_reason": "Player remained outside the material phase.",
            }
        )
        self.complete_required_audits(payload, mode="extracted_stills")
        payload["review_substrate"]["baseline_step_seconds"] = 1.0
        result = coverage.audit_manifest(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("baseline_step_seconds" in error for error in result["errors"]))

    def test_requires_all_three_category_rescans(self):
        payload = coverage.build_manifest(["10:00-10:30"])
        block = payload["blocks"][0]
        block.update(
            {
                "tracking_pass": "reviewed",
                "action_pass": "reviewed",
                "identity_status": "confirmed",
                "player_visibility": "visible",
                "quiet_reason": "Player remained outside the material phase.",
            }
        )
        self.complete_required_audits(payload)
        payload["category_rescans"]["defensive_responsibility"]["status"] = "pending"
        result = coverage.audit_manifest(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("defensive_responsibility" in error for error in result["errors"]))

    def test_unresolved_candidate_prevents_completeness(self):
        payload = coverage.build_manifest(["10:00-10:30"])
        block = payload["blocks"][0]
        block.update(
            {
                "tracking_pass": "reviewed",
                "action_pass": "reviewed",
                "identity_status": "confirmed",
                "player_visibility": "visible",
                "quiet_reason": "Player remained outside the material phase.",
            }
        )
        self.complete_required_audits(payload)
        payload["candidate_generation_used"] = True
        payload["candidate_dispositions"] = [
            {
                "id": "C001",
                "timestamp": "10:15",
                "disposition": "unresolved",
                "notes": "Two matching black-shirted players overlap in the source frame.",
            }
        ]
        result = coverage.audit_manifest(payload)
        self.assertTrue(result["valid"])
        self.assertFalse(result["complete_eligible"])
        self.assertTrue(any("Unresolved" in warning for warning in result["warnings"]))

    def test_requires_same_type_rescan_after_a_miss(self):
        payload = coverage.build_manifest(["10:00-10:30"])
        block = payload["blocks"][0]
        block.update(
            {
                "tracking_pass": "reviewed",
                "action_pass": "reviewed",
                "identity_status": "confirmed",
                "player_visibility": "visible",
                "quiet_reason": "Player remained outside the material phase.",
            }
        )
        payload["miss_root_cause_audits"] = [
            {"missed_event_id": "E009", "same_type_rescan": "pending"}
        ]
        self.complete_required_audits(payload)
        result = coverage.audit_manifest(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("same-type" in error for error in result["errors"]))

    def test_rejected_identity_anchor_requires_full_downstream_rebuild(self):
        payload = coverage.build_manifest(["10:00-10:30"])
        payload["blocks"][0].update(
            {
                "tracking_pass": "reviewed",
                "action_pass": "reviewed",
                "identity_status": "confirmed",
                "player_visibility": "visible",
                "quiet_reason": "Player stayed outside the material phase.",
            }
        )
        self.complete_required_audits(payload)
        payload["candidate_generation_used"] = True
        payload["candidate_dispositions"] = [
            {
                "id": "C001",
                "timestamp": "10:15",
                "disposition": "rejected_other_player",
                "notes": "Visible shirt number belongs to a teammate.",
            }
        ]
        payload["identity_reference_audit"].update(
            {
                "appearance_matching_used": True,
                "anchors": [
                    {"id": "A1", "timestamp": "10:01", "result": "confirmed_positive", "cues": ["plain shirt", "blue boots"]},
                    {"id": "A2", "timestamp": "10:10", "result": "confirmed_positive", "cues": ["plain shirt", "dark socks"]},
                    {"id": "A3", "timestamp": "10:15", "result": "rejected_wrong_player", "notes": "Gold number visible."},
                ],
            }
        )
        result = coverage.audit_manifest(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("downstream" in error for error in result["errors"]))
        payload["identity_reference_audit"]["downstream_rebuild"] = "reviewed"
        result = coverage.audit_manifest(payload)
        self.assertTrue(result["valid"])

    def test_challenged_report_cannot_be_closed_with_a_patch_only(self):
        payload = coverage.build_manifest(["10:00-10:30"])
        payload["blocks"][0].update(
            {
                "tracking_pass": "reviewed",
                "action_pass": "reviewed",
                "identity_status": "confirmed",
                "player_visibility": "visible",
                "quiet_reason": "Player stayed outside the material phase.",
            }
        )
        self.complete_required_audits(payload)
        payload["revision_audit"].update(
            {
                "prior_report_challenged": True,
                "status": "reviewed",
                "superseded_report": "old-report.md",
                "notes": "Player reported repeated omissions and identity drift.",
            }
        )
        result = coverage.audit_manifest(payload)
        self.assertFalse(result["valid"])
        self.assertTrue(any("full-interval rebuild" in error for error in result["errors"]))
        payload["revision_audit"]["full_interval_rebuild"] = "reviewed"
        payload["revision_audit"]["old_event_dispositions_completed"] = "reviewed"
        result = coverage.audit_manifest(payload)
        self.assertTrue(result["valid"])


class SkillContractTests(unittest.TestCase):
    def test_skill_requires_automatic_review_not_user_timestamps(self):
        skill = (ROOT / "skills" / "analyze-football-match-video" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Do not require the player to summarize the match or mark timestamps first", skill)
        self.assertIn("every visible, confidently attributable material sequence involving the player", skill)
        self.assertIn("Every defensive press, duel, tackle, interception", skill)
        self.assertIn("Defensive sequences and meaningful no-touch actions belong in the main ledger", skill)
        self.assertIn("Use blocks of no more than 30 seconds", skill)
        self.assertIn("coverage disposition", skill)
        self.assertIn("Candidate clips, contact sheets, highlights, ball detections, and user markers are navigation aids only", skill)
        self.assertIn("re-scan the full playing time for the same event family", skill)
        self.assertIn("coverage_audit.py validate", skill)
        self.assertIn("0.5-second gaps", skill)
        self.assertIn("mandatory category rescans", skill)
        self.assertIn("Never force identity into one global best path", skill)
        self.assertIn("appearance matching, tracking, or crop similarity", skill)
        self.assertIn("treat every downstream similarity score", skill)
        self.assertIn("withdraw that report's completeness claim immediately", skill)
        self.assertIn("Compare with the player's history", skill)
        self.assertIn("Default to a complete review", skill)
        self.assertIn("Do not add a match entry when access failed", skill)

    def test_profile_template_contains_onboarding_and_issue_tracker(self):
        template = (
            ROOT
            / "skills"
            / "analyze-football-match-video"
            / "assets"
            / "player-profile-template.md"
        ).read_text(encoding="utf-8")
        for heading in (
            "## Player background",
            "## Self-assessed playing profile",
            "## Usual competition context",
            "## Active issue tracker",
        ):
            self.assertIn(heading, template)


if __name__ == "__main__":
    unittest.main()
