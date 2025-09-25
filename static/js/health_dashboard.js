/**
 * Health Dashboard Module
 * Handles the personalized health dashboard feature
 */
const HealthDashboard = {
    // Chart instances
    charts: {},
    
    // Current user ID
    userId: null,
    
    // Initialize the dashboard
    initialize: function(userId) {
        this.userId = userId;
        
        // Set up filter event listeners
        document.getElementById('dashboardFilterForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.fetchDashboardData();
        });
        
        // Connect wearable device button
        document.getElementById('connectDeviceBtn').addEventListener('click', this.showConnectDeviceModal.bind(this));
        
        // Fetch dashboard data
        this.fetchDashboardData();
        
        // Fetch wearable devices
        this.fetchWearableDevices();
    },
    
    // Fetch dashboard data
    fetchDashboardData: function() {
        // Get filter values
        const startDate = document.getElementById('dashboardStartDate').value;
        const endDate = document.getElementById('dashboardEndDate').value;
        
        // Show loading state
        document.getElementById('dashboardContainer').innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading health dashboard data...</p></div>';
        
        // Build URL with filter params
        let url = `/api/users/${this.userId}/health-dashboard`;
        const params = new URLSearchParams();
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        // Fetch data
        fetch(url)
            .then(response => response.json())
            .then(data => {
                this.renderDashboard(data);
            })
            .catch(error => {
                console.error('Error fetching dashboard data:', error);
                document.getElementById('dashboardContainer').innerHTML = '<div class="alert alert-danger">Error loading dashboard data. Please try again.</div>';
            });
    },
    
    // Fetch connected wearable devices
    fetchWearableDevices: function() {
        fetch(`/api/users/${this.userId}/wearable-devices`)
            .then(response => response.json())
            .then(devices => {
                this.renderWearableDevices(devices);
            })
            .catch(error => {
                console.error('Error fetching wearable devices:', error);
            });
    },
    
    // Render the dashboard
    renderDashboard: function(data) {
        // Clear dashboard container
        document.getElementById('dashboardContainer').innerHTML = '';
        
        // Render user health summary
        this.renderHealthSummary(data.health_summary);
        
        // Render metrics charts
        this.renderMetricsCharts(data.metrics);
        
        // Render symptoms summary
        this.renderSymptomsSummary(data.symptoms);
        
        // Render risk assessments
        this.renderRiskAssessments(data.risk_assessments);
    },
    
    // Render user health summary
    renderHealthSummary: function(summary) {
        const userInfo = summary.user_info || {};
        const bmiCategory = userInfo.bmi_category || 'N/A';
        let bmiClass = 'secondary';
        
        // Determine BMI category styling
        if (bmiCategory === 'Normal weight') {
            bmiClass = 'success';
        } else if (bmiCategory === 'Underweight') {
            bmiClass = 'info';
        } else if (bmiCategory === 'Overweight') {
            bmiClass = 'warning';
        } else if (bmiCategory.includes('Obese')) {
            bmiClass = 'danger';
        }
        
        // Create health summary card
        const summaryCard = document.createElement('div');
        summaryCard.className = 'card mb-4';
        summaryCard.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">Health Summary</h5>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <strong>Name:</strong> ${userInfo.name || 'N/A'}
                        </div>
                        <div class="mb-3">
                            <strong>Age:</strong> ${userInfo.age || 'N/A'}
                        </div>
                        <div class="mb-3">
                            <strong>Gender:</strong> ${userInfo.gender || 'N/A'}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <strong>Height:</strong> ${userInfo.height ? userInfo.height + ' cm' : 'N/A'}
                        </div>
                        <div class="mb-3">
                            <strong>Weight:</strong> ${userInfo.weight ? userInfo.weight + ' kg' : 'N/A'}
                        </div>
                        <div class="mb-3">
                            <strong>BMI:</strong> ${userInfo.bmi || 'N/A'}
                            <span class="badge bg-${bmiClass} ms-2">${bmiCategory}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('dashboardContainer').appendChild(summaryCard);
    },
    
    // Render health metrics charts
    renderMetricsCharts: function(metrics) {
        if (!metrics || metrics.length === 0) {
            const noDataCard = document.createElement('div');
            noDataCard.className = 'card mb-4';
            noDataCard.innerHTML = `
                <div class="card-body text-center py-5">
                    <h5 class="card-title">No Health Metrics</h5>
                    <p class="card-text text-muted">Connect a wearable device or manually add health metrics to see data here.</p>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addMetricModal">
                        <i class="fas fa-plus-circle me-1"></i> Add Health Metric
                    </button>
                </div>
            `;
            document.getElementById('dashboardContainer').appendChild(noDataCard);
            return;
        }
        
        // Create metrics card
        const metricsCard = document.createElement('div');
        metricsCard.className = 'card mb-4';
        metricsCard.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h5 class="card-title mb-0">Health Metrics</h5>
                    <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#addMetricModal">
                        <i class="fas fa-plus-circle me-1"></i> Add Metric
                    </button>
                </div>
                <div id="metricsContainer" class="row"></div>
            </div>
        `;
        
        document.getElementById('dashboardContainer').appendChild(metricsCard);
        
        // Render individual metric charts
        metrics.forEach((metric, index) => {
            const metricContainer = document.createElement('div');
            metricContainer.className = 'col-md-6 mb-4';
            metricContainer.innerHTML = `
                <div class="card h-100">
                    <div class="card-body">
                        <h6 class="card-title">${this.formatMetricName(metric.type)}</h6>
                        <canvas id="metricChart${index}" height="250"></canvas>
                    </div>
                </div>
            `;
            
            document.getElementById('metricsContainer').appendChild(metricContainer);
            
            // Prepare chart data
            const chartData = {
                labels: metric.data.map(item => item.date),
                datasets: [{
                    label: `${this.formatMetricName(metric.type)} (${metric.unit || ''})`,
                    data: metric.data.map(item => item.value),
                    borderColor: this.getMetricColor(metric.type),
                    backgroundColor: this.getMetricColor(metric.type, 0.1),
                    tension: 0.1,
                    fill: true
                }]
            };
            
            // Configure chart
            const config = {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: metric.unit || ''
                            }
                        }
                    }
                }
            };
            
            // Create chart
            this.charts[`metric-${index}`] = new Chart(
                document.getElementById(`metricChart${index}`).getContext('2d'),
                config
            );
        });
    },
    
    // Render symptoms summary
    renderSymptomsSummary: function(symptoms) {
        if (!symptoms || symptoms.length === 0) {
            return;
        }
        
        // Group symptoms by date
        const symptomsByDate = {};
        symptoms.forEach(symptom => {
            if (!symptomsByDate[symptom.date]) {
                symptomsByDate[symptom.date] = [];
            }
            symptomsByDate[symptom.date].push(symptom);
        });
        
        // Sort dates in descending order
        const sortedDates = Object.keys(symptomsByDate).sort((a, b) => 
            new Date(b) - new Date(a)
        );
        
        // Create symptoms card
        const symptomsCard = document.createElement('div');
        symptomsCard.className = 'card mb-4';
        symptomsCard.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">Recent Symptoms</h5>
                <div id="recentSymptomsContainer"></div>
            </div>
        `;
        
        document.getElementById('dashboardContainer').appendChild(symptomsCard);
        
        // Limit to 7 most recent dates
        const recentDates = sortedDates.slice(0, 7);
        
        // Render symptoms for each date
        recentDates.forEach(date => {
            const dateSymptoms = symptomsByDate[date];
            const dateGroup = document.createElement('div');
            dateGroup.className = 'mb-3';
            
            const formattedDate = new Date(date).toLocaleDateString();
            dateGroup.innerHTML = `<h6 class="text-muted mb-2">${formattedDate}</h6>`;
            
            const symptomsList = document.createElement('div');
            symptomsList.className = 'list-group mb-3';
            
            dateSymptoms.forEach(symptom => {
                const listItem = document.createElement('div');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                
                listItem.innerHTML = `
                    <span>${symptom.symptom_name}</span>
                    <span class="badge bg-${this.getSeverityClass(symptom.severity)} rounded-pill">${symptom.severity}</span>
                `;
                
                symptomsList.appendChild(listItem);
            });
            
            dateGroup.appendChild(symptomsList);
            document.getElementById('recentSymptomsContainer').appendChild(dateGroup);
        });
    },
    
    // Render risk assessments
    renderRiskAssessments: function(assessments) {
        if (!assessments || assessments.length === 0) {
            return;
        }
        
        // Create risk assessment card
        const riskCard = document.createElement('div');
        riskCard.className = 'card mb-4';
        riskCard.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h5 class="card-title mb-0">Health Risk Assessments</h5>
                    <button class="btn btn-sm btn-primary" id="newRiskAssessmentBtn">
                        <i class="fas fa-chart-line me-1"></i> New Assessment
                    </button>
                </div>
                <div id="riskAssessmentsContainer"></div>
            </div>
        `;
        
        document.getElementById('dashboardContainer').appendChild(riskCard);
        
        // Add event listener for new assessment button
        setTimeout(() => {
            document.getElementById('newRiskAssessmentBtn').addEventListener('click', this.requestRiskAssessment.bind(this));
        }, 0);
        
        // Render individual risk assessments
        assessments.forEach(assessment => {
            const assessmentDiv = document.createElement('div');
            assessmentDiv.className = 'card mb-3';
            
            let riskClass = 'secondary';
            if (assessment.risk_level === 'low') riskClass = 'success';
            if (assessment.risk_level === 'moderate') riskClass = 'warning';
            if (assessment.risk_level === 'high') riskClass = 'danger';
            if (assessment.risk_level === 'critical') riskClass = 'dark';
            
            assessmentDiv.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h6 class="card-title">${assessment.disease_name}</h6>
                        <span class="badge bg-${riskClass}">${assessment.risk_level}</span>
                    </div>
                    <div class="progress mt-2 mb-3">
                        <div class="progress-bar bg-${riskClass}" 
                             role="progressbar" 
                             style="width: ${assessment.risk_score}%" 
                             aria-valuenow="${assessment.risk_score}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                            ${assessment.risk_score}%
                        </div>
                    </div>
                    ${assessment.recommendations ? `<p class="card-text small">${assessment.recommendations}</p>` : ''}
                    <div class="text-muted small mt-2">Assessed on ${new Date(assessment.date).toLocaleDateString()}</div>
                </div>
            `;
            
            document.getElementById('riskAssessmentsContainer').appendChild(assessmentDiv);
        });
    },
    
    // Render wearable devices
    renderWearableDevices: function(devices) {
        const container = document.getElementById('connectedDevices');
        container.innerHTML = '';
        
        if (!devices || devices.length === 0) {
            container.innerHTML = '<p class="text-muted">No wearable devices connected</p>';
            return;
        }
        
        devices.forEach(device => {
            const deviceDiv = document.createElement('div');
            deviceDiv.className = 'mb-2';
            deviceDiv.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-${this.getDeviceIcon(device.device_type)} me-2"></i>
                    <span>${this.formatDeviceName(device.device_type)}</span>
                    <span class="badge ${device.is_active ? 'bg-success' : 'bg-secondary'} ms-2">
                        ${device.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <button class="btn btn-sm btn-outline-danger ms-auto" data-device-id="${device.id}">
                        <i class="fas fa-unlink"></i>
                    </button>
                </div>
                <div class="text-muted small">Last synced: ${device.last_synced_at ? new Date(device.last_synced_at).toLocaleString() : 'Never'}</div>
            `;
            
            // Add event listener for disconnect button
            setTimeout(() => {
                const disconnectBtn = deviceDiv.querySelector('button[data-device-id]');
                disconnectBtn.addEventListener('click', () => {
                    this.disconnectDevice(device.id);
                });
            }, 0);
            
            container.appendChild(deviceDiv);
        });
    },
    
    // Show connect device modal
    showConnectDeviceModal: function() {
        const modal = new bootstrap.Modal(document.getElementById('connectDeviceModal'));
        modal.show();
    },
    
    // Connect wearable device
    connectDevice: function() {
        const deviceType = document.getElementById('deviceType').value;
        const deviceId = document.getElementById('deviceId').value;
        
        // Validate inputs
        if (!deviceType) {
            this.showNotification('Please select a device type', 'error');
            return;
        }
        
        // In a real app, you would handle OAuth2 flow or other authentication here
        // For this demo, we'll just simulate a successful connection
        
        // Prepare data
        const deviceData = {
            device_type: deviceType,
            device_id: deviceId || 'demo-' + Date.now(),
            access_token: 'demo-token',
            is_active: true
        };
        
        // Send data to server
        fetch(`/api/users/${this.userId}/wearable-devices`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deviceData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(result => {
            // Hide modal
            bootstrap.Modal.getInstance(document.getElementById('connectDeviceModal')).hide();
            
            // Show success message
            this.showNotification(`${this.formatDeviceName(deviceType)} connected successfully`, 'success');
            
            // Refresh devices list
            this.fetchWearableDevices();
            
            // In a real app, you would sync data from the device here
            // For the demo, let's add some sample data
            this.addSampleMetrics(deviceType);
        })
        .catch(error => {
            console.error('Error connecting device:', error);
            this.showNotification('Error connecting device. Please try again.', 'error');
        });
    },
    
    // Disconnect wearable device
    disconnectDevice: function(deviceId) {
        if (confirm('Are you sure you want to disconnect this device?')) {
            // In a real app, you would make an API call to disconnect the device
            // For the demo, we'll just simulate success
            this.showNotification('Device disconnected successfully', 'success');
            
            // Refresh devices list
            this.fetchWearableDevices();
        }
    },
    
    // Add health metric manually
    addHealthMetric: function() {
        const metricType = document.getElementById('metricType').value;
        const metricValue = document.getElementById('metricValue').value;
        const metricUnit = document.getElementById('metricUnit').value;
        const metricDate = document.getElementById('metricDate').value;
        
        // Validate inputs
        if (!metricType) {
            this.showNotification('Please select a metric type', 'error');
            return;
        }
        
        if (!metricValue || isNaN(metricValue)) {
            this.showNotification('Please enter a valid metric value', 'error');
            return;
        }
        
        // Prepare data
        const metricData = {
            metric_type: metricType,
            value: parseFloat(metricValue),
            unit: metricUnit,
            source: 'manual'
        };
        
        if (metricDate) {
            metricData.recorded_at = new Date(metricDate).toISOString();
        }
        
        // Send data to server
        fetch(`/api/users/${this.userId}/health-metrics`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(metricData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(result => {
            // Reset form
            document.getElementById('addMetricForm').reset();
            
            // Hide modal
            bootstrap.Modal.getInstance(document.getElementById('addMetricModal')).hide();
            
            // Show success message
            this.showNotification('Health metric added successfully', 'success');
            
            // Refresh dashboard
            this.fetchDashboardData();
        })
        .catch(error => {
            console.error('Error adding health metric:', error);
            this.showNotification('Error adding health metric. Please try again.', 'error');
        });
    },
    
    // Request new risk assessment
    requestRiskAssessment: function() {
        // Show loading state
        const btn = document.getElementById('newRiskAssessmentBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        btn.disabled = true;
        
        // For a real app, we would collect additional health data here
        const additionalFactors = {
            smoking: document.querySelector('input[name="smoking"]:checked')?.value || 'no',
            physical_activity: document.querySelector('input[name="physical_activity"]:checked')?.value || 'moderate',
            high_sodium_diet: document.querySelector('input[name="sodium"]:checked')?.value || 'no',
            stress_level: document.querySelector('input[name="stress"]:checked')?.value || 'moderate'
        };
        
        // Send request to server
        fetch(`/api/users/${this.userId}/predict-health-risks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ additional_factors: additionalFactors })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(result => {
            // Show success message
            this.showNotification('Health risk assessment completed', 'success');
            
            // Refresh dashboard
            this.fetchDashboardData();
            
            // Reset button
            btn.innerHTML = originalText;
            btn.disabled = false;
        })
        .catch(error => {
            console.error('Error performing risk assessment:', error);
            this.showNotification('Error performing risk assessment. Please try again.', 'error');
            
            // Reset button
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
    },
    
    // Add sample health metrics for demo purposes
    addSampleMetrics: function(deviceType) {
        const today = new Date();
        const metrics = [];
        
        // Generate 30 days of data
        for (let i = 0; i < 30; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            // Heart rate (60-100 bpm)
            metrics.push({
                metric_type: 'heart_rate',
                value: 60 + Math.floor(Math.random() * 40),
                unit: 'bpm',
                source: deviceType,
                recorded_at: date.toISOString()
            });
            
            // Steps (3000-15000)
            metrics.push({
                metric_type: 'steps',
                value: 3000 + Math.floor(Math.random() * 12000),
                unit: 'steps',
                source: deviceType,
                recorded_at: date.toISOString()
            });
            
            // Sleep duration (5-9 hours)
            metrics.push({
                metric_type: 'sleep_duration',
                value: 5 + Math.random() * 4,
                unit: 'hours',
                source: deviceType,
                recorded_at: date.toISOString()
            });
            
            // Blood pressure (systolic: 110-140, diastolic: 70-90)
            if (deviceType === 'apple_watch' || deviceType === 'fitbit') {
                metrics.push({
                    metric_type: 'systolic_bp',
                    value: 110 + Math.floor(Math.random() * 30),
                    unit: 'mmHg',
                    source: deviceType,
                    recorded_at: date.toISOString()
                });
                
                metrics.push({
                    metric_type: 'diastolic_bp',
                    value: 70 + Math.floor(Math.random() * 20),
                    unit: 'mmHg',
                    source: deviceType,
                    recorded_at: date.toISOString()
                });
            }
        }
        
        // Send data to server in batches
        fetch(`/api/users/${this.userId}/health-metrics`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(metrics)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(result => {
            // Show success message
            this.showNotification('Device data synced successfully', 'success');
            
            // Refresh dashboard
            this.fetchDashboardData();
        })
        .catch(error => {
            console.error('Error syncing device data:', error);
        });
    },
    
    // Helper methods
    formatMetricName: function(metricType) {
        const names = {
            'heart_rate': 'Heart Rate',
            'steps': 'Steps',
            'blood_glucose': 'Blood Glucose',
            'systolic_bp': 'Systolic Blood Pressure',
            'diastolic_bp': 'Diastolic Blood Pressure',
            'sleep_duration': 'Sleep Duration',
            'weight': 'Weight',
            'temperature': 'Body Temperature',
            'oxygen_saturation': 'Oxygen Saturation'
        };
        
        return names[metricType] || metricType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    
    getMetricColor: function(metricType, alpha = 1) {
        const colors = {
            'heart_rate': `rgba(255, 99, 132, ${alpha})`,
            'steps': `rgba(54, 162, 235, ${alpha})`,
            'blood_glucose': `rgba(255, 206, 86, ${alpha})`,
            'systolic_bp': `rgba(75, 192, 192, ${alpha})`,
            'diastolic_bp': `rgba(153, 102, 255, ${alpha})`,
            'sleep_duration': `rgba(255, 159, 64, ${alpha})`,
            'weight': `rgba(199, 199, 199, ${alpha})`,
            'temperature': `rgba(83, 144, 217, ${alpha})`,
            'oxygen_saturation': `rgba(0, 184, 148, ${alpha})`
        };
        
        return colors[metricType] || `rgba(128, 128, 128, ${alpha})`;
    },
    
    getDeviceIcon: function(deviceType) {
        const icons = {
            'fitbit': 'watch',
            'apple_watch': 'watch',
            'google_fit': 'mobile-alt',
            'samsung_health': 'mobile-alt',
            'garmin': 'watch',
            'withings': 'weight',
            'manual': 'clipboard'
        };
        
        return icons[deviceType] || 'microchip';
    },
    
    formatDeviceName: function(deviceType) {
        const names = {
            'fitbit': 'Fitbit',
            'apple_watch': 'Apple Watch',
            'google_fit': 'Google Fit',
            'samsung_health': 'Samsung Health',
            'garmin': 'Garmin',
            'withings': 'Withings',
            'manual': 'Manual Entry'
        };
        
        return names[deviceType] || deviceType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    
    getSeverityClass: function(severity) {
        if (severity <= 3) return 'success';
        if (severity <= 6) return 'warning';
        return 'danger';
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('dashboard-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'dashboard-notification';
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
        const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
        toast.show();
        
        // Remove toast after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    }
};

async function loadDashboard() {
    try {
        const res = await fetch('/api/user/health');
        const data = await res.json();
        if (data.error) {
            document.querySelector('#userName').textContent = "Error loading user";
            return;
        }
        // Example: update name and health summary
        if (document.querySelector('#userName')) {
            document.querySelector('#userName').textContent = data.name || 'User';
        }
        if (document.querySelector('#healthSummary')) {
            document.querySelector('#healthSummary').innerHTML = `
                <ul>
                    <li>Weight: ${data.health_data.weight}</li>
                    <li>Height: ${data.health_data.height}</li>
                    <li>Blood Pressure: ${data.health_data.blood_pressure}</li>
                    <li>Last Checkup: ${data.health_data.last_checkup}</li>
                </ul>
            `;
        }
        // Optionally update metrics, etc.
        if (document.querySelector('#metricsSteps')) {
            document.querySelector('#metricsSteps').textContent = data.metrics.steps || '0';
        }
        if (document.querySelector('#metricsSleep')) {
            document.querySelector('#metricsSleep').textContent = data.metrics.sleep || '0';
        }
        if (document.querySelector('#metricsCalories')) {
            document.querySelector('#metricsCalories').textContent = data.metrics.calories || '0';
        }
    } catch (e) {
        if (document.querySelector('#userName')) {
            document.querySelector('#userName').textContent = "Error loading user";
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Add these new elements to your existing 'elements' object
    const elements = {
        userName: document.getElementById('userName'),
        healthSummary: document.getElementById('healthSummary'),
        symptomTimelineContainer: document.getElementById('symptomTimelineContainer'),
        healthMetricsContainer: document.getElementById('healthMetricsContainer'),
        recentSymptomsList: document.getElementById('recentSymptomsList'),
        addSymptomForm: document.getElementById('addSymptomForm'),
        editHealthDataForm: document.getElementById('editHealthDataForm'), // New
        refreshDataBtn: document.getElementById('refreshDataBtn'),
        symptomChartCanvas: document.getElementById('symptomChart'), // New
        findHospitalsBtn: document.getElementById('findHospitalsBtn'),
        mapContainer: document.getElementById('map'),
        hospitalList: document.getElementById('hospital-list'), // New
        mapError: document.getElementById('map-error'),
    };

    const addSymptomModal = new bootstrap.Modal(document.getElementById('addSymptomModal'));
    const editHealthDataModal = new bootstrap.Modal(document.getElementById('editHealthDataModal')); // New
    let symptomChart = null; // To hold the chart instance
    let map = null; // To hold the map instance
    let userMarker = null;
    let hospitalMarkers = [];

    async function fetchData() {
        try {
            const response = await fetch('/api/user/health');
            if (!response.ok) throw new Error('Failed to fetch data');
            const data = await response.json();
            renderDashboard(data);
            populateEditForm(data.health_data); // New
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        }
    }

    function renderDashboard(data) {
        // Render User Info
        elements.userName.textContent = data.name || 'User';
        elements.healthSummary.textContent = `Weight: ${data.health_data?.weight} kg | Height: ${data.health_data?.height} cm | BP: ${data.health_data?.blood_pressure}`;
        
        const symptoms = data.symptoms || [];
        const sortedSymptoms = symptoms.sort((a, b) => new Date(b.datetime) - new Date(a.datetime));
        
        // Nicer Symptom Presentation
        if (sortedSymptoms.length > 0) {
            elements.symptomTimelineContainer.innerHTML = sortedSymptoms.map(s => `
                <div class="card card-body mb-2 shadow-sm">
                    <div class="d-flex justify-content-between">
                        <h6 class="mb-1">${s.symptom}</h6>
                        <span class="badge bg-light text-dark">${s.severity}</span>
                    </div>
                    <p class="mb-1">${s.notes || 'No notes.'}</p>
                    <small class="text-muted">${new Date(s.datetime).toLocaleString()}</small>
                </div>
            `).join('');
        } else {
            elements.symptomTimelineContainer.innerHTML = '<p>No symptoms recorded yet.</p>';
        }

        renderSymptomChart(symptoms); // New
    }

    // NEW: Function to render Chart.js chart
    function renderSymptomChart(symptoms) {
        if (!elements.symptomChartCanvas) return;

        // Group by symptom name
        const grouped = {};
        symptoms.forEach(s => {
            if (!grouped[s.symptom]) grouped[s.symptom] = [];
            grouped[s.symptom].push({
                x: new Date(s.datetime),
                y: parseInt(s.severity)
            });
        });

        // Generate a color for each symptom
        const colorList = [
            '#5E936C', '#FF6B6B', '#4ECDC4', '#FFD166', '#6C63FF', '#FFB6B9', '#A8E6CF', '#FF8C42'
        ];
        const datasets = Object.entries(grouped).map(([symptom, points], i) => ({
            label: symptom,
            data: points.sort((a, b) => a.x - b.x),
            borderColor: colorList[i % colorList.length],
            backgroundColor: colorList[i % colorList.length] + '33',
            tension: 0.3,
            pointRadius: 5,
            pointHoverRadius: 7,
            fill: false
        }));

        if (symptomChart) symptomChart.destroy();

        symptomChart = new Chart(elements.symptomChartCanvas, {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: true },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const sev = ctx.parsed.y;
                                return `${ctx.dataset.label}: ${['', 'Mild', 'Moderate', 'Severe'][sev]} (${sev}) at ${ctx.parsed.x.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'day', tooltipFormat: 'PPpp' },
                        title: { display: true, text: 'Date/Time' }
                    },
                    y: {
                        min: 1,
                        max: 3,
                        ticks: {
                            stepSize: 1,
                            callback: v => ['', 'Mild', 'Moderate', 'Severe'][v]
                        },
                        title: { display: true, text: 'Severity' }
                    }
                }
            }
        });
    }

    async function handleAddSymptom(event) {
        event.preventDefault();
        const symptomData = {
            symptom: document.getElementById('symptomName').value,
            severity: document.getElementById('symptomSeverity').value,
            notes: document.getElementById('symptomNotes').value,
            datetime: new Date().toISOString(),
        };

        try {
            const response = await fetch('/api/user/symptom', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(symptomData),
            });

            if (!response.ok) {
                throw new Error('Failed to add symptom');
            }
            
            elements.addSymptomForm.reset();
            addSymptomModal.hide();
            await fetchData(); // Refresh data on the dashboard
        } catch (error) {
            console.error('Error adding symptom:', error);
            alert('Could not add symptom. Please try again.');
        }
    }

    // NEW: Populate the edit form with current data
    function populateEditForm(healthData) {
        if (!healthData) return;
        document.getElementById('editWeight').value = healthData.weight || '';
        document.getElementById('editHeight').value = healthData.height || '';
        document.getElementById('editBloodPressure').value = healthData.blood_pressure || '';
        document.getElementById('editBloodGroup').value = healthData.blood_group || '';
    }

    // NEW: Handle the submission of the edit form
    async function handleEditHealthData(event) {
        event.preventDefault();
        const updatedData = {
            weight: document.getElementById('editWeight').value,
            height: document.getElementById('editHeight').value,
            blood_pressure: document.getElementById('editBloodPressure').value,
            blood_group: document.getElementById('editBloodGroup').value,
        };

        try {
            const response = await fetch('/api/user/health', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedData),
            });
            if (!response.ok) throw new Error('Failed to update data');
            
            editHealthDataModal.hide();
            await fetchData(); // Refresh dashboard
        } catch (error) {
            console.error('Error updating health data:', error);
            alert('Could not update data. Please try again.');
        }
    }

    // This function handles the entire "Find Hospitals" process
    async function handleFindHospitals() {
        elements.findHospitalsBtn.disabled = true;
        elements.findHospitalsBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Finding your location...';
        elements.mapError.textContent = '';
        elements.hospitalList.innerHTML = ''; // Clear previous list

        if (!navigator.geolocation) {
            elements.mapError.textContent = 'Geolocation is not supported by your browser.';
            elements.findHospitalsBtn.disabled = false;
            elements.findHospitalsBtn.innerHTML = '<i class="fas fa-hospital me-1"></i> Find Nearby Hospitals';
            return;
        }

        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            
            // --- CHANGED: Render map immediately ---
            renderMap(latitude, longitude);
            
            elements.findHospitalsBtn.innerHTML = '<i class="fas fa-search-location me-1"></i> Finding hospitals...';

            try {
                const response = await fetch('/api/nearby-hospitals', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ latitude, longitude }),
                });
                
                const hospitals = await response.json();
                if (response.ok) {
                    // Render the list and markers with the data
                    renderHospitalDetails(hospitals);
                } else {
                    throw new Error(hospitals.error || 'Failed to fetch hospital data.');
                }

            } catch (error) {
                console.error('Error finding hospitals:', error);
                elements.hospitalList.innerHTML = `<div class="list-group-item text-danger">${error.message}</div>`;
            } finally {
                elements.findHospitalsBtn.disabled = false;
                elements.findHospitalsBtn.innerHTML = '<i class="fas fa-hospital me-1"></i> Find Nearby Hospitals';
            }

        }, (error) => {
            console.error('Geolocation error:', error);
            elements.mapError.textContent = 'Could not get your location. Please enable location services.';
            elements.findHospitalsBtn.disabled = false;
            elements.findHospitalsBtn.innerHTML = '<i class="fas fa-hospital me-1"></i> Find Nearby Hospitals';
        });
    }

    // --- CHANGED: This function now ONLY renders the map and user marker ---
    function renderMap(userLat, userLon) {
        elements.mapContainer.style.display = 'block';

        if (!map) {
            map = L.map('map').setView([userLat, userLon], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
        } else {
            map.setView([userLat, userLon], 13);
        }

        if (userMarker) userMarker.remove();
        userMarker = L.marker([userLat, userLon]).addTo(map)
            .bindPopup('<b>You are here</b>').openPopup();
    }

    // --- NEW: This function renders the hospital list and map markers ---
    function renderHospitalDetails(hospitals) {
        // Clear old hospital markers and list
        hospitalMarkers.forEach(marker => marker.remove());
        hospitalMarkers = [];
        elements.hospitalList.innerHTML = '';

        if (!hospitals || hospitals.length === 0) {
            elements.hospitalList.innerHTML = '<div class="list-group-item">No hospitals found nearby.</div>';
            return;
        }

        hospitals.forEach(hospital => {
            const googleMapsLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(hospital.name + ', ' + hospital.address)}`;
            
            // Add marker to map
            const marker = L.marker([hospital.lat, hospital.lon]).addTo(map)
                .bindPopup(`<b>${hospital.name}</b>`);
            hospitalMarkers.push(marker);

            // Add item to list below map
            const listItem = document.createElement('a');
            listItem.href = googleMapsLink;
            listItem.target = '_blank';
            listItem.className = 'list-group-item list-group-item-action';
            listItem.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${hospital.name}</h6>
                    <small><i class="fas fa-external-link-alt"></i></small>
                </div>
                <p class="mb-1">${hospital.address}</p>
            `;
            elements.hospitalList.appendChild(listItem);
        });
    }

    // Initial data load
    fetchData();

    // Event Listeners
    elements.addSymptomForm.addEventListener('submit', handleAddSymptom);
    elements.editHealthDataForm.addEventListener('submit', handleEditHealthData); // New
    elements.refreshDataBtn.addEventListener('click', fetchData);
    elements.findHospitalsBtn.addEventListener('click', handleFindHospitals);
});

window.addEventListener('DOMContentLoaded', loadDashboard);