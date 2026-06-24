#!/usr/bin/env python3
"""Generate an SVG progress bar image."""

import argparse
import re
import subprocess
import sys
from datetime import date, timedelta
from typing import Optional


DEFAULT_START_DATE = date(2026, 1, 1)


def count_pdf_pages(path: str) -> int:
    """Return the total page count of a PDF using pdfinfo."""
    try:
        result = subprocess.run(
            ["pdfinfo", path],
            capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        raise RuntimeError("'pdfinfo' not found. Install poppler-utils to use this script.")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"pdfinfo failed for '{path}': {e.stderr.strip()}")
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not parse page count from pdfinfo output for '{path}'.")
    return int(match.group(1))




def estimate_completion(progress: int, start_date: date, today: date) -> str:
    """Return an estimated completion date string based on linear progress."""
    if progress <= 0:
        return "N/A (no progress recorded)"
    if progress >= 100:
        return today.strftime("%B %-d, %Y") + " (complete)"
    days_elapsed = (today - start_date).days
    if days_elapsed <= 0:
        return "N/A (start date is today or in the future)"
    total_days = days_elapsed * 100 / progress
    completion_date = start_date + timedelta(days=total_days)
    return completion_date.strftime("%B %-d, %Y")

def generate_progress_bar_svg(progress: int, start_date: date = DEFAULT_START_DATE, today: Optional[date] = None) -> str:
    """Generate an SVG progress bar for the given progress percentage."""
    if not 0 <= progress <= 100:
        raise ValueError(f"Progress must be between 0 and 100, got {progress}")
    if today is None:
        today = date.today()

    completion_label = "Estimated Completion: " + estimate_completion(progress, start_date, today)

    # Layout dimensions
    bar_x = 8
    bar_y = 8
    bar_width = 500
    bar_height = 30
    total_width = bar_x + bar_width + 8
    label_y = bar_y + bar_height + 16
    total_height = label_y + 6

    # Tick mark settings: ticks rise upward from the bottom of the bar
    tick_y_bottom = bar_y + bar_height

    filled_width = bar_width * progress / 100

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}">')
    lines.append('  <style>')
    lines.append('    :root {')
    lines.append('      --pb-bg:       #ffffff;')
    lines.append('      --pb-text:     #1a1a1a;')
    lines.append('      --pb-subtext:  #555555;')
    lines.append('      --pb-empty:    #d8d8d8;')
    lines.append('      --pb-border:   #888888;')
    lines.append('      --pb-tick-a:   rgba(0,0,0,0.50);')
    lines.append('      --pb-tick-b:   rgba(0,0,0,0.38);')
    lines.append('      --pb-tick-c:   rgba(0,0,0,0.24);')
    lines.append('      --pb-needle:   #1565c0;')
    lines.append('    }')
    lines.append('    @media (prefers-color-scheme: dark) {')
    lines.append('      :root {')
    lines.append('        --pb-bg:       #0d1117;')
    lines.append('        --pb-text:     #e6edf3;')
    lines.append('        --pb-subtext:  #8b949e;')
    lines.append('        --pb-empty:    #30363d;')
    lines.append('        --pb-border:   #656d76;')
    lines.append('        --pb-tick-a:   rgba(255,255,255,0.65);')
    lines.append('        --pb-tick-b:   rgba(255,255,255,0.48);')
    lines.append('        --pb-tick-c:   rgba(255,255,255,0.30);')
    lines.append('        --pb-needle:   #58a6ff;')
    lines.append('      }')
    lines.append('    }')
    lines.append('    .pb-bg      { fill: var(--pb-bg); }')
    lines.append('    .pb-label   { font-family: sans-serif; font-size: 12px; font-weight: bold; fill: var(--pb-text); }')
    lines.append('    .pb-sublabel{ font-family: sans-serif; font-size: 11px; fill: var(--pb-subtext); }')
    lines.append('    .pb-empty   { fill: var(--pb-empty); }')
    lines.append('    .pb-border  { fill: none; stroke: var(--pb-border); stroke-width: 1.5; }')
    lines.append('    .pb-tick-a  { stroke: var(--pb-tick-a); }')
    lines.append('    .pb-tick-b  { stroke: var(--pb-tick-b); }')
    lines.append('    .pb-tick-c  { stroke: var(--pb-tick-c); }')
    lines.append('    .pb-needle  { stroke: var(--pb-needle); stroke-width: 2; stroke-dasharray: 3,2; fill: none; }')
    lines.append('  </style>')

    # Background
    lines.append(f'  <rect class="pb-bg" width="{total_width}" height="{total_height}"/>')

    # Progress label: lower-left
    lines.append(f'  <text class="pb-label" x="{bar_x}" y="{label_y}" text-anchor="start">Progress: {progress}%</text>')

    # Estimated completion: lower-right
    bar_right = bar_x + bar_width
    lines.append(f'  <text class="pb-sublabel" x="{bar_right}" y="{label_y}" text-anchor="end">{completion_label}</text>')

    # Bar background (empty track)
    lines.append(f'  <rect class="pb-empty" x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="4"/>')

    # Bar fill
    if progress > 0:
        lines.append(f'  <rect x="{bar_x}" y="{bar_y}" width="{filled_width:.2f}" height="{bar_height}" rx="4" fill="#4caf50"/>')
        # Square off the right edge of the fill when not at 100%
        if progress < 100:
            lines.append(f'  <rect x="{bar_x + filled_width - 4:.2f}" y="{bar_y}" width="4" height="{bar_height}" fill="#4caf50"/>')

    # Bar border
    lines.append(f'  <rect class="pb-border" x="{bar_x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" rx="4"/>')

    # Tick marks every 5% (skip 0% and 100%)
    for pct in range(0, 101, 5):
        if pct == 0 or pct == 100:
            continue

        x = bar_x + bar_width * pct / 100

        if pct == 50:
            tick_height = 24
            stroke_width = 2.5
            tick_class = "pb-tick-a"
        elif pct % 10 == 0:
            tick_height = 16
            stroke_width = 1.8
            tick_class = "pb-tick-b"
        else:
            tick_height = 8
            stroke_width = 1.0
            tick_class = "pb-tick-c"

        lines.append(
            f'  <line class="{tick_class}" x1="{x:.2f}" y1="{tick_y_bottom - tick_height}" '
            f'x2="{x:.2f}" y2="{tick_y_bottom}" stroke-width="{stroke_width}"/>'
        )

    # Progress indicator line (needle)
    if 0 < progress < 100:
        needle_x = bar_x + bar_width * progress / 100
        lines.append(
            f'  <line class="pb-needle" x1="{needle_x:.2f}" y1="{bar_y - 2}" '
            f'x2="{needle_x:.2f}" y2="{bar_y + bar_height + 2}"/>'
        )

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate an SVG progress bar from a PDF page count.")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("target", type=int, help="Target total page count (100% mark)")
    parser.add_argument("-o", "--output", help="Output file path (default: stdout)")
    parser.add_argument(
        "--start-date",
        default="2026-01-01",
        help="Start date for linear completion estimate in YYYY-MM-DD format (default: 2026-01-01)",
    )
    args = parser.parse_args()

    try:
        start_date = date.fromisoformat(args.start_date)
    except ValueError:
        print(f"Error: Invalid start date '{args.start_date}'. Expected YYYY-MM-DD.", file=sys.stderr)
        sys.exit(1)

    try:
        page_count = count_pdf_pages(args.pdf)
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.target <= 0:
        print("Error: Target page count must be greater than 0.", file=sys.stderr)
        sys.exit(1)

    progress = min(round(page_count * 100 / args.target), 100)

    try:
        svg = generate_progress_bar_svg(progress, start_date=start_date)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"SVG written to {args.output}")
    else:
        print(svg)


if __name__ == "__main__":
    main()
