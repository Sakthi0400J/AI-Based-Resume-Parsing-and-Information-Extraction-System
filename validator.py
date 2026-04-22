"""
Step 7 - Validation & Normalization Layer
- Ensures mandatory fields exist (fills None/empty where missing)
- Deduplicates repeated entries
- Standardizes skill names
- Returns clean, machine-readable JSON-ready dict
"""

import re


# ── Field standardization ─────────────────────────────────────────────────────

SKILL_ALIASES = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "ml": "machine learning",
    "dl": "deep learning",
    "cv": "computer vision",
    "sklearn": "scikit-learn",
    "node": "node.js",
    "nodejs": "node.js",
    "reactjs": "react",
    "vuejs": "vue",
    "angularjs": "angular",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "tf": "tensorflow"
}

def _normalize_skill(skill: str) -> str:
    """Standardize a single skill string."""
    skill = skill.strip().lower()
    return SKILL_ALIASES.get(skill, skill).title()


def _deduplicate(items: list, key_fn=None) -> list:
    """Remove duplicate items from a list. Uses key_fn to compare if given."""
    seen = set()
    result = []
    for item in items:
        key = key_fn(item) if key_fn else item
        if isinstance(key, str):
            key = key.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _ensure_fields(entry: dict, required_fields: list) -> dict:
    """Fill missing fields with None."""
    for field in required_fields:
        if field not in entry or entry[field] == "":
            entry[field] = None
    return entry


# ── Section validators ────────────────────────────────────────────────────────

def _validate_experience(experience: list) -> list:
    required = ["role", "organization", "duration", "description"]
    cleaned = []
    for entry in experience:
        entry = _ensure_fields(entry, required)
        # Skip entries that have absolutely nothing useful
        if all(entry[f] is None for f in required):
            continue
        cleaned.append(entry)
    return _deduplicate(cleaned, key_fn=lambda e: f"{e['role']}-{e['organization']}-{e['duration']}")


def _validate_projects(projects: list) -> list:
    required = ["name", "tech_stack", "date", "description"]
    cleaned = []
    for entry in projects:
        entry = _ensure_fields(entry, required)
        if entry["name"] is None:
            continue
        # Normalize tech stack items
        if entry["tech_stack"]:
            entry["tech_stack"] = [_normalize_skill(s) for s in entry["tech_stack"]]
        cleaned.append(entry)
    return _deduplicate(cleaned, key_fn=lambda e: e["name"])


def _validate_skills(skills: dict) -> dict:
    """Normalize and deduplicate all skills in each category."""
    validated = {}
    for category, skill_list in skills.items():
        if not skill_list:
            continue
        normalized = [_normalize_skill(s) for s in skill_list]
        deduped = list(dict.fromkeys(normalized))  # preserve order, remove duplicates
        if deduped:
            validated[category] = deduped
    return validated


def _validate_education(education: list) -> list:
    required = ["degree", "institution", "year", "cgpa"]
    cleaned = []
    for entry in education:
        entry = _ensure_fields(entry, required)
        if entry["degree"] is None and entry["institution"] is None:
            continue
        cleaned.append(entry)
    return _deduplicate(cleaned, key_fn=lambda e: f"{e['degree']}-{e['institution']}")


def _validate_certifications(certs: list) -> list:
    cleaned = []
    for entry in certs:
        entry = _ensure_fields(entry, ["title", "issuer_or_date"])
        if not entry["title"]:
            continue
        cleaned.append(entry)
    return _deduplicate(cleaned, key_fn=lambda e: e["title"])


# ── Main validation entry point ───────────────────────────────────────────────

def validate_schema(schema: dict) -> dict:
    """
    Step 7 - Validates and normalizes the full resume schema.
    Returns clean, machine-readable dict ready for JSON output.
    """
    schema["experience"] = _validate_experience(schema.get("experience") or [])
    schema["projects"] = _validate_projects(schema.get("projects") or [])
    schema["skills"] = _validate_skills(schema.get("skills") or {})
    schema["education"] = _validate_education(schema.get("education") or [])
    schema["certifications"] = _validate_certifications(schema.get("certifications") or [])

    # Normalize summary
    if schema.get("summary"):
        schema["summary"] = re.sub(r"\s+", " ", schema["summary"]).strip() or None

    return schema
