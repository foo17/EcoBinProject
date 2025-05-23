const API_BASE_URL = '/analyticsReport';

// DOM elements
const reportTypeSelect = document.getElementById('report-type');
const universitySelect = document.getElementById('university');
const startDateInput = document.getElementById('start-date');
const endDateInput = document.getElementById('end-date');
const generateReportBtn = document.querySelector('.actions .btn-primary');
const exportBtn = document.querySelector('.actions .btn-outline');
const reportChart = document.getElementById('report-chart');
const dataTable = document.querySelector('.data-table tbody');
const reportTabs = document.querySelectorAll('.report-type');
const summaryStats = document.querySelector('.summary-stats');
const tableBody = document.querySelector('.report-content .Anomalytable tbody');


// Set default date range (last 30 days)
function setDefaultDates() {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    startDateInput.value = formatDate(thirtyDaysAgo);
    endDateInput.value = formatDate(today);
}


// Initialize report
document.addEventListener('DOMContentLoaded', function() {
    // Set default dates
    setDefaultDates();
    
    // Load universities dropdown
    loadUniversities();
    
    // Set up event listeners
    reportTypeSelect.addEventListener('change', updateReportView);
    universitySelect.addEventListener('change', () => {
        if (document.querySelector('.report-type.active').textContent === 'Detailed Report') {
            fetchReportData();
        }
    });
    startDateInput.addEventListener('change', () => {
        if (document.querySelector('.report-type.active').textContent === 'Detailed Report') {
            fetchReportData();
        }
    });
    endDateInput.addEventListener('change', () => {
        if (document.querySelector('.report-type.active').textContent === 'Detailed Report') {
            fetchReportData();
        }
    });
    generateReportBtn.addEventListener('click', fetchReportData);
 
    // Create dropdown for export formats
    const dropdownHTML = `
        <div class="export-dropdown">
            <button class="export-option" data-format="csv">CSV</button>
            <button class="export-option" data-format="json">JSON</button>
        </div>
    `;
    
    // Create container for export button and dropdown
    const exportContainer = document.createElement('div');
    exportContainer.className = 'export-container';
    
    // Replace the existing export button with the container
    exportBtn.parentNode.replaceChild(exportContainer, exportBtn);
    
    // Add the export button to the container
    exportContainer.appendChild(exportBtn);
    
    // Add the dropdown to the container
    const dropdownContainer = document.createElement('div');
    dropdownContainer.innerHTML = dropdownHTML;
    exportContainer.appendChild(dropdownContainer.firstElementChild);
    
    // Show/hide dropdown when clicking the export button
    exportBtn.addEventListener('click', function(e) {
        e.stopPropagation(); // Prevent event from bubbling up
        const dropdown = document.querySelector('.export-dropdown');
        dropdown.classList.toggle('show');
    });
    
    // Handle format selection
    document.querySelectorAll('.export-option').forEach(option => {
        option.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            exportReport(format);
            document.querySelector('.export-dropdown').classList.remove('show');
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.btn-outline') && !e.target.matches('.export-option')) {
            const dropdown = document.querySelector('.export-dropdown');
            if (dropdown && dropdown.classList.contains('show')) {
                dropdown.classList.remove('show');
            }
        }
    });
    
    // Add event listeners for report tabs
    reportTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            reportTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            if (tab.textContent === 'Detailed Report') {
                fetchReportData();
            } else if (tab.textContent === 'Summary Report') {
                fetchSummaryReport();
            } else if (tab.textContent === 'Charts & Visualizations') {
                fetchChartData();
            }
        });
    });

    // Initial data load
    fetchReportData();

});
// Load universities from API
async function loadUniversities() {
    try {
        showLoadingState();
        // Changed from '/reports/universities/' to use API_BASE_URL
        const response = await fetch(`${API_BASE_URL}/universities/`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        
        // Keep the "All Universities" option
        const defaultOption = universitySelect.querySelector('option');
        universitySelect.innerHTML = '';
        universitySelect.appendChild(defaultOption);
        
        // Add universities from database - handle different response formats
        data.universities.forEach(university => {
            const option = document.createElement('option');
            option.value = university.id || university.university_id; // Handle both formats
            option.textContent = university.university_name;
            universitySelect.appendChild(option);
        });
        hideLoadingState();
    } catch (error) {
        console.error('Error loading universities:', error);
        showErrorMessage('Failed to load universities. Please try again.');
        hideLoadingState();
    }
}

// Update the report view based on selected report type
function updateReportView() {
    const reportType = reportTypeSelect.value;
    
    // Clear previous data
    clearReportData();
    
    // Update UI elements based on report type
    switch(reportType) {
        case 'ewaste-log':
            document.querySelector('.report-title').textContent = 'E-Waste Collection Report';
            break;
        case 'user-activity':
            document.querySelector('.report-title').textContent = 'User Activity Report';
            break;
        case 'incentives':
            document.querySelector('.report-title').textContent = 'Incentives Utilization Report';
            break;
        case 'component-processing':
            document.querySelector('.report-title').textContent = 'Component Processing Report';
            break;
    }
    
    
    // Set the active tab to Detailed Report
    reportTabs.forEach(tab => tab.classList.remove('active'));
    reportTabs[0].classList.add('active');
    
    // Fetch fresh data for the selected report type
    fetchReportData();
}

// Fetch report data from API
async function fetchReportData() {
    const reportType = reportTypeSelect.value;
    const universityId = universitySelect?.value || "all";
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    try {
        // Show loading state
        showLoadingState();
        
        let endpoint;
        let params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate
        });
        
        if (universityId !== 'all') {
            params.append('university_id', universityId);
        }
        
        // Determine which API endpoint to use based on report type
        switch(reportType) {
            case 'ewaste-log':
                endpoint = `${API_BASE_URL}/ewaste-collections?${params.toString()}`;
                break;
            case 'user-activity':
                endpoint = `${API_BASE_URL}/user-activities?${params.toString()}`;
                break;
            case 'incentives':
                endpoint = `${API_BASE_URL}/incentives-report?${params.toString()}`;
                break;
            case 'component-processing':
                endpoint = `${API_BASE_URL}/component-processing-report?${params.toString()}`;
                break;
        }
        
        const response = await fetch(endpoint);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Process and display the data
        displayReportData(reportType, data);
        
    } catch (error) {
        console.error('Error fetching report data:', error);
        showErrorMessage('Failed to load report data. Please try again.');
    } finally {
        // Hide loading state
        hideLoadingState();
    }
}

