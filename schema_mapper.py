"""
Step 6 - Schema Mapping Layer
Maps all extracted entities into a single consistent JSON output schema.
"""

from entity_extractor import (
    parse_experience,
    parse_projects,
    categorize_skills,
    parse_education,
    parse_certifications
)
from anchoring import extract_skills_raw


def build_resume_schema(sections: dict, name: str = None) -> dict:
    """
    Takes segmented sections dict and returns the full structured resume schema.

    Schema:
    {
        "candidate": { name },
        "summary": str,
        "experience": [ { role, organization, duration, description } ],
        "projects":  [ { name, tech_stack, date, description } ],
        "skills":    { category: [skill, ...] },
        "education": [ { degree, institution, year, cgpa } ],
        "certifications": [ { title, issuer_or_date } ]
    }
    """

    # Summary
    summary_lines = sections.get("summary", [])
    summary = " ".join(summary_lines).strip() or None

    # Experience
    experience = parse_experience(sections.get("experience", []))

    # Projects
    projects = parse_projects(sections.get("projects", []))

    # Skills
    raw_skills = extract_skills_raw(sections.get("skills", []))
    skills = categorize_skills(raw_skills)

    # Education
    education = parse_education(sections.get("education", []))

    # Certifications
    certifications = parse_certifications(sections.get("certifications", []))

    return {
        "candidate": {
            "name": name or None
        },
        "summary": summary,
        "experience": experience,
        "projects": projects,
        "skills": skills,
        "education": education,
        "certifications": certifications
    }
