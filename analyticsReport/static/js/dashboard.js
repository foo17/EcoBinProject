// E-Waste Analytics Platform - Combined Dashboard
// Main JavaScript file for the combined dashboard and analytics page

// API Base URLs
const DASHBOARD_API = '/analyticsReport';

// Chart instances storage
const charts = {};

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize date inputs
  setDefaultDates();
  
  // Add event listeners
  initEventListeners();
  
  // Initialize tabs
  initTabs();
  
  // Fetch dashboard data
  fetchDashboardData();
  
  // Set up automatic data refresh (every 2 minutes)
  setInterval(fetchDashboardData, 120000);
});

// Initialize event listeners
function initEventListeners() {
  // Time period change
  document.getElementById('time-period').addEventListener('change', function() {
    fetchDashboardData();
  });
  const timePeriodSelect = document.getElementById('time-period');
  if (timePeriodSelect) {
    timePeriodSelect.value = 'month';
  }
  
  // View type change for collection trends
  document.getElementById('view-filter').addEventListener('change', function() {
    fetchCollectionTrendsData();
  });
  
  
  // Device type filter for collection trends
  const deviceTypeFilter = document.getElementById('device-type-filter');
  if (deviceTypeFilter) {
    deviceTypeFilter.addEventListener('change', function() {
      fetchCollectionTrendsData();
    });
  }
  
  // Campus filter for campus expert activity
  const campusFilter = document.getElementById('campus-filter');
  if (campusFilter) {
    campusFilter.addEventListener('change', function() {
      fetchCampusExpertData();
    });
  }
  const componentTimePeriodSelect = document.getElementById('component-time-period');
  if (componentTimePeriodSelect) {
    componentTimePeriodSelect.addEventListener('change', fetchComponentProcessingData);
  }

  // Update insights button
  document.getElementById('update-insights-btn').addEventListener('click', function() {
    fetchDashboardData();
  });
  
  // Tab navigation
  document.querySelectorAll('.tab-link').forEach(tab => {
    tab.addEventListener('click', function(e) {
      e.preventDefault();
      const tabId = this.getAttribute('data-tab');
      switchTab(tabId);
    });
  });
}

// Initialize tabs
function initTabs() {
  // Show default tab (overview)
  document.getElementById('overview-tab').classList.remove('hidden');
  
  // Set active tab
  document.querySelector('.tab-link[data-tab="overview"]').classList.add('active');
}

// Switch between tabs
function switchTab(tabId) {
  // Hide all tab contents
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.add('hidden');
  });
  
  // Remove active class from all tabs
  document.querySelectorAll('.tab-link').forEach(tab => {
    tab.classList.remove('text-green-800', 'border-b-2', 'border-green-800');
    tab.classList.add('text-gray-500');
  });
  
  // Show selected tab content
  const selectedTab = document.getElementById(`${tabId}-tab`);
  if (selectedTab) {
    selectedTab.classList.remove('hidden');
  }
  
  // Set active tab
  const activeTab = document.querySelector(`.tab-link[data-tab="${tabId}"]`);
  if (activeTab) {
    activeTab.classList.remove('text-gray-500');
    activeTab.classList.add('text-green-800', 'border-b-2', 'border-green-800');
  }
  
  // Load tab-specific data
  switch(tabId) {
    case 'overview':
      fetchDashboardData();
      break;
    case 'advanced':
      fetchAdvancedAnalyticsData();
      break;
    case 'predictive':
      fetchPredictiveInsightsData();
      break;
    case 'university':
      fetchUniversityComparisonData();
      break;
    case 'components':
    fetchComponentProcessingData();
    break;
  }
}

// Set default dates for date pickers
function setDefaultDates() {
  const today = new Date();
  
  // Set report dates
  if (document.getElementById('report-start-date')) {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    document.getElementById('report-start-date').valueAsDate = thirtyDaysAgo;
    document.getElementById('report-end-date').valueAsDate = today;
  }
  
  // Update the date range display
  const startOfYear = new Date(today.getFullYear(), 0, 1);
  const dateRangeEl = document.getElementById('date-range');
  if (dateRangeEl) {
    dateRangeEl.textContent = `${formatDateShort(startOfYear)} - ${formatDateShort(today)}`;
  }
  
  // Update last updated date
  const lastUpdatedEl = document.getElementById('last-updated');
  if (lastUpdatedEl) {
    lastUpdatedEl.textContent = formatDateFull(today);
  }
}