// Fetch summary report data
async function fetchSummaryReport() {
    const reportType = reportTypeSelect.value;
    const universityId = universitySelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    try {
        showLoadingState();
        
        let endpoint;
        let params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate,
            summary: 'true'
        });
        
        if (universityId !== 'all') {
            params.append('university_id', universityId);
        }
        
        // Choose the right endpoint based on report type
        switch(reportType) {
            case 'ewaste-log':
                endpoint = `${API_BASE_URL}/ewaste-collections?${params.toString()}`;
                break;
            case 'user-activity':
                endpoint = `${API_BASE_URL}/user-activities?${params.toString()}`;
                break;
            case 'incentives':
                endpoint = `${API_BASE_URL}/incentives-report?${params.toString()}`;
                break;
            case 'component-processing':
                endpoint = `${API_BASE_URL}/component-processing-report?${params.toString()}`;
                break;
        }
        
        const response = await fetch(endpoint);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display only the summary section
        displaySummaryReport(reportType, data);
        
    } catch (error) {
        console.error('Error fetching summary data:', error);
        showErrorMessage('Failed to load summary data. Please try again.');
    } finally {
        hideLoadingState();
    }
}

// Fetch chart data
async function fetchChartData() {
    const reportType = reportTypeSelect.value;
    const universityId = universitySelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    try {
        showLoadingState();
        
        let endpoint;
        let params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate,
            chart_only: 'true'
        });
        
        if (universityId !== 'all') {
            params.append('university_id', universityId);
        }
        
        // Choose the right endpoint based on report type
        switch(reportType) {
            case 'ewaste-log':
                endpoint = `${API_BASE_URL}/ewaste-collections?${params.toString()}`;
                break;
            case 'user-activity':
                endpoint = `${API_BASE_URL}/user-activities?${params.toString()}`;
                break;
            case 'incentives':
                endpoint = `${API_BASE_URL}/incentives-report?${params.toString()}`;
                break;
            case 'component-processing':
                endpoint = `${API_BASE_URL}/component-processing-report?${params.toString()}`;
                break;
        }
        
        const response = await fetch(endpoint);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display only charts
        displayChartView(reportType, data);
        
    } catch (error) {
        console.error('Error fetching chart data:', error);
        showErrorMessage('Failed to load chart data. Please try again.');
    } finally {
        hideLoadingState();
    }
}
// Display report data based on type
function displayReportData(reportType, data) {
    clearReportData();
    
    // Show chart area and summary stats by default
    document.querySelector('.chart-area').style.display = 'block';
    document.querySelector('.summary-stats').style.display = 'flex';
    
    switch(reportType) {
        case 'ewaste-log':
            displayWasteCollectionReport(data);
            break;
        case 'user-activity':
            displayUserActivityReport(data);
            break;
        case 'incentives':
            displayIncentivesReport(data);
            break;
        case 'component-processing':
            displayComponentProcessingReport(data);
            break;
    }
}

