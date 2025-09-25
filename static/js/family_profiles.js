/**
 * Family Health Profiles Module
 * Handles the smart family health profiles feature
 */
const FamilyProfiles = {
    // Current user ID
    userId: null,
    
    // Initialize the module
    initialize: function(userId) {
        this.userId = userId;
        
        // Set up event listeners
        document.getElementById('addFamilyMemberBtn').addEventListener('click', this.showAddMemberModal.bind(this));
        document.getElementById('addHealthHistoryBtn').addEventListener('click', this.showAddHistoryModal.bind(this));
        
        // Fetch family dashboard data
        this.fetchFamilyDashboard();
        
        // Set up form submission handlers
        document.getElementById('saveFamilyMemberBtn').addEventListener('click', this.saveFamilyMember.bind(this));
        document.getElementById('saveHealthHistoryBtn').addEventListener('click', this.saveHealthHistory.bind(this));
    },
    
    // Fetch family dashboard data
    fetchFamilyDashboard: function() {
        // Show loading state
        document.getElementById('familyProfilesContainer').innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading family profile data...</p></div>';
        
        // Fetch data from server
        fetch(`/api/users/${this.userId}/family-dashboard`)
            .then(response => response.json())
            .then(data => {
                this.renderFamilyDashboard(data);
            })
            .catch(error => {
                console.error('Error fetching family dashboard data:', error);
                document.getElementById('familyProfilesContainer').innerHTML = '<div class="alert alert-danger">Error loading family profiles. Please try again.</div>';
            });
    },
    
    // Render family dashboard
    renderFamilyDashboard: function(data) {
        // Clear container
        document.getElementById('familyProfilesContainer').innerHTML = '';
        
        // Render family members
        this.renderFamilyMembers(data.family_members);
        
        // Render family health history
        this.renderFamilyHealthHistory(data.family_health_history);
    },
    
    // Render family members
    renderFamilyMembers: function(members) {
        if (!members || members.length === 0) {
            return;
        }
        
        // Create family members card
        const membersCard = document.createElement('div');
        membersCard.className = 'card mb-4';
        membersCard.innerHTML = `
            <div class="card-body">
                <h5 class="card-title mb-4">Family Members</h5>
                <div class="row" id="familyMembersContainer"></div>
            </div>
        `;
        
        document.getElementById('familyProfilesContainer').appendChild(membersCard);
        
        // Render each family member
        members.forEach(member => {
            // Skip if no user ID (should not happen)
            if (!member.user_id) return;
            
            const memberDiv = document.createElement('div');
            memberDiv.className = 'col-md-6 col-lg-4 mb-3';
            
            let healthStatus = '';
            if (member.health_summary && member.health_summary.latest_risk_assessment) {
                const risk = member.health_summary.latest_risk_assessment;
                let riskClass = 'success';
                
                if (risk.risk_level === 'moderate') riskClass = 'warning';
                if (risk.risk_level === 'high') riskClass = 'danger';
                if (risk.risk_level === 'critical') riskClass = 'dark';
                
                healthStatus = `
                    <div class="mt-2">
                        <span class="badge bg-${riskClass}">${risk.risk_level} risk</span>
                        <small class="text-muted ms-1">${risk.disease}</small>
                    </div>
                `;
            }
            
            // Recent symptoms
            let symptomsHtml = '';
            if (member.health_summary && member.health_summary.recent_symptoms && member.health_summary.recent_symptoms.length > 0) {
                symptomsHtml = `
                    <div class="mt-2 small">
                        <strong>Recent symptoms:</strong>
                        <ul class="list-unstyled ms-1 mb-0">
                            ${member.health_summary.recent_symptoms.map(s => `
                                <li>
                                    <span class="badge bg-${this.getSeverityClass(s.severity)}">${s.severity}</span>
                                    ${s.symptom_name} (${s.date})
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            }
            
            // Build card
            memberDiv.innerHTML = `
                <div class="card h-100 ${member.relationship === 'self' ? 'border-primary' : ''}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <h6 class="card-title">${member.name || `User ${member.user_id}`}</h6>
                            ${member.relationship !== 'self' ? `
                                <span class="badge bg-info">${member.relationship}</span>
                            ` : ''}
                        </div>
                        
                        <div class="mt-2 small">
                            <div><strong>Age:</strong> ${member.age || 'N/A'}</div>
                            <div><strong>Gender:</strong> ${member.gender || 'N/A'}</div>
                            ${member.health_summary && member.health_summary.bmi ? `
                                <div><strong>BMI:</strong> ${member.health_summary.bmi} 
                                (${member.health_summary.bmi_category || 'N/A'})</div>
                            ` : ''}
                        </div>
                        
                        ${healthStatus}
                        
                        ${member.access_level === 'full' ? symptomsHtml : ''}
                        
                        ${member.relationship !== 'self' ? `
                            <div class="mt-3">
                                <small class="text-muted">Access level: ${member.access_level}</small>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            document.getElementById('familyMembersContainer').appendChild(memberDiv);
        });
    },
    
    // Render family health history
    renderFamilyHealthHistory: function(history) {
        // Create history card
        const historyCard = document.createElement('div');
        historyCard.className = 'card mb-4';
        historyCard.innerHTML = `
            <div class="card-body">
                <h5 class="card-title mb-4">Family Health History</h5>
                <div id="familyHistoryContainer"></div>
            </div>
        `;
        
        document.getElementById('familyProfilesContainer').appendChild(historyCard);
        
        // Check if there's any history data
        if (!history || Object.keys(history).length === 0) {
            document.getElementById('familyHistoryContainer').innerHTML = `
                <p class="text-muted">No family health history recorded.</p>
                <p>Recording your family health history helps to identify patterns of diseases and conditions that may run in your family.</p>
            `;
            return;
        }
        
        // Render history for each relationship type
        for (const [relationship, conditions] of Object.entries(history)) {
            const relationshipDiv = document.createElement('div');
            relationshipDiv.className = 'mb-4';
            relationshipDiv.innerHTML = `
                <h6 class="border-bottom pb-2">${this.formatRelationship(relationship)}</h6>
            `;
            
            const conditionsList = document.createElement('ul');
            conditionsList.className = 'list-group';
            
            conditions.forEach(condition => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                
                listItem.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <strong>${condition.condition}</strong>
                            ${condition.age_at_diagnosis ? `<div class="small text-muted">Age at diagnosis: ${condition.age_at_diagnosis}</div>` : ''}
                            ${condition.notes ? `<div class="small">${condition.notes}</div>` : ''}
                        </div>
                    </div>
                `;
                
                conditionsList.appendChild(listItem);
            });
            
            relationshipDiv.appendChild(conditionsList);
            document.getElementById('familyHistoryContainer').appendChild(relationshipDiv);
        }
    },
    
    // Show modal to add family member
    showAddMemberModal: function() {
        // Fetch users for dropdown
        fetch('/api/users')
            .then(response => response.json())
            .then(users => {
                const dropdown = document.getElementById('relativeId');
                dropdown.innerHTML = '';
                
                // Filter out current user
                const otherUsers = users.filter(user => user.id != this.userId);
                
                otherUsers.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = user.name || user.phone_number || `User ${user.id}`;
                    dropdown.appendChild(option);
                });
                
                // Show modal
                const modal = new bootstrap.Modal(document.getElementById('addFamilyMemberModal'));
                modal.show();
            })
            .catch(error => {
                console.error('Error fetching users:', error);
                this.showNotification('Error loading users. Please try again.', 'error');
            });
    },
    
    // Show modal to add family health history
    showAddHistoryModal: function() {
        const modal = new bootstrap.Modal(document.getElementById('addHealthHistoryModal'));
        modal.show();
    },
    
    // Save new family member
    saveFamilyMember: function() {
        const relativeId = document.getElementById('relativeId').value;
        const relationshipType = document.getElementById('relationshipType').value;
        const accessLevel = document.getElementById('accessLevel').value;
        
        // Validate inputs
        if (!relativeId) {
            this.showNotification('Please select a family member', 'error');
            return;
        }
        
        if (!relationshipType) {
            this.showNotification('Please select a relationship type', 'error');
            return;
        }
        
        // Prepare data
        const relationshipData = {
            relative_id: parseInt(relativeId),
            relationship_type: relationshipType,
            access_level: accessLevel
        };
        
        // Send data to server
        fetch(`/api/users/${this.userId}/family-members`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(relationshipData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(result => {
            // Reset form
            document.getElementById('addFamilyMemberForm').reset();
            
            // Hide modal
            bootstrap.Modal.getInstance(document.getElementById('addFamilyMemberModal')).hide();
            
            // Show success message
            this.showNotification('Family member added successfully', 'success');
            
            // Refresh dashboard
            this.fetchFamilyDashboard();
        })
        .catch(error => {
            console.error('Error adding family member:', error);
            this.showNotification('Error adding family member. Please try again.', 'error');
        });
    },
    
    // Save new family health history
    saveHealthHistory: function() {
        const conditionName = document.getElementById('conditionName').value;
        const relationship = document.getElementById('historyRelationship').value;
        const ageAtDiagnosis = document.getElementById('ageAtDiagnosis').value;
        const historyNotes = document.getElementById('historyNotes').value;
        
        // Validate inputs
        if (!conditionName) {
            this.showNotification('Please enter a condition name', 'error');
            return;
        }
        
        if (!relationship) {
            this.showNotification('Please select a relationship', 'error');
            return;
        }
        
        // Prepare data
        const historyData = {
            condition_name: conditionName,
            relationship: relationship,
            notes: historyNotes
        };
        
        if (ageAtDiagnosis) {
            historyData.age_at_diagnosis = parseInt(ageAtDiagnosis);
        }
        
        // Send data to server
        fetch(`/api/users/${this.userId}/family-history`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(historyData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(result => {
            // Reset form
            document.getElementById('addHealthHistoryForm').reset();
            
            // Hide modal
            bootstrap.Modal.getInstance(document.getElementById('addHealthHistoryModal')).hide();
            
            // Show success message
            this.showNotification('Family health history added successfully', 'success');
            
            // Refresh dashboard
            this.fetchFamilyDashboard();
        })
        .catch(error => {
            console.error('Error adding family health history:', error);
            this.showNotification('Error adding family health history. Please try again.', 'error');
        });
    },
    
    // Helper methods
    formatRelationship: function(relationship) {
        const labels = {
            'mother': 'Mother',
            'father': 'Father',
            'sister': 'Sister',
            'brother': 'Brother',
            'daughter': 'Daughter',
            'son': 'Son',
            'grandmother': 'Grandmother',
            'grandfather': 'Grandfather',
            'aunt': 'Aunt',
            'uncle': 'Uncle',
            'cousin': 'Cousin'
        };
        
        return labels[relationship] || relationship.replace(/\b\w/g, l => l.toUpperCase());
    },
    
    getSeverityClass: function(severity) {
        if (severity <= 3) return 'success';
        if (severity <= 6) return 'warning';
        return 'danger';
    },
    
    // Show notification
    showNotification: function(message, type = 'info') {
        // Create notification element if it doesn't exist
        let notification = document.getElementById('family-notification');
        
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'family-notification';
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