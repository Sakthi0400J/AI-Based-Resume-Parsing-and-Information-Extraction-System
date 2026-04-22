import re

# ─────────────────────────────────────────────────────────────────────────────
# Step 2 – Section Segmentation Layer
# ─────────────────────────────────────────────────────────────────────────────

SECTION_KEYWORDS = {
    "summary": [
        "summary", "professional summary", "career summary", "objective",
        "career objective", "about me", "profile", "about"
    ],
    "experience": [
        "experience", "work experience", "internship experience",
        "internships", "internship", "employment", "work history",
        "professional experience", "experience & activities",
        "interns", "online internships", "experience & activities :"
    ],
    "projects": [
        "projects", "project experience", "personal projects",
        "academic projects", "key projects", "project", "my projects"
    ],
    "skills": [
        "skills", "technical skills", "core skills", "competencies",
        "technologies", "tech stack", "expertise areas", "skills summary"
    ],
    "education": [
        "education", "academic background", "educational qualification",
        "qualifications", "academics", "education credentials",
        "academic qualification", "academic qualifications"
    ],
    "certifications": [
        "certifications", "certification", "certificates", "certificate",
        "achievements", "awards", "accomplishments", "honors",
        "certifications & achievements", "certifications participation",
        "achievements and awards", "activities", "positions of responsibility",
        "certificates & achievements"
    ]
}

_KW_MAP: dict = {}
for _sec, _kws in SECTION_KEYWORDS.items():
    for _kw in _kws:
        _KW_MAP[_kw.lower().strip()] = _sec


def _detect_section(line: str):
    s = line.strip().lower()
    s = re.sub(r"[:\-_*=]+$", "", s).strip()
    if not s or len(s) > 55:
        return None
    if s in _KW_MAP:
        return _KW_MAP[s]
    for kw, section in _KW_MAP.items():
        if s == kw or s.startswith(kw + " ") or s.startswith(kw + "&") or s.startswith(kw + " &"):
            return section
    return None


def _education_fallback(line: str) -> bool:
    edu_signals = [
        "b.tech", "b. tech", "b.e", "m.tech", "bca", "mca", "b.sc", "m.sc",
        "bachelor", "master", "phd", "college", "university",
        "cgpa", "gpa", "10th", "12th", "sslc", "hsc", "higher secondary"
    ]
    lower = line.lower()
    return any(sig in lower for sig in edu_signals)


def segment_sections(resume_text: str) -> dict:
    sections = {key: [] for key in SECTION_KEYWORDS}
    current_section = None
    lines = [l.strip() for l in resume_text.split("\n") if l.strip()]

    for line in lines:
        detected = _detect_section(line)
        if detected:
            current_section = detected
            continue
        if current_section is None and _education_fallback(line):
            current_section = "education"
        if current_section:
            sections[current_section].append(line.lower())

    return sections
