#!/usr/bin/env python3
"""
University of Yggdrasil 2040 — Course Content Generator
Generates 12 lectures and 5 assignments per course based on curriculum data.
"""
import os
import re
import json
import sys
from pathlib import Path

BASE = Path("/home/pi/RunaUniversity2040")

# University lore and naming conventions
UNI_NAME = "University of Yggdrasil"
YEAR = 2040
RUNE_HEADERS = ["ᚠ", "ᚢ", "ᚦ", "ᚬ", "ᚱ", "ᚴ", "ᚺ", "ᚾ", "ᛁ", "ᛃ", "ᛇ", "ᛈ"]

def parse_curriculum(filepath: Path) -> list[dict]:
    """Parse a curriculum.md to extract courses."""
    courses = []
    content = filepath.read_text()
    # Find all course entries in table rows: | CS101 | Course Name | 4 | Description |
    for match in re.finditer(r'\|\s*([A-Z]{2,4}\d{3})\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|', content):
        code, name, credits, desc = match.groups()
        courses.append({
            "code": code.strip(),
            "name": name.strip(),
            "credits": int(credits.strip()),
            "description": desc.strip()
        })
    return courses

def get_degree_info(filepath: Path) -> dict:
    """Extract degree-level info from curriculum."""
    content = filepath.read_text()
    # Extract degree name from first line
    first_line = content.split('\n')[0]
    # e.g. "# Bachelor of Science in Computer Science — University of Yggdrasil, 2040"
    degree_match = re.search(r'#\s*(.+?)\s*—', first_line)
    degree_name = degree_match.group(1).strip() if degree_match else "Unknown Degree"
    return {"degree_name": degree_name, "raw_first_line": first_line}

def generate_lecture_content(course: dict, lecture_num: int, degree_info: dict) -> str:
    """Generate content for a single lecture."""
    code = course["code"]
    name = course["name"]
    desc = course["description"]
    rune = RUNE_HEADERS[(lecture_num - 1) % 12]
    
    # Lecture topics mapped by lecture number
    if lecture_num == 1:
        title = f"Introduction to {name}"
        focus = "foundations"
    elif lecture_num == 2:
        title = f"Core Concepts of {name}"
        focus = "concepts"
    elif lecture_num == 3:
        title = f"Historical Context and Evolution"
        focus = "history"
    elif lecture_num == 4:
        title = f"Theoretical Framework"
        focus = "theory"
    elif lecture_num == 5:
        title = f"Key Methods and Approaches"
        focus = "methods"
    elif lecture_num == 6:
        title = f"Practical Applications I"
        focus = "practice1"
    elif lecture_num == 7:
        title = f"Practical Applications II"
        focus = "practice2"
    elif lecture_num == 8:
        title = f"Advanced Topics in {name}"
        focus = "advanced"
    elif lecture_num == 9:
        title = f"Interdisciplinary Connections"
        focus = "connections"
    elif lecture_num == 10:
        title = f"Ethical Considerations and Societal Impact"
        focus = "ethics"
    elif lecture_num == 11:
        title = f"Current Research and Future Directions"
        focus = "research"
    elif lecture_num == 12:
        title = f"Synthesis and Comprehensive Review"
        focus = "synthesis"
    
    return f"""{rune} **Lecture {lecture_num}: {title}**

**Course:** {code} — {name}  
**Degree:** {degree_info['degree_name']}, {YEAR}

---

### Overview

This lecture explores {focus} aspects of {name.lower()}, building on foundational knowledge from previous sessions. By 2040, {desc.lower()}, and this session examines how {focus}-level understanding shapes both theory and practice.

### Key Topics

- **Topic 1:** Core definitions and terminology specific to {name.lower()}
- **Topic 2:** How {focus} perspectives reshape our understanding of {desc.lower()}
- **Topic 3:** Practical implications for students entering the field in the {YEAR}s
- **Topic 4:** Connections to other courses in the {degree_info['degree_name']} program

### Lecture Notes

The field of {name.lower()} has undergone significant transformation since the early 2020s. Where earlier approaches focused on individual techniques, modern practice emphasizes holistic integration — understanding how {desc.lower()} requires both technical depth and contextual awareness.

Students should pay particular attention to:
1. The progression from foundational techniques to advanced applications
2. How theoretical models inform practical implementation
3. The role of ethics and sustainability in modern {name.lower()}
4. Emerging paradigms that may reshape the field by 2050

### Required Reading

- Course textbook, chapters relevant to {title.lower()}
- Selected research papers from the {YEAR}-2 UoY reading list

### Discussion Questions

1. How has the understanding of {name.lower()} evolved over the past two decades?
2. What are the most significant open problems in this area?
3. How do {focus} considerations change the way we approach practical challenges?

### Practice Problems

- Work through the exercises at the end of the relevant textbook chapters
- Prepare one original question for next session's discussion

---

"""

