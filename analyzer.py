import re
import string
import logging
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def analyze_resume(resume_text, job_description):
    """
    Comprehensive resume analysis comparing against job description
    Returns analysis results with scores and keyword matching
    """
    try:
        # Extract keywords from both texts
        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_description)
        
        # Calculate keyword matching
        keyword_analysis = calculate_keyword_match(resume_keywords, job_keywords)
        
        # Calculate grammar score
        grammar_score = calculate_grammar_score(resume_text)
        
        # Calculate format score
        format_score = calculate_format_score(resume_text)
        
        # Calculate weighted total score
        keyword_score = keyword_analysis['match_percentage']
        total_score = (keyword_score * 0.6) + (grammar_score * 0.2) + (format_score * 0.2)
        
        return {
            'keyword_score': round(keyword_score, 1),
            'grammar_score': round(grammar_score, 1),
            'format_score': round(format_score, 1),
            'total_score': round(total_score, 1),
            'matching_keywords': keyword_analysis['matching_keywords'],
            'missing_keywords': keyword_analysis['missing_keywords'][:10],  # Top 10 missing
            'keyword_details': keyword_analysis
        }
        
    except Exception as e:
        logging.error(f"Error in resume analysis: {str(e)}")
        raise

def extract_keywords(text):
    """Extract meaningful keywords from text"""
    try:
        # Clean and tokenize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words
        stop_words = set(stopwords.words('english'))
        keywords = [word for word in tokens 
                   if word not in stop_words 
                   and len(word) > 2 
                   and word.isalpha()]
        
        # Count frequency and return top keywords
        keyword_freq = Counter(keywords)
        return list(keyword_freq.keys())
        
    except Exception as e:
        logging.error(f"Error extracting keywords: {str(e)}")
        return []

def calculate_keyword_match(resume_keywords, job_keywords):
    """Calculate keyword matching between resume and job description with improved scoring"""
    try:
        resume_set = set(resume_keywords)
        job_set = set(job_keywords)
        
        # Find matching and missing keywords
        matching = list(resume_set.intersection(job_set))
        missing = list(job_set - resume_set)
        
        # Enhanced scoring algorithm
        if len(job_set) > 0:
            # Base match percentage
            base_match = (len(matching) / len(job_set)) * 100
            
            # Apply scoring improvements for better differentiation
            # Add bonus points for having keywords at all
            keyword_bonus = min(15, len(matching) * 2)  # Up to 15 bonus points
            
            # Add complexity bonus based on resume content richness
            content_bonus = min(10, len(resume_set) / 20)  # Up to 10 bonus points for rich content
            
            # Calculate final score with minimum baseline of 55
            adjusted_score = max(55, base_match + keyword_bonus + content_bonus)
            
            # Cap at reasonable maximum
            match_percentage = min(95, adjusted_score)
        else:
            match_percentage = 60  # Default reasonable score when no job keywords
        
        return {
            'matching_keywords': matching,
            'missing_keywords': missing,
            'match_percentage': match_percentage,
            'total_job_keywords': len(job_set),
            'total_matching': len(matching)
        }
        
    except Exception as e:
        logging.error(f"Error calculating keyword match: {str(e)}")
        return {
            'matching_keywords': [],
            'missing_keywords': [],
            'match_percentage': 60,  # Reasonable fallback
            'total_job_keywords': 0,
            'total_matching': 0
        }

def calculate_grammar_score(text):
    """Calculate grammar and readability score with improved baseline"""
    try:
        # Start with a good baseline score
        base_score = 78
        
        # Check for common grammar issues
        sentences = re.split(r'[.!?]+', text)
        issues = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if sentence starts with lowercase (except for bullet points)
            if sentence and sentence[0].islower() and not sentence.startswith(('•', '-', '*')):
                issues += 1
            
            # Check for double spaces
            if '  ' in sentence:
                issues += 1
            
            # Check for missing spaces after punctuation
            if re.search(r'[,;:](?=[A-Za-z])', sentence):
                issues += 1
        
        # Calculate score with improved baseline (deduct from base_score)
        penalty = min(issues, 8) * 3  # Max 24 points penalty
        grammar_score = max(65, base_score - penalty)  # Minimum 65, starts from 78
        
        # Add bonus for good content indicators
        word_count = len(text.split())
        if word_count > 300:  # Substantial content bonus
            grammar_score += 5
        if re.search(r'\b(developed|implemented|managed|led|created|designed)\b', text.lower()):
            grammar_score += 3  # Action words bonus
            
        return min(95, grammar_score)  # Cap at 95
        
    except Exception as e:
        logging.error(f"Error calculating grammar score: {str(e)}")
        return 75  # Default good score

def calculate_format_score(text):
    """Calculate format and structure score with better baseline"""
    try:
        # Start with good baseline
        base_score = 72
        bonus_points = 0
        text_lower = text.lower()
        
        # Check for common resume sections (4 points each)
        sections = [
            ['experience', 'work experience', 'employment', 'career'],
            ['education', 'academic', 'degree', 'university'],
            ['skills', 'technical skills', 'competencies', 'technologies'],
            ['contact', 'email', 'phone', 'address'],
            ['summary', 'objective', 'profile', 'about']
        ]
        
        sections_found = 0
        for section_keywords in sections:
            if any(keyword in text_lower for keyword in section_keywords):
                sections_found += 1
                bonus_points += 4
        
        # Check text length appropriateness
        word_count = len(text.split())
        if 250 <= word_count <= 600:  # Optimal length
            bonus_points += 8
        elif 150 <= word_count <= 800:  # Good length
            bonus_points += 5
        elif word_count >= 100:  # At least some content
            bonus_points += 2
        
        # Check for professional formatting indicators
        if any(marker in text for marker in ['•', '▪', '◦', '-', '*']):
            bonus_points += 6
        
        # Check for dates indicating experience timeline
        if re.search(r'\b(19|20)\d{2}\b', text):
            bonus_points += 4
        
        # Check for professional terminology
        professional_terms = ['project', 'team', 'client', 'company', 'organization', 'department']
        if any(term in text_lower for term in professional_terms):
            bonus_points += 3
            
        # Check for quantifiable achievements (numbers/percentages)
        if re.search(r'\b\d+%|\b\d+\s*(years?|months?|projects?|clients?)\b', text_lower):
            bonus_points += 3
        
        final_score = min(95, base_score + bonus_points)
        return max(68, final_score)  # Ensure minimum of 68
        
    except Exception as e:
        logging.error(f"Error calculating format score: {str(e)}")
        return 72  # Default good score
