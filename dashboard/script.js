// Chart instances to update them later
let chartInstances = {};

// Theme colors
const colors = {
    cyan: '#00e5ff',
    blue: '#3b82f6',
    red: '#ef4444',
    green: '#10b981',
    orange: '#f59e0b',
    purple: '#8b5cf6',
    dark: 'rgba(17, 24, 39, 0.7)',
    white: '#f3f4f6'
};

// Initialize Date/Time
function updateClock() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute:'2-digit', second:'2-digit' };
    document.getElementById('datetime-display').innerText = now.toLocaleDateString('en-IN', options);
}
setInterval(updateClock, 1000);
updateClock();

// --- DATA FETCHING & UI UPDATES ---

function getFilterQueryString() {
    const filterDate = document.getElementById('filter-date');
    if(!filterDate) return "";
    const val = filterDate.value;
    if(val === 'all') return "";
    
    let params = new URLSearchParams();
    if(val === '7') params.append('days', 7);
    else if(val === '30') params.append('days', 30);
    else if(val === 'custom') {
        const start = document.getElementById('filter-start-date').value;
        const end = document.getElementById('filter-end-date').value;
        if(start) params.append('start_date', start);
        if(end) params.append('end_date', end);
    }
    const q = params.toString();
    return q ? '?' + q : '';
}

async function fetchAPI(endpoint) {
    try {
        const query = getFilterQueryString();
        const separator = endpoint.includes('?') ? (query ? '&' + query.substring(1) : '') : query;
        const res = await fetch(`/api/dashboard/${endpoint}${separator}`);
        if(!res.ok) throw new Error("API Error");
        return await res.json();
    } catch (e) {
        console.error("Error fetching", endpoint, e);
        return null;
    }
}

async function updateKPIs() {
    const data = await fetchAPI('kpi');
    if (!data) return;
    
    document.getElementById('kpi-collected').innerText = data.TotalArticles;
    document.getElementById('kpi-processed').innerText = data.ProcessedArticles;
    document.getElementById('kpi-events').innerText = data.TotalCrimeEvents;
    document.getElementById('kpi-active-cases').innerText = data.ActiveCases;
    document.getElementById('kpi-solved').innerText = data.SolvedCases;
    
    document.getElementById('kpi-arrested').innerText = data.ArrestedCases;
    document.getElementById('kpi-investigation').innerText = data.UnderInvestigation;
    document.getElementById('kpi-police-mentioned').innerText = data.PoliceMentioned;
    
    document.getElementById('kpi-avg-police-sent').innerText = data.AvgPoliceSentiment;
    const pIcon = document.getElementById('icon-sentiment-police');
    pIcon.className = 'kpi-icon ' + (data.AvgPoliceSentiment > 0 ? 'green' : data.AvgPoliceSentiment < 0 ? 'red' : 'yellow');
    
    document.getElementById('kpi-avg-officer-sent').innerText = data.AvgOfficerSentiment;
    const oIcon = document.getElementById('icon-sentiment-officer');
    oIcon.className = 'kpi-icon ' + (data.AvgOfficerSentiment > 0 ? 'green' : data.AvgOfficerSentiment < 0 ? 'red' : 'yellow');
}