// Display summary report view
function displaySummaryReport(reportType, data) {
    clearReportData();
    
    // Hide chart and table, only show summary
    document.querySelector('.chart-area').style.display = 'none';
    document.querySelector('.data-table').style.display = 'none';
    document.querySelector('.pagination').style.display = 'none';
    document.querySelector('.summary-stats').style.display = 'flex';
    
    // Update summary stats based on report type
    switch(reportType) {
        case 'ewaste-log':
            updateWasteSummaryStats(data.summary);
            break;
        case 'user-activity':
            updateActivitySummaryStats(data.summary);
            break;
        case 'incentives':
            updateIncentivesSummaryStats(data.summary);
            break;
        case 'component-processing':
            updateComponentSummaryStats(data.summary);
            break;
    }
}

// Display charts view
function displayChartView(reportType, data) {
    clearReportData();
    
    // Show only chart, hide table and pagination
    document.querySelector('.chart-area').style.display = 'block';
    document.querySelector('.data-table').style.display = 'none';
    document.querySelector('.pagination').style.display = 'none';
    document.querySelector('.summary-stats').style.display = 'none';
    
    // Display the appropriate chart based on report type
    switch(reportType) {
        case 'ewaste-log':
            createWasteChart(data.chartData);
            break;
        case 'user-activity':
            createActivityChart(data.chartData);
            break;
        case 'incentives':
            createIncentivesChart(data.chartData);
            break;;
        case 'component-processing':
            createComponentProcessingChart(data.chartData);
            break;
    }
}

