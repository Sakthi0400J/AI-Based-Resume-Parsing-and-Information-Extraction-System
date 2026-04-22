"""
Step 9 - Output Layer
Handles writing the structured resume schema to:
  - JSON file
  - CSV file
  - Plain text summary
"""

import json
import csv
import os


def save_json(schema: dict, output_path: str) -> str:
    """Save the full schema as a pretty-printed JSON file."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    return output_path


def save_csv(schema: dict, output_dir: str) -> list[str]:
    """
    Save each section as a separate CSV file in output_dir.
    Returns list of file paths created.
    """
    os.makedirs(output_dir, exist_ok=True)
    files_created = []

    # Experience
    exp = schema.get("experience", [])
    if exp:
        path = os.path.join(output_dir, "experience.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["role", "organization", "duration", "description"])
            writer.writeheader()
            writer.writerows(exp)
        files_created.append(path)

    # Projects
    proj = schema.get("projects", [])
    if proj:
        path = os.path.join(output_dir, "projects.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "tech_stack", "date", "description"])
            writer.writeheader()
            for p in proj:
                row = dict(p)
                row["tech_stack"] = ", ".join(p["tech_stack"]) if p["tech_stack"] else ""
                writer.writerow(row)
        files_created.append(path)

    # Education
    edu = schema.get("education", [])
    if edu:
        path = os.path.join(output_dir, "education.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["degree", "institution", "year", "cgpa"])
            writer.writeheader()
            writer.writerows(edu)
        files_created.append(path)

    # Skills (flatten category → skill)
    skills = schema.get("skills", {})
    if skills:
        path = os.path.join(output_dir, "skills.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["category", "skill"])
            writer.writeheader()
            for category, skill_list in skills.items():
                for skill in skill_list:
                    writer.writerow({"category": category, "skill": skill})
        files_created.append(path)

    # Certifications
    certs = schema.get("certifications", [])
    if certs:
        path = os.path.join(output_dir, "certifications.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "issuer_or_date"])
            writer.writeheader()
            writer.writerows(certs)
        files_created.append(path)

    return files_created


def save_text_summary(schema: dict, output_path: str) -> str:
    """Save a human-readable plain text summary of the resume."""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    lines = []

    name = schema.get("candidate", {}).get("name") or "Unknown"
    lines.append(f"RESUME SUMMARY — {name.upper()}")
    lines.append("=" * 60)

    if schema.get("summary"):
        lines.append("\nSUMMARY")
        lines.append("-" * 30)
        lines.append(schema["summary"])

    if schema.get("experience"):
        lines.append("\nEXPERIENCE")
        lines.append("-" * 30)
        for e in schema["experience"]:
            lines.append(f"  Role        : {e['role'] or 'N/A'}")
            lines.append(f"  Organization: {e['organization'] or 'N/A'}")
            lines.append(f"  Duration    : {e['duration'] or 'N/A'}")
            if e["description"]:
                lines.append(f"  Description : {e['description'][:150]}...")
            lines.append("")

    if schema.get("projects"):
        lines.append("\nPROJECTS")
        lines.append("-" * 30)
        for p in schema["projects"]:
            lines.append(f"  Name      : {p['name'] or 'N/A'}")
            lines.append(f"  Tech Stack: {', '.join(p['tech_stack']) if p['tech_stack'] else 'N/A'}")
            lines.append(f"  Date      : {p['date'] or 'N/A'}")
            if p["description"]:
                lines.append(f"  Description: {p['description'][:150]}...")
            lines.append("")

    if schema.get("skills"):
        lines.append("\nSKILLS")
        lines.append("-" * 30)
        for category, skill_list in schema["skills"].items():
            lines.append(f"  {category.replace('_', ' ').title()}: {', '.join(skill_list)}")

    if schema.get("education"):
        lines.append("\nEDUCATION")
        lines.append("-" * 30)
        for e in schema["education"]:
            lines.append(f"  Degree     : {e['degree'] or 'N/A'}")
            lines.append(f"  Institution: {e['institution'] or 'N/A'}")
            lines.append(f"  Year       : {e['year'] or 'N/A'}")
            lines.append(f"  CGPA       : {e['cgpa'] or 'N/A'}")
            lines.append("")

    if schema.get("certifications"):
        lines.append("\nCERTIFICATIONS")
        lines.append("-" * 30)
        for c in schema["certifications"]:
            lines.append(f"  - {c['title']} ({c['issuer_or_date'] or 'N/A'})")

    text = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path
