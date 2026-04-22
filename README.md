# 🧠 AI Resume Analyzer (ATS + LLM Powered)

An intelligent resume parsing system that extracts structured information from resumes (PDF/DOCX) using a hybrid approach:
- ⚙️ Rule-based NLP pipeline (fast & deterministic)
- 🤖 LLM fallback (Claude API) for handling complex/unstructured resumes

---

## 🚀 Features

- 📄 Supports **PDF, DOCX, TXT**
- 🧩 Extracts structured data:
  - Candidate Name
  - Summary
  - Experience
  - Projects
  - Skills (categorized)
  - Education
  - Certifications
- 🧠 Handles **multiple resume formats** (tested on 19+ real resumes)
- 🔍 Smart section detection (even with non-standard headings)
- 🔗 Anchoring logic for experience & projects
- 🧹 Text normalization (bullets, unicode, whitespace)
- 📊 JSON output (ATS-friendly)
- 🤖 **LLM fallback** for universal resume parsing

---

## 🏗️ Project Architecture


Resume Analyzer Pipeline

Input (PDF / DOCX / TXT)
↓
extractor.py → Extract raw text
↓
normalizer.py → Clean & standardize text
↓
segmenter.py → Split into sections
↓
anchoring.py → Detect entry boundaries
↓
entity_extractor.py → Extract structured fields
↓
schema_mapper.py → Build unified JSON schema
↓
validator.py → Clean, deduplicate, normalize
↓
Output → Terminal (JSON / readable format)
Optional:
→ Claude API fallback for missing sections

---

## 📂 Project Structure

```bash
resume_analyser/
│
├── main.py
├── extractor.py
├── normalizer.py
├── segmenter.py
├── anchoring.py
├── entity_extractor.py
├── project_parser.py
├── schema_mapper.py
├── validator.py
├── output_writer.py
├── requirements.txt
└── methodology.txt
⚙️ Installation
git clone https://github.com/your-username/resume-analyser.git
cd resume-analyser

pip install -r requirements.txt
▶️ Usage
🔹 Single Resume
python main.py "path/to/resume.pdf"
🔹 Folder of Resumes
python main.py "path/to/resumes_folder/"
🔹 JSON Output
python main.py "resume.pdf" --json
🤖 Claude API (Optional - Universal Parsing)

For handling complex or non-standard resumes, enable LLM fallback.

Set API Key
# Windows
set ANTHROPIC_API_KEY=your_api_key_here
Behavior
Rule-based parser runs first
If sections are missing → Claude API is triggered
Returns structured JSON
🧪 Supported Resume Types

✅ Works well for:

Standard resumes (Experience, Projects, Skills, Education)
Tech resumes (internships, projects)
Multi-format layouts (tested on 19 real resumes)

⚠️ Limitations:

Scanned/image PDFs (no text extraction)
Highly designed resumes (multi-column layouts)
Non-English resumes
🔍 Example Output (JSON)
{
  "candidate": {
    "name": "John Doe"
  },
  "summary": "Software developer with experience in web applications",
  "experience": [
    {
      "role": "Software Intern",
      "organization": "ABC Tech",
      "duration": "Jun 2024 - Aug 2024",
      "description": "Worked on backend APIs..."
    }
  ],
  "projects": [
    {
      "name": "Resume Analyzer",
      "tech_stack": ["Python", "NLP"],
      "date": "2025",
      "description": "Built a resume parsing system..."
    }
  ]
}
🧠 Key Concepts Used
Rule-based NLP
Regex pattern matching
Text segmentation & normalization
Heuristic anchoring
Schema mapping & validation
Hybrid AI systems (Rule-based + LLM)
🚧 Future Improvements
🌐 Web UI (React + FastAPI)
📊 Resume scoring (ATS score)
🎯 Job description matching
☁️ Deployment (Vercel + Render)
🌍 Multi-language support
🧾 OCR for scanned resumes
👨‍💻 Author : Sakthi Shriram K

GitHub: https://github.com/Sakthi0400J
LinkedIn: linkedin.com/in/sakthi-shriram-k-6a7410292
⭐ If you like this project

Give it a star ⭐ and feel free to contribute!