// Display E-Waste Collection Report
function displayWasteCollectionReport(data) {
     // Clear the table before adding new rows
    dataTable.innerHTML = '';
    // Update summary statistics
    updateWasteSummaryStats(data.summary);
    
    // Update chart
    createWasteChart(data.chartData);
    
    // Create table headers for waste collection
    const tableHead = document.querySelector('.data-table thead tr');
    tableHead.innerHTML = `
        <th>ID</th>
        <th>Date</th>
        <th>University</th>
        <th>Device Type</th>
        <th>Weight (kg)</th>
        <th>Serial Number</th>
        <th>Status</th>
    `;
    // Check if collections data exists
    if (!data.collections) {
        console.error("Error: data.collections is missing", data);
        // Show no data message
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="7" class="text-center">No data available</td>';
        dataTable.appendChild(row);
        return;
    }   
    
    // Handle both array and object responses (MySQL vs API responses can vary)
    const collections = Array.isArray(data.collections) ? data.collections : 
                       (typeof data.collections === 'object' ? Object.values(data.collections) : []);
    
    if (collections.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="7" class="text-center">No records found</td>';
        dataTable.appendChild(row);
        return;
    }
    // Populate table with waste collection data
    collections.forEach(item => {
        try {
            const row = document.createElement('tr');
            const status = item.status ? item.status.toLowerCase() : 'unknown';
            const statusDisplay = item.status ? capitalizeFirstLetter(item.status) : 'Unknown';
            
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${formatDateDisplay(item.collection_date)}</td>
                <td>${item.university_name || 'N/A'}</td>
                <td>${item.waste_type || 'Electronics'}</td>
                <td>${parseFloat(item.weight_kg).toFixed(2)}</td>
                <td>${item.serial_number || 'N/A'}</td>
                <td><span class="status status-${status}">${statusDisplay}</span></td>
            `;
        
            dataTable.appendChild(row);
        } catch (error) {
            console.error("Error processing collection item:", error, item);
        }
    });
    
    // Update pagination if available
    if (data.pagination) {
        updatePagination(data.pagination);
    } else {
        // Hide pagination if not available
        document.querySelector('.pagination').style.display = 'none';
    }
}
// Display User Activity Report
function displayUserActivityReport(data) {
    updateActivitySummaryStats(data.summary);

    if (data.chartData) {
        createActivityChart(data.chartData);
    } else {
        console.warn('Chart data is missing, skipping chart update.');
    }

    // Ensure table reference is correct
    const tableHead = document.querySelector('.data-table thead tr');
    const dataTable = document.querySelector('.data-table tbody');

    if (!tableHead || !dataTable) {
        console.error("Table elements not found.");
        return;
    }

    tableHead.innerHTML = `
        <th>ID</th>
        <th>Date</th>
        <th>User</th>
        <th>University</th>
        <th>Activity Type</th>
        <th>Points Earned</th>
        <th>Description</th>
    `;

    dataTable.innerHTML = ''; // Clear existing rows before adding new data

    // Populate table with user activity data
    data.activities.forEach(item => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${item.id}</td>
            <td>${formatDateDisplay(item.activity_date)}</td>
            <td>${item.username}</td>
            <td>${item.university_name}</td>
            <td>${capitalizeFirstLetter(item.activity_type)}</td>
            <td>${item.points_earned}</td>
            <td>${item.description || 'N/A'}</td>
        `;

        dataTable.appendChild(row);
    });

    updatePagination(data.pagination);
}

// Display Incentives Report
function displayIncentivesReport(data) {
    // Update summary statistics
    updateIncentivesSummaryStats(data.summary);

    if (data.chartData) {
        createIncentivesChart(data.chartData);
    } else {
        console.warn('Chart data is missing, skipping chart update.');
    }

    // Create table headers for incentives
    const tableHead = document.querySelector('.data-table thead tr');
    tableHead.innerHTML = `
        <th>ID</th>
        <th>Date</th>
        <th>User</th>
        <th>University</th>
        <th>Incentive</th>
        <th>Points Used</th>
        <th>Status</th>
    `;
    
    // Populate table with incentives data
    data.incentives.forEach(item => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${formatDateDisplay(item.redemption_date)}</td>
            <td>${item.username}</td>
            <td>${item.university_name}</td>
            <td>${item.incentive_name}</td>
            <td>${item.points_used}</td>
            <td><span class="status status-${getStatusClass(item.status)}">${capitalizeFirstLetter(item.status)}</span></td>
        `;
        
        dataTable.appendChild(row);
    });
    
    updatePagination(data.pagination);
}
// Display Component Processing Report
function displayComponentProcessingReport(data) {
    // Clear the table before adding new rows
    dataTable.innerHTML = '';
    
    // Update summary statistics
    updateComponentSummaryStats(data.summary);
    
    // Update chart
    createComponentProcessingChart(data.chartData);
    
    // Create table headers for component processing
    const tableHead = document.querySelector('.data-table thead tr');
    tableHead.innerHTML = `
        <th>ID</th>
        <th>Component</th>
        <th>Appliance</th>
        <th>Serial Number</th>
        <th>University</th>
        <th>Process Status</th>
        <th>Recycle Status</th>
    `;
    
    // Check if components data exists
    if (!data.components || data.components.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="7" class="text-center">No data available</td>';
        dataTable.appendChild(row);
        return;
    }   
    
    // Populate table with component data
    data.components.forEach(item => {
        try {
            const row = document.createElement('tr');
            
            // Determine status classes
            const processStatus = item.is_processed ? 'Processed' : 'Pending';
            const recycleStatus = item.is_recycled ? 'Recycled' : (item.is_processed ? 'Pending' : 'Waiting');
            
            const processClass = item.is_processed ? 'status-recycled' : 'status-processing';
            const recycleClass = item.is_recycled ? 'status-recycled' : 'status-collected';
            
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.component_name}</td>
                <td>${item.appliance}</td>
                <td>${item.serial_number}</td>
                <td>${item.university}</td>
                <td><span class="status ${processClass}">${processStatus}</span></td>
                <td><span class="status ${recycleClass}">${recycleStatus}</span></td>
            `;
        
            dataTable.appendChild(row);
        } catch (error) {
            console.error("Error processing component item:", error, item);
        }
    });
    
    // Update pagination if available
    if (data.pagination) {
        updatePagination(data.pagination);
    } else {
        // Hide pagination if not available
        document.querySelector('.pagination').style.display = 'none';
    }
}

