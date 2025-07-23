# Gopi's Resume Analyzer

## Overview

This is Gopi's personalized Flask-based web application that helps job seekers optimize their resumes for Applicant Tracking Systems (ATS). The application analyzes uploaded resumes against job descriptions, providing scoring, keyword matching, AI-powered suggestions, and downloadable PDF reports with comprehensive feedback.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional Model-View-Controller (MVC) architecture built with Flask:

- **Backend**: Python Flask web framework with SQLAlchemy ORM
- **Frontend**: Bootstrap 5 dark theme with vanilla JavaScript
- **Database**: SQLite (development) with SQLAlchemy for database abstraction
- **File Processing**: PyMuPDF for PDF extraction, python-docx for Word documents
- **AI Integration**: OpenAI API for intelligent suggestions with fallback support
- **Text Analysis**: NLTK for natural language processing and keyword extraction

## Key Components

### Core Application Files
- `app.py` - Flask application factory and configuration
- `main.py` - Application entry point
- `routes.py` - HTTP route handlers and request processing
- `models.py` - SQLAlchemy database models

### Analysis Engine
- `analyzer.py` - Core resume analysis logic with keyword matching and scoring
- `file_processor.py` - Document text extraction from PDF and DOCX files
- `ai_suggestions.py` - OpenAI integration for intelligent recommendations
- `pdf_generator.py` - PDF report generation with comprehensive analysis results

### Frontend
- `templates/` - Jinja2 HTML templates with Bootstrap styling
- `static/` - CSS, JavaScript, and other static assets

## Data Flow

1. **File Upload**: User uploads resume (PDF/DOCX) and enters job description
2. **Text Extraction**: Application extracts text content from uploaded document
3. **Analysis Processing**: 
   - Keywords extracted from both resume and job description using NLTK
   - Scoring calculated based on keyword matching (60%), grammar (20%), and format (20%)
   - Missing keywords identified for recommendations
4. **AI Enhancement**: OpenAI API provides intelligent suggestions for ATS optimization
5. **Results Display**: Interactive dashboard shows scores, charts, and recommendations  
6. **PDF Generation**: Comprehensive analysis reports can be downloaded as professionally formatted PDFs
7. **Data Persistence**: Analysis results stored in database for future reference and report generation

## External Dependencies

### Required Python Packages
- Flask (web framework)
- SQLAlchemy (database ORM)
- PyMuPDF (PDF processing)
- python-docx (Word document processing)
- NLTK (natural language processing)
- OpenAI (AI suggestions)
- ReportLab (PDF report generation)

### Frontend Libraries
- Bootstrap 5 (UI framework)
- Chart.js (data visualization)
- Bootstrap Icons (iconography)

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key for AI suggestions (optional)
- `SESSION_SECRET` - Flask session secret key
- `DATABASE_URL` - Database connection string (defaults to SQLite)

## Deployment Strategy

The application is designed for easy deployment on various platforms:

- **Development**: Local Flask development server with SQLite
- **Production**: Configurable database URL supports PostgreSQL for production use
- **File Handling**: Upload directory creation and file cleanup mechanisms
- **Security**: File type validation, size limits, and secure filename handling
- **Scalability**: Database connection pooling and proper resource management

### Key Configuration Options
- Maximum file upload size: 16MB
- Supported file types: PDF, DOCX
- Database connection pooling with automatic reconnection
- Proxy support for deployment behind reverse proxies

The application gracefully handles missing AI API keys by providing fallback suggestions, ensuring core functionality remains available even without external AI services.

## Recent Changes (July 23, 2025)
- **✓ Enhanced Scoring System**: Improved algorithm provides realistic scores (65-95 range) that vary meaningfully between resumes
- **✓ Clear Score Breakdown**: Display shows X/60 for keywords, X/20 for grammar/format with status badges
- **✓ Comprehensive PDF Reports**: Enhanced PDF generation with 3x more content including:
  - Immediate Action Plan with Priority Actions, Quick Wins, and Long-term Goals
  - Industry-specific recommendations based on resume content analysis
  - Personalized suggestions that vary by resume content and scores
  - Detailed score explanations with improvement strategies
- **✓ Smart Content Analysis**: PDF suggestions adapt based on detected industry (tech, business, management)
- **✓ Actionable Feedback**: Each resume receives 12+ personalized suggestions with specific keywords to add