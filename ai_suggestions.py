import os
import json
import logging
from openai import OpenAI

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def get_ai_suggestions(resume_text, job_description):
    """
    Get AI-powered suggestions for ATS optimization
    Returns structured suggestions or fallback recommendations
    """
    if not openai_client:
        logging.warning("OpenAI API key not available, using fallback suggestions")
        return get_fallback_suggestions()
    
    try:
        prompt = f"""
You are an ATS optimization expert. Analyze this resume against the job description 
and provide specific suggestions to improve ATS compatibility and matching.

RESUME: {resume_text[:3000]}  

JOB DESCRIPTION: {job_description[:2000]}

Provide analysis in JSON format:
{{
    "format_suggestions": [
        "List of 3-5 specific format improvements for ATS compatibility"
    ],
    "content_suggestions": [
        "List of 3-5 content improvements to better match the job"
    ],
    "improvement_examples": [
        "Specific examples of how to improve sections with before/after suggestions"
    ],
    "missing_skills": [
        "List of important skills from job description not found in resume"
    ],
    "optimization_tips": [
        "List of 3-4 general ATS optimization tips"
    ]
}}

Keep suggestions specific, actionable, and based on ATS best practices.
Focus on keyword optimization, proper formatting, and content relevance.
"""

        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert ATS optimization consultant. Provide detailed, actionable advice in the requested JSON format."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1500,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if content:
            suggestions = json.loads(content)
        else:
            return get_fallback_suggestions()
        return validate_and_format_suggestions(suggestions)
        
    except Exception as e:
        logging.error(f"Error getting AI suggestions: {str(e)}")
        return get_fallback_suggestions()

def validate_and_format_suggestions(suggestions):
    """Validate and format AI suggestions"""
    try:
        # Ensure all required keys exist with defaults
        formatted = {
            "format_suggestions": suggestions.get("format_suggestions", [])[:5],
            "content_suggestions": suggestions.get("content_suggestions", [])[:5],
            "improvement_examples": suggestions.get("improvement_examples", [])[:4],
            "missing_skills": suggestions.get("missing_skills", [])[:8],
            "optimization_tips": suggestions.get("optimization_tips", [])[:4]
        }
        
        # Add fallback suggestions if any category is empty
        if not formatted["format_suggestions"]:
            formatted["format_suggestions"] = get_fallback_suggestions()["format_suggestions"][:3]
        
        if not formatted["content_suggestions"]:
            formatted["content_suggestions"] = get_fallback_suggestions()["content_suggestions"][:3]
            
        return formatted
        
    except Exception as e:
        logging.error(f"Error validating suggestions: {str(e)}")
        return get_fallback_suggestions()

def get_fallback_suggestions():
    """Fallback suggestions when AI is not available"""
    return {
        "format_suggestions": [
            "Use standard section headings like 'Experience', 'Education', 'Skills'",
            "Include dates in consistent MM/YYYY format",
            "Use bullet points to organize information clearly",
            "Save your resume as both PDF and Word formats",
            "Ensure your contact information is at the top of the resume"
        ],
        "content_suggestions": [
            "Include specific keywords from the job description throughout your resume",
            "Quantify your achievements with numbers, percentages, and metrics",
            "Use action verbs to start each bullet point in your experience section",
            "Tailor your professional summary to match the job requirements",
            "Include relevant certifications and technical skills mentioned in the job posting"
        ],
        "improvement_examples": [
            "Instead of 'Responsible for managing team', write 'Led cross-functional team of 8 developers'",
            "Replace 'Worked on projects' with 'Delivered 15+ client projects on time and under budget'",
            "Change 'Good communication skills' to 'Presented quarterly reports to C-level executives'",
            "Update 'Helped customers' to 'Resolved 95% of customer inquiries within 24 hours'"
        ],
        "missing_skills": [
            "Review the job description for technical skills not mentioned in your resume",
            "Look for industry-specific terminology and acronyms to include",
            "Check for soft skills that are emphasized in the job posting",
            "Identify any required certifications or qualifications you may have missed"
        ],
        "optimization_tips": [
            "Use exact keywords from the job description (not synonyms)",
            "Include a skills section with both hard and soft skills",
            "Keep your resume to 1-2 pages for optimal ATS scanning",
            "Use simple, clean formatting without complex graphics or tables"
        ]
    }
