// Dedicated JavaScript for Dashboard Overview Tab
let chartInstances = {};

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
    const el = document.getElementById('datetime-display');
    if (el) el.innerText = now.toLocaleDateString('en-IN', options);
}
setInterval(updateClock, 1000);

function getFilterQueryString() {
    let params = new URLSearchParams();
    
    const filterDate = document.getElementById('filter-date');
    if(filterDate) {
        const val = filterDate.value;
        if(val === '7') params.append('days', 7);
        else if(val === '30') params.append('days', 30);
        else if(val === 'custom') {
            const start = document.getElementById('filter-start-date')?.value;
            const end = document.getElementById('filter-end-date')?.value;
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
    
    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val !== undefined ? val : 0; };
    setVal('kpi-odisha-crimes', data.OdishaCrimes !== undefined ? data.OdishaCrimes : data.ProcessedArticles);
    setVal('kpi-nayagarh-crimes', data.NayagarhCrimes !== undefined ? data.NayagarhCrimes : 0);
    setVal('kpi-events', data.TotalCrimeEvents);
    setVal('kpi-active-cases', data.ActiveCases);
    setVal('kpi-solved', data.SolvedCases);
    setVal('kpi-arrested', data.ArrestedCases);
    setVal('kpi-investigation', data.UnderInvestigation);
    setVal('kpi-police-mentioned', data.PoliceMentioned);
    setVal('kpi-avg-crime-sent', data.AvgCrimeSentiment);
    setVal('kpi-avg-officer-sent', data.AvgOfficerSentiment);
    setVal('kpi-positive-crimes', data.PositiveCrimes);
    setVal('kpi-negative-crimes', data.NegativeCrimes);
    setVal('kpi-neutral-crimes', data.NeutralCrimes);

    const pIcon = document.getElementById('icon-sentiment-crime');
    if(pIcon) pIcon.className = 'kpi-icon ' + (data.AvgCrimeSentiment > 0 ? 'green' : data.AvgCrimeSentiment < 0 ? 'red' : 'yellow');
    
    const oIcon = document.getElementById('icon-sentiment-officer');
    if(oIcon) oIcon.className = 'kpi-icon ' + (data.AvgOfficerSentiment > 0 ? 'green' : data.AvgOfficerSentiment < 0 ? 'red' : 'yellow');
}

async function updateCharts() {
    const data = await fetchAPI('crime-analytics');
    if (!data) return;

    const ctxMonthlyEl = document.getElementById('chart-monthly-trend');
    if (ctxMonthlyEl) {
        const ctxMonthly = ctxMonthlyEl.getContext('2d');
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
    }

    const ctxPieEl = document.getElementById('chart-category-pie');
    if (ctxPieEl) {
        const ctxPie = ctxPieEl.getContext('2d');
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
    }

    const ctxWeekEl = document.getElementById('chart-weekly-dist');
    if (ctxWeekEl) {
        const ctxWeek = ctxWeekEl.getContext('2d');
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
}

let map;
let markers = [];
function initMap() {
    const mapEl = document.getElementById('district-map');
    if(!mapEl) return;
    map = L.map('district-map').setView([20.1245, 85.1054], 10);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    }).addTo(map);
}

async function updateMap() {
    if(!map) initMap();
    if(!map) return;
    const data = await fetchAPI('map-data');
    if(!data) return;

    markers.forEach(m => map.removeLayer(m));
    markers = [];

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
        const radius = Math.max(loc.count * 1.5, 5);
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
    const tbody = document.querySelector('#table-officers tbody');
    if(!data || !tbody) return;
    tbody.innerHTML = '';
    
    data.forEach(off => {
        const total = max(off.mentions, 1);
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

function max(a, b) { return a > b ? a : b; }

async function updateSentimentCharts() {
    const sentData = await fetchAPI('police-sentiment');
    const ctxPolEl = document.getElementById('chart-police-sentiment');
    if(sentData && ctxPolEl) {
        const ctxPol = ctxPolEl.getContext('2d');
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

    const caseData = await fetchAPI('case-status');
    const ctxCaseEl = document.getElementById('chart-case-status');
    if(caseData && ctxCaseEl) {
        const ctxCase = ctxCaseEl.getContext('2d');
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

async function refreshDashboard() {
    updateKPIs();
    updateCharts();
    updateMap();
    updateNewsEvents();
    updateLatestNews();
    updateOfficerTable();
    updateSentimentCharts();
}

document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    initMap();
    loadFilterOptions();
    refreshDashboard();
    
    const filterDate = document.getElementById('filter-date');
    const customDateFields = document.getElementById('custom-date-fields');
    if (filterDate && customDateFields) {
        filterDate.addEventListener('change', (e) => {
            customDateFields.style.display = e.target.value === 'custom' ? 'flex' : 'none';
        });
    }
    
    const btnApplyFilters = document.getElementById('btn-apply-filters');
    if (btnApplyFilters) btnApplyFilters.addEventListener('click', refreshDashboard);
    
    ['filter-category', 'filter-location', 'filter-priority', 'filter-date'].forEach(id => {
        const el = document.getElementById(id);
        if(el) el.addEventListener('change', refreshDashboard);
    });
    
    const searchInput = document.getElementById('search-input');
    if(searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(refreshDashboard, 400);
        });
    }
    
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (toggleBtn && sidebar && mainContent) {
        toggleBtn.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
            }
        });
    }
    
    const btnRunPipeline = document.getElementById('btn-run-pipeline');
    if(btnRunPipeline) {
        btnRunPipeline.addEventListener('click', async () => {
            btnRunPipeline.disabled = true;
            const originalHTML = btnRunPipeline.innerHTML;
            btnRunPipeline.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';
            try {
                const res = await fetch('/api/dashboard/run-pipeline', { method: 'POST' });
                alert(res.ok ? 'Pipeline started in the background.' : 'Failed to start pipeline.');
            } catch(e) {
                console.error("Pipeline trigger error:", e);
            }
            setTimeout(() => {
                btnRunPipeline.disabled = false;
                btnRunPipeline.innerHTML = originalHTML;
            }, 5000);
        });
    }

    setInterval(refreshDashboard, 30000);
});

// --- Header Interactivity ---
window.toggleDropdown = function(menuId) {
    const menus = document.querySelectorAll('.dropdown-menu');
    menus.forEach(m => {
        if (m.id !== menuId) m.classList.remove('show');
    });
    const menu = document.getElementById(menuId);
    if (menu) menu.classList.toggle('show');
};

document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-container')) {
        document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('show'));
    }
});

window.logout = async function() {
    try {
        const res = await fetch('/api/logout', { method: 'POST' });
        if (res.ok) {
            window.location.href = '/dashboard/login.html';
        }
    } catch (err) {
        console.error('Error logging out:', err);
    }
};

// --- Theme Toggle ---
window.toggleTheme = function() {
    document.documentElement.classList.toggle('light-mode');
    const isLight = document.documentElement.classList.contains('light-mode');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    updateThemeUI(isLight);
};

window.updateThemeUI = function(isLight) {
    const themeBtns = document.querySelectorAll('#theme-toggle-btn');
    themeBtns.forEach(btn => {
        btn.innerHTML = isLight 
            ? '<i class="fas fa-sun"></i> Light Mode (Active)' 
            : '<i class="fas fa-moon"></i> Dark Mode (Active)';
    });
};

// Initialize theme on load
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.documentElement.classList.add('light-mode');
        updateThemeUI(true);
    }
});

// Force sidebar to be collapsed by default on load
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (sidebar && mainContent && window.innerWidth > 768) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
    }
});
