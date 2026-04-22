import re

# ─────────────────────────────────────────────────────────────────────────────
# Step 3 & 5 — Anchor Detection + Proximity-Based Grouping
# Covers every resume style observed in the 19-resume corpus
# ─────────────────────────────────────────────────────────────────────────────

MONTH_ABBR = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
YEAR       = r"\d{4}"

DATE_RANGE  = re.compile(
    rf"({MONTH_ABBR}\.?\s*{YEAR})\s*[-/–to]+\s*({MONTH_ABBR}\.?\s*{YEAR}|present|current)",
    re.I
)
SINGLE_DATE = re.compile(rf"{MONTH_ABBR}\.?\s*{YEAR}", re.I)
# "01 Jul 2025 – 31 Jul 2025" style (pure date-only lines)
PURE_DATE_LINE = re.compile(rf"^\d{{1,2}}\s+{MONTH_ABBR}\s+{YEAR}", re.I)

# Short inline date ranges like "sep-oct 2025" or "jan-feb 2025"
SHORT_DATE = re.compile(rf"{MONTH_ABBR}\s*[-–]\s*{MONTH_ABBR}\s+{YEAR}", re.I)


def _extract_date(line: str) -> str:
    m = DATE_RANGE.search(line)
    if m: return m.group(0)
    m = SHORT_DATE.search(line)
    if m: return m.group(0)
    m = SINGLE_DATE.search(line)
    if m: return m.group(0)
    return ""


# ── EXPERIENCE ANCHORING ──────────────────────────────────────────────────────

INTERN_KW = re.compile(
    r"\b(intern(ship)?|trainee|apprentice|job simulation|virtual internship)\b", re.I
)
ROLE_KW = re.compile(
    r"\b(developer|engineer|analyst|designer|researcher|consultant|manager|lead|"
    r"architect|scientist|specialist|associate|coordinator|intern(ship)?|trainee|"
    r"assistant|programmer|full[\s-]?stack|machine learning|artificial intelligence|"
    r"ui[\s/]?ux|devops|data science|web dev(elopment)?|web developer)\b", re.I
)
# "OrgName Month YYYY" or "OrgName Month YYYY – Month YYYY"
ORG_DATE_ANCHOR = re.compile(rf"^[A-Za-z][^\n]{{3,55}}\s+{MONTH_ABBR}\s+{YEAR}", re.I)

# "Role at Org  Date"  (Jeya Kartika, Kiruthika style)
ROLE_AT_ORG = re.compile(r"^.+\s+at\s+.+", re.I)


def _is_experience_anchor(line: str) -> bool:
    s = line.strip()
    # Long description bullets are never anchors
    if s.startswith("-") and len(s) > 70:
        return False
    # Pure date lines are never anchors
    if PURE_DATE_LINE.match(s):
        return False

    has_intern = bool(INTERN_KW.search(s))
    has_role   = bool(ROLE_KW.search(s))
    has_date   = bool(_extract_date(s))

   
    if ROLE_AT_ORG.match(s) and (has_intern or has_role):
        return True

    if has_date and (has_role or has_intern or ORG_DATE_ANCHOR.match(s)):
        return True

    if has_intern and not s.startswith("-"):
        return True

    if re.match(r"^-\s+[A-Za-z]", s) and (has_intern or has_role):
        return True

    if re.search(r"[A-Za-z][-:][A-Za-z]", s) and (has_intern or has_role) and not s.startswith("-"):
        return True

    return False


def _is_role_only_line(line: str) -> bool:
    s = line.strip()
    if len(s) > 60 or s.startswith("-") or _extract_date(s):
        return False
    return bool(ROLE_KW.search(s))


# Lines that are certification/non-experience entries that leak in
CERT_LEAK = re.compile(
    r"(certifications?\(|tcs ion|ibm skills|iitm foundation|tata forage|google data analytics\()",
    re.I
)


def extract_internships(experience_lines: list) -> list:
    
    groups = []
    current = None

    for line in experience_lines:
        s = line.strip()
        if not s:
            continue

        if CERT_LEAK.search(s):
            continue

        if _is_experience_anchor(s):
            if current:
                groups.append(current)
            current = {
                "raw_title":   s,
                "org_line":    "",
                "date":        _extract_date(s),
                "description": []
            }
        elif current:
            date_found = _extract_date(s)

            if PURE_DATE_LINE.match(s):
                if not current["date"]:
                    current["date"] = date_found

            elif _is_role_only_line(s) and not current["org_line"]:
                current["org_line"] = s

            elif date_found and not current["date"] and len(s) < 60:
                current["date"] = date_found
                if len(s) > len(date_found) + 5:
                    current["description"].append(s)

            elif not s.startswith("-") and len(s) < 60 and not current["org_line"]:
                current["org_line"] = s

            else:
                current["description"].append(s)

    if current:
        groups.append(current)
    return groups