async function updateCharts() {
    const data = await fetchAPI('crime-analytics');
    if (!data) return;

    // Monthly Trend Line Chart
    const ctxMonthly = document.getElementById('chart-monthly-trend').getContext('2d');
    const labelsMonth = data.monthly_trend.map(d => d.month);
    const dataMonth = data.monthly_trend.map(d => d.count);
    
    if(chartInstances.monthly) chartInstances.monthly.destroy();
    chartInstances.monthly = new Chart(ctxMonthly, {
        type: 'line',
        data: {
            labels: labelsMonth,
            datasets: [{
                label: 'Crime Reports',
                data: dataMonth,
                borderColor: colors.cyan,
                backgroundColor: 'rgba(0, 229, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: colors.white } },
                x: { grid: { display: false }, ticks: { color: colors.white } }
            }
        }
    });

    // Category Pie Chart
    const ctxPie = document.getElementById('chart-category-pie').getContext('2d');
    const labelsCat = Object.keys(data.category_counts);
    const dataCat = Object.values(data.category_counts);
    
    if(chartInstances.pie) chartInstances.pie.destroy();
    chartInstances.pie = new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: labelsCat,
            datasets: [{
                data: dataCat,
                backgroundColor: [colors.cyan, colors.blue, colors.red, colors.orange, colors.purple, colors.green, '#eab308', '#14b8a6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            cutout: '70%',
            plugins: {
                legend: { position: 'right', labels: { color: colors.white, font: { size: 10 } } }
            }
        }
    });

    // Weekly Bar Chart
    const ctxWeek = document.getElementById('chart-weekly-dist').getContext('2d');
    const labelsWeek = Object.keys(data.weekly_distribution);
    const dataWeek = Object.values(data.weekly_distribution);

    if(chartInstances.week) chartInstances.week.destroy();
    chartInstances.week = new Chart(ctxWeek, {
        type: 'bar',
        data: {
            labels: labelsWeek,
            datasets: [{
                label: 'Reports',
                data: dataWeek,
                backgroundColor: colors.blue,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: colors.white } },
                x: { grid: { display: false }, ticks: { color: colors.white } }
            }
        }
    });
}

// Map Initialization
let map;
let markers = [];
function initMap() {
    map = L.map('district-map').setView([20.1245, 85.1054], 10); // Nayagarh coordinates
    
    // Dark matter tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    }).addTo(map);
}

async function updateMap() {
    if(!map) initMap();
    const data = await fetchAPI('map-data');
    if(!data) return;

    // Clear old markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    // Dummy coords for demonstration (Nayagarh district blocks)
    const coords = {
        "Nayagarh": [20.1245, 85.1054],
        "Ranpur": [20.0631, 85.3444],
        "Daspalla": [20.3400, 84.8500],
        "Odagaon": [19.9822, 85.0069],
        "Khandapada": [20.2600, 85.1700],
        "Nuagaon": [20.2100, 85.0200],
        "Gania": [20.4000, 85.0500],
        "Sarankul": [20.0600, 85.0700],
        "Bhapur": [20.2700, 85.2900]
    };

    data.forEach(loc => {
        const c = coords[loc.location];
        if(!c) return;
        
        const radius = Math.max(loc.count * 1.5, 5); // size by count
        
        const circle = L.circleMarker(c, {
            radius: radius,
            fillColor: colors.cyan,
            color: colors.cyan,
            weight: 1,
            opacity: 0.8,
            fillOpacity: 0.4
        }).addTo(map);
        
        circle.bindPopup(`
            <div style="color:#0a0f1d;">
                <h4 style="margin:0;padding:0;">${loc.location}</h4>
                <p style="margin:4px 0;font-size:12px;"><b>Crime Count:</b> ${loc.count}</p>
                <p style="margin:4px 0;font-size:12px;"><b>Types:</b> ${loc.crime_types}</p>
                <p style="margin:4px 0;font-size:12px;"><b>Sentiment:</b> ${loc.sentiment_trend}</p>
            </div>
        `);
        
        markers.push(circle);
    });
}

async function updateNewsEvents() {
    const data = await fetchAPI('news-events');
    if(!data) return;
    
    const container = document.getElementById('events-list-container');
    container.innerHTML = '';
    
    data.forEach(evt => {
        container.innerHTML += `
            <div class="list-item">
                <div class="list-item-content">
                    <h4>${evt.title}</h4>
                    <p>Event ID: ${evt.event_id} | ${evt.timeline}</p>
                    <div class="tags">
                        ${evt.publishers.map(p => `<span class="tag">${p}</span>`).join('')}
                        <span class="tag" style="background:var(--accent-blue);">Similarity: ${evt.similarity}</span>
                    </div>
                </div>
            </div>
        `;
    });
}

