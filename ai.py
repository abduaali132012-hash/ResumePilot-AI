"""
ResumePilot AI - Core AI Module
Handles all AI-powered resume analysis, score calculations, and recommendations.
"""

import re
from typing import Dict, List, Any



def extract_key_skills(text: str) -> List[str]:
    """
    Extract key skills from resume or job description text.
    
    Args:
        text: The resume or job description text
        
    Returns:
        List of extracted skill keywords
    """
    # Common skill patterns and keywords
    skill_patterns = [
        r'\b(?:Python|JavaScript|TypeScript|Java|C\+\+|C#|Go|Rust|PHP|Ruby|Swift)\b',
        r'\b(?:React|Vue|Angular|Django|Flask|FastAPI|Spring|Node\.js)\b',
        r'\b(?:AWS|Azure|GCP|Kubernetes|Docker|Jenkins|GitLab|GitHub)\b',
        r'\b(?:SQL|PostgreSQL|MongoDB|Redis|Elasticsearch)\b',
        r'\b(?:Machine Learning|AI|NLP|Deep Learning|TensorFlow|PyTorch)\b',
        r'\b(?:REST API|GraphQL|Microservices|CI\/CD)\b',
        r'\b(?:Leadership|Communication|Project Management|Agile|Scrum)\b',
    ]
    
    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)
    
    return list(set(skills))  # Remove duplicates


def calculate_ats_score(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Calculate ATS compatibility score between resume and job description.
    
    Args:
        resume_text: The resume content
        job_description: The target job description
        
    Returns:
        Dictionary with score metrics
    """
    resume_skills = set(skill.lower() for skill in extract_key_skills(resume_text))
    job_skills = set(skill.lower() for skill in extract_key_skills(job_description))
    
    # Calculate match percentage
    if not job_skills:
        match_percentage = 0
    else:
        matches = len(resume_skills & job_skills)
        match_percentage = (matches / len(job_skills)) * 100
    
    return {
        "score": round(match_percentage, 2),
        "matched_skills": list(resume_skills & job_skills),
        "missing_skills": list(job_skills - resume_skills),
        "total_job_skills": len(job_skills),
        "matched_count": len(resume_skills & job_skills),
    }


def find_skill_gaps(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Identify skill gaps between resume and job requirements.
    
    Args:
        resume_text: The resume content
        job_description: The target job description
        
    Returns:
        Dictionary with skill gap analysis
    """
    ats_result = calculate_ats_score(resume_text, job_description)
    missing_skills = ats_result.get("missing_skills", [])
    
    return {
        "critical_gaps": missing_skills[:5] if missing_skills else [],
        "total_gaps": len(missing_skills),
        "recommendations": [
            f"Add experience with {skill}" for skill in missing_skills[:3]
        ] if missing_skills else ["Resume covers all key job requirements!"],
    }


def calculate_match_percentage(resume_text: str, job_description: str) -> float:
    """
    Calculate overall match percentage between resume and job description.
    
    Args:
        resume_text: The resume content
        job_description: The target job description
        
    Returns:
        Match percentage as float (0-100)
    """
    ats_result = calculate_ats_score(resume_text, job_description)
    return ats_result.get("score", 0)


def analyze_resume_structure(resume_text: str) -> Dict[str, Any]:
    """
    Analyze the structure and completeness of a resume.
    
    Args:
        resume_text: The resume content
        
    Returns:
        Dictionary with structural analysis
    """
    sections = {
        "contact": bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)),
        "experience": bool(re.search(r'(?i)(experience|employment|work history)', resume_text)),
        "education": bool(re.search(r'(?i)(education|degree|university|college|school)', resume_text)),
        "skills": bool(re.search(r'(?i)(skills|technical skills|core competencies)', resume_text)),
        "certifications": bool(re.search(r'(?i)(certifications?|licenses?|awards?)', resume_text)),
    }
    
    present_sections = sum(sections.values())
    completeness = (present_sections / len(sections)) * 100
    
    return {
        "sections_present": sections,
        "completeness_score": round(completeness, 2),
        "missing_sections": [k for k, v in sections.items() if not v],
        "suggestions": [
            f"Add a {section} section" for section, present in sections.items() if not present
        ],
    }


def get_ai_insights_summary(resume_text: str, job_description: str) -> str:
    """
    Generate a summary of key insights for the resume-job match.
    
    Args:
        resume_text: The resume content
        job_description: The target job description
        
    Returns:
        Summary string of insights
    """
    match_pct = calculate_match_percentage(resume_text, job_description)
    ats_result = calculate_ats_score(resume_text, job_description)
    structure = analyze_resume_structure(resume_text)
    
    if match_pct >= 80:
        fit_assessment = "excellent"
    elif match_pct >= 60:
        fit_assessment = "good"
    elif match_pct >= 40:
        fit_assessment = "moderate"
    else:
        fit_assessment = "limited"
    
    summary = f"""
    Resume-Job Match Analysis:
    - Overall Match: {match_pct}% ({fit_assessment} fit)
    - Matched Skills: {ats_result['matched_count']} out of {ats_result['total_job_skills']} required
    - Critical Gaps: {len(ats_result['missing_skills'])} skills missing
    - Resume Completeness: {structure['completeness_score']}%
    """
    
    return summary.strip()


# Export public API
__all__ = [
    "extract_key_skills",
    "calculate_ats_score",
    "find_skill_gaps",
    "calculate_match_percentage",
    "analyze_resume_structure",
    "get_ai_insights_summary",
]

