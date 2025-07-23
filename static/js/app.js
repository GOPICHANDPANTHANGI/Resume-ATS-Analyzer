// Resume ATS Analyzer - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize upload functionality
    initializeFileUpload();
    
    // Initialize form handling
    initializeFormHandling();
    
    // Initialize tooltips and other Bootstrap components
    initializeBootstrapComponents();
});

function initializeFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resume');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    
    if (!uploadArea || !fileInput) return;
    
    // Click handler for upload area
    uploadArea.addEventListener('click', function(e) {
        if (e.target.type !== 'file') {
            fileInput.click();
        }
    });
    
    // File input change handler
    fileInput.addEventListener('change', function(e) {
        handleFileSelection(e.target.files[0]);
    });
    
    // Drag and drop handlers
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });
    
    function handleFileSelection(file) {
        if (!file) return;
        
        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type)) {
            showAlert('Please select a PDF or DOCX file.', 'danger');
            return;
        }
        
        // Validate file size (16MB)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            showAlert('File size must be less than 16MB.', 'danger');
            return;
        }
        
        // Update file input and display info
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
        
        // Show file details with size and type
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        const fileType = file.type.includes('pdf') ? 'PDF' : 'DOCX';
        fileName.innerHTML = `<strong>${file.name}</strong> (${fileType} - ${fileSize} MB)`;
        fileInfo.style.display = 'block';
        
        // Add a success overlay instead of replacing content
        let successOverlay = uploadArea.querySelector('.upload-success');
        if (!successOverlay) {
            successOverlay = document.createElement('div');
            successOverlay.className = 'upload-success position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center';
            successOverlay.style.backgroundColor = 'rgba(25, 135, 84, 0.95)';
            successOverlay.style.borderRadius = '0.375rem';
            uploadArea.style.position = 'relative';
            uploadArea.appendChild(successOverlay);
        }
        
        successOverlay.innerHTML = `
            <i class="bi bi-check-circle-fill display-4 text-white mb-3"></i>
            <p class="text-white mb-2"><strong>Document Uploaded Successfully!</strong></p>
            <p class="text-white-50 small">${file.name}</p>
            <button type="button" class="btn btn-outline-light btn-sm" onclick="resetUploadArea()">
                <i class="bi bi-arrow-clockwise me-1"></i>Choose Different File
            </button>
        `;
        
        // Add uploaded state styling
        uploadArea.classList.add('uploaded', 'success-animation');
        setTimeout(() => {
            uploadArea.classList.remove('success-animation');
        }, 600);
    }
}

function initializeFormHandling() {
    const form = document.getElementById('analysisForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        // Validate form before submission
        if (!validateForm()) {
            e.preventDefault();
            return;
        }
        
        // Show loading modal
        showLoadingState();
        loadingModal.show();
        
        // Disable form submission button
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
        }
    });
    
    function validateForm() {
        const fileInput = document.getElementById('resume');
        const jobDescription = document.getElementById('job_description');
        
        if (!fileInput.files.length) {
            showAlert('Please upload a resume file.', 'danger');
            return false;
        }
        
        if (!jobDescription.value.trim()) {
            showAlert('Please enter a job description.', 'danger');
            return false;
        }
        
        if (jobDescription.value.trim().length < 50) {
            showAlert('Job description is too short. Please provide more details.', 'warning');
            return false;
        }
        
        return true;
    }
    
    function showLoadingState() {
        // Add loading class to form
        form.classList.add('loading');
        
        // Simulate progress for better UX
        simulateProgress();
    }
    
    function simulateProgress() {
        const progressBar = document.querySelector('.progress-bar');
        if (!progressBar) return;
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) {
                progress = 90;
                clearInterval(interval);
            }
            progressBar.style.width = progress + '%';
        }, 500);
    }
}

function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert alert at top of page
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        if (bsAlert) {
            bsAlert.close();
        }
    }, 5000);
}

// Utility functions for results page
function animateScoreCircle(score) {
    const scoreCircle = document.querySelector('.score-circle');
    if (scoreCircle) {
        scoreCircle.style.setProperty('--score', score);
        scoreCircle.style.animation = 'scoreAnimation 2s ease-out forwards';
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showAlert('Copied to clipboard!', 'success');
    }).catch(function() {
        showAlert('Failed to copy to clipboard.', 'danger');
    });
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function sanitizeInput(input) {
    const temp = document.createElement('div');
    temp.textContent = input;
    return temp.innerHTML;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('analysisForm');
        if (form && !form.classList.contains('loading')) {
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
});

// Reset upload area function
function resetUploadArea() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resume');
    const fileInfo = document.getElementById('fileInfo');
    
    if (uploadArea && fileInput && fileInfo) {
        // Reset file input
        fileInput.value = '';
        
        // Hide file info
        fileInfo.style.display = 'none';
        
        // Remove uploaded styling and success overlay
        uploadArea.classList.remove('uploaded');
        const successOverlay = uploadArea.querySelector('.upload-success');
        if (successOverlay) {
            successOverlay.remove();
        }
    }
}

// Export functions for use in other scripts
window.ATS = {
    showAlert,
    animateScoreCircle,
    copyToClipboard,
    validateEmail,
    sanitizeInput,
    resetUploadArea
};
