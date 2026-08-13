#!/usr/bin/env python3
"""Normalize football-video timestamps and playing intervals."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass


TIME_RE = re.compile(r"^\s*(\d+)(?:[:.](\d{1,2}))?(?:[:.](\d{1,2}))?\s*$")
DASH_RE = re.compile(r"\s*(?:-|–|—)\s*")


def parse_time(value: str) -> int:
    """Return seconds for MM:SS, HH:MM:SS, or dotted equivalents."""
    match = TIME_RE.match(value)
    if not match:
        raise ValueError(f"invalid timestamp: {value!r}")
    parts = [int(part) for part in match.groups() if part is not None]
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        minutes, seconds = parts
        if seconds >= 60:
            raise ValueError(f"seconds must be below 60: {value!r}")
        return minutes * 60 + seconds
    hours, minutes, seconds = parts
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"minutes and seconds must be below 60: {value!r}")
    return hours * 3600 + minutes * 60 + seconds


def format_time(seconds: int) -> str:
    if seconds < 0:
        raise ValueError("timestamp cannot be negative")
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


@dataclass(frozen=True)
class Interval:
    start: int
    end: int

    @property
    def duration(self) -> int:
        return self.end - self.start


def parse_interval(value: str, video_duration: int | None = None) -> Interval:
    parts = DASH_RE.split(value.strip())
    if len(parts) != 2:
        raise ValueError(f"interval must contain one dash: {value!r}")
    start = parse_time(parts[0])
    if parts[1].lower() == "end":
        if video_duration is None:
            raise ValueError("'end' requires --duration")
        end = video_duration
    else:
        end = parse_time(parts[1])
    if end <= start:
        raise ValueError(f"interval end must be after start: {value!r}")
    if video_duration is not None and end > video_duration:
        raise ValueError(f"interval exceeds video duration: {value!r}")
    return Interval(start, end)


def build_payload(stints: list[str], events: list[str], duration: str | None) -> dict:
    video_duration = parse_time(duration) if duration else None
    intervals = [parse_interval(value, video_duration) for value in stints]
    event_seconds = [parse_time(value) for value in events]
    if video_duration is not None and any(value > video_duration for value in event_seconds):
        raise ValueError("an event exceeds video duration")
    return {
        "video_duration": format_time(video_duration) if video_duration is not None else None,
        "stints": [
            {
                "start": format_time(item.start),
                "end": format_time(item.end),
                "duration": format_time(item.duration),
                "start_seconds": item.start,
                "end_seconds": item.end,
            }
            for item in intervals
        ],
        "total_playing_time": format_time(sum(item.duration for item in intervals)),
        "events": [
            {"input": raw, "normalized": format_time(value), "seconds": value}
            for raw, value in zip(events, event_seconds)
        ],
    }


def render_markdown(payload: dict) -> str:
    lines = ["# Normalized timestamps", "", f"Total playing time: **{payload['total_playing_time']}**", ""]
    if payload["stints"]:
        lines.extend(["| Stint | Start | End | Duration |", "|---:|---:|---:|---:|"])
        for index, stint in enumerate(payload["stints"], 1):
            lines.append(f"| {index} | {stint['start']} | {stint['end']} | {stint['duration']} |")
        lines.append("")
    if payload["events"]:
        lines.extend(["| Input | Normalized |", "|---|---:|"])
        for event in payload["events"]:
            lines.append(f"| {event['input']} | {event['normalized']} |")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stint", action="append", default=[], help="playing interval, for example 12:30-36:10")
    parser.add_argument("--event", action="append", default=[], help="event timestamp; may be repeated")
    parser.add_argument("--duration", help="video duration, required when a stint ends with 'end'")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    try:
        payload = build_payload(args.stint, args.event, args.duration)
    except ValueError as exc:
        parser.error(str(exc))
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