// Format date in short format (MMM DD, YYYY)
function formatDateShort(date) {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

// Format date in full format (Month DD, YYYY)
function formatDateFull(date) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

// Format number with commas
function formatNumber(num) {
  // Handle undefined or null values
  if (num === undefined || num === null) {
    return "0";
  }
  
  // Convert to number in case it's a string
  num = Number(num);
  
  // Check if it's a valid number
  if (isNaN(num)) {
    return "0";
  }
  
  // For total weight, round to 1 decimal place
  if (Math.abs(num) > 1000) {
    // For large numbers, show no decimals
    return num.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  } else if (Math.abs(num) >= 10) {
    // For medium numbers, show 1 decimal place
    return num.toFixed(1).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  } else {
    // For small numbers, show 2 decimal places
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
}

// Get status class based on status
function getStatusClass(status) {
  switch(status.toLowerCase()) {
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'processing':
      return 'bg-yellow-100 text-yellow-800';
    case 'pending':
      return 'bg-blue-100 text-blue-800';
    case 'cancelled':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

// Fetch all dashboard data
function fetchDashboardData() {
  showLoading(true);
  
  // Get selected time period
  const timePeriod = document.getElementById('time-period').value;
  
  // Get year for waste collection
  const year = new Date().getFullYear();
  
  // Promise all to fetch data in parallel
  Promise.all([
    fetchStatistics(),
    fetchCollectionTrendsData(),
    fetchCampusExpertData(),
    fetchCommunityBreakdownData(),
    fetchWasteStatusData(),
    fetchComponentDistributionData(),
    fetchRecentCollectionsData(),
    fetchAdvancedAnalyticsData(),
    fetchPredictiveInsightsData(),
    fetchUniversityComparisonData(),
    fetchAnalyticsHighlights(),
    fetchComponentProcessingData(),
    fetchUserRoleEngagementData()
  ])
  .then(() => {
    showLoading(false);
  })
  .catch(error => {
    console.error('Error fetching dashboard data:', error);
    showLoading(false);
    showError('Failed to load some dashboard data. Please try refreshing.');
  });
}


// New function to update collection metrics
function updateCollectionMetrics(data) {
  // Check if we have metadata in the response
  if (data.metadata) {
    // Update top device type
    if (data.metadata.top_device) {
      document.getElementById('top-device-type').textContent = data.metadata.top_device.name;
      document.getElementById('top-device-percentage').textContent = 
        `${data.metadata.top_device.percentage.toFixed(1)}% of total`;
    }
    
    // Update collection efficiency
    if (data.metadata.efficiency !== undefined) {
      document.getElementById('collection-efficiency').textContent = 
        `${data.metadata.efficiency.toFixed(1)}%`;
    }
    
    // Update monthly growth
    if (data.metadata.growth !== undefined) {
      const growthEl = document.getElementById('monthly-growth');
      const growth = data.metadata.growth;
      
      growthEl.textContent = `${growth >= 0 ? '+' : ''}${growth.toFixed(1)}%`;
      
      // Set color based on growth value
      if (growth >= 0) {
        growthEl.classList.remove('text-red-800');
        growthEl.classList.add('text-green-800');
      } else {
        growthEl.classList.remove('text-green-800');
        growthEl.classList.add('text-red-800');
      }
    }
    
    // Update collection method
    if (data.metadata.top_method) {
      document.getElementById('top-collection-method').textContent = 
        data.metadata.top_method.name;
      document.getElementById('top-method-percentage').textContent = 
        `${data.metadata.top_method.percentage.toFixed(1)}% of pickups`;
    }
  } else {
    // Set default values if metadata is not available
    setDefaultCollectionMetrics();
  }
}

// Set default values for collection metrics when data is not available
function setDefaultCollectionMetrics() {
  document.getElementById('top-device-type').textContent = 'N/A';
  document.getElementById('top-device-percentage').textContent = '0% of total';
  document.getElementById('collection-efficiency').textContent = '0%';
  document.getElementById('monthly-growth').textContent = '0%';
  document.getElementById('top-collection-method').textContent = 'N/A';
  document.getElementById('top-method-percentage').textContent = '0% of pickups';
}

// Fetch statistics
function fetchStatistics() {
  return fetch(`${DASHBOARD_API}/statistics/`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Update statistics with proper formatting
      const totalWasteEl = document.getElementById('total-waste');
      if (totalWasteEl) {
        // The backend now returns appliance count instead of weight
        const totalWaste = Number(data.total_waste);
        if (!isNaN(totalWaste)) {
          // For appliance count, show as integer with units
          totalWasteEl.textContent = `${formatNumber(Math.round(totalWaste))} kg`;
        } else {
          totalWasteEl.textContent = '0 kg';
        }
      }
      
      // Other statistics update with simple formatting
      document.getElementById('university-count').textContent = formatNumber(data.university_count);
      document.getElementById('user-count').textContent = formatNumber(data.user_count);
      document.getElementById('reward-count').textContent = formatNumber(data.reward_count);
    })
    .catch(error => {
      console.error('Error fetching statistics:', error);
      document.getElementById('total-waste').textContent = '0 kg';
      document.getElementById('university-count').textContent = '0';
      document.getElementById('user-count').textContent = '0';
      document.getElementById('reward-count').textContent = '0';
    });
}

// Updated E-Waste Collection Analytics function
function fetchCollectionTrendsData() {
  const viewFilter = document.getElementById('view-filter').value;
  const deviceTypeFilter = document.getElementById('device-type-filter')?.value || 'all';
  const year = new Date().getFullYear();
  
  return fetch(`${DASHBOARD_API}/waste-collection/?year=${year}&viewType=${viewFilter}&deviceType=${deviceTypeFilter}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Create or update chart
      createOrUpdateCollectionTrendsChart(data);
      
      // Update the additional metrics
      updateCollectionMetrics(data);
    })
    .catch(error => {
      console.error('Error fetching collection trends:', error);
      
      // Create chart with empty data
      const emptyData = {
        labels: viewFilter === 'monthly' ? 
          ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] :
          ['Q1', 'Q2', 'Q3', 'Q4'],
        datasets: [{
          label: 'No Data Available',
          data: Array(viewFilter === 'monthly' ? 12 : 4).fill(0),
          borderColor: '#cccccc',
          backgroundColor: 'rgba(204, 204, 204, 0.1)',
          tension: 0.3
        }]
      };
      
      createOrUpdateCollectionTrendsChart(emptyData);
      
      // Set default values for metrics
      setDefaultCollectionMetrics();
    });
}

// Fetch community breakdown data
function fetchCommunityBreakdownData() {
  const timePeriod = document.getElementById('time-period').value;
  
  return fetch(`${DASHBOARD_API}/community-breakdown/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Create or update chart
      createOrUpdateCommunityChart(data);
    })
    .catch(error => {
      console.error('Error fetching community breakdown data:', error);
      
      // Create chart with empty data
      const emptyData = {
        labels: ['No Data Available'],
        datasets: [{
          data: [100],
          backgroundColor: ['#cccccc']
        }]
      };
      
      createOrUpdateCommunityChart(emptyData);
    });
}


// Fetch waste status data
function fetchWasteStatusData() {
  const timePeriod = document.getElementById('time-period').value;

  return fetch(`${DASHBOARD_API}/waste-status/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Create or update chart
      createOrUpdateStatusChart(data);
      
      // Update processing rate in analytics highlights
      if (data.labels.includes('processing') && data.datasets[0].data) {
        const totalCount = data.datasets[0].data.reduce((sum, val) => sum + val, 0);
        const processingIndex = data.labels.indexOf('processing');
        
        if (totalCount > 0 && processingIndex !== -1) {
          const processingRate = Math.round((data.datasets[0].data[processingIndex] / totalCount) * 100);
          document.getElementById('processing-rate').textContent = `${processingRate}%`;
        }
      }
    })
    .catch(error => {
      console.error('Error fetching waste status data:', error);
      
      // Create chart with empty data
      const emptyData = {
        labels: ['No Data Available'],
        datasets: [{
          data: [100],
          backgroundColor: ['#cccccc']
        }]
      };
      
      createOrUpdateStatusChart(emptyData);
    });
}

// Fetch component distribution data
function fetchComponentDistributionData() {
  const timePeriod = document.getElementById('time-period').value;
  
  return fetch(`${DASHBOARD_API}/component-distribution/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Create or update chart
      createOrUpdateComponentDistributionChart(data);
    })
    .catch(error => {
      console.error('Error fetching component distribution data:', error);
      
      // Create chart with empty data
      const emptyData = {
        labels: ['No Data Available'],
        datasets: [{
          data: [100],
          backgroundColor: ['#cccccc']
        }]
      };
      
      createOrUpdateComponentDistributionChart(emptyData);
    });
}

// Fetch analytics highlights data
function fetchAnalyticsHighlights() {
  // Get selected time period
  const timePeriod = document.getElementById('time-period').value;
  
  console.log('Fetching analytics highlights for period:', timePeriod);
  
  return fetch(`${DASHBOARD_API}/analytics-highlights/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      console.log('Analytics highlights data received:', data);
      
      // Update forecasted growth
      const forecastedGrowth = document.getElementById('forecasted-growth');
      if (forecastedGrowth) {
        const growthValue = data.forecasted_growth || 0;
        // Format with + sign for positive values
        const formattedGrowth = growthValue >= 0 ? 
          `+${growthValue.toFixed(1)}%` : 
          `${growthValue.toFixed(1)}%`;
        
        forecastedGrowth.textContent = formattedGrowth;
        
        // Update color based on growth
        if (growthValue >= 0) {
          forecastedGrowth.classList.remove('text-red-800');
          forecastedGrowth.classList.add('text-green-800');
        } else {
          forecastedGrowth.classList.remove('text-green-800');
          forecastedGrowth.classList.add('text-red-800');
        }
      }
      
      // Update processing rate
      const processingRate = document.getElementById('processing-rate');
      if (processingRate) {
        processingRate.textContent = `${data.processing_rate || 0}%`;
      }
      
      // Update peak collection day
      const peakCollection = document.getElementById('peak-collection');
      if (peakCollection) {
        peakCollection.textContent = data.peak_collection_day || 'Monday';
      }
      
      return data;
    })
    .catch(error => {
      console.error('Error fetching analytics highlights:', error);
      
      // Set default values on error
      const forecastedGrowth = document.getElementById('forecasted-growth');
      if (forecastedGrowth) forecastedGrowth.textContent = '+0.0%';
      
      const processingRate = document.getElementById('processing-rate');
      if (processingRate) processingRate.textContent = '0%';
      
      const peakCollection = document.getElementById('peak-collection');
      if (peakCollection) peakCollection.textContent = 'Monday';
    });
}

// Fetch recent collections data
// Update function to fetch recent collections
function fetchRecentCollectionsData() {
  // Initialize pagination variables if they don't exist
  window.currentPage = window.currentPage || 1;
  // Change the limit to 5 for the dashboard view
  window.pageLimit = 5;
  
  return fetch(`${DASHBOARD_API}/recent-collections/?page=${window.currentPage}&limit=${window.pageLimit}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Populate recent collections table
      const tbody = document.getElementById('recent-collections');
      tbody.innerHTML = '';
      
      if (data.collections.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6" class="px-6 py-4 text-center text-gray-500">No collections available</td>';
        tbody.appendChild(row);
      } else {
        data.collections.forEach(item => {
          const row = document.createElement('tr');
          
          row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">${item.date}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.university}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.type}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.weight} kg</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs rounded-full ${getStatusClass(item.status)}">${item.status}</span>
            </td>
          `;
          
          tbody.appendChild(row);
        });
      }
      
      // Update pagination info
      const paginationInfo = document.getElementById('pagination-info');
      const start = (data.pagination.page - 1) * data.pagination.limit + 1;
      const end = Math.min(start + data.collections.length - 1, data.pagination.total);
      paginationInfo.textContent = `Showing ${start}-${end} of ${data.pagination.total} entries`;
      
      // Hide pagination controls since we're limiting to 5 entries
      const paginationControls = document.getElementById('pagination-controls');
      if (paginationControls) {
        paginationControls.style.display = 'none';
      }
      
      return data;
    })
    .catch(error => {
      console.error('Error fetching recent collections:', error);
      
      // Show error in table
      const tbody = document.getElementById('recent-collections');
      tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-red-500">Failed to load recent collections. Please try again.</td></tr>';
      
      // Clear pagination info
      document.getElementById('pagination-info').textContent = 'No data available';
    });
}

// Fetch advanced analytics data
function fetchAdvancedAnalyticsData() {
  showLoading(true);
  
  // Get selected time period
  const timePeriod = document.getElementById('time-period').value;

  // Get year for waste collection
  const year = new Date().getFullYear();
  
  // Promise all to fetch data in parallel
  Promise.all([
    fetchUserRoleEngagementData(timePeriod),
    fetchWasteInsightsData(timePeriod)
  ])
  .then(() => {
    showLoading(false);
  })
  .catch(error => {
    console.error('Error fetching advanced analytics data:', error);
    showLoading(false);
    showError('Failed to load advanced analytics data. Please try refreshing.');
  });
}
// Add this function to fetch user role engagement data
function fetchUserRoleEngagementData(timePeriod) {
  const period = timePeriod || document.getElementById('time-period').value;
  
  return fetch(`${DASHBOARD_API}/user-role-engagement/?period=${period}&_=${Date.now()}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Update role counters
      updateRoleCounters(data.roles);
      
      // Create or update role engagement chart
      createOrUpdateRoleEngagementChart(data);
      
      return data;
    })
    .catch(error => {
      console.error('Error fetching user role engagement data:', error);
      
      // Set default values for counters
      document.getElementById('university-community').textContent = '0';
      document.getElementById('campus-experts').textContent = '0';
      document.getElementById('collection-team').textContent = '0';
      document.getElementById('processing-team').textContent = '0';
      document.getElementById('recycling-team').textContent = '0';
      
      // Create empty chart
      createOrUpdateRoleEngagementChart({
        labels: ['No Data'],
        datasets: [{
          label: 'No Data Available',
          data: [0],
          backgroundColor: ['#cccccc']
        }]
      });
    });
}

// Update role counters function
function updateRoleCounters(roles) {
  if (!roles) return;
  
  // Update each role counter
  document.getElementById('university-community').textContent = formatNumber(roles.university_community || 0);
  document.getElementById('campus-experts').textContent = formatNumber(roles.campus_expert || 0);
  document.getElementById('collection-team').textContent = formatNumber(roles.collection_team || 0);
  document.getElementById('processing-team').textContent = formatNumber(roles.processing_team || 0);
  document.getElementById('recycling-team').textContent = formatNumber(roles.recycling_team || 0);
}


// Fetch waste insights data
function fetchWasteInsightsData(timePeriod) {
  return fetch(`${DASHBOARD_API}/waste-insights/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Update growth metrics
      if (data.growth_metrics) {
        const latestGrowth = data.growth_metrics.latest_growth_rate || 0;
        const avgGrowth = data.growth_metrics.avg_growth_rate || 0;
        
        // Set latest growth with appropriate color
        const latestGrowthElement = document.getElementById('latest-growth');
        latestGrowthElement.textContent = `${latestGrowth}%`;
        if (latestGrowth >= 0) {
          latestGrowthElement.classList.remove('text-red-800');
          latestGrowthElement.classList.add('text-green-800');
        } else {
          latestGrowthElement.classList.remove('text-green-800');
          latestGrowthElement.classList.add('text-red-800');
        }
        
        // Set average growth with appropriate color
        const avgGrowthElement = document.getElementById('avg-growth');
        avgGrowthElement.textContent = `${avgGrowth}%`;
        if (avgGrowth >= 0) {
          avgGrowthElement.classList.remove('text-red-800');
          avgGrowthElement.classList.add('text-green-800');
        } else {
          avgGrowthElement.classList.remove('text-green-800');
          avgGrowthElement.classList.add('text-red-800');
        }
        
        // Also update forecasted growth in overview
        const forecastedGrowthElement = document.getElementById('forecasted-growth');
        forecastedGrowthElement.textContent = `${avgGrowth >= 0 ? '+' : ''}${avgGrowth.toFixed(1)}%`;
        if (avgGrowth >= 0) {
          forecastedGrowthElement.classList.remove('text-red-800');
          forecastedGrowthElement.classList.add('text-green-800');
        } else {
          forecastedGrowthElement.classList.remove('text-green-800');
          forecastedGrowthElement.classList.add('text-red-800');
        }
      }
      
      // Update peak collection day
      if (data.peak_collection_day) {
        document.getElementById('peak-day').textContent = data.peak_collection_day;
        document.getElementById('peak-collection').textContent = data.peak_collection_day;
      }
      
      // Create or update waste by type chart
      if (data.waste_by_type) {
        createOrUpdateWasteByTypeChart(data.waste_by_type);
      }
      
      // Create or update monthly trend chart
      if (data.monthly_trend) {
        createOrUpdateMonthlyTrendChart(data.monthly_trend);
      }
    })
    .catch(error => {
      console.error('Error fetching waste insights data:', error);
      
      // Clear metrics
      document.getElementById('latest-growth').textContent = '0%';
      document.getElementById('avg-growth').textContent = '0%';
      document.getElementById('peak-day').textContent = '-';
      
      // Create empty charts
      createOrUpdateWasteByTypeChart([]);
      createOrUpdateMonthlyTrendChart([]);
    });
}

// Fetch predictive insights data
function fetchPredictiveInsightsData() {
  showLoading(true);
  
  // Get selected time period
  const timePeriod = document.getElementById('time-period').value;
  
  fetch(`${DASHBOARD_API}/predictive-insights/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Create or update forecast chart
      if (data.waste_forecast) {
        createOrUpdateForecastChart(data.waste_forecast);
      } else {
        // Even if there's no data, we should update the forecast details to show "No data available"
        updateForecastDetails([]);
      }
      
      showLoading(false);
    })
    .catch(error => {
      console.error('Error fetching predictive insights data:', error);
      
      // Create empty charts
      createOrUpdateForecastChart([]);
      
      showLoading(false);
      showError('Failed to load predictive insights data. Please try refreshing.');
    });
}

// Fetch university comparison data
function fetchUniversityComparisonData() {
  showLoading(true);
  
  // Get selected time period
  const timePeriod = document.getElementById('time-period').value;
  
  fetch(`${DASHBOARD_API}/university-comparison/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      if (data.universities) {
        // Create or update university weight chart
        createOrUpdateUniversityWeightChart(data.universities);
        
        // Create or update university efficiency chart
        createOrUpdateUniversityEfficiencyChart(data.universities);
        
        // Populate university table
        populateUniversityTable(data.universities);
      }
      
      showLoading(false);
    })
    .catch(error => {
      console.error('Error fetching university comparison data:', error);
      
      // Create empty charts
      createOrUpdateUniversityWeightChart([]);
      createOrUpdateUniversityEfficiencyChart([]);
      
      // Empty table
      populateUniversityTable([]);
      
      showLoading(false);
      showError('Failed to load university comparison data. Please try refreshing.');
    });
}

// Chart creation and update functions
function createOrUpdateCollectionTrendsChart(data) {
  const ctx = document.getElementById('collection-trends-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.collectionTrends) {
    charts.collectionTrends.destroy();
  }
  
  // Create new chart
  charts.collectionTrends = new Chart(ctx, {
    type: 'line',
    data: data,
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

// Create or update community chart
function createOrUpdateCommunityChart(data) {
  const ctx = document.getElementById('community-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.community) {
    charts.community.destroy();
  }
  
  // Create new chart
  charts.community = new Chart(ctx, {
    type: 'doughnut',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 12,
            padding: 15
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.dataset.data.reduce((sum, val) => sum + val, 0);
              const percentage = Math.round((value / total) * 100);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

// Create or update component distribution chart
function createOrUpdateComponentDistributionChart(data) {
  const ctx = document.getElementById('verification-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.verification) {
    charts.verification.destroy();
  }
  
  // Create new chart
  charts.verification = new Chart(ctx, {
    type: 'pie',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            boxWidth: 12
          }
        },
        title: {
          display: true,
          text: 'Component Distribution',
          font: {
            size: 14
          }
        }
      }
    }
  });
}
function createOrUpdateStatusChart(data) {
  const ctx = document.getElementById('status-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.status) {
    charts.status.destroy();
  }
  
  // Create new chart
  charts.status = new Chart(ctx, {
    type: 'pie',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
        }
      }
    }
  });
}

function createOrUpdateVerificationChart(data) {
  const ctx = document.getElementById('verification-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.verification) {
    charts.verification.destroy();
  }
  
  // Create new chart
  charts.verification = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
}

// Create or update role engagement chart
function createOrUpdateRoleEngagementChart(data) {
  const ctx = document.getElementById('user-role-engagement-chart').getContext('2d');
  
  // Prepare data for chart
  const chartData = {
    labels: data.labels || [],
    datasets: data.datasets || []
  };
  
  // Destroy existing chart if it exists
  if (charts.roleEngagement) {
    charts.roleEngagement.destroy();
  }
  
  // Create new chart
  charts.roleEngagement = new Chart(ctx, {
    type: 'bar',
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Activity by User Role',
          font: {
            size: 14
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Activities'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Role'
          }
        }
      }
    }
  });
}



function createOrUpdateWasteByTypeChart(wasteData) {
  const ctx = document.getElementById('waste-by-type-chart').getContext('2d');
  
  // Extract data - handle possible field name changes
  const labels = wasteData.map(item => item.product_type || item.product_name || item.waste_type);
  const data = wasteData.map(item => item.total_weight || item.total_count || 0);
  
  // Define colors
  const colors = ['#1b5e20', '#2e7d32', '#388e3c', '#43a047', '#4caf50', '#66bb6a', '#81c784', '#a5d6a7'];
  
  // Destroy existing chart if it exists
  if (charts.wasteByType) {
    charts.wasteByType.destroy();
  }
  
  // Create new chart
  charts.wasteByType = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [{
        data: data.length ? data : [100],
        backgroundColor: data.length ? colors.slice(0, data.length) : ['#cccccc'],
        borderWidth: 0
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
   // Generate and display insights
   generateWasteInsights(wasteData);
}

function createOrUpdateMonthlyTrendChart(trendData) {
  const ctx = document.getElementById('monthly-trend-chart').getContext('2d');
  
  // Extract data
  const labels = trendData.map(item => item.month);
  const data = trendData.map(item => item.total_weight);
  
  // Destroy existing chart if it exists
  if (charts.monthlyTrend) {
    charts.monthlyTrend.destroy();
  }
  
  // Create new chart
  charts.monthlyTrend = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [{
        label: 'Total Weight (kg)',
        data: data.length ? data : [0],
        borderColor: '#1b5e20',
        backgroundColor: 'rgba(27, 94, 32, 0.1)',
        fill: true,
        tension: 0.3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
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
// Add this function to dashboard.js
function updateForecastDetails(forecastData) {
  const forecastDetailsElement = document.getElementById('forecast-details');
  
  if (!forecastData || !forecastData.length) {
    forecastDetailsElement.innerHTML = '<p class="text-gray-500 text-center mt-4">No forecast data available</p>';
    return;
  }
  
  // Calculate total predicted weight
  const totalPredictedWeight = forecastData.reduce((sum, item) => sum + item.predicted_weight, 0);
  
  // Calculate percentage change from most recent data
  let percentageChange = 0;
  
  // Get current chart data to compare with predictions
  if (charts.monthlyTrend) {
    const currentData = charts.monthlyTrend.data.datasets[0].data;
    if (currentData && currentData.length > 0) {
      // Calculate average of last 3 months if available, or use last month
      const recentMonthsCount = Math.min(3, currentData.length);
      const recentMonths = currentData.slice(-recentMonthsCount);
      const avgRecentWeight = recentMonths.reduce((sum, val) => sum + val, 0) / recentMonthsCount;
      
      // Calculate monthly average of predicted weight
      const avgPredictedWeight = totalPredictedWeight / forecastData.length;
      
      // Calculate percentage change
      percentageChange = avgRecentWeight > 0 ? 
        ((avgPredictedWeight - avgRecentWeight) / avgRecentWeight * 100) : 0;
    }
  }
  
  // Create the forecast details HTML
  let detailsHTML = `
    <div class="mt-4 p-4 bg-gray-50 rounded-lg">
      <h4 class="font-medium text-gray-700 mb-3">Forecast Details</h4>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-sm text-gray-600">Total Predicted Weight</p>
          <p class="text-xl font-bold text-green-800">${formatNumber(totalPredictedWeight)} kg</p>
        </div>
        <div>
          <p class="text-sm text-gray-600">Projected Change</p>
          <p class="text-xl font-bold ${percentageChange >= 0 ? 'text-green-800' : 'text-red-600'}">
            ${percentageChange >= 0 ? '+' : ''}${percentageChange.toFixed(1)}%
          </p>
        </div>
      </div>
      <div class="mt-4">
        <h4 class="font-medium text-gray-700 mb-2">Monthly Breakdown</h4>
        <div class="flex flex-col">
  `;
  
  // Add each month's forecast
  forecastData.forEach(month => {
    detailsHTML += `
      <div class="flex justify-between items-center py-2 border-b border-gray-200">
        <span class="text-gray-700">${month.month}</span>
        <span class="font-medium">${formatNumber(month.predicted_weight)} kg</span>
      </div>
    `;
  });
  
  detailsHTML += `
        </div>
      </div>
    </div>
  `;
  
  forecastDetailsElement.innerHTML = detailsHTML;
}


function createOrUpdateForecastChart(forecastData) {
  const ctx = document.getElementById('forecast-chart').getContext('2d');
  
  // Extract data
  const labels = forecastData.map(item => item.month);
  const data = forecastData.map(item => item.predicted_weight);
  
  // Destroy existing chart if it exists
  if (charts.forecast) {
    charts.forecast.destroy();
  }
  
  // Create new chart
  charts.forecast = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [{
        label: 'Predicted Weight (kg)',
        data: data.length ? data : [0],
        backgroundColor: 'rgba(2, 119, 189, 0.7)',
        borderColor: 'rgb(2, 119, 189)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
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
  updateForecastDetails(forecastData);
}

function createOrUpdateUniversityWeightChart(universities) {
  const ctx = document.getElementById('university-weight-chart').getContext('2d');
  
  // Extract data
  const labels = universities.map(uni => uni.name);
  const data = universities.map(uni => uni.total_weight);
  
  // Define colors
  const colors = ['#1b5e20', '#2e7d32', '#388e3c', '#43a047', '#4caf50', '#66bb6a', '#81c784', '#a5d6a7'];
  
  // Destroy existing chart if it exists
  if (charts.universityWeight) {
    charts.universityWeight.destroy();
  }
  
  // Create new chart
  charts.universityWeight = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [{
        label: 'Total Weight (kg)',
        data: data.length ? data : [0],
        backgroundColor: data.length ? colors.slice(0, data.length) : ['#cccccc']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
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

function createOrUpdateUniversityEfficiencyChart(universities) {
  const ctx = document.getElementById('university-efficiency-chart').getContext('2d');
  
  // Extract data
  const labels = universities.map(uni => uni.name);
  const data = universities.map(uni => uni.weight_per_user);
  
  // Define colors
  const colors = ['#0277bd', '#0288d1', '#039be5', '#03a9f4', '#29b6f6', '#4fc3f7', '#81d4fa', '#b3e5fc'];
  
  // Destroy existing chart if it exists
  if (charts.universityEfficiency) {
    charts.universityEfficiency.destroy();
  }
  
  // Create new chart
  charts.universityEfficiency = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [{
        label: 'Weight per User (kg)',
        data: data.length ? data : [0],
        backgroundColor: data.length ? colors.slice(0, data.length) : ['#cccccc']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Weight per User (kg)'
          }
        }
      }
    }
  });
}
// New function to generate waste insights
function generateWasteInsights(wasteData) {
  // Get the insights container
  const insightsContainer = document.getElementById('waste-insights-container');
  if (!insightsContainer) return;
  
  // Clear previous insights
  insightsContainer.innerHTML = '';
  
  // Handle empty data
  if (!wasteData || wasteData.length === 0) {
    insightsContainer.innerHTML = '<p class="text-gray-500">No waste collection data available for analysis.</p>';
    return;
  }
  
  // Calculate total - handle field name changes
  const totalWeight = wasteData.reduce((sum, item) => sum + (item.total_weight || item.total_count || 0), 0);
  
  // Sort waste types by weight (descending)
  const sortedWaste = [...wasteData].sort((a, b) => 
    (b.total_weight || b.total_count || 0) - (a.total_weight || a.total_count || 0)
  );
  
  // Generate insights
  let insights = '';
  
  // Top waste type
  if (sortedWaste.length > 0) {
    const topType = sortedWaste[0];
    const topTypeName = topType.product_type || topType.product_name || topType.waste_type;
    const topTypeWeight = topType.total_weight || topType.total_count || 0;
    const topPercentage = ((topTypeWeight / totalWeight) * 100).toFixed(1);
    
    insights += `<p class="mb-2"><span class="font-semibold">${topTypeName}</span> constitutes the largest portion of e-waste at <span class="font-semibold text-green-800">${topPercentage}%</span> (${formatNumber(topTypeWeight)} units) of total collected waste.</p>`;
  }
  
  // Distribution insight
  if (sortedWaste.length > 2) {
    // Top 3 types combined percentage
    const top3Weight = sortedWaste.slice(0, 3).reduce((sum, item) => 
      sum + (item.total_weight || item.total_count || 0), 0
    );
    const top3Percentage = ((top3Weight / totalWeight) * 100).toFixed(1);
    
    insights += `<p class="mb-2">The top 3 e-waste categories represent <span class="font-semibold text-green-800">${top3Percentage}%</span> of all collected materials.</p>`;
  }
  
  // Diversity insight
  if (sortedWaste.length >= 4) {
    insights += `<p class="mb-2">Collection efforts have captured <span class="font-semibold">${sortedWaste.length}</span> distinct types of electronic waste, showing a diverse recycling program.</p>`;
  }
  
  // Opportunities for improvement
  if (sortedWaste.length >= 2) {
    const leastCollected = sortedWaste[sortedWaste.length - 1];
    const leastTypeName = leastCollected.product_type || leastCollected.product_name || leastCollected.waste_type;
    const leastTypeWeight = leastCollected.total_weight || leastCollected.total_count || 0;
    const leastPercentage = ((leastTypeWeight / totalWeight) * 100).toFixed(1);
    
    insights += `<p class="mb-2"><span class="font-semibold">${leastTypeName}</span> has the lowest collection rate at just <span class="font-semibold">${leastPercentage}%</span>, indicating a potential opportunity for targeted collection campaigns.</p>`;
  }
  
  // Add all insights to the container
  insightsContainer.innerHTML = `
    <div class="bg-gray-50 p-4 rounded-lg mt-4">
      <h4 class="font-medium text-gray-700 mb-3">Waste Collection Insights</h4>
      ${insights}
      <p class="text-sm text-gray-500 mt-3">Total e-waste collected: ${formatNumber(totalWeight)} units</p>
    </div>
  `;
}

function populateUniversityTable(universities) {
  const tbody = document.getElementById('university-table-body');
  tbody.innerHTML = '';
  
  if (!universities.length) {
    const row = document.createElement('tr');
    row.innerHTML = '<td colspan="6" class="px-6 py-4 text-center text-gray-500">No data available</td>';
    tbody.appendChild(row);
    return;
  }
  
  universities.forEach(uni => {
    const row = document.createElement('tr');
    
    // Handle field name changes
    const totalWeight = uni.total_weight || uni.total_appliances || 0;
    const weightPerUser = uni.weight_per_user || uni.appliances_per_user || 0;
    const weightChange = uni.weight_change_percent || uni.appliance_change_percent || 0;
    
    // Determine CSS classes for change values
    const weightChangeClass = weightChange >= 0 ? 'text-green-600' : 'text-red-600';
    const userChangeClass = uni.user_change_percent >= 0 ? 'text-green-600' : 'text-red-600';
    
    // Format change values with + or - prefix
    const weightChangeFormatted = `${weightChange >= 0 ? '+' : ''}${weightChange}%`;
    const userChangeFormatted = `${uni.user_change_percent >= 0 ? '+' : ''}${uni.user_change_percent}%`;
    
    row.innerHTML = `
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${uni.name}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${formatNumber(totalWeight)}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${formatNumber(uni.active_users)}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${weightPerUser.toFixed(2)}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm ${weightChangeClass} font-medium">${weightChangeFormatted}</td>
      <td class="px-6 py-4 whitespace-nowrap text-sm ${userChangeClass} font-medium">${userChangeFormatted}</td>
    `;
    
    tbody.appendChild(row);
  });
}

// UI Helper Functions
function showLoading(isLoading) {
  // Could implement a loading indicator here
  if (isLoading) {
    document.querySelector('body').style.cursor = 'wait';
  } else {
    document.querySelector('body').style.cursor = 'default';
  }
}

function showError(message) {
  // Create error toast notification
  const toast = document.createElement('div');
  toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50';
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.5s ease-out';
    
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 500);
  }, 5000);
}

// Add CSS for chart containers
document.addEventListener('DOMContentLoaded', function() {
  const style = document.createElement('style');
  style.textContent = `
    .chart-container {
      position: relative;
      height: 300px;
      width: 100%;
    }
    
    .tab-content.hidden {
      display: none;
    }
    
    .analytics-section {
      margin-bottom: 2rem;
    }
  `;
  document.head.appendChild(style);
});

// Fetch component processing data
function fetchComponentProcessingData() {
  showLoading(true);
  
  // Get selected time period
  const timePeriod = document.getElementById('component-time-period')?.value || 'month';
  
  fetch(`${DASHBOARD_API}/component-processing-timeline/?period=${timePeriod}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Update metrics in cards
      document.getElementById('total-components-metric').textContent = formatNumber(data.summary.total_components);
      document.getElementById('processed-components-metric').textContent = formatNumber(data.summary.processed_components);
      document.getElementById('recycled-components-metric').textContent = formatNumber(data.summary.recycled_components);
      document.getElementById('processing-rate-metric').textContent = `${data.summary.processing_rate}%`;
      
      // Create or update charts
      createOrUpdateComponentTimelineChart(data.timeline_data);
      createOrUpdateComponentTypesChart(data.component_types);
      
      // Populate recent components table
      populateComponentsTable(data.recent_components);
      
      showLoading(false);
    })
    .catch(error => {
      console.error('Error fetching component processing data:', error);
      
      // Clear metrics
      document.getElementById('total-components-metric').textContent = '0';
      document.getElementById('processed-components-metric').textContent = '0';
      document.getElementById('recycled-components-metric').textContent = '0';
      document.getElementById('processing-rate-metric').textContent = '0%';
      
      // Create empty charts
      createOrUpdateComponentTimelineChart([]);
      createOrUpdateComponentTypesChart([]);
      
      // Empty table
      populateComponentsTable([]);
      
      showLoading(false);
      showError('Failed to load component processing data. Please try refreshing.');
    });
}

// Create/update timeline chart for component processing
function createOrUpdateComponentTimelineChart(timelineData) {
  const ctx = document.getElementById('component-timeline-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.componentTimeline) {
    charts.componentTimeline.destroy();
  }
  
  // Extract data points
  const labels = timelineData.map(item => item.date);
  const totalData = timelineData.map(item => item.total);
  const processedData = timelineData.map(item => item.processed);
  const recycledData = timelineData.map(item => item.recycled);
  
  // Create new chart
  charts.componentTimeline = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [
        {
          label: 'Total Components',
          data: totalData.length ? totalData : [0],
          borderColor: '#1b5e20',
          backgroundColor: 'rgba(27, 94, 32, 0.1)',
          tension: 0.3,
          fill: false
        },
        {
          label: 'Processed',
          data: processedData.length ? processedData : [0],
          borderColor: '#0277bd',
          backgroundColor: 'rgba(2, 119, 189, 0.1)',
          tension: 0.3,
          fill: false
        },
        {
          label: 'Recycled',
          data: recycledData.length ? recycledData : [0],
          borderColor: '#ff9800',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          tension: 0.3,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Count'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Date'
          }
        }
      }
    }
  });
}

