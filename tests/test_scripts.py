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


class SkillContractTests(unittest.TestCase):
    def test_skill_requires_automatic_review_not_user_timestamps(self):
        skill = (ROOT / "skills" / "analyze-football-match-video" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Do not require the player to summarize the match or mark timestamps first", skill)
        self.assertIn("every visible, confidently attributable material sequence involving the player", skill)
        self.assertIn("Every defensive press, duel, tackle, interception", skill)
        self.assertIn("Defensive sequences and meaningful no-touch actions belong in the main ledger", skill)
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