CATEGORY_HEADERS = re.compile(
    r"^(ui/?ux projects?|data analyst projects?|ai projects?|data science projects?|"
    r"academic projects?|personal projects?|key projects?|ml projects?|"
    r"web projects?|software projects?)$", re.I
)
PROJECT_DATE_SUFFIX = re.compile(rf"({MONTH_ABBR}\s+{YEAR})\s*$", re.I)

DESC_STARTERS = {
    "developed", "built", "designed", "implemented", "created", "worked",
    "gained", "assisted", "participated", "conducted", "the", "a", "an",
    "this", "we", "it", "used", "applied", "integrated", "engineered",
    "automated", "led", "secured", "solved", "proposed", "presented",
    "published", "earned", "completed", "achieved", "won", "attended",
    "certified", "focused", "mapped", "ensured", "performed", "delivered",
    "crafted", "partnered", "resolved", "refactored", "focused", "processed"
}

NUMBERED_PROJECT = re.compile(r"^\d+[\)\.]\s+[A-Za-z]")

TECH_LINE = re.compile(r"^technologies?\s*:", re.I)


def _is_project_title(line: str) -> bool:
    s = line.strip()

    if CATEGORY_HEADERS.match(s):  return False
    if TECH_LINE.match(s):         return False
    if s.startswith("-") and len(s) > 60: return False
    if len(s) < 4:                 return False

    if NUMBERED_PROJECT.match(s):
        return True

    if "|" in s:
        return True

    if re.search(r"\s[–]\s", s) and len(s) < 120:
        parts = re.split(r"\s[–]\s", s, 1)
        if len(parts) == 2 and 3 <= len(parts[0]) <= 70:
            return True

    if re.search(r"\s-\s", s) and not s.startswith("-") and len(s) < 120:
        parts = s.split(" - ", 1)
        if len(parts) == 2 and 3 <= len(parts[0]) <= 70:
            return True

    # Date-at-end title (karuppanan/sarmila)
    if PROJECT_DATE_SUFFIX.search(s) and not s.startswith("-"):
        first = s.split()[0].lower() if s.split() else ""
        if first not in DESC_STARTERS:
            return True

    # Short (2-8 word) title phrase not starting with a description verb
    words = s.split()
    if 2 <= len(words) <= 8:
        first = words[0].lower().rstrip(".")
        if first not in DESC_STARTERS and not s.startswith("-"):
            if any(w[0].isupper() for w in words if w and w[0].isalpha()):
                return True

    return False


def extract_projects(project_lines: list) -> list:
    groups = []
    current = None
    for line in project_lines:
        s = line.strip()
        if not s: continue
        if CATEGORY_HEADERS.match(s): continue
        if _is_project_title(s):
            if current: groups.append(current)
            current = {"title": s, "description": []}
        elif current:
            current["description"].append(s)
    if current:
        groups.append(current)
    return groups


# ── SKILLS ─────────────────────────────────────────────────────────────────────

def extract_skills_raw(skills_lines: list) -> list:
    raw = []
    for line in skills_lines:
        line = line.strip().lstrip("-•*").strip()
        if ":" in line:
            line = line.split(":", 1)[1]
        for token in re.split(r"[,|;/]", line):
            token = token.strip()
            if 1 < len(token) < 40:
                raw.append(token)
    return raw



DEGREE_PATTERN = re.compile(
    r"\b(b\.?\s*tech|b\.?\s*e\.?|m\.?\s*tech|m\.?\s*e\.?|bca|mca|b\.?\s*sc|m\.?\s*sc|"
    r"bachelor|master|phd|diploma|"
    r"10th|12th|sslc|hsc|higher secondary|secondary|matriculation)\b",
    re.I
)

CONTACT_LINE = re.compile(r"(@gmail|@yahoo|@hotmail|\+91|linkedin|github|leetcode)", re.I)


def extract_education(education_lines: list) -> list:
    groups = []
    current = None
    for line in education_lines:
        s = line.strip()
        if not s: continue
        if CONTACT_LINE.search(s): continue   # skip contact info lines
        if DEGREE_PATTERN.search(s):
            if current: groups.append(current)
            current = {"degree_line": s, "description": []}
        elif current:
            current["description"].append(s)
    if current:
        groups.append(current)
    return groups



def extract_certifications(cert_lines: list) -> list:
    certs = []
    for line in cert_lines:
        s = line.strip().lstrip("-•*").strip()
        if s:
            certs.append({"title": s, "detail": ""})
    return certs
