"""
Resume Analyser — main.py
Full 9-step pipeline. Prints structured output to terminal.

Usage:
    # Analyse a single resume
    python main.py path/to/resume.pdf

    # Analyse all resumes in a folder
    python main.py path/to/folder/

    # Print raw JSON instead of formatted output
    python main.py path/to/resume.pdf --json
"""

import os
import sys
import json
import argparse

from extractor      import extract_text_from_file
from normalizer     import normalize_text
from segmenter      import segment_sections
from schema_mapper  import build_resume_schema
from validator      import validate_schema

# ── Helpers ───────────────────────────────────────────────────────────────────

def _guess_name(file_path: str) -> str:
    base  = os.path.splitext(os.path.basename(file_path))[0]
    noise = {"resume", "cv", "curriculum", "vitae", "final", "updated", "new",
             "v1", "v2", "v3", "r", "k", "s", "t", "m", "g", "sk"}
    tokens = [t for t in base.replace("_", " ").split() if t.lower() not in noise]
    name   = " ".join(tokens).strip().title()
    return name if len(name) > 2 else None


def _divider(char="─", width=62):
    return char * width


def _section_header(title: str) -> str:
    return f"\n  ┌── {title.upper()} {'─' * max(0, 54 - len(title))}┐"


def _fmt_list(items, indent="    "):
    if not items:
        return f"{indent}(none)"
    return "\n".join(f"{indent}• {item}" for item in items)


# ── Terminal pretty-printer ───────────────────────────────────────────────────

def print_schema(schema: dict, filename: str):
    name = schema.get("candidate", {}).get("name") or "Unknown"

    print()
    print(_divider("═"))
    print(f"  RESUME: {filename}")
    print(f"  NAME  : {name}")
    print(_divider("═"))

    # Summary
    if schema.get("summary"):
        print(_section_header("Summary"))
        summary = schema["summary"]
        # Word-wrap at 56 chars
        words = summary.split()
        line, lines = "", []
        for w in words:
            if len(line) + len(w) + 1 > 56:
                lines.append(line)
                line = w
            else:
                line = (line + " " + w).strip()
        if line:
            lines.append(line)
        for l in lines:
            print(f"    {l}")

    # Experience
    exp = schema.get("experience", [])
    print(_section_header(f"Experience ({len(exp)} entries)"))
    if exp:
        for i, e in enumerate(exp, 1):
            role = e.get("role") or "Unknown Role"
            org  = e.get("organization") or "Unknown Org"
            dur  = e.get("duration") or "N/A"
            desc = e.get("description") or ""
            print(f"    [{i}] {role}")
            print(f"        Org      : {org}")
            print(f"        Duration : {dur}")
            if desc:
                short_desc = desc[:120] + "..." if len(desc) > 120 else desc
                print(f"        Details  : {short_desc}")
    else:
        print("    (none found)")

    # Projects
    proj = schema.get("projects", [])
    print(_section_header(f"Projects ({len(proj)} entries)"))
    if proj:
        for i, p in enumerate(proj, 1):
            name  = p.get("name") or "Unnamed"
            tech  = ", ".join(p.get("tech_stack") or []) or "N/A"
            date  = p.get("date") or "N/A"
            desc  = p.get("description") or ""
            print(f"    [{i}] {name}")
            print(f"        Tech Stack : {tech}")
            print(f"        Date       : {date}")
            if desc:
                short = desc[:110] + "..." if len(desc) > 110 else desc
                print(f"        Details    : {short}")
    else:
        print("    (none found)")

    # Skills
    skills = schema.get("skills", {})
    print(_section_header("Skills"))
    if skills:
        for cat, skill_list in skills.items():
            label = cat.replace("_", " ").title()
            print(f"    {label:28}: {', '.join(skill_list)}")
    else:
        print("    (none found)")

    # Education
    edu = schema.get("education", [])
    print(_section_header(f"Education ({len(edu)} entries)"))
    if edu:
        for i, e in enumerate(edu, 1):
            degree = e.get("degree") or "N/A"
            inst   = e.get("institution") or "N/A"
            year   = e.get("year") or "N/A"
            cgpa   = e.get("cgpa") or "N/A"
            print(f"    [{i}] {degree}")
            print(f"        Institution : {inst}")
            print(f"        Year        : {year}  |  CGPA: {cgpa}")
    else:
        print("    (none found)")

    # Certifications
    certs = schema.get("certifications", [])
    print(_section_header(f"Certifications ({len(certs)})"))
    if certs:
        for c in certs[:10]:  # cap display at 10
            title = c.get("title", "")[:60]
            print(f"    • {title}")
        if len(certs) > 10:
            print(f"    ... and {len(certs) - 10} more")
    else:
        print("    (none found)")

    print()
    print(_divider("─"))


