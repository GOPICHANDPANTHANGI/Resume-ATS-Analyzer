import os
import json
import logging
import zipfile
import tempfile
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from app import app, db
from models import Analysis
from file_processor import process_file
from analyzer import analyze_resume
from ai_suggestions import get_ai_suggestions
from pdf_generator import generate_analysis_pdf
import time

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Validate form data
        if 'resume' not in request.files:
            flash('No resume file uploaded', 'error')
            return redirect(url_for('index'))
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '').strip()
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        if not job_description:
            flash('Job description is required', 'error')
            return redirect(url_for('index'))
        
        if not allowed_file(file.filename):
            flash('Only PDF and DOCX files are allowed', 'error')
            return redirect(url_for('index'))
        
        # Save uploaded file
        original_filename = file.filename or "resume"
        filename = secure_filename(original_filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process the file
            resume_text = process_file(filepath)
            
            if not resume_text.strip():
                flash('Could not extract text from the uploaded file', 'error')
                return redirect(url_for('index'))
            
            # Analyze the resume
            analysis_result = analyze_resume(resume_text, job_description)
            
            # Get AI suggestions
            ai_suggestions = get_ai_suggestions(resume_text, job_description)
            
            # Save analysis to database
            analysis = Analysis()
            analysis.filename = file.filename or "resume"
            analysis.job_description = job_description
            analysis.resume_text = resume_text
            analysis.keyword_score = analysis_result['keyword_score']
            analysis.grammar_score = analysis_result['grammar_score']
            analysis.format_score = analysis_result['format_score']
            analysis.total_score = analysis_result['total_score']
            analysis.matching_keywords = json.dumps(analysis_result['matching_keywords'])
            analysis.missing_keywords = json.dumps(analysis_result['missing_keywords'])
            analysis.ai_suggestions = json.dumps(ai_suggestions)
            
            db.session.add(analysis)
            db.session.commit()
            
            return redirect(url_for('results', analysis_id=analysis.id))
            
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        logging.error(f"Error during analysis: {str(e)}")
        flash('An error occurred during analysis. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/results/<int:analysis_id>')
def results(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Parse JSON data
    matching_keywords = json.loads(analysis.matching_keywords)
    missing_keywords = json.loads(analysis.missing_keywords)
    ai_suggestions = json.loads(analysis.ai_suggestions)
    
    return render_template('results.html',
                         analysis=analysis,
                         matching_keywords=matching_keywords,
                         missing_keywords=missing_keywords,
                         ai_suggestions=ai_suggestions)

@app.route('/download/<int:analysis_id>')
def download_pdf(analysis_id):
    """Download analysis results as PDF"""
    try:
        analysis = Analysis.query.get_or_404(analysis_id)
        
        # Prepare data for PDF generation
        analysis_data = {
            'filename': analysis.filename,
            'job_description': analysis.job_description,
            'resume_text': analysis.resume_text,
            'keyword_score': analysis.keyword_score,
            'grammar_score': analysis.grammar_score,
            'format_score': analysis.format_score,
            'total_score': analysis.total_score,
            'matching_keywords': analysis.matching_keywords,
            'missing_keywords': analysis.missing_keywords,
            'ai_suggestions': analysis.ai_suggestions,
            'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S') if analysis.created_at else 'Unknown'
        }
        
        # Generate PDF
        pdf_buffer = generate_analysis_pdf(analysis_data)
        
        # Create filename with timestamp
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        filename = f"resume_analysis_report_{timestamp}.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        flash('Error generating PDF report. Please try again.', 'error')
        return redirect(url_for('results', analysis_id=analysis_id))

@app.route('/download-source')
def download_source():
    """Download complete source code as ZIP"""
    try:
        # Create a temporary zip file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        # List of files to include in the zip
        source_files = [
            'main.py', 'app.py', 'routes.py', 'models.py',
            'analyzer.py', 'file_processor.py', 'ai_suggestions.py', 
            'pdf_generator.py', 'pyproject.toml', 'replit.md'
        ]
        
        # Directories to include
        directories = ['templates', 'static']
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add individual files
            for file in source_files:
                if os.path.exists(file):
                    zipf.write(file, file)
            
            # Add directories and their contents
            for directory in directories:
                if os.path.exists(directory):
                    for root, dirs, files in os.walk(directory):
                        # Skip __pycache__ directories
                        dirs[:] = [d for d in dirs if d != '__pycache__']
                        for file in files:
                            if not file.endswith('.pyc'):
                                file_path = os.path.join(root, file)
                                arc_path = os.path.relpath(file_path, '.')
                                zipf.write(file_path, arc_path)
        
        temp_zip.close()
        
        def remove_file(response):
            try:
                os.unlink(temp_zip.name)
            except Exception:
                pass
            return response
        
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name='gopi-resume-analyzer-source.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        logging.error(f"Error creating source zip: {e}")
        flash('Error creating source download. Please try again.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

import time
