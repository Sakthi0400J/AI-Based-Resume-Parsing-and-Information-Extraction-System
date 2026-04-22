import re
from anchoring import (
    extract_internships, extract_projects, extract_skills_raw,
    extract_education, extract_certifications,
    _extract_date, DEGREE_PATTERN, ROLE_KW, ORG_DATE_ANCHOR
)

# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Entity Extraction Layer
# ─────────────────────────────────────────────────────────────────────────────

CGPA_PATTERN = re.compile(r"(cgpa|gpa|grade)\s*[:\-\[]?\s*(\d+\.\d+|\d+/\d+)", re.I)
YEAR_ONLY    = re.compile(r"\b(20\d{2}|19\d{2})\b")
MONTH_P      = re.compile(
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}", re.I
)

# ── Skills Taxonomy ───────────────────────────────────────────────────────────

SKILL_TAXONOMY = {
    "programming_languages": [
        "python", "java", "c", "c++", "c#", "javascript", "typescript",
        "r", "go", "rust", "kotlin", "swift", "php", "ruby", "scala",
        "matlab", "bash", "shell", "perl", "dart", "flutter", "sql",
        "script.js", "react.js", "node.js"
    ],
    "web_technologies": [
        "html", "html5", "css", "css3", "react", "angular", "vue",
        "node", "nodejs", "express", "django", "flask", "fastapi",
        "spring", "asp.net", "bootstrap", "tailwind", "jquery",
        "next.js", "nuxt", "php", "mern", "rest api", "rest apis"
    ],
    "databases": [
        "mysql", "postgresql", "sqlite", "mongodb", "redis", "oracle",
        "sql server", "cassandra", "dynamodb", "firebase", "supabase",
        "mariadb", "neo4j", "wamp", "mangodb"
    ],
    "ai_ml": [
        "machine learning", "deep learning", "nlp",
        "natural language processing", "computer vision",
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "pandas", "numpy", "matplotlib", "seaborn", "opencv",
        "huggingface", "transformers", "bert", "gpt", "llm", "rag",
        "xgboost", "lightgbm", "spacy", "generative ai", "langchain",
        "catboost", "lstm", "rnn", "gnn", "vision transformer", "cnn",
        "reinforcement learning", "bayesian", "predictive modeling",
        "model context protocol", "mcp", "llms", "agentic ai",
        "prompt engineering", "wav2vec2", "torchaudio", "torchvision",
        "data analysis", "data preprocessing", "feature engineering",
        "statistical analysis"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "jenkins", "github actions", "gitlab ci", "terraform", "ansible",
        "linux", "ubuntu", "nginx", "apache", "ci/cd", "ibm cloud",
        "google earth engine", "mlops", "edge ai", "vercel", "cloud"
    ],
    "tools_platforms": [
        "git", "github", "gitlab", "bitbucket", "jira", "trello",
        "figma", "postman", "vs code", "pycharm", "intellij", "eclipse",
        "jupyter", "colab", "notion", "slack", "excel", "tableau",
        "powerbi", "power bi", "adobe xd", "canva", "blender",
        "android sdk", "jetpack compose", "esp32", "arduino",
        "google colab", "replit", "wamp", "power bi"
    ],
    "soft_skills": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "time management", "adaptability",
        "collaboration", "innovative thinking", "decision making",
        "presentation skills"
    ]
}

_SKILL_LOOKUP: dict = {}
for _cat, _sl in SKILL_TAXONOMY.items():
    for _s in _sl:
        _SKILL_LOOKUP[_s.lower()] = _cat


def categorize_skills(raw_skills: list) -> dict:
    categorized = {cat: [] for cat in SKILL_TAXONOMY}
    categorized["other"] = []
    for skill in raw_skills:
        sl = skill.lower().strip()
        matched = False
        if sl in _SKILL_LOOKUP:
            cat = _SKILL_LOOKUP[sl]
            if skill not in categorized[cat]:
                categorized[cat].append(skill)
            matched = True
        if not matched:
            for known, cat in _SKILL_LOOKUP.items():
                if known in sl or sl in known:
                    if skill not in categorized[cat]:
                        categorized[cat].append(skill)
                    matched = True
                    break
        if not matched and sl:
            if skill not in categorized["other"]:
                categorized["other"].append(skill)
    return {k: v for k, v in categorized.items() if v}


# ── EXPERIENCE PARSING ────────────────────────────────────────────────────────