// Update waste summary statistics
function updateWasteSummaryStats(summary) {
    summaryStats.innerHTML = `
        <div class="summary-stat">
            <h3>Total E-Waste</h3>
            <div class="value">${summary.total_weight.toLocaleString()} kg</div>
        </div>
        <div class="summary-stat">
            <h3>Items Collected</h3>
            <div class="value">${summary.total_items.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Processing Rate</h3>
            <div class="value">${summary.processing_rate}%</div>
        </div>
        <div class="summary-stat">
            <h3>Recycling Rate</h3>
            <div class="value">${summary.recycling_rate}%</div>
        </div>
    `;
}

// Update activity summary statistics
function updateActivitySummaryStats(summary) {
    summaryStats.innerHTML = `
        <div class="summary-stat">
            <h3>Total Activities</h3>
            <div class="value">${summary.total_activities.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Active Users</h3>
            <div class="value">${summary.active_users.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Points Awarded</h3>
            <div class="value">${summary.total_points.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Avg Per User</h3>
            <div class="value">${summary.avg_activities_per_user}</div>
        </div>
    `;
}

// Update incentives summary statistics
function updateIncentivesSummaryStats(summary) {
    summaryStats.innerHTML = `
        <div class="summary-stat">
            <h3>Total Redemptions</h3>
            <div class="value">${summary.total_redemptions.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Users Rewarded</h3>
            <div class="value">${summary.unique_users.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Points Redeemed</h3>
            <div class="value">${summary.total_points_used.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Approval Rate</h3>
            <div class="value">${summary.approval_rate}%</div>
        </div>
    `;
}


// Update component summary statistics
function updateComponentSummaryStats(summary) {
    summaryStats.innerHTML = `
        <div class="summary-stat">
            <h3>Total Components</h3>
            <div class="value">${summary.total_components.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Processed</h3>
            <div class="value">${summary.processed_components.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Recycled</h3>
            <div class="value">${summary.recycled_components.toLocaleString()}</div>
        </div>
        <div class="summary-stat">
            <h3>Processing Rate</h3>
            <div class="value">${summary.processing_rate}%</div>
        </div>
    `;
}