async function updateLatestNews() {
    const data = await fetchAPI('latest-news');
    if(!data) return;
    
    const container = document.getElementById('news-feed-container');
    container.innerHTML = '';
    
    data.forEach(news => {
        const sentClass = news.sentiment.toLowerCase() === 'positive' ? 'positive' : (news.sentiment.toLowerCase() === 'negative' ? 'negative' : '');
        container.innerHTML += `
            <div class="list-item">
                <div class="list-item-content">
                    <h4>${news.title}</h4>
                    <p>${news.publisher} | ${news.time}</p>
                    <div class="tags">
                        <span class="tag cyber">${news.category || 'Unknown'}</span>
                        <span class="tag"><i class="fas fa-map-marker-alt"></i> ${news.location || 'N/A'}</span>
                        <span class="tag sentiment ${sentClass}">Sentiment: ${news.sentiment}</span>
                    </div>
                </div>
            </div>
        `;
    });
}

async function updateOfficerTable() {
    const data = await fetchAPI('officer-analytics');
    if(!data) return;
    
    const tbody = document.querySelector('#table-officers tbody');
    tbody.innerHTML = '';
    
    data.forEach(off => {
        const total = off.mentions;
        const pPct = (off.positive / total) * 100;
        const nPct = (off.neutral / total) * 100;
        const negPct = (off.negative / total) * 100;
        
        const trendIcon = off.trend === 'Up' ? '<i class="fas fa-arrow-up" style="color:var(--accent-green)"></i>' : 
                         (off.trend === 'Down' ? '<i class="fas fa-arrow-down" style="color:var(--accent-red)"></i>' : '-');
                         
        tbody.innerHTML += `
            <tr>
                <td><strong>${off.name}</strong></td>
                <td>${off.designation}</td>
                <td>${off.mentions}</td>
                <td>
                    <div style="font-size:10px;">Pos:${off.positive} Neu:${off.neutral} Neg:${off.negative}</div>
                    <div class="progress-bar-container">
                        <div class="pb-pos" style="width:${pPct}%"></div>
                        <div class="pb-neu" style="width:${nPct}%"></div>
                        <div class="pb-neg" style="width:${negPct}%"></div>
                    </div>
                </td>
                <td>${trendIcon} ${off.trend}</td>
            </tr>
        `;
    });
}

