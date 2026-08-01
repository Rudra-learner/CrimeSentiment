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
    let params = new URLSearchParams();
    
    const filterDate = document.getElementById('filter-date');
    if(filterDate) {
        const val = filterDate.value;
        if(val === '7') params.append('days', 7);
        else if(val === '30') params.append('days', 30);
        else if(val === 'custom') {
            const start = document.getElementById('filter-start-date').value;
            const end = document.getElementById('filter-end-date').value;
            if(start) params.append('start_date', start);
            if(end) params.append('end_date', end);
        }
    }
    
    const filterPriority = document.getElementById('filter-priority');
    if(filterPriority && filterPriority.value !== 'all') {
        params.append('priority', filterPriority.value);
    }
    
    const filterCategory = document.getElementById('filter-category');
    if(filterCategory && filterCategory.value !== 'all') {
        params.append('category', filterCategory.value);
    }
    
    const filterLocation = document.getElementById('filter-location');
    if(filterLocation && filterLocation.value !== 'all') {
        params.append('location', filterLocation.value);
    }
    
    const searchInput = document.getElementById('search-input');
    if(searchInput && searchInput.value.trim() !== '') {
        params.append('search', searchInput.value.trim());
    }
    
    const q = params.toString();
    return q ? '?' + q : '';
}

async function loadFilterOptions() {
    try {
        const res = await fetch('/api/dashboard/filter-options');
        if(!res.ok) return;
        const data = await res.json();
        
        const catSelect = document.getElementById('filter-category');
        if(catSelect && data.categories) {
            const currentVal = catSelect.value;
            catSelect.innerHTML = '<option value="all">All Categories</option>';
            data.categories.forEach(c => {
                catSelect.innerHTML += `<option value="${c}">${c}</option>`;
            });
            if(currentVal) catSelect.value = currentVal;
        }
        
        const locSelect = document.getElementById('filter-location');
        if(locSelect && data.locations) {
            const currentVal = locSelect.value;
            locSelect.innerHTML = '<option value="all">All Locations</option>';
            data.locations.forEach(l => {
                locSelect.innerHTML += `<option value="${l}">${l}</option>`;
            });
            if(currentVal) locSelect.value = currentVal;
        }
    } catch (e) {
        console.error("Error loading filter options", e);
    }
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
    
    document.getElementById('kpi-avg-crime-sent').innerText = data.AvgCrimeSentiment;
    const pIcon = document.getElementById('icon-sentiment-crime');
    pIcon.className = 'kpi-icon ' + (data.AvgCrimeSentiment > 0 ? 'green' : data.AvgCrimeSentiment < 0 ? 'red' : 'yellow');
    
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
    const container = document.getElementById('events-list-container');
    if(!container) return;
    container.innerHTML = '';
    
    if(!data || data.length === 0) {
        container.innerHTML = '<p style="padding: 15px; color: var(--text-muted); font-size: 0.9rem;">No news events matched your filter criteria.</p>';
        return;
    }
    
    data.forEach(evt => {
        const titleHtml = evt.url && evt.url !== '#' ? `<a href="${evt.url}" target="_blank" style="color:var(--text-white); text-decoration:none;">${evt.title} <i class="fas fa-external-link-alt" style="font-size:0.8rem; color:var(--accent-blue); margin-left:4px;"></i></a>` : evt.title;
        container.innerHTML += `
            <div class="list-item">
                <div class="list-item-content">
                    <h4 style="margin-bottom: 4px;">${titleHtml}</h4>
                    <p style="margin-bottom: 6px;"><strong style="color:var(--accent-purple);">${evt.event_id}</strong> | ${evt.timeline}</p>
                    <div class="tags">
                        ${evt.publishers ? evt.publishers.map(p => `<span class="tag" style="background:rgba(255,255,255,0.08);">${p}</span>`).join('') : ''}
                        <span class="tag" style="background:var(--accent-blue); color:#fff;">Similarity: ${evt.similarity}</span>
                    </div>
                </div>
            </div>
        `;
    });
}

