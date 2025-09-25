/**
 * Health Risk Predictor Module
 * Handles the AI-powered health risk prediction feature
 */
const HealthRiskPredictor = {
    // Current user ID
    userId: null,
    
    // Initialize the module
    initialize: function(userId) {
        console.log('Initializing Health Risk Predictor with user ID:', userId);
        this.userId = userId;
        
        // Set up event listeners
        const riskPredictBtn = document.getElementById('riskPredictBtn');
        if (riskPredictBtn) {
            console.log('Adding click listener to riskPredictBtn');
            riskPredictBtn.addEventListener('click', this.predictRisks.bind(this));
        } else {
            console.error('riskPredictBtn element not found');
        }
        
        // Fetch existing risk assessments
        this.fetchRiskAssessments();
        
        // Initialize lifestyle factor form visibility
        const lifestyleFactorsBtn = document.getElementById('lifestyleFactorsBtn');
        if (lifestyleFactorsBtn) {
            console.log('Adding click listener to lifestyleFactorsBtn');
            lifestyleFactorsBtn.addEventListener('click', function() {
                const factorsForm = document.getElementById('lifestyleFactorsForm');
                if (factorsForm) {
                    factorsForm.classList.toggle('d-none');
                    this.innerHTML = factorsForm.classList.contains('d-none') ? 
                        '<i class="fas fa-plus-circle me-1"></i> Show Lifestyle Factors' : 
                        '<i class="fas fa-minus-circle me-1"></i> Hide Lifestyle Factors';
                } else {
                    console.error('lifestyleFactorsForm element not found');
                }
            });
        } else {
            console.error('lifestyleFactorsBtn element not found');
        }
    },
    
    // Fetch existing risk assessments
    fetchRiskAssessments: function() {
        // Show loading state
        document.getElementById('riskAssessmentsContainer').innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading risk assessments...</p></div>';
        
        console.log(`Fetching risk assessments for user ID: ${this.userId}`);
        
        // Fetch data from server
        fetch(`/api/users/${this.userId}/risk-assessments`)
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error: ${response.status}`);
                }
                return response.json();
            })
            .then(assessments => {
                console.log('Fetched assessments:', assessments);
                this.renderRiskAssessments(assessments);
            })
            .catch(error => {
                console.error('Error fetching risk assessments:', error);
                document.getElementById('riskAssessmentsContainer').innerHTML = '<div class="alert alert-danger">Error loading risk assessments. Please try again.</div>';
            });
    },
    
    // Render risk assessments
    renderRiskAssessments: function(assessments) {
        const container = document.getElementById('riskAssessmentsContainer');
        if (!container) {
            console.error('riskAssessmentsContainer element not found');
            return;
        }
        
        container.innerHTML = '';
        
        if (!assessments || assessments.length === 0) {
            console.log('No risk assessments found');
            container.innerHTML = `
                <div class="text-center p-4">
                    <p class="text-muted mb-4">No risk assessments found. Complete the form to get your first health risk prediction.</p>
                </div>
            `;
            return;
        }
        
        console.log(`Rendering ${assessments.length} risk assessments`);
        
        // Group assessments by date
        const groupedAssessments = {};
        assessments.forEach(assessment => {
            // Make sure assessment_date exists and is valid
            if (!assessment.assessment_date) {
                console.warn('Assessment missing assessment_date:', assessment);
                return;
            }
            
            try {
                const date = new Date(assessment.assessment_date).toLocaleDateString();
                
                if (!groupedAssessments[date]) {
                    groupedAssessments[date] = [];
                }
                
                groupedAssessments[date].push(assessment);
            } catch (error) {
                console.error('Error processing assessment date:', error, assessment);
            }
        });
        
        // Sort dates in descending order
        const sortedDates = Object.keys(groupedAssessments).sort((a, b) => 
            new Date(b) - new Date(a)
        );
        
        console.log(`Grouped assessments by ${sortedDates.length} dates`);
        
        // Render assessments by date
        sortedDates.forEach(date => {
            const dateAssessments = groupedAssessments[date];
            
            const dateGroup = document.createElement('div');
            dateGroup.className = 'mb-4';
            
            dateGroup.innerHTML = `<h6 class="border-bottom pb-2 mb-3">Assessment from ${date}</h6>`;
            
            const assessmentsList = document.createElement('div');
            assessmentsList.className = 'row';
            
            dateAssessments.forEach(assessment => {
                const assessmentCol = document.createElement('div');
                assessmentCol.className = 'col-md-6 mb-3';
                
                let riskClass = 'secondary';
                if (assessment.risk_level === 'low') riskClass = 'success';
                if (assessment.risk_level === 'moderate') riskClass = 'warning';
                if (assessment.risk_level === 'high') riskClass = 'danger';
                if (assessment.risk_level === 'critical') riskClass = 'dark';
                
                // Format risk factors
                let riskFactorsHtml = '';
                if (assessment.risk_factors && assessment.risk_factors.length > 0) {
                    const factorsList = assessment.risk_factors.map(factor => 
                        `<li class="list-group-item p-2">
                            <div class="d-flex justify-content-between align-items-center">
                                <span>${factor.name}</span>
                                <span class="badge bg-${factor.impact === 'high' ? 'danger' : (factor.impact === 'medium' ? 'warning' : 'info')}">${factor.impact}</span>
                            </div>
                        </li>`
                    ).join('');
                    
                    riskFactorsHtml = `
                        <div class="mt-3">
                            <h6 class="card-subtitle mb-2">Risk Factors:</h6>
                            <ul class="list-group list-group-flush">
                                ${factorsList}
                            </ul>
                        </div>
                    `;
                }
                
                assessmentCol.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <h6 class="card-title">${assessment.disease_name}</h6>
                                <span class="badge bg-${riskClass}">${assessment.risk_level}</span>
                            </div>
                            
                            <div class="progress mt-3">
                                <div class="progress-bar bg-${riskClass}" role="progressbar" 
                                     style="width: ${assessment.risk_score}%" 
                                     aria-valuenow="${assessment.risk_score}" 
                                     aria-valuemin="0" 
                                     aria-valuemax="100">
                                    ${assessment.risk_score}%
                                </div>
                            </div>
                            
                            ${riskFactorsHtml}
                            
                            ${assessment.recommendations ? `
                                <div class="mt-3">
                                    <h6 class="card-subtitle mb-2">Recommendations:</h6>
                                    <p class="card-text small">${assessment.recommendations}</p>
                                </div>
                            ` : ''}
                            
                            <div class="text-muted small mt-3">
                                <i class="fas fa-info-circle me-1"></i>
                                Model version: ${assessment.model_version || 'N/A'}
                            </div>
                        </div>
                    </div>
                `;
                
                assessmentsList.appendChild(assessmentCol);
            });
            
            dateGroup.appendChild(assessmentsList);
            container.appendChild(dateGroup);
        });
    },
    
    // Predict health risks
    predictRisks: function() {
        // Show loading state
        const btn = document.getElementById('riskPredictBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        btn.disabled = true;
        
        // Collect lifestyle factors
        const lifestyleFactors = {
            smoking: document.querySelector('input[name="smoking"]:checked')?.value || 'no',
            physical_activity: document.querySelector('input[name="physical_activity"]:checked')?.value || 'moderate',
            high_sodium_diet: document.querySelector('input[name="sodium"]:checked')?.value || 'no',
            stress_level: document.querySelector('input[name="stress"]:checked')?.value || 'moderate',
            sleep_quality: document.querySelector('input[name="sleep"]:checked')?.value || 'good',
            alcohol_consumption: document.querySelector('input[name="alcohol"]:checked')?.value || 'moderate'
        };
        
        console.log(`Sending risk prediction request for user ID: ${this.userId}`);
        console.log('Lifestyle factors:', lifestyleFactors);
        
        // Send prediction request
        fetch(`/api/users/${this.userId}/predict-health-risks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ additional_factors: lifestyleFactors })
        })
        .then(response => {
            console.log('Prediction response status:', response.status);
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            console.log('Prediction result:', result);
            // Show success message
            this.showNotification('Health risk assessment completed successfully', 'success');
            
            // Reset button
            btn.innerHTML = originalText;
            btn.disabled = false;
            
            // Fetch updated risk assessments
            this.fetchRiskAssessments();
            
            // Scroll to assessments
            document.getElementById('riskAssessmentsContainer').scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            console.error('Error predicting health risks:', error);
            this.showNotification('Error performing risk assessment. Please try again.', 'error');
            
            // Reset button
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        console.log(`Showing notification: ${message} (type: ${type})`);
        
        try {
            // Create notification element if it doesn't exist
            let notification = document.getElementById('risk-notification');
            
            if (!notification) {
                notification = document.createElement('div');
                notification.id = 'risk-notification';
                notification.className = 'position-fixed bottom-0 end-0 p-3';
                notification.style.zIndex = 1050;
                document.body.appendChild(notification);
            }
            
            // Create toast
            const toastId = 'toast-' + Date.now();
            const toastHTML = `
                <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body">
                            ${message}
                        </div>
                        <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                </div>
            `;
            
            notification.innerHTML += toastHTML;
            
            // Show toast - make sure bootstrap is loaded
            const toastElement = document.getElementById(toastId);
            if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
                const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
                toast.show();
                
                // Remove toast after it's hidden
                toastElement.addEventListener('hidden.bs.toast', function() {
                    this.remove();
                });
            } else {
                console.error('Bootstrap Toast is not available');
                // Simple fallback - remove toast after 3 seconds
                setTimeout(() => {
                    if (toastElement) toastElement.remove();
                }, 3000);
            }
        } catch (error) {
            console.error('Error showing notification:', error);
            // Display a fallback alert in case of errors
            alert(message);
        }
    }
};