async function updateSentimentCharts() {
    // Police Sentiment
    const sentData = await fetchAPI('police-sentiment');
    if(sentData) {
        const ctxPol = document.getElementById('chart-police-sentiment').getContext('2d');
        if(chartInstances.polSent) chartInstances.polSent.destroy();
        chartInstances.polSent = new Chart(ctxPol, {
            type: 'pie',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    data: [sentData.positive_pct, sentData.neutral_pct, sentData.negative_pct],
                    backgroundColor: [colors.green, colors.white, colors.red],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: colors.white } } }
            }
        });
    }

    // Case Status
    const caseData = await fetchAPI('case-status');
    if(caseData) {
        const ctxCase = document.getElementById('chart-case-status').getContext('2d');
        if(chartInstances.caseStat) chartInstances.caseStat.destroy();
        
        const cLabels = Object.keys(caseData);
        const cValues = Object.values(caseData);
        
        chartInstances.caseStat = new Chart(ctxCase, {
            type: 'doughnut',
            data: {
                labels: cLabels,
                datasets: [{
                    data: cValues,
                    backgroundColor: [colors.green, colors.orange, colors.cyan, colors.blue, colors.red],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                cutout: '60%',
                plugins: { legend: { position: 'bottom', labels: { color: colors.white, font:{size:10} } } }
            }
        });
    }
}

// Master Refresh Function
async function refreshDashboard() {
    updateKPIs();
    updateCharts();
    updateMap();
    updateNewsEvents();
    updateLatestNews();
    updateOfficerTable();
    updateSentimentCharts();
}

// --- TABULAR VIEWS LOGIC ---
const paginationState = {
    'view-news-collection': { page: 1, limit: 25 },
    'view-crime-analytics': { page: 1, limit: 25 },
    'view-news-events': { page: 1, limit: 25 },
    'view-sentiment-analysis': { page: 1, limit: 25 },
    'view-officer-analytics': { page: 1, limit: 25 }
};

async function loadTableData(endpoint, tableId, rowMapper, viewId) {
    const state = paginationState[viewId];
    const paginatedEndpoint = `${endpoint}?page=${state.page}&limit=${state.limit}`;
    
    const result = await fetchAPI(paginatedEndpoint);
    if(!result) return;
    
    // Handle both old (flat array) and new (paginated object) backend responses
    // in case the FastAPI server hasn't been restarted yet.
    const actualData = result.data ? result.data : (Array.isArray(result) ? result : []);
    const totalItems = result.total !== undefined ? result.total : actualData.length;
    const currentPage = result.page || state.page;
    const currentLimit = result.limit || state.limit;
    
    const tbody = document.querySelector(`#${tableId} tbody`);
    if(tbody) {
        tbody.innerHTML = '';
        actualData.forEach(item => {
            tbody.innerHTML += rowMapper(item);
        });
    }

    // Update Pagination UI
    const totalPages = Math.ceil(totalItems / currentLimit) || 1;
    const paginationControls = document.getElementById(`pagination-${viewId}`);
    
    if (paginationControls) {
        paginationControls.querySelector('.current-page').innerText = currentPage;
        paginationControls.querySelector('.total-pages').innerText = totalPages;
        
        const prevBtn = paginationControls.querySelector('.prev-page');
        const nextBtn = paginationControls.querySelector('.next-page');
        
        prevBtn.disabled = currentPage <= 1;
        nextBtn.disabled = currentPage >= totalPages;
        
        // Remove old event listeners
        const newPrev = prevBtn.cloneNode(true);
        const newNext = nextBtn.cloneNode(true);
        prevBtn.replaceWith(newPrev);
        nextBtn.replaceWith(newNext);
        
        newPrev.addEventListener('click', () => {
            if (state.page > 1) {
                state.page--;
                viewsConfig[viewId]();
            }
        });
        
        newNext.addEventListener('click', () => {
            if (state.page < totalPages) {
                state.page++;
                viewsConfig[viewId]();
            }
        });
    }
}

const viewsConfig = {
    'view-news-collection': () => loadTableData('table/raw-articles', 'table-raw-articles', item => `
        <tr><td>${item.id}</td><td><a href="${item.url}" target="_blank" style="color:#00e5ff; text-decoration:none;">${item.title || 'N/A'}</a></td><td>${item.source || 'N/A'}</td><td>${item.date || 'N/A'}</td><td>${item.collected_at || ''}</td></tr>`, 'view-news-collection'),
    'view-crime-analytics': () => loadTableData('table/processed-articles', 'table-processed-articles', item => `
        <tr><td>${item.id}</td><td><a href="${item.url}" target="_blank" style="color:#00e5ff; text-decoration:none;">${item.title || 'N/A'}</a></td><td>${item.source || 'N/A'}</td><td>${item.category || 'N/A'}</td><td>${item.location || 'N/A'}</td><td>${item.status || 'N/A'}</td><td>${item.processed_at || ''}</td></tr>`, 'view-crime-analytics'),
    'view-news-events': () => loadTableData('table/news-events', 'table-events', item => `
        <tr><td>${item.id}</td><td><a href="${item.url}" target="_blank" style="color:#00e5ff; text-decoration:none;">${item.title || 'N/A'}</a></td><td>${item.category || 'N/A'}</td><td>${item.location || 'N/A'}</td><td>${item.created_at || ''}</td></tr>`, 'view-news-events'),
    'view-sentiment-analysis': () => loadTableData('table/analysis-results', 'table-analysis', item => {
        const sent = item.sentiment || 'Neutral';
        const sentClass = sent.toLowerCase() === 'positive' ? 'positive' : sent.toLowerCase() === 'negative' ? 'negative' : '';
        const severity = item.severity_score !== undefined ? item.severity_score : 3;
        const cpi = item.cpi || 'Low';
        let cpiColor = '#10b981'; // Green for Low
        if (cpi === 'Very High' || cpi === 'High') cpiColor = '#ef4444'; // Red
        else if (cpi === 'Medium') cpiColor = '#f59e0b'; // Yellow/Orange
        return `<tr><td>${item.id}</td><td><a href="${item.url}" target="_blank" style="color:#00e5ff; text-decoration:none;">${item.article_title || 'N/A'}</a></td><td>${item.source || 'N/A'}</td>
        <td><span class="tag sentiment ${sentClass}">${sent}</span></td>
        <td>${severity}</td>
        <td><span class="tag" style="background-color: transparent; border: 1px solid ${cpiColor}; color: ${cpiColor};">${cpi}</span></td>
        <td>${item.confidence ? item.confidence.toFixed(2) : 'N/A'}</td><td>${item.analyzed_at || ''}</td></tr>`;
    }, 'view-sentiment-analysis'),
    'view-officer-analytics': () => loadTableData('table/officer-mentions', 'table-officer-mentions', item => `
        <tr><td>${item.id}</td><td>${item.officer_name || 'N/A'} <a href="${item.url}" target="_blank" style="color:#00e5ff; margin-left:8px;" title="View Article"><i class="fas fa-external-link-alt"></i></a></td><td>${item.designation || 'N/A'}</td><td>${item.police_station || 'N/A'}</td></tr>`, 'view-officer-analytics')
};

function switchView(targetId) {
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    
    const target = document.getElementById(targetId);
    if(target) {
        target.style.display = 'block';
        setTimeout(() => target.classList.add('active'), 10);
        
        if (viewsConfig[targetId]) {
            viewsConfig[targetId](); // Load table data
        }
    }
}

// Initial Load and Event Setup
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    refreshDashboard();
    
    // Global Filters Logic
    const filterDate = document.getElementById('filter-date');
    const customDateFields = document.getElementById('custom-date-fields');
    if (filterDate) {
        filterDate.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                customDateFields.style.display = 'flex';
            } else {
                customDateFields.style.display = 'none';
            }
        });
    }
    
    const btnApplyFilters = document.getElementById('btn-apply-filters');
    if (btnApplyFilters) {
        btnApplyFilters.addEventListener('click', () => {
            const activeView = document.querySelector('.view-section.active');
            if (activeView && activeView.id === 'view-dashboard') {
                refreshDashboard();
            } else if (activeView && viewsConfig[activeView.id]) {
                viewsConfig[activeView.id]();
            }
        });
    }
    
    // Sidebar Toggle Logic
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
            }
        });
    }
    
    // Setup Navigation
    const navLinks = document.querySelectorAll('#sidebar-menu a[data-target]');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // update active class on sidebar
            document.querySelectorAll('#sidebar-menu li').forEach(li => li.classList.remove('active'));
            e.currentTarget.parentElement.classList.add('active');
            
            const targetId = e.currentTarget.getAttribute('data-target');
            switchView(targetId);
            
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('show');
            }
        });
    });
    // Pipeline Trigger Logic
    const btnRunPipeline = document.getElementById('btn-run-pipeline');
    if(btnRunPipeline) {
        btnRunPipeline.addEventListener('click', async () => {
            btnRunPipeline.disabled = true;
            const originalHTML = btnRunPipeline.innerHTML;
            btnRunPipeline.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
            
            try {
                const res = await fetch('/api/dashboard/run-pipeline', { method: 'POST' });
                if(res.ok) {
                    alert('Pipeline started in the background. Dashboard will update automatically in a few seconds.');
                } else {
                    alert('Failed to start pipeline.');
                }
            } catch(e) {
                console.error("Pipeline trigger error:", e);
                alert('Error starting pipeline.');
            }
            
            setTimeout(() => {
                btnRunPipeline.disabled = false;
                btnRunPipeline.innerHTML = originalHTML;
            }, 5000); // Re-enable after 5s
        });
    }

    // Poll every 30 seconds for real-time updates across all views
    setInterval(() => {
        const activeView = document.querySelector('.view-section.active');
        if (activeView) {
            if (activeView.id === 'view-dashboard') {
                refreshDashboard();
            } else if (viewsConfig[activeView.id]) {
                viewsConfig[activeView.id](); // Refresh the active table's data
            }
        }
    }, 30000);
});
