/**
 * Symptom Timeline Module
 * Handles the interactive symptom timeline feature
 */
const SymptomTimeline = {
    // Chart instance
    chart: null,
    
    // Current user ID
    userId: null,
    
    // Initialize the timeline
    initialize: function(userId, containerId = 'symptomTimelineChart') {
        this.userId = userId;
        this.containerId = containerId;
        
        // Fetch symptoms for dropdown
        this.fetchSymptoms();
        
        // Set up event listeners - check if elements exist first
        const addSymptomBtn = document.getElementById('addSymptomBtn');
        if (addSymptomBtn) {
            addSymptomBtn.addEventListener('click', this.showAddSymptomForm.bind(this));
        } else {
            console.log('Warning: addSymptomBtn element not found');
        }
        
        const saveSymptomBtn = document.getElementById('saveSymptomBtn');
        if (saveSymptomBtn) {
            saveSymptomBtn.addEventListener('click', this.saveSymptomRecord.bind(this));
        } else {
            console.log('Warning: saveSymptomBtn element not found');
        }
        
        const cancelSymptomBtn = document.getElementById('cancelSymptomBtn');
        if (cancelSymptomBtn) {
            cancelSymptomBtn.addEventListener('click', this.hideAddSymptomForm.bind(this));
        } else {
            console.log('Warning: cancelSymptomBtn element not found');
        }
        
        // Initialize date picker
        const datePicker = document.getElementById('symptomDatetime');
        if (datePicker) {
            // Set default value to current date and time
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            datePicker.value = `${year}-${month}-${day}T${hours}:${minutes}`;
        } else {
            console.log('Warning: symptomDatetime element not found');
        }
        
        // Set up filter event listeners
        const timelineFilterForm = document.getElementById('timelineFilterForm');
        if (timelineFilterForm) {
            timelineFilterForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.applyFilters();
            });
        } else {
            console.log('Warning: timelineFilterForm element not found');
        }
        
        // Fetch and render timeline data
        this.fetchTimelineData();
    },
    
    // Fetch available symptoms
    fetchSymptoms: function() {
        fetch('/api/symptoms')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(symptoms => {
                const dropdown = document.getElementById('symptomId');
                if (!dropdown) {
                    console.error('Error: symptomId dropdown element not found');
                    return;
                }
                
                dropdown.innerHTML = '';
                
                if (!symptoms || !Array.isArray(symptoms)) {
                    console.error('Unexpected symptoms data format:', symptoms);
                    return;
                }
                
                symptoms.forEach(symptom => {
                    const option = document.createElement('option');
                    option.value = symptom.id;
                    option.textContent = symptom.name;
                    dropdown.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching symptoms:', error);
                this.showNotification('Error loading symptoms. Please try again.', 'error');
            });
    },
    
    // Fetch timeline data
    fetchTimelineData: function() {
        // Get filter values
        let startDate, endDate;
        const startDateElement = document.getElementById('timelineStartDate');
        const endDateElement = document.getElementById('timelineEndDate');
        
        if (startDateElement) {
            startDate = startDateElement.value;
        }
        
        if (endDateElement) {
            endDate = endDateElement.value;
        }
        
        // Show loading state
        const containerElement = document.getElementById(this.containerId);
        if (containerElement) {
            containerElement.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading timeline data...</p></div>';
        } else {
            console.error(`Timeline container with ID '${this.containerId}' not found`);
            return;
        }
        
        // Build URL with filter params
        let url = `/api/users/${this.userId}/timeline`;
        const params = new URLSearchParams();
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        console.log(`Fetching timeline data from: ${url}`);
        
        // Fetch data
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Timeline data received:', data);
                this.renderTimeline(data);
                this.updateSymptomsList(data);
            })
            .catch(error => {
                console.error('Error fetching timeline data:', error);
                if (containerElement) {
                    containerElement.innerHTML = '<div class="alert alert-danger">Error loading timeline data. Please try again.</div>';
                }
            });
    },
    
    // Render timeline visualization
    renderTimeline: function(data) {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Timeline container with ID '${this.containerId}' not found`);
            return;
        }
        
        // Check if we can get the canvas context
        let ctx;
        try {
            ctx = container.getContext('2d');
        } catch (error) {
            console.error('Error getting canvas context:', error);
            container.innerHTML = '<div class="alert alert-warning">Unable to initialize chart canvas. Your browser may not support this feature.</div>';
            return;
        }
        
        // Destroy existing chart if it exists
        if (this.chart) {
            this.chart.destroy();
        }
        
        // Validate data
        if (!data || !data.labels || !data.datasets) {
            console.error('Invalid timeline data structure:', data);
            container.innerHTML = '<div class="alert alert-danger">Invalid timeline data format received.</div>';
            return;
        }
        
        // Prepare data for Chart.js
        const chartData = {
            labels: data.labels,
            datasets: Array.isArray(data.datasets) ? 
                data.datasets.filter(dataset => dataset.data && dataset.data.some(point => point && point.y > 0)) : 
                []
        };
        
        // Check if we have data to display
        if (chartData.datasets.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No timeline data available for the selected period.</div>';
            return;
        }
        
        // Configure chart
        const config = {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Severity (1-10)'
                        },
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const dataPoint = context.raw;
                                return dataPoint.notes ? `Notes: ${dataPoint.notes}` : '';
                            }
                        }
                    },
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Symptom Severity Timeline'
                    }
                },
                interaction: {
                    mode: 'nearest',
                    intersect: false
                },
                onClick: (event, elements) => {
                    if (!elements || elements.length === 0) return;
                    
                    const element = elements[0];
                    const datasetIndex = element.datasetIndex;
                    const index = element.index;
                    
                    const recordId = chartData.datasets[datasetIndex].data[index].record_id;
                    if (recordId) {
                        this.showSymptomDetails(recordId);
                    }
                }
            }
        };
        
        // Create chart
        this.chart = new Chart(ctx, config);
        
        // Update chart height based on number of symptoms
        const chartContainer = document.getElementById(this.containerId).parentNode;
        const minHeight = 400;
        const heightPerDataset = 50;
        const calculatedHeight = Math.max(minHeight, chartData.datasets.length * heightPerDataset);
        chartContainer.style.height = `${calculatedHeight}px`;
    },
    
    // Update the list of symptoms in the timeline
    updateSymptomsList: function(data) {
        const listContainer = document.getElementById('symptomListContainer');
        if (!listContainer) {
            console.log('Warning: symptomListContainer element not found');
            return;
        }
        
        listContainer.innerHTML = '';
        
        if (!data || !data.datasets || !Array.isArray(data.datasets) || data.datasets.length === 0) {
            listContainer.innerHTML = '<p class="text-muted">No symptoms recorded in this time period.</p>';
            return;
        }
        
        // Group datasets by category
        const categories = {};
        data.datasets.forEach(dataset => {
            const category = dataset.symptom_category || 'Uncategorized';
            
            if (!categories[category]) {
                categories[category] = [];
            }
            
            // Only include if there's at least one non-zero data point
            if (dataset.data.some(point => point.y > 0)) {
                categories[category].push(dataset);
            }
        });
        
        // Create category groups
        for (const [category, datasets] of Object.entries(categories)) {
            if (datasets.length === 0) continue;
            
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'mb-3';
            
            const categoryHeader = document.createElement('h6');
            categoryHeader.className = 'text-muted mb-2';
            categoryHeader.textContent = category;
            categoryDiv.appendChild(categoryHeader);
            
            const symptomList = document.createElement('div');
            symptomList.className = 'list-group';
            
            datasets.forEach(dataset => {
                // Find the last recorded date with severity
                let lastRecord = null;
                for (let i = dataset.data.length - 1; i >= 0; i--) {
                    if (dataset.data[i].y > 0) {
                        lastRecord = dataset.data[i];
                        break;
                    }
                }
                
                if (lastRecord) {
                    const listItem = document.createElement('div');
                    listItem.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
                    listItem.dataset.recordId = lastRecord.record_id;
                    
                    const nameSpan = document.createElement('span');
                    nameSpan.textContent = dataset.label;
                    
                    const infoDiv = document.createElement('div');
                    infoDiv.className = 'd-flex align-items-center';
                    
                    const severityBadge = document.createElement('span');
                    severityBadge.className = `badge rounded-pill bg-${this.getSeverityClass(lastRecord.y)} me-2`;
                    severityBadge.textContent = lastRecord.y;
                    
                    const dateSpan = document.createElement('small');
                    dateSpan.className = 'text-muted';
                    dateSpan.textContent = new Date(lastRecord.x).toLocaleDateString();
                    
                    infoDiv.appendChild(severityBadge);
                    infoDiv.appendChild(dateSpan);
                    
                    listItem.appendChild(nameSpan);
                    listItem.appendChild(infoDiv);
                    
                    listItem.addEventListener('click', () => {
                        if (lastRecord.record_id) {
                            this.showSymptomDetails(lastRecord.record_id);
                        }
                    });
                    
                    symptomList.appendChild(listItem);
                }
            });
            
            categoryDiv.appendChild(symptomList);
            listContainer.appendChild(categoryDiv);
        }
    },
    
    // Show symptom record details
    showSymptomDetails: function(recordId) {
        fetch(`/api/users/${this.userId}/symptoms/${recordId}`)
            .then(response => response.json())
            .then(record => {
                // Get symptom name
                fetch(`/api/symptoms`)
                    .then(response => response.json())
                    .then(symptoms => {
                        const symptom = symptoms.find(s => s.id === record.symptom_id);
                        const symptomName = symptom ? symptom.name : 'Unknown Symptom';
                        
                        // Format record date
                        const recordDate = new Date(record.recorded_at);
                        const formattedDate = recordDate.toLocaleDateString() + ' ' + recordDate.toLocaleTimeString();
                        
                        // Build details HTML
                        const detailsHTML = `
                            <h5>${symptomName}</h5>
                            <div class="mb-3">
                                <span class="badge bg-${this.getSeverityClass(record.severity)} fs-6">Severity: ${record.severity}/10</span>
                                <span class="text-muted ms-2">${formattedDate}</span>
                            </div>
                            ${record.notes ? `<div class="mb-3"><strong>Notes:</strong><p>${record.notes}</p></div>` : ''}
                            ${record.medication_taken ? `<div class="mb-3"><strong>Medication taken:</strong> ${record.medication_taken}</div>` : ''}
                            <div class="mb-3">
                                <strong>Doctor visited:</strong> ${record.doctor_visited ? 'Yes' : 'No'}
                            </div>
                            <div class="d-flex justify-content-end mt-4">
                                <button class="btn btn-outline-danger me-2" onclick="SymptomTimeline.deleteSymptomRecord(${record.id})">Delete</button>
                                <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        `;
                        
                        // Update modal content
                        document.getElementById('symptomDetailsContent').innerHTML = detailsHTML;
                        
                        // Show modal
                        const modal = new bootstrap.Modal(document.getElementById('symptomDetailsModal'));
                        modal.show();
                    })
                    .catch(error => {
                        console.error('Error fetching symptom details:', error);
                        this.showNotification('Error loading symptom details', 'error');
                    });
            })
            .catch(error => {
                console.error('Error fetching symptom record:', error);
                this.showNotification('Error loading symptom record', 'error');
            });
    },
    
    // Show add symptom form
    showAddSymptomForm: function() {
        document.getElementById('addSymptomForm').style.display = 'block';
        document.getElementById('addSymptomBtn').style.display = 'none';
    },
    
    // Hide add symptom form
    hideAddSymptomForm: function() {
        document.getElementById('addSymptomForm').style.display = 'none';
        document.getElementById('addSymptomBtn').style.display = 'block';
    },
    
    // Save symptom record
    saveSymptomRecord: function() {
        const form = document.getElementById('addSymptomForm');
        const symptomId = document.getElementById('symptomId').value;
        const severity = document.getElementById('symptomSeverity').value;
        const notes = document.getElementById('symptomNotes').value;
        const datetime = document.getElementById('symptomDatetime').value;
        const medicationTaken = document.getElementById('medicationTaken').value;
        const doctorVisited = document.getElementById('doctorVisited').checked;
        
        // Validate inputs
        if (!symptomId) {
            this.showNotification('Please select a symptom', 'error');
            return;
        }
        
        if (!severity || severity < 1 || severity > 10) {
            this.showNotification('Please enter a severity between 1-10', 'error');
            return;
        }
        
        // Prepare data
        const recordData = {
            symptom_id: parseInt(symptomId),
            severity: parseInt(severity),
            notes: notes,
            medication_taken: medicationTaken,
            doctor_visited: doctorVisited
        };
        
        if (datetime) {
            recordData.recorded_at = new Date(datetime).toISOString();
        }
        
        // Send data to server
        fetch(`/api/users/${this.userId}/symptoms`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(recordData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(result => {
            // Reset form
            form.reset();
            
            // Hide form
            this.hideAddSymptomForm();
            
            // Show success message
            this.showNotification('Symptom recorded successfully', 'success');
            
            // Refresh timeline
            this.fetchTimelineData();
        })
        .catch(error => {
            console.error('Error saving symptom record:', error);
            this.showNotification('Error saving symptom record. Please try again.', 'error');
        });
    },
    
    // Delete symptom record
    deleteSymptomRecord: function(recordId) {
        if (confirm('Are you sure you want to delete this symptom record?')) {
            fetch(`/api/users/${this.userId}/symptoms/${recordId}`, {
                method: 'DELETE'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error');
                }
                return response.json();
            })
            .then(result => {
                // Close modal
                bootstrap.Modal.getInstance(document.getElementById('symptomDetailsModal')).hide();
                
                // Show success message
                this.showNotification('Symptom record deleted successfully', 'success');
                
                // Refresh timeline
                this.fetchTimelineData();
            })
            .catch(error => {
                console.error('Error deleting symptom record:', error);
                this.showNotification('Error deleting symptom record', 'error');
            });
        }
    },
    
    // Apply timeline filters
    applyFilters: function() {
        this.fetchTimelineData();
    },
    
    // Get severity CSS class based on severity value
    getSeverityClass: function(severity) {
        if (severity <= 3) return 'success';
        if (severity <= 6) return 'warning';
        return 'danger';
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        try {
            // Check if bootstrap is available
            if (typeof bootstrap === 'undefined') {
                console.error('Bootstrap is not loaded. Cannot show toast notification.');
                // Fallback to console
                const consoleMethod = type === 'error' ? 'error' : type === 'warning' ? 'warn' : 'info';
                console[consoleMethod](`Notification: ${message}`);
                return;
            }
            
            // Create notification element if it doesn't exist
            let notification = document.getElementById('symptom-notification');
            
            if (!notification) {
                notification = document.createElement('div');
                notification.id = 'symptom-notification';
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
            
            // Show toast
            const toastElement = document.getElementById(toastId);
            if (toastElement) {
                const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
                toast.show();
                
                // Remove toast after it's hidden
                toastElement.addEventListener('hidden.bs.toast', function() {
                    this.remove();
                });
            } else {
                console.error('Failed to create toast element');
            }
        } catch (error) {
            console.error('Error showing notification:', error);
            console.info(`Notification (fallback): ${message}`);
        }
    }
};

async function loadSymptomTimeline() {
    try {
        const res = await fetch('/api/user/health');
        const data = await res.json();
        if (data.error) {
            document.querySelector('#symptomTimeline').innerHTML = `<div class="alert alert-danger">Error loading timeline data. Please try again.</div>`;
            return;
        }
        const symptoms = data.symptoms || [];
        if (symptoms.length === 0) {
            document.querySelector('#symptomTimeline').innerHTML = `<div>No symptoms recorded yet.</div>`;
            return;
        }
        let html = '<ul>';
        for (const s of symptoms) {
            html += `<li>${s.datetime}: ${s.symptom} (${s.severity}) - ${s.notes}</li>`;
        }
        html += '</ul>';
        document.querySelector('#symptomTimeline').innerHTML = html;
    } catch (e) {
        document.querySelector('#symptomTimeline').innerHTML = `<div class="alert alert-danger">Error loading timeline data. Please try again.</div>`;
    }
}

document.querySelector('#addSymptomBtn').onclick = async function() {
    const symptom = document.querySelector('#symptomInput').value;
    const severity = document.querySelector('#severityInput').value;
    const notes = document.querySelector('#notesInput').value;
    const datetime = document.querySelector('#datetimeInput').value;
    await fetch('/api/user/symptom', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({symptom, severity, notes, datetime})
    });
    loadSymptomTimeline();
};

window.addEventListener('DOMContentLoaded', loadSymptomTimeline);