// Create waste collection chart
function createWasteChart(chartData) {
    const chartArea = document.querySelector('.chart-area');
    chartArea.style.display = 'block';
    
    if (window.reportChartInstance) {
        window.reportChartInstance.destroy();
    }
    
    const ctx = reportChart.getContext('2d');
    window.reportChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Collected',
                    data: chartData.collected,
                    backgroundColor: '#42a5f5'
                },
                {
                    label: 'Processing',
                    data: chartData.processing,
                    backgroundColor: '#ffca28'
                },
                {
                    label: 'Recycled',
                    data: chartData.recycled,
                    backgroundColor: '#66bb6a'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Weight (kg)'
                    }
                }
            }
        }
    });
}
function createActivityChart(chartData) {
    const chartArea = document.querySelector('.chart-area');
    chartArea.style.display = 'block';

    if (window.reportChartInstance) {
        window.reportChartInstance.destroy();
    }

    const ctx = reportChart.getContext('2d');
    window.reportChartInstance = new Chart(ctx, {
        type: 'bar',
        data: chartData, // Use the whole chartData object, not just labels
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.raw} activities`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Activities'
                    }
                }
            }
        }
    });


    // Add event listener to update legend style if needed
    reportChart.addEventListener('mousemove', () => {
        const canvas = activityChartInstance.canvas;
        const rect = canvas.getBoundingClientRect();
        if (rect.width < 400) {
            activityChartInstance.options.plugins.legend.position = 'bottom';
        } else {
            activityChartInstance.options.plugins.legend.position = 'top';
        }
        activityChartInstance.update();
    });
}

// Create incentives chart
function createIncentivesChart(chartData) {
    const chartArea = document.querySelector('.chart-area');
    chartArea.style.display = 'block';
    
    if (window.reportChartInstance) {
        window.reportChartInstance.destroy();
    }
    
    const ctx = reportChart.getContext('2d');
    window.reportChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.backgroundColor
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });
}

// Create component processing chart
function createComponentProcessingChart(chartData) {
    const chartArea = document.querySelector('.chart-area');
    chartArea.style.display = 'block';
    
    if (window.reportChartInstance) {
        window.reportChartInstance.destroy();
    }
    
    const ctx = reportChart.getContext('2d');
    
    // Process data for chart
    const labels = chartData.map(item => item.component_name);
    const totalData = chartData.map(item => item.total);
    const processedData = chartData.map(item => item.processed);
    const recycledData = chartData.map(item => item.recycled);
    
    window.reportChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total',
                    data: totalData,
                    backgroundColor: '#42a5f5'
                },
                {
                    label: 'Processed',
                    data: processedData,
                    backgroundColor: '#ffca28'
                },
                {
                    label: 'Recycled',
                    data: recycledData,
                    backgroundColor: '#66bb6a'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            }
        }
    });
}
// Update pagination based on API response
function updatePagination(pagination) {
    const paginationContainer = document.querySelector('.pagination');
    paginationContainer.style.display = 'flex';
    paginationContainer.innerHTML = '';
    
    // Previous page button
    const prevBtn = document.createElement('div');
    prevBtn.classList.add('pagination-item');
    prevBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>';
    if (pagination.current_page > 1) {
        prevBtn.addEventListener('click', () => changePage(pagination.current_page - 1));
    } else {
        prevBtn.style.opacity = '0.5';
        prevBtn.style.cursor = 'not-allowed';
    }
    paginationContainer.appendChild(prevBtn);
    
    // Page numbers
    for (let i = 1; i <= pagination.total_pages; i++) {
        const pageItem = document.createElement('div');
        pageItem.classList.add('pagination-item');
        if (i === pagination.current_page) {
            pageItem.classList.add('active');
        }
        pageItem.textContent = i;
        pageItem.addEventListener('click', () => changePage(i));
        paginationContainer.appendChild(pageItem);
    }
    
    // Next page button
    const nextBtn = document.createElement('div');
    nextBtn.classList.add('pagination-item');
    nextBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>';
    if (pagination.current_page < pagination.total_pages) {
        nextBtn.addEventListener('click', () => changePage(pagination.current_page + 1));
    } else {
        nextBtn.style.opacity = '0.5';
        nextBtn.style.cursor = 'not-allowed';
    }
    paginationContainer.appendChild(nextBtn);
}

// Change page
function changePage(page) {
    // Update hidden input or URL parameter
    const params = new URLSearchParams(window.location.search);
    params.set('page', page);
    
    // Either update URL or just reload with new page parameter
    // window.location.search = params.toString();
    
    // Alternative: just refetch data with the new page
    const reportType = reportTypeSelect.value;
    const universityId = universitySelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    fetchPagedData(reportType, universityId, startDate, endDate, page);
}
// Fetch data for specific page (continued)
async function fetchPagedData(reportType, universityId, startDate, endDate, page) {
    try {
        showLoadingState();
        
        let endpoint;
        let params = new URLSearchParams({
            start_date: startDate,
            end_date: endDate,
            page: page
        });
        
        if (universityId !== 'all') {
            params.append('university_id', universityId);
        }
        
        // Determine which API endpoint to use based on report type
        switch(reportType) {
            case 'ewaste-log':
                endpoint = `${API_BASE_URL}/ewaste-collections?${params.toString()}`;
                break;
            case 'user-activity':
                endpoint = `${API_BASE_URL}/user-activities?${params.toString()}`;
                break;
            case 'incentives':
                endpoint = `${API_BASE_URL}/incentives-report?${params.toString()}`;
                break;
            case 'component-processing':
                endpoint = `${API_BASE_URL}/component-processing-report?${params.toString()}`;
                break;
        }
        
        const response = await fetch(endpoint);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Process and display the data
        displayReportData(reportType, data);
        
    } catch (error) {
        console.error('Error fetching paged data:', error);
        showErrorMessage('Failed to load page data. Please try again.');
    } finally {
        hideLoadingState();
    }
}

// Export report data
// Update the exportReport function to accept format parameter
function exportReport() {
    const reportType = reportTypeSelect.value;
    const universityId = universitySelect.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    let params = new URLSearchParams({
        report_type: reportType,
        start_date: startDate,
        end_date: endDate,
        format: 'csv'
    });
    
    if (universityId !== 'all') {
        params.append('university_id', universityId);
    }
    
    // Redirect to the export endpoint
    window.location.href = `${API_BASE_URL}/export?${params.toString()}`;
}
function exportReport(format = 'json') {
    const reportType = document.getElementById('report-type').value;
    const universityId = document.getElementById('university').value;
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    let params = new URLSearchParams({
        report_type: reportType,
        start_date: startDate,
        end_date: endDate,
        format: format
    });
    
    if (universityId !== 'all') {
        params.append('university_id', universityId);
    }
    
    // Redirect to the export endpoint
    window.location.href = `${API_BASE_URL}/export?${params.toString()}`;
}


// Helper Functions
function clearReportData() {
    // Clear table
    dataTable.innerHTML = '';
    
    // Reset chart
    if (window.reportChartInstance) {
        window.reportChartInstance.destroy();
    }
    
    // Make sure table is visible
    document.querySelector('.data-table').style.display = 'table';
}

function showLoadingState() {
    // Add loading indicators as needed
    generateReportBtn.innerHTML = '<span class="loading-spinner"></span> Loading...';
    generateReportBtn.disabled = true;
}

function hideLoadingState() {
    // Remove loading indicators
    generateReportBtn.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" 
        stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
    </svg>
    Refresh
`;
    generateReportBtn.disabled = false;
}

function showErrorMessage(message) {
    // Create error toast notification
    const toast = document.createElement('div');
    toast.className = 'toast toast-error';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 5000);
}

