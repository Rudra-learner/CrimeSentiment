// Dedicated JavaScript for Nayagarh Crimes with Sentiment Tab
const paginationState = { page: 1, limit: 25 };

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
    if(filterPriority && filterPriority.value !== 'all') params.append('priority', filterPriority.value);
    
    const filterCategory = document.getElementById('filter-category');
    if(filterCategory && filterCategory.value !== 'all') params.append('category', filterCategory.value);
    
    const filterLocation = document.getElementById('filter-location');
    if(filterLocation && filterLocation.value !== 'all') params.append('location', filterLocation.value);
    
    const searchInput = document.getElementById('search-input');
    if(searchInput && searchInput.value.trim() !== '') params.append('search', searchInput.value.trim());
    
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
            data.categories.forEach(c => catSelect.innerHTML += `<option value="${c}">${c}</option>`);
            if(currentVal) catSelect.value = currentVal;
        }
        const locSelect = document.getElementById('filter-location');
        if(locSelect && data.locations) {
            const currentVal = locSelect.value;
            locSelect.innerHTML = '<option value="all">All Locations</option>';
            data.locations.forEach(l => locSelect.innerHTML += `<option value="${l}">${l}</option>`);
            if(currentVal) locSelect.value = currentVal;
        }
    } catch (e) { console.error("Error loading filter options", e); }
}

async function fetchAPI(endpoint) {
    try {
        const query = getFilterQueryString();
        const separator = endpoint.includes('?') ? (query ? '&' + query.substring(1) : '') : query;
        const res = await fetch(`/api/dashboard/${endpoint}${separator}`);
        if(!res.ok) throw new Error("API Error");
        return await res.json();
    } catch (e) { console.error("Error fetching", endpoint, e); return null; }
}

async function loadNayagarhTable() {
    const paginatedEndpoint = `table/nayagarh-sentiment?page=${paginationState.page}&limit=${paginationState.limit}`;
    const result = await fetchAPI(paginatedEndpoint);
    if(!result) return;
    
    const actualData = result.data ? result.data : (Array.isArray(result) ? result : []);
    const totalItems = result.total !== undefined ? result.total : actualData.length;
    const currentPage = result.page || paginationState.page;
    const currentLimit = result.limit || paginationState.limit;
    
    const badge = document.getElementById('badge-nayagarh-count');
    if(badge) badge.innerText = `Total: ${totalItems}`;
    
    const tbody = document.querySelector('#table-nayagarh-sentiment tbody');
    if(tbody) {
        tbody.innerHTML = '';
        if (actualData.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding: 25px; color: var(--text-muted); font-size: 1rem;">No matching Nayagarh sentiment records found for the selected filters.</td></tr>`;
        } else {
            actualData.forEach(item => {
                const sent = item.sentiment || 'Neutral';
                const sentClass = sent.toLowerCase() === 'positive' ? 'positive' : sent.toLowerCase() === 'negative' ? 'negative' : '';
                const severity = item.severity_score !== undefined ? item.severity_score : 3;
                const cpi = item.cpi || 'Low';
                let cpiColor = '#10b981';
                if (cpi === 'Very High' || cpi === 'High') cpiColor = '#ef4444';
                else if (cpi === 'Medium') cpiColor = '#f59e0b';
                
                tbody.innerHTML += `<tr>
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
            });
        }
    }

    const totalPages = Math.ceil(totalItems / currentLimit) || 1;
    const paginationControls = document.getElementById('pagination-view-nayagarh-sentiment');
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
            if (paginationState.page > 1) { paginationState.page--; loadNayagarhTable(); }
        });
        newNext.addEventListener('click', () => {
            if (paginationState.page < totalPages) { paginationState.page++; loadNayagarhTable(); }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    updateClock();
    loadFilterOptions();
    loadNayagarhTable();
    
    const filterDate = document.getElementById('filter-date');
    const customDateFields = document.getElementById('custom-date-fields');
    if (filterDate && customDateFields) {
        filterDate.addEventListener('change', (e) => {
            customDateFields.style.display = e.target.value === 'custom' ? 'flex' : 'none';
        });
    }
    
    const triggerUpdate = () => { paginationState.page = 1; loadNayagarhTable(); };
    
    const btnApplyFilters = document.getElementById('btn-apply-filters');
    if (btnApplyFilters) btnApplyFilters.addEventListener('click', triggerUpdate);
    
    ['filter-category', 'filter-location', 'filter-priority', 'filter-date'].forEach(id => {
        const el = document.getElementById(id);
        if(el) el.addEventListener('change', triggerUpdate);
    });
    
    const searchInput = document.getElementById('search-input');
    if(searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(triggerUpdate, 400);
        });
    }
    
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (toggleBtn && sidebar && mainContent) {
        toggleBtn.addEventListener('click', () => {
            if (window.innerWidth <= 768) sidebar.classList.toggle('show');
            else { sidebar.classList.toggle('collapsed'); mainContent.classList.toggle('expanded'); }
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
            } catch(e) { console.error("Pipeline trigger error:", e); }
            setTimeout(() => { btnRunPipeline.disabled = false; btnRunPipeline.innerHTML = originalHTML; }, 5000);
        });
    }

    setInterval(loadNayagarhTable, 30000);
});
