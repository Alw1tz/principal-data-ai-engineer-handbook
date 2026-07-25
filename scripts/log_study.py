#!/usr/bin/env python3
"""Append a session to the Study Log table in STUDY_PLAN.md.

Usage:
    python3 scripts/log_study.py <topic-slug> <hours> [--notes "..."] [--date YYYY-MM-DD]

Example:
    python3 scripts/log_study.py spark 2.5 --notes "Read chapter 1, did the AWS lab"
"""
import argparse

from _lib import ROOT, inject, today

START = "<!-- LOG:START -->"
END = "<!-- LOG:END -->"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topic", help="Topic slug this session covered, e.g. 'spark'")
    parser.add_argument("hours", type=float, help="Hours spent")
    parser.add_argument("--notes", default="", help="Free-text notes")
    parser.add_argument("--date", default=None, help="Defaults to today")
    args = parser.parse_args()

    date = args.date or today()
    path = ROOT / "STUDY_PLAN.md"
    content = path.read_text()

    before, rest = content.split(START, 1)
    existing, after = rest.split(END, 1)
    existing = existing.strip("\n")

    new_row = f"| {date} | {args.topic} | {args.hours} | {args.notes} |"
    body = f"{existing}\n{new_row}".strip("\n") if existing else new_row

    inject(path, START, END, body)
    print(f"Logged: {date} | {args.topic} | {args.hours}h | {args.notes}")


if __name__ == "__main__":
    main()