// Create/update component types chart
function createOrUpdateComponentTypesChart(componentTypes) {
  const ctx = document.getElementById('component-types-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.componentTypes) {
    charts.componentTypes.destroy();
  }
  
  // Extract data points
  const labels = componentTypes.map(type => type.component_name);
  const processedData = componentTypes.map(type => type.processed);
  const recycledData = componentTypes.map(type => type.recycled);
  const pendingData = componentTypes.map(type => type.total - type.processed);
  
  // Create new chart
  charts.componentTypes = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [
        {
          label: 'Recycled',
          data: recycledData.length ? recycledData : [0],
          backgroundColor: 'rgba(46, 125, 50, 0.8)',
        },
        {
          label: 'Processed (Not Recycled)',
          data: processedData.length ? processedData.map((val, idx) => val - recycledData[idx]) : [0],
          backgroundColor: 'rgba(2, 119, 189, 0.8)',
        },
        {
          label: 'Pending',
          data: pendingData.length ? pendingData : [0],
          backgroundColor: 'rgba(255, 152, 0, 0.8)',
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          stacked: true,
          title: {
            display: true,
            text: 'Count'
          }
        },
        x: {
          stacked: true,
          title: {
            display: true,
            text: 'Component Type'
          }
        }
      }
    }
  });
}