ROLE_LIST = [
    "artificial intelligence intern", "data science intern", "data analyst intern",
    "machine learning intern", "web development intern", "web developer intern",
    "software developer intern", "software engineer intern",
    "ui/ux design intern", "ui/ux intern", "ui ux design intern",
    "devops intern", "cloud intern", "ai intern", "nlp intern",
    "cybersecurity intern", "research intern", "full stack developer",
    "full-stack developer", "software developer", "software engineer",
    "web developer", "frontend developer", "backend developer",
    "data analyst", "data scientist", "data engineer",
    "machine learning engineer", "ml engineer", "ai engineer",
    "devops engineer", "cloud engineer", "system engineer",
    "ui/ux designer", "ui designer", "ux designer",
    "product manager", "project manager", "business analyst",
    "research assistant", "technical trainee",
    "data analytics and visualization job simulation"
]

NOISE_TOKENS = re.compile(
    r"^(intern(ship)?|trainee|at|in|the|and|for|of|a|an|via|by|from|"
    r"successfully|completed|focused|on|using|leveraging|virtual|online|"
    r"offline|week|program|organized|conducted|collaboration|with|"
    r"aicte|foundation|has|th|this|was|4|15|7|to|24th|25th|"
    r"feb|jan|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)$",
    re.I
)

# "Role at Org" — extract org from the " at " split
AT_SPLIT = re.compile(r"^(.+?)\s+at\s+(.+?)(\s+\w+\s+\d{4}.*)?\s*$", re.I)


def _extract_role(text: str) -> str:
    lower = text.lower()
    for role in sorted(ROLE_LIST, key=len, reverse=True):
        if role in lower:
            return role.title()
    return ""


def _clean_org(text: str, role: str, date: str) -> str:
    if role:
        text = re.sub(re.escape(role), " ", text, flags=re.I)
    if date:
        text = re.sub(re.escape(date), " ", text, flags=re.I)
    text = re.sub(r"[-–|@,•()]", " ", text)
    tokens = [t for t in text.split()
              if not NOISE_TOKENS.match(t.strip(".")) and len(t) > 1 and not t.isdigit()]
    org = " ".join(tokens[:5]).strip().title()
    return org if len(org) > 2 else ""


def _merge_consecutive(groups: list) -> list:
    """
    Merge Karuppanan/Srinath pattern:
      Group N:   raw_title = "SkillCraft Technology July 2025"  (org+date, no role)
      Group N+1: raw_title = "Machine Learning Intern"          (role, no date)
    → merged into one entry with role + org + date
    """
    merged = []
    i = 0
    while i < len(groups):
        g    = groups[i]
        role = _extract_role(g["raw_title"])
        date = g["date"]

        if (not role and date and i + 1 < len(groups)):
            nxt      = groups[i + 1]
            nxt_role = _extract_role(nxt["raw_title"])
            nxt_date = nxt["date"]
            if nxt_role and not nxt_date:
                merged.append({
                    "raw_title":   nxt["raw_title"],
                    "org_line":    g["raw_title"],
                    "date":        date,
                    "description": nxt["description"] + g["description"]
                })
                i += 2
                continue
        merged.append(g)
        i += 1
    return merged


def parse_experience(experience_lines: list) -> list:
    groups = extract_internships(experience_lines)
    groups = _merge_consecutive(groups)
    results = []

    for g in groups:
        raw    = g["raw_title"]
        org_ln = g["org_line"]
        date   = g["date"]

        # "Role at Org Date" pattern (Jeya Kartika, Kiruthika)
        at_m = AT_SPLIT.match(raw)
        if at_m and " at " in raw.lower():
            role_part = at_m.group(1).strip()
            org_part  = at_m.group(2).strip()
            role = _extract_role(role_part) or role_part.title()
            org  = org_part.split(",")[0].strip().title()
        else:
            role = _extract_role(raw)
            if org_ln and not role:
                role = _extract_role(org_ln) or _extract_role(raw)
                org  = _clean_org(org_ln, role, date)
            elif org_ln:
                org = org_ln.split(",")[0].strip().title()
                # Remove date from org if it snuck in
                org_date = _extract_date(org)
                if org_date:
                    org = re.sub(re.escape(org_date), "", org).strip().title()
            else:
                org = _clean_org(raw, role, date)

        # Final clean of org: remove any date still present
        if org:
            leftover_date = _extract_date(org)
            if leftover_date:
                org = re.sub(re.escape(leftover_date), "", org).strip()
                org = re.sub(r"[-–\s]+$", "", org).strip().title()

        results.append({
            "role":         role or None,
            "organization": org  or None,
            "duration":     date or None,
            "description":  " ".join(g["description"]) if g["description"] else None
        })

    return results


# ── PROJECT PARSING ───────────────────────────────────────────────────────────

def parse_projects(project_lines: list) -> list:
    groups = extract_projects(project_lines)
    results = []

    for g in groups:
        title = g["title"]
        desc  = g["description"]

        if "|" in title:
            parts = [p.strip() for p in title.split("|") if p.strip()]
            name  = parts[0]
            tech, date = [], ""
            for p in parts[1:]:
                if "link" in p.lower() or "http" in p.lower(): continue
                d = _extract_date(p)
                if d: date = d; continue
                tech = [t.strip() for t in p.split(",") if t.strip()] if "," in p else ([p] if p else [])

        elif re.search(r"\s[–]\s", title):
            parts = re.split(r"\s[–]\s", title, 1)
            name  = parts[0].strip()
            rest  = parts[1] if len(parts) > 1 else ""
            date  = _extract_date(rest)
            rest2 = re.sub(re.escape(date), "", rest).strip() if date else rest
            tech  = [t.strip() for t in rest2.split(",") if t.strip()]

        elif re.search(r"\s-\s", title) and not title.startswith("-"):
            parts = title.split(" - ", 1)
            name  = parts[0].strip()
            rest  = parts[1] if len(parts) > 1 else ""
            date  = _extract_date(rest)
            rest2 = re.sub(re.escape(date), "", rest).strip() if date else rest
            tech  = [t.strip() for t in rest2.split(",") if t.strip()]

        else:
            date = _extract_date(title)
            name = re.sub(re.escape(date), "", title).strip() if date else title.strip()
            # Clean numbered prefix "1) " or "1. "
            name = re.sub(r"^\d+[\)\.]\s*", "", name).strip()
            tech = []

        # Fallback: date from description
        if not date:
            for dl in desc:
                d = _extract_date(dl)
                if d: date = d; break

        # Fallback: tech from "Tech Stack: ..." or "Technologies: ..."
        if not tech:
            for dl in desc:
                if re.search(r"(tech stack|technologies)\s*:", dl, re.I):
                    after = dl.split(":", 1)[-1]
                    tech  = [t.strip() for t in after.split(",") if t.strip()]
                    break

        results.append({
            "name":        name.strip().title() if name else None,
            "tech_stack":  tech if tech else None,
            "date":        date or None,
            "description": " ".join(desc) if desc else None
        })

    return results


# ── EDUCATION PARSING ─────────────────────────────────────────────────────────

EDU_NOISE = re.compile(
    r"^(cgpa|gpa|grade|batch|of|in|the|and|data|science|artificial|"
    r"intelligence|technology|engineering|percentage|hslc|hsc|sslc|pass|"
    r"expected|cumulative|up|to|iv|sem|relevant|coursework|dbms|"
    r"networks|algorithms|computer|structures|network|web|"
    r"a|an|is|at|for|from|with|this|was|has|are|"
    r"aug|sep|jan|feb|mar|apr|may|jun|jul|oct|nov|dec)$",
    re.I
)


def parse_education(education_lines: list) -> list:
    groups = extract_education(education_lines)
    results = []

    for g in groups:
        dl      = g["degree_line"]
        all_ln  = [dl] + g["description"]
        combined= " ".join(all_ln)

        dm     = DEGREE_PATTERN.search(dl)
        degree = dm.group(0).upper().replace(".", "").strip() if dm else None

        cm   = CGPA_PATTERN.search(combined)
        cgpa = cm.group(2) if cm else None

        ym   = YEAR_ONLY.search(combined)
        year = ym.group(0) if ym else None

        inst = combined
        if dm:  inst = inst.replace(dm.group(0), " ")
        if cm:  inst = inst.replace(cm.group(0), " ")
        if ym:  inst = inst.replace(ym.group(0), " ")
        inst = re.sub(r"[:\-|,/\\()\[\]@]", " ", inst)
        inst = re.sub(r"\s+", " ", inst).strip()

        tokens = [t for t in inst.split()
                  if not EDU_NOISE.match(t) and len(t) > 1 and not t.isdigit()
                  and not re.match(r"\d+\.?\d*%?$", t)]
        institution = " ".join(tokens[:7]).strip().title()

        results.append({
            "degree":      degree or None,
            "institution": institution or None,
            "year":        year or None,
            "cgpa":        cgpa or None
        })

    return results


# ── CERTIFICATION PARSING ──────────────────────────────────────────────────────

def parse_certifications(cert_lines: list) -> list:
    groups = extract_certifications(cert_lines)
    results = []
    for g in groups:
        title = g["title"].strip().title()
        if title:
            results.append({"title": title, "issuer_or_date": g["detail"].strip() or None})
    return results