# ── Core pipeline ─────────────────────────────────────────────────────────────

def analyse_resume(file_path: str, as_json: bool = False) -> dict:
    """Run the full 9-step pipeline on a single file."""

    # Step 1: Extract + Normalize
    raw_text   = extract_text_from_file(file_path)
    clean_text = normalize_text(raw_text)

    # Step 2: Segment
    sections = segment_sections(clean_text)

    # Steps 3-6: Anchor + Extract + Group + Map to Schema
    name   = _guess_name(file_path)
    schema = build_resume_schema(sections, name=name)

    # Step 7: Validate
    schema = validate_schema(schema)

    # Steps 8-9: Output
    filename = os.path.basename(file_path)
    if as_json:
        print(json.dumps({filename: schema}, indent=2, ensure_ascii=False))
    else:
        print_schema(schema, filename)

    return schema


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Resume Analyser — extracts structured data from PDF/DOCX/TXT resumes."
    )
    parser.add_argument(
        "path",
        help="Path to a resume file (PDF/DOCX/TXT) or a folder of resumes."
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Print raw JSON output instead of formatted text."
    )
    args = parser.parse_args()

    target = args.path

    if os.path.isdir(target):
        files = sorted([
            os.path.join(target, f) for f in os.listdir(target)
            if f.lower().endswith((".pdf", ".docx", ".txt"))
        ])
        if not files:
            print(f"No resume files found in: {target}")
            sys.exit(1)

        print(f"\nFound {len(files)} resume(s) in '{target}'")
        ok, skipped = 0, 0
        for fp in files:
            try:
                analyse_resume(fp, as_json=args.json)
                ok += 1
            except Exception as e:
                print(f"\n  [SKIP] {os.path.basename(fp)}: {e}")
                skipped += 1

        print(f"\n{'═'*62}")
        print(f"  Done. Processed: {ok}  |  Skipped: {skipped}")
        print(f"{'═'*62}\n")

    elif os.path.isfile(target):
        try:
            analyse_resume(target, as_json=args.json)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print(f"Path not found: {target}")
        sys.exit(1)


# ── Quick test block ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        # Default: run all PDFs in uploads folder
        UPLOADS = r"C:\Users\admin\resume_analyser\resumes"
        if os.path.isdir(UPLOADS):
            pdfs = sorted([
                os.path.join(UPLOADS, f)
                for f in os.listdir(UPLOADS)
                if f.lower().endswith(".pdf")
            ])
            print(f"\nRunning on {len(pdfs)} resumes in {UPLOADS}")
            ok, skipped = 0, 0
            for fp in pdfs:
                try:
                    analyse_resume(fp)
                    ok += 1
                except Exception as e:
                    print(f"\n  [SKIP] {os.path.basename(fp)}: {e}\n")
                    skipped += 1
            print(f"\n{'═'*62}")
            print(f"  Done. Processed: {ok}  |  Skipped: {skipped}")
            print(f"{'═'*62}\n")
        else:
            print("Usage: python main.py <resume.pdf>")
            print("       python main.py <folder/>")
            print("       python main.py <resume.pdf> --json")