async function updateLatestNews() {
    const data = await fetchAPI('latest-news');
    const container = document.getElementById('news-feed-container');
    if(!container) return;
    container.innerHTML = '';
    
    if(!data || data.length === 0) {
        container.innerHTML = '<p style="padding: 15px; color: var(--text-muted); font-size: 0.9rem;">No crime news articles found for the selected time period or filter.</p>';
        return;
    }
    
    data.forEach(news => {
        const sent = news.sentiment || 'Neutral';
        const sentClass = sent.toLowerCase() === 'positive' ? 'positive' : (sent.toLowerCase() === 'negative' ? 'negative' : '');
        const titleHtml = news.url && news.url !== '#' ? `<a href="${news.url}" target="_blank" style="color:var(--primary-cyan); text-decoration:none;">${news.title} <i class="fas fa-external-link-alt" style="font-size:0.8rem; color:var(--accent-blue); margin-left:4px;"></i></a>` : news.title;
        
        container.innerHTML += `
            <div class="list-item">
                <div class="list-item-content">
                    <h4 style="margin-bottom: 4px; line-height: 1.3;">${titleHtml}</h4>
                    <p style="margin-bottom: 8px;"><strong>${news.publisher || 'Unknown Source'}</strong> | ${news.time}</p>
                    <div class="tags">
                        <span class="tag cyber">${news.category || 'Unknown'}</span>
                        <span class="tag"><i class="fas fa-map-marker-alt" style="color:var(--accent-orange)"></i> ${news.location || 'N/A'}</span>
                        <span class="tag sentiment ${sentClass}">Stance: ${sent}</span>
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
    'view-nayagarh-sentiment': { page: 1, limit: 25 },
    'view-odisha-crime': { page: 1, limit: 25 }
};

async function loadTableData(endpoint, tableId, rowMapper, viewId, badgeId) {
    const state = paginationState[viewId] || { page: 1, limit: 25 };
    const paginatedEndpoint = `${endpoint}?page=${state.page}&limit=${state.limit}`;
    
    const result = await fetchAPI(paginatedEndpoint);
    if(!result) return;
    
    const actualData = result.data ? result.data : (Array.isArray(result) ? result : []);
    const totalItems = result.total !== undefined ? result.total : actualData.length;
    const currentPage = result.page || state.page;
    const currentLimit = result.limit || state.limit;
    
    const badge = document.getElementById(badgeId);
    if(badge) {
        badge.innerText = `Total: ${totalItems}`;
    }
    
    const tbody = document.querySelector(`#${tableId} tbody`);
    if(tbody) {
        tbody.innerHTML = '';
        if (actualData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding: 20px; color: var(--text-muted);">No matching crime records found for the selected filters.</td></tr>`;
        } else {
            actualData.forEach(item => {
                tbody.innerHTML += rowMapper(item);
            });
        }
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
    'view-nayagarh-sentiment': () => loadTableData('table/nayagarh-sentiment', 'table-nayagarh-sentiment', item => {
        const sent = item.sentiment || 'Neutral';
        const sentClass = sent.toLowerCase() === 'positive' ? 'positive' : sent.toLowerCase() === 'negative' ? 'negative' : '';
        const severity = item.severity_score !== undefined ? item.severity_score : 3;
        const cpi = item.cpi || 'Low';
        let cpiColor = '#10b981'; // Green for Low
        if (cpi === 'Very High' || cpi === 'High') cpiColor = '#ef4444'; // Red
        else if (cpi === 'Medium') cpiColor = '#f59e0b'; // Orange/Yellow
        
        return `<tr>
            <td>${item.id}</td>
            <td style="max-width: 380px; line-height: 1.4;">
                <a href="${item.url}" target="_blank" style="color:var(--primary-cyan); text-decoration:none; font-weight: 500;">${item.title}</a>
                <a href="${item.url}" target="_blank" style="margin-left: 8px; color: var(--accent-blue);" title="Redirect to Original Article"><i class="fas fa-external-link-alt"></i></a>
            </td>
            <td><span class="tag" style="background: rgba(255,255,255,0.08);">${item.source}</span></td>
            <td><span class="tag cyber" style="display:inline-block; margin-bottom: 3px;">${item.category}</span>${item.subcategory ? `<br><small style="color:var(--text-muted)">${item.subcategory}</small>` : ''}</td>
            <td><i class="fas fa-map-marker-alt" style="color:var(--accent-orange)"></i> ${item.location}</td>
            <td><span style="color:var(--accent-purple); font-family: monospace; font-weight: 600;">${item.event_id}</span></td>
            <td><span class="tag sentiment ${sentClass}">${sent}</span></td>
            <td>
                <strong>Sev: ${severity}/5</strong><br>
                <span class="tag" style="background-color: transparent; border: 1px solid ${cpiColor}; color: ${cpiColor}; margin-top: 3px; display:inline-block;">${cpi}</span>
            </td>
            <td>${item.confidence}%</td>
            <td style="white-space: nowrap; font-size: 0.85rem;">${item.published_date}</td>
        </tr>`;
    }, 'view-nayagarh-sentiment', 'badge-nayagarh-count'),

    'view-odisha-crime': () => loadTableData('table/odisha-crimes', 'table-odisha-crime', item => {
        let statusColor = '#3b82f6';
        if (item.case_status === 'SOLVED') statusColor = '#10b981';
        else if (item.case_status === 'PARTIALLY_SOLVED') statusColor = '#f59e0b';

        return `<tr>
            <td>${item.id}</td>
            <td style="max-width: 420px; line-height: 1.4;">
                <a href="${item.url}" target="_blank" style="color:var(--primary-cyan); text-decoration:none; font-weight: 500;">${item.title}</a>
                <a href="${item.url}" target="_blank" style="margin-left: 8px; color: var(--accent-blue);" title="Redirect to Original Article"><i class="fas fa-external-link-alt"></i></a>
            </td>
            <td><span class="tag" style="background: rgba(255,255,255,0.08);">${item.source}</span></td>
            <td><span class="tag cyber" style="display:inline-block; margin-bottom: 3px;">${item.category}</span>${item.subcategory ? `<br><small style="color:var(--text-muted)">${item.subcategory}</small>` : ''}</td>
            <td><i class="fas fa-map-marker-alt" style="color:var(--accent-orange)"></i> ${item.location}</td>
            <td><span class="tag" style="background-color: transparent; border: 1px solid ${statusColor}; color: ${statusColor};">${item.case_status}</span></td>
            <td><span style="color:var(--accent-purple); font-family: monospace; font-weight: 600;">${item.event_id}</span></td>
            <td style="white-space: nowrap; font-size: 0.85rem;">${item.published_date}</td>
        </tr>`;
    }, 'view-odisha-crime', 'badge-odisha-count')
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
    loadFilterOptions();
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
    
    function triggerActiveViewUpdate() {
        const activeView = document.querySelector('.view-section.active');
        if (activeView && activeView.id === 'view-dashboard') {
            refreshDashboard();
        } else if (activeView && viewsConfig[activeView.id]) {
            if (paginationState[activeView.id]) paginationState[activeView.id].page = 1;
            viewsConfig[activeView.id]();
        }
    }

    const btnApplyFilters = document.getElementById('btn-apply-filters');
    if (btnApplyFilters) {
        btnApplyFilters.addEventListener('click', triggerActiveViewUpdate);
    }
    
    ['filter-category', 'filter-location', 'filter-priority', 'filter-date'].forEach(id => {
        const el = document.getElementById(id);
        if(el) el.addEventListener('change', triggerActiveViewUpdate);
    });
    
    const searchInput = document.getElementById('search-input');
    if(searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(triggerActiveViewUpdate, 400);
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
