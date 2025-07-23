import json
import os
from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY


def generate_analysis_pdf(analysis_data, filename="resume_analysis_report.pdf"):
    """
    Generate a comprehensive PDF report from analysis data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#0d6efd'),
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#198754'),
        borderWidth=1,
        borderColor=colors.HexColor('#198754'),
        borderPadding=5
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.HexColor('#6c757d')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Build document content
    story = []
    
    # Title and header
    story.append(Paragraph("Resume ATS Analysis Report", title_style))
    story.append(Paragraph("Gopi's Resume Analyzer", styles['Heading3']))
    story.append(Spacer(1, 20))
    
    # Analysis summary
    story.append(Paragraph("Analysis Summary", heading_style))
    story.append(Spacer(1, 10))
    
    # Create summary table
    summary_data = [
        ['Metric', 'Score', 'Status'],
        ['Overall ATS Score', f"{analysis_data.get('total_score', 0)}/100", get_score_status(analysis_data.get('total_score', 0))],
        ['Keyword Match', f"{analysis_data.get('keyword_score', 0)}/60", get_score_status(analysis_data.get('keyword_score', 0), 60)],
        ['Grammar & Language', f"{analysis_data.get('grammar_score', 0)}/20", get_score_status(analysis_data.get('grammar_score', 0), 20)],
        ['Format & Structure', f"{analysis_data.get('format_score', 0)}/20", get_score_status(analysis_data.get('format_score', 0), 20)],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Keyword Analysis
    story.append(Paragraph("Keyword Analysis", heading_style))
    story.append(Spacer(1, 10))
    
    # Matching keywords
    matching_keywords = json.loads(analysis_data.get('matching_keywords', '[]'))
    if matching_keywords:
        story.append(Paragraph("✓ Matching Keywords Found:", subheading_style))
        keywords_text = ", ".join(matching_keywords[:15])  # Limit to first 15 keywords
        if len(matching_keywords) > 15:
            keywords_text += f" and {len(matching_keywords) - 15} more..."
        story.append(Paragraph(keywords_text, body_style))
        story.append(Spacer(1, 10))
    
    # Missing keywords
    missing_keywords = json.loads(analysis_data.get('missing_keywords', '[]'))
    if missing_keywords:
        story.append(Paragraph("⚠ Missing Keywords to Add:", subheading_style))
        missing_text = ", ".join(missing_keywords[:15])  # Limit to first 15 keywords
        if len(missing_keywords) > 15:
            missing_text += f" and {len(missing_keywords) - 15} more..."
        story.append(Paragraph(missing_text, body_style))
        story.append(Spacer(1, 15))
    
    # AI Suggestions
    story.append(Paragraph("AI-Powered Optimization Suggestions", heading_style))
    story.append(Spacer(1, 10))
    
    ai_suggestions = json.loads(analysis_data.get('ai_suggestions', '[]'))
    if ai_suggestions:
        for i, suggestion in enumerate(ai_suggestions, 1):
            story.append(Paragraph(f"{i}. {suggestion}", body_style))
            story.append(Spacer(1, 5))
    else:
        # Provide fallback suggestions based on score
        fallback_suggestions = generate_fallback_suggestions(analysis_data)
        for i, suggestion in enumerate(fallback_suggestions, 1):
            story.append(Paragraph(f"{i}. {suggestion}", body_style))
            story.append(Spacer(1, 5))
    
    story.append(Spacer(1, 20))
    
    # Action Plan Section
    story.append(Paragraph("Immediate Action Plan", heading_style))
    story.append(Spacer(1, 10))
    
    action_plan = generate_action_plan(analysis_data)
    
    # Priority Actions
    story.append(Paragraph("🎯 Priority Actions (Complete First)", subheading_style))
    for i, action in enumerate(action_plan['priority'], 1):
        story.append(Paragraph(f"{i}. {action}", body_style))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 10))
    
    # Quick Wins
    story.append(Paragraph("⚡ Quick Wins (Easy Improvements)", subheading_style))
    for i, action in enumerate(action_plan['quick_wins'], 1):
        story.append(Paragraph(f"{i}. {action}", body_style))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 10))
    
    # Long-term Goals
    story.append(Paragraph("📈 Long-term Improvements", subheading_style))
    for i, action in enumerate(action_plan['long_term'], 1):
        story.append(Paragraph(f"{i}. {action}", body_style))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 15))
    
    # Detailed Recommendations
    story.append(Paragraph("Detailed Improvement Recommendations", heading_style))
    story.append(Spacer(1, 10))
    
    recommendations = generate_detailed_recommendations(analysis_data)
    for category, recs in recommendations.items():
        story.append(Paragraph(category, subheading_style))
        for rec in recs:
            story.append(Paragraph(f"• {rec}", body_style))
        story.append(Spacer(1, 10))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#6c757d')))
    story.append(Spacer(1, 10))
    
    footer_text = f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    story.append(Paragraph(footer_text, styles['Normal']))
    story.append(Paragraph("Generated by Gopi's Resume Analyzer", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def get_score_status(score, max_score=100):
    """Get status text based on score"""
    percentage = (score / max_score) * 100
    if percentage >= 80:
        return "Excellent"
    elif percentage >= 60:
        return "Good"
    elif percentage >= 40:
        return "Fair"
    else:
        return "Needs Improvement"


def generate_fallback_suggestions(analysis_data):
    """Generate comprehensive, personalized suggestions based on resume analysis"""
    suggestions = []
    total_score = analysis_data.get('total_score', 0)
    keyword_score = analysis_data.get('keyword_score', 0)
    grammar_score = analysis_data.get('grammar_score', 0)
    format_score = analysis_data.get('format_score', 0)
    resume_text = analysis_data.get('resume_text', '').lower()
    
    # Keyword-specific suggestions
    if keyword_score < 45:
        matching_keywords = json.loads(analysis_data.get('matching_keywords', '[]'))
        missing_keywords = json.loads(analysis_data.get('missing_keywords', '[]'))
        
        if len(matching_keywords) < 5:
            suggestions.append("Critical: Add more job-relevant keywords. Currently only matching " + str(len(matching_keywords)) + " key terms")
        
        if missing_keywords:
            suggestions.append("Include these missing keywords: " + ", ".join(missing_keywords[:8]))
        
        suggestions.append("Mirror exact phrases from the job description (e.g., 'project management' instead of 'managing projects')")
        suggestions.append("Add a 'Core Competencies' or 'Technical Skills' section with relevant keywords")
    
    # Grammar and content suggestions
    if grammar_score < 17:
        suggestions.append("Proofread thoroughly - grammar issues detected that could hurt ATS ranking")
        suggestions.append("Use consistent verb tenses (past tense for previous roles, present for current position)")
    
    # Content enhancement based on resume analysis
    if 'managed' not in resume_text and 'led' not in resume_text:
        suggestions.append("Add leadership examples using action verbs like 'managed,' 'led,' or 'supervised'")
    
    if not any(word in resume_text for word in ['increased', 'improved', 'reduced', 'achieved']):
        suggestions.append("Include quantifiable achievements (e.g., 'Increased sales by 25%' or 'Reduced processing time by 30%')")
    
    if not any(word in resume_text for word in ['project', 'team', 'collaboration']):
        suggestions.append("Highlight teamwork and project experience to show collaborative skills")
    
    # Format-specific suggestions
    if format_score < 16:
        if 'education' not in resume_text:
            suggestions.append("Add an Education section with your degree, institution, and graduation year")
        if 'experience' not in resume_text and 'work' not in resume_text:
            suggestions.append("Include a clear Work Experience or Professional Experience section")
        if not any(char in analysis_data.get('resume_text', '') for char in ['•', '-', '*']):
            suggestions.append("Use bullet points to organize information for better readability")
    
    # Industry-specific suggestions based on content
    if any(tech_term in resume_text for tech_term in ['python', 'javascript', 'software', 'development']):
        suggestions.append("For tech roles: Include specific programming languages, frameworks, and tools you've used")
        suggestions.append("Add links to your GitHub profile or portfolio to showcase your technical work")
    
    if any(business_term in resume_text for business_term in ['sales', 'marketing', 'business', 'customer']):
        suggestions.append("For business roles: Quantify your impact on revenue, customer satisfaction, or market growth")
        suggestions.append("Include relevant certifications or training in business methodologies")
    
    # Score-based personalized advice
    if total_score >= 80:
        suggestions.append("Your resume is strong! Focus on tailoring keywords for each specific job application")
        suggestions.append("Consider adding industry certifications or recent training to stay competitive")
    elif total_score >= 70:
        suggestions.append("Good foundation! Small improvements in keyword matching will significantly boost your ATS score")
        suggestions.append("Add more specific examples of your accomplishments with measurable results")
    else:
        suggestions.append("Priority: Focus on adding job-relevant keywords and improving resume structure")
        suggestions.append("Consider having a professional review your resume for additional improvements")
    
    # Length-based suggestions
    word_count = len(analysis_data.get('resume_text', '').split())
    if word_count < 200:
        suggestions.append("Expand your resume content - aim for 300-600 words to provide sufficient detail")
    elif word_count > 800:
        suggestions.append("Consider condensing content - focus on most relevant and recent experiences")
    
    # Always include strategic suggestions
    suggestions.extend([
        "Customize your resume for each job application using specific keywords from the posting",
        "Include a professional summary that mirrors the job requirements and your key qualifications",
        "Use standard section headers (Experience, Education, Skills) for ATS compatibility"
    ])
    
    return suggestions[:12]  # Return up to 12 personalized suggestions


def generate_detailed_recommendations(analysis_data):
    """Generate detailed, personalized recommendations by category"""
    recommendations = {}
    
    keyword_score = analysis_data.get('keyword_score', 0)
    grammar_score = analysis_data.get('grammar_score', 0)
    format_score = analysis_data.get('format_score', 0)
    resume_text = analysis_data.get('resume_text', '').lower()
    missing_keywords = json.loads(analysis_data.get('missing_keywords', '[]'))
    matching_keywords = json.loads(analysis_data.get('matching_keywords', '[]'))
    
    # Strategic Keyword Optimization
    keyword_recs = []
    if keyword_score < 45:
        keyword_recs.extend([
            f"Priority: Add {min(8, len(missing_keywords))} missing keywords from job description",
            "Use exact phrases from job posting (e.g., 'data analysis' not 'analyzing data')",
            "Include synonyms and related terms (e.g., 'ML' and 'Machine Learning')",
            "Integrate keywords naturally in context, not just in lists"
        ])
        if missing_keywords:
            keyword_recs.append(f"Specifically add: {', '.join(missing_keywords[:6])}")
    else:
        keyword_recs.extend([
            f"Strong keyword alignment with {len(matching_keywords)} matches",
            "Fine-tune by adding industry-specific terminology",
            "Include emerging skills relevant to your field"
        ])
    
    # Professional Writing Enhancement
    content_recs = []
    if grammar_score < 17:
        content_recs.extend([
            "Review for grammar consistency - detected issues that reduce professional impact",
            "Use parallel structure in bullet points (start each with action verb)",
            "Eliminate filler words and redundant phrases",
            "Ensure consistent formatting of dates, locations, and job titles"
        ])
    
    # Add content-specific recommendations
    if 'achieved' not in resume_text and 'accomplished' not in resume_text:
        content_recs.append("Add specific achievements and outcomes (not just responsibilities)")
    
    if not any(metric in resume_text for metric in ['%', 'increased', 'reduced', 'improved']):
        content_recs.append("Quantify your impact with percentages, dollar amounts, or time savings")
    
    content_recs.extend([
        "Use industry-specific action verbs relevant to your field",
        "Show progression and growth in your career trajectory",
        "Demonstrate problem-solving abilities with concrete examples"
    ])
    
    # Structure and Formatting
    format_recs = []
    if format_score < 16:
        format_recs.extend([
            "Ensure clear section headers (Experience, Education, Skills, etc.)",
            "Use consistent formatting for dates and locations",
            "Maintain uniform bullet point style throughout",
            "Check that contact information is prominently displayed"
        ])
    
    # Add format-specific analysis
    if 'skills' not in resume_text and 'competencies' not in resume_text:
        format_recs.append("Add a dedicated Skills or Core Competencies section")
    
    if not any(bullet in analysis_data.get('resume_text', '') for bullet in ['•', '-', '*']):
        format_recs.append("Use bullet points to organize information for easy scanning")
    
    format_recs.extend([
        "Use standard fonts (Arial, Calibri, Times New Roman) for ATS compatibility",
        "Maintain appropriate white space for readability",
        "Ensure consistent indentation and alignment"
    ])
    
    # Industry-Specific Recommendations
    industry_recs = []
    
    # Tech industry suggestions
    if any(tech_term in resume_text for tech_term in ['software', 'developer', 'engineer', 'programming']):
        industry_recs.extend([
            "Include specific programming languages, frameworks, and tools",
            "Mention software development methodologies (Agile, Scrum, etc.)",
            "Add links to GitHub, portfolio, or technical blog",
            "Quantify code contributions (lines of code, features delivered, etc.)"
        ])
    
    # Business/Sales suggestions
    elif any(biz_term in resume_text for biz_term in ['sales', 'business', 'marketing', 'account']):
        industry_recs.extend([
            "Highlight revenue generation and client acquisition numbers",
            "Include customer satisfaction scores or retention rates",
            "Mention CRM systems and sales tools you've used",
            "Show market expansion or territory growth achievements"
        ])
    
    # Management suggestions
    elif any(mgmt_term in resume_text for mgmt_term in ['manager', 'director', 'supervisor', 'lead']):
        industry_recs.extend([
            "Specify team sizes managed and organizational scope",
            "Include budget management and cost reduction achievements",
            "Highlight process improvements and efficiency gains",
            "Show measurable team performance improvements"
        ])
    
    # General industry recommendations
    if not industry_recs:
        industry_recs.extend([
            "Research industry-specific keywords and terminology for your field",
            "Include relevant certifications and professional development",
            "Highlight transferable skills relevant to target positions",
            "Show understanding of industry trends and challenges"
        ])
    
    # Strategic Improvements
    strategic_recs = [
        "Tailor your resume for each specific job application",
        "Use job description keywords in context throughout your resume",
        "Align your professional summary with the target role requirements",
        "Include relevant volunteer work or projects if experience is limited",
        "Show continuous learning through courses, certifications, or training"
    ]
    
    # Score-based priority recommendations
    total_score = analysis_data.get('total_score', 0)
    if total_score < 70:
        strategic_recs.insert(0, "Priority: Focus on keyword optimization and content enhancement first")
    elif total_score < 85:
        strategic_recs.insert(0, "Focus on fine-tuning keywords and adding quantified achievements")
    else:
        strategic_recs.insert(0, "Excellent foundation - focus on customization for each application")
    
    # Build recommendations dictionary
    if keyword_recs:
        recommendations["Keyword Optimization"] = keyword_recs
    if content_recs:
        recommendations["Content & Language"] = content_recs
    if format_recs:
        recommendations["Format & Structure"] = format_recs
    if industry_recs:
        recommendations["Industry-Specific Tips"] = industry_recs
    recommendations["Strategic Improvements"] = strategic_recs
    
    return recommendations


def generate_action_plan(analysis_data):
    """Generate a prioritized action plan based on analysis results"""
    total_score = analysis_data.get('total_score', 0)
    keyword_score = analysis_data.get('keyword_score', 0)
    grammar_score = analysis_data.get('grammar_score', 0)
    format_score = analysis_data.get('format_score', 0)
    resume_text = analysis_data.get('resume_text', '').lower()
    missing_keywords = json.loads(analysis_data.get('missing_keywords', '[]'))
    
    priority_actions = []
    quick_wins = []
    long_term = []
    
    # Priority actions based on lowest scores
    if keyword_score < 40:
        priority_actions.append(f"Add the top 5 missing keywords: {', '.join(missing_keywords[:5])}")
        priority_actions.append("Create a 'Core Competencies' section with job-relevant skills")
    
    if format_score < 15:
        priority_actions.append("Add clear section headers: Professional Summary, Experience, Education, Skills")
        priority_actions.append("Use bullet points to organize your experience descriptions")
    
    if grammar_score < 16:
        priority_actions.append("Proofread entire document for grammar and spelling errors")
        priority_actions.append("Ensure consistent verb tenses throughout the resume")
    
    # Quick wins - easy improvements
    if 'phone' not in resume_text and 'email' not in resume_text:
        quick_wins.append("Add complete contact information (phone, email, location)")
    
    if not any(date in analysis_data.get('resume_text', '') for date in ['2020', '2021', '2022', '2023', '2024']):
        quick_wins.append("Include employment dates to show your career timeline")
    
    if not any(bullet in analysis_data.get('resume_text', '') for bullet in ['•', '-', '*']):
        quick_wins.append("Convert job descriptions to bullet points for better readability")
    
    if 'summary' not in resume_text and 'objective' not in resume_text:
        quick_wins.append("Add a professional summary that highlights your key qualifications")
    
    # Content-based quick wins
    if len(analysis_data.get('resume_text', '').split()) < 250:
        quick_wins.append("Expand your experience descriptions with more specific details")
    
    if not any(action in resume_text for action in ['managed', 'led', 'developed', 'implemented']):
        quick_wins.append("Start bullet points with strong action verbs (managed, developed, implemented)")
    
    # Industry-specific quick wins
    if any(tech_term in resume_text for tech_term in ['software', 'developer', 'programming']):
        quick_wins.append("List specific programming languages and technical tools you've used")
    elif any(biz_term in resume_text for biz_term in ['sales', 'marketing', 'business']):
        quick_wins.append("Add quantifiable results (revenue generated, clients acquired, etc.)")
    
    # Long-term improvements
    long_term.append("Research and add emerging skills relevant to your target industry")
    long_term.append("Obtain relevant certifications or complete professional development courses")
    long_term.append("Build a portfolio or online presence to complement your resume")
    
    if total_score < 70:
        long_term.append("Consider having your resume professionally reviewed by industry experts")
        long_term.append("Attend networking events to understand current industry requirements")
    
    # Score-specific long-term goals
    if keyword_score >= 45:
        long_term.append("Stay updated with industry terminology and adjust keywords for each application")
    else:
        long_term.append("Create multiple resume versions tailored to different job types")
    
    long_term.extend([
        "Update your LinkedIn profile to match your optimized resume",
        "Prepare specific examples and stories to support each resume accomplishment",
        "Set up job alerts for positions matching your updated keyword profile"
    ])
    
    # Ensure we have content for each category
    if not priority_actions:
        priority_actions.append("Continue fine-tuning keywords for each specific job application")
        priority_actions.append("Review and update resume content regularly to stay current")
    
    if not quick_wins:
        quick_wins.append("Review formatting consistency throughout the document")
        quick_wins.append("Ensure all information is current and accurate")
    
    return {
        'priority': priority_actions[:4],  # Max 4 priority items
        'quick_wins': quick_wins[:6],      # Max 6 quick wins
        'long_term': long_term[:5]         # Max 5 long-term goals
    }