function showSuccessMessage(message) {
    // Create success toast notification
    const toast = document.createElement('div');
    toast.className = 'toast toast-success';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 5000);
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function formatDateDisplay(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function getStatusClass(status) {
    switch(status.toLowerCase()) {
        case 'collected':
        case 'pending':
            return 'collected';
        case 'processing':
        case 'approved':
            return 'processing';
        case 'recycled':
        case 'completed':
            return 'recycled';
        case 'disposed':
        case 'declined':
            return 'disposed';
        default:
            return 'collected';
    }
}

function getSeverityClass(verificationStatus) {
    switch(verificationStatus) {
        case 'valid':
            return 'Low';
        case 'duplicate':
            return 'Medium';
        case 'unregistered':
        case 'flagged':
            return 'High';
        default:
            return 'Low';
    }
}



function getDefaultDescription(verificationStatus, serialNumber) {
    switch(verificationStatus) {
        case 'duplicate':
            return `Serial number ${serialNumber} appears multiple times in system`;
        case 'unregistered':
            return 'Device not properly entered in system';
        case 'flagged':
            return 'Suspicious pattern detected in waste collection';
        default:
            return 'Unknown issue detected';
    }
}

// Add CSS for toasts since they're not in the original CSS
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            opacity: 1;
            transition: opacity 0.3s ease;
        }
        .toast-error {
            background-color: #f44336;
        }
        .toast-success {
            background-color: #4caf50;
        }
        .loading-spinner {
            display: inline-block;
            width: 12px;
            height: 12px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s infinite linear;
            margin-right: 5px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
});