def generate_assignment_content(course: dict, assignment_num: int, degree_info: dict) -> str:
    """Generate content for a single assignment."""
    code = course["code"]
    name = course["name"]
    desc = course["description"]
    
    assignment_types = [
        ("Foundational Exercise", "Practice core skills and verify understanding of fundamental concepts"),
        ("Applied Analysis", "Apply course concepts to a realistic scenario or case study"),
        ("Research & Synthesis", "Investigate a topic in depth, synthesize findings, and present coherent analysis"),
        ("Design & Implementation", "Design a solution to a given problem and implement or prototype it"),
        ("Comprehensive Project", "Integrate all course concepts in an open-ended project with multiple deliverables"),
    ]
    
    atype, adesc = assignment_types[(assignment_num - 1) % 5]
    
    return f"""\n### Assignment {assignment_num}: {atype}

**Course:** {code} — {name}  
**Type:** {atype}  
**Objective:** {adesc}, specifically within the domain of {name.lower()}.

**Task:** {description_for_assignment(course, assignment_num)}

**Deliverables:**
- Written report or documented solution (as specified)
- Supporting materials (code, diagrams, data as appropriate)
- Self-assessment reflection (150-250 words)

**Grading Rubric:**
- Technical correctness (30%): Solution accurately applies course concepts
- Depth of analysis (25%): Thorough exploration of the topic with evidence
- Communication quality (25%): Clear, well-organized presentation
- Reflection (20%): Thoughtful self-assessment of learning process

**Due:** End of Week {assignment_num * 3} (see course schedule for exact date)

---

"""

def description_for_assignment(course: dict, num: int) -> str:
    """Generate a specific task description based on course and assignment number."""
    name = course["name"]
    desc = course["description"]
    
    templates = [
        f"Complete a set of exercises that demonstrate mastery of core concepts in {name.lower()}. Include worked examples, proofs of correctness where applicable, and reflection on which concepts were most challenging.",
        f"Analyze a real-world scenario related to {desc.lower()}. Identify key challenges, apply relevant frameworks from the course, propose solutions, and evaluate trade-offs. Your analysis should reference at least 3 course topics.",
        f"Conduct research on a contemporary issue in {name.lower()}. Synthesize at least 5 sources (academic papers, industry reports, or reputable journalism from 2035-2040). Present findings as a structured literature review with critical analysis.",
        f"Design and prototype a solution to a problem in {name.lower()}. Begin with requirements analysis, proceed through design, implement a proof-of-concept, and evaluate your solution against stated success criteria.",
        f"Integrate concepts from across the entire course to address a complex, open-ended challenge in {name.lower()}. Your project should demonstrate decomposition, abstraction, analytical rigor, and practical application. Include a project proposal, progress report, and final deliverable.",
    ]
    
    return templates[(num - 1) % 5]


def generate_course_file(course: dict, degree_info: dict, degree_path: Path) -> Path:
    """Generate the full lectures+assignments markdown file for one course."""
    code = course["code"]
    name = course["name"]
    desc = course["description"]
    
    # Create course directory
    course_dir = degree_path / code
    course_dir.mkdir(parents=True, exist_ok=True)
    
    # Build content
    content = f"""# {code}: {name}
## {degree_info['degree_name']} — {UNI_NAME}, {YEAR}

**Credits:** {course['credits']}  
**Description:** {desc}

---

"""
    
    # Add lectures
    content += "## Lectures\n\n"
    for i in range(1, 13):
        content += generate_lecture_content(course, i, degree_info)
    
    # Add assignments
    content += "## Assignments\n\n"
    for i in range(1, 6):
        content += generate_assignment_content(course, i, degree_info)
    
    # Write file
    filepath = course_dir / "lectures.md"
    filepath.write_text(content)
    return filepath


def process_degree(degree_path: Path) -> list[Path]:
    """Process one degree: generate all course content."""
    curriculum_file = degree_path / "curriculum.md"
    if not curriculum_file.exists():
        print(f"  ⚠ No curriculum.md in {degree_path}")
        return []
    
    degree_info = get_degree_info(curriculum_file)
    courses = parse_curriculum(curriculum_file)
    
    if not courses:
        print(f"  ⚠ No courses found in {curriculum_file}")
        return []
    
    print(f"  📚 {degree_info['degree_name']}: {len(courses)} courses")
    files = []
    for course in courses:
        filepath = generate_course_file(course, degree_info, degree_path)
        files.append(filepath)
        print(f"    ✅ {course['code']}: {course['name']}")
    
    return files


def main():
    all_files = []
    
    for level in ["bachelors", "masters", "phd"]:
        level_path = BASE / level
        if not level_path.exists():
            continue
        
        print(f"\n🏛️  Processing {level.upper()}")
        for degree_dir in sorted(level_path.iterdir()):
            if degree_dir.is_dir() and (degree_dir / "curriculum.md").exists():
                files = process_degree(degree_dir)
                all_files.extend(files)
    
    print(f"\n✨ Generated {len(all_files)} course content files")
    print(f"   Total lectures: {len(all_files) * 12}")
    print(f"   Total assignments: {len(all_files) * 5}")


if __name__ == "__main__":
    main()