function populateComponentsTable(components) {
  const tbody = document.getElementById('components-table-body');
  tbody.innerHTML = '';
  
  if (!components || !components.length) {
    const row = document.createElement('tr');
    row.innerHTML = '<td colspan="4" class="px-3 py-2 text-center text-gray-500">No component data available</td>';
    tbody.appendChild(row);
    return;
  }
  
  components.forEach(comp => {
    const row = document.createElement('tr');
    
    // Determine status class
    let statusText, statusClass;
    if (comp.is_recycled) {
      statusText = 'Recycled';
      statusClass = 'bg-green-100 text-green-800';
    } else if (comp.is_processed) {
      statusText = 'Processed';
      statusClass = 'bg-blue-100 text-blue-800';
    } else {
      statusText = 'Pending';
      statusClass = 'bg-yellow-100 text-yellow-800';
    }
    
    row.innerHTML = `
      <td class="px-3 py-2 text-sm text-gray-900">${comp.component_name}</td>
      <td class="px-3 py-2 text-sm text-gray-700">${comp.appliance || 'N/A'}</td>
      <td class="px-3 py-2">
        <span class="px-2 py-1 text-xs rounded-full ${statusClass}">${statusText}</span>
      </td>
      <td class="px-3 py-2 text-sm text-gray-900">${comp.processing_time || '-'} ${comp.processing_time ? 'days' : ''}</td>
    `;
    
    tbody.appendChild(row);
  });
}

// New function to fetch Campus Expert Activity
function fetchCampusExpertData() {
  const campusFilter = document.getElementById('campus-filter').value;
  const timePeriod = document.getElementById('time-period').value;
  
  return fetch(`${DASHBOARD_API}/campus-experts/?period=${timePeriod}&filter=${campusFilter}`)
    .then(response => {
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      return response.json();
    })
    .then(data => {
      // Create or update chart
      createOrUpdateCampusExpertChart(data);
      
      // Update the metrics
      updateCampusExpertMetrics(data);
    })
    .catch(error => {
      console.error('Error fetching campus expert data:', error);
      
      // Create chart with empty data
      const emptyData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
          label: 'No Data Available',
          data: Array(12).fill(0),
          backgroundColor: 'rgba(204, 204, 204, 0.5)'
        }]
      };
      
      createOrUpdateCampusExpertChart(emptyData);
      
      // Set default values for metrics
      setDefaultCampusExpertMetrics();
    });
}

// Create or update campus expert chart
function createOrUpdateCampusExpertChart(data) {
  const ctx = document.getElementById('campus-expert-chart').getContext('2d');
  
  // Destroy existing chart if it exists
  if (charts.campusExpert) {
    charts.campusExpert.destroy();
  }
  
  // Create new chart
  charts.campusExpert = new Chart(ctx, {
    type: 'bar',
    data: data,
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
            text: 'Activities'
          }
        }
      }
    }
  });
}
// Update campus expert metrics
function updateCampusExpertMetrics(data) {
  // Check if we have summary in the response
  if (data.summary) {
    document.getElementById('active-experts').textContent = 
      formatNumber(data.summary.active_experts);
    document.getElementById('expert-publications').textContent = 
      formatNumber(data.summary.publications);
    document.getElementById('expert-events').textContent = 
      formatNumber(data.summary.events);
  } else {
    // Set default values if summary is not available
    setDefaultCampusExpertMetrics();
  }
}

// Set default values for campus expert metrics
function setDefaultCampusExpertMetrics() {
  document.getElementById('active-experts').textContent = '0';
  document.getElementById('expert-publications').textContent = '0';
  document.getElementById('expert-events').textContent = '0';
}

// Create or update the processing status chart
function createOrUpdateProcessingChart(componentTypes) {
  const ctx = document.getElementById('component-status-chart').getContext('2d');
  
  // Process data for chart
  const labels = componentTypes.map(type => type.component_name);
  const totalData = componentTypes.map(type => type.total);
  const processedData = componentTypes.map(type => type.processed);
  const recycledData = componentTypes.map(type => type.recycled);
  
  // Destroy existing chart if it exists
  if (charts.componentStatus) {
    charts.componentStatus.destroy();
  }
  
  // Create new chart
  charts.componentStatus = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['No Data'],
      datasets: [
        {
          label: 'Total',
          data: totalData.length ? totalData : [0],
          backgroundColor: 'rgba(27, 94, 32, 0.6)'
        },
        {
          label: 'Processed',
          data: processedData.length ? processedData : [0],
          backgroundColor: 'rgba(2, 119, 189, 0.6)'
        },
        {
          label: 'Recycled',
          data: recycledData.length ? recycledData : [0],
          backgroundColor: 'rgba(255, 143, 0, 0.6)'
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

// Populate the components tables
function populateComponentsTable(components) {
  // For the small summary table
  const summaryTbody = document.getElementById('components-table-body');
  if (summaryTbody) {
    summaryTbody.innerHTML = '';
    
    if (!components.length) {
      const row = document.createElement('tr');
      row.innerHTML = '<td colspan="3" class="px-3 py-2 text-center text-gray-500">No component data available</td>';
      summaryTbody.appendChild(row);
    } else {
      // Only show the first 5 components in the summary table
      components.slice(0, 5).forEach(comp => {
        const row = document.createElement('tr');
        
        // Determine status 
        const status = comp.is_processed ? 
          (comp.is_recycled ? 'Recycled' : 'Processing') : 
          'Pending';
        
        const statusClass = comp.is_recycled ? 
          'bg-green-100 text-green-800' : 
          (comp.is_processed ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800');
        
        row.innerHTML = `
          <td class="px-3 py-2 text-sm text-gray-900">${comp.component_name}</td>
          <td class="px-3 py-2">
            <span class="px-2 py-1 text-xs rounded-full ${statusClass}">${status}</span>
          </td>
          <td class="px-3 py-2 text-sm text-gray-900">${comp.processing_time || '-'} ${comp.processing_time ? 'days' : ''}</td>
        `;
        
        summaryTbody.appendChild(row);
      });
    }
  }
  
  // For the full table
  const fullTbody = document.getElementById('full-components-table-body');
  if (fullTbody) {
    fullTbody.innerHTML = '';
    
    if (!components.length) {
      const row = document.createElement('tr');
      row.innerHTML = '<td colspan="6" class="px-4 py-3 text-center text-gray-500">No component data available</td>';
      fullTbody.appendChild(row);
    } else {
      components.forEach(comp => {
        const row = document.createElement('tr');
        
        // Determine status classes
        const processStatus = comp.is_processed ? 'Processed' : 'Pending';
        const recycleStatus = comp.is_recycled ? 'Recycled' : (comp.is_processed ? 'Pending' : 'Waiting');
        
        const processClass = comp.is_processed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
        const recycleClass = comp.is_recycled ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800';
        
        row.innerHTML = `
          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">${comp.component_name}</td>
          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">${comp.appliance}</td>
          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">${comp.serial_number}</td>
          <td class="px-4 py-3 whitespace-nowrap">
            <span class="px-2 py-1 text-xs rounded-full ${processClass}">${processStatus}</span>
          </td>
          <td class="px-4 py-3 whitespace-nowrap">
            <span class="px-2 py-1 text-xs rounded-full ${recycleClass}">${recycleStatus}</span>
          </td>
          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">${comp.processing_time || '-'} ${comp.processing_time ? 'days' : ''}</td>
        `;
        
        fullTbody.appendChild(row);
      });
    }
  }
}