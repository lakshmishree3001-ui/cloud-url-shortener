/**
 * Cloud URL Shortener - Enterprise Single Page Application
 * Pure Vanilla JavaScript (ES6+)
 * Zero Emojis Enforced (Clean SVG and CSS Badges Only)
 */

document.addEventListener('DOMContentLoaded', () => {
  // ==========================================
  // State Management
  // ==========================================
  const state = {
    allUrls: [],
    currentTab: 'tab-shorten',
    searchQuery: '',
    statusFilter: 'all',
  };

  // ==========================================
  // DOM Element References
  // ==========================================
  const brandLogo = document.getElementById('brand-logo');
  const systemStatusIndicator = document.getElementById('system-status-indicator');
  const systemStatusText = document.getElementById('system-status-text');

  // Stats Counters
  const statTotalLinks = document.getElementById('stat-total-links');
  const statTotalClicks = document.getElementById('stat-total-clicks');
  const statActiveLinks = document.getElementById('stat-active-links');
  const statExpiredLinks = document.getElementById('stat-expired-links');

  // Tabs
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  // Single Shorten
  const formShorten = document.getElementById('form-shorten');
  const inputLongUrl = document.getElementById('input-long-url');
  const inputCustomCode = document.getElementById('input-custom-code');
  const selectExpiration = document.getElementById('select-expiration');
  const resultBox = document.getElementById('result-box');
  const resultShortUrlText = document.getElementById('result-short-url-text');
  const resultStatusBadge = document.getElementById('result-status-badge');
  const btnCopyResult = document.getElementById('btn-copy-result');
  const btnVisitResult = document.getElementById('btn-visit-result');
  const resultCodeVal = document.getElementById('result-code-val');
  const resultDomainVal = document.getElementById('result-domain-val');
  const resultTypeVal = document.getElementById('result-type-val');
  const resultExpiresVal = document.getElementById('result-expires-val');

  // Batch Shorten
  const formBatch = document.getElementById('form-batch');
  const textareaBatchUrls = document.getElementById('textarea-batch-urls');
  const selectBatchExpiration = document.getElementById('select-batch-expiration');
  const batchResultsContainer = document.getElementById('batch-results-container');
  const batchCountVal = document.getElementById('batch-count-val');
  const batchResultsTbody = document.getElementById('batch-results-tbody');

  // Link Explorer Table
  const inputTableSearch = document.getElementById('input-table-search');
  const selectTableFilter = document.getElementById('select-table-filter');
  const btnRefreshTable = document.getElementById('btn-refresh-table');
  const urlsTableTbody = document.getElementById('urls-table-tbody');

  // Analytics
  const topLinksList = document.getElementById('top-links-list');
  const domainDistributionList = document.getElementById('domain-distribution-list');

  // Observability
  const btnTriggerCleanup = document.getElementById('btn-trigger-cleanup');
  const btnFetchCloudwatch = document.getElementById('btn-fetch-cloudwatch');
  const telemetryLog = document.getElementById('telemetry-log');

  // Modal
  const statsModal = document.getElementById('stats-modal');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const modalCode = document.getElementById('modal-code');
  const modalUrl = document.getElementById('modal-url');
  const modalDomain = document.getElementById('modal-domain');
  const modalClicks = document.getElementById('modal-clicks');
  const modalCreated = document.getElementById('modal-created');
  const modalAccessed = document.getElementById('modal-accessed');
  const modalExpires = document.getElementById('modal-expires');
  const modalStatus = document.getElementById('modal-status');

  // Toasts
  const toastContainer = document.getElementById('toast-container');

  // ==========================================
  // Toast Notification System (Zero Emojis)
  // ==========================================
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const iconSvg = type === 'success'
      ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`
      : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;

    toast.innerHTML = `
      ${iconSvg}
      <span>${escapeHtml(message)}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px) scale(0.95)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 250);
    }, 3500);
  }

  // ==========================================
  // Helper Utilities
  // ==========================================
  function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatDate(isoStr) {
    if (!isoStr) return 'Never';
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoStr;
    }
  }

  function copyTextToClipboard(text, customMessage = 'Copied to clipboard') {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text)
        .then(() => showToast(customMessage, 'success'))
        .catch(() => fallbackCopy(text, customMessage));
    } else {
      fallbackCopy(text, customMessage);
    }
  }

  function fallbackCopy(text, customMessage) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    try {
      document.execCommand('copy');
      showToast(customMessage, 'success');
    } catch {
      showToast('Failed to copy to clipboard', 'error');
    }
    document.body.removeChild(textarea);
  }

  function parseExpirationValue(val) {
    if (val === '1h') return { expires_in_hours: 1 };
    if (val === '24h') return { expires_in_hours: 24 };
    if (val === '7d') return { expires_in_days: 7 };
    if (val === '30d') return { expires_in_days: 30 };
    return {};
  }

  // ==========================================
  // Tab Switching
  // ==========================================
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-tab');
      if (!targetId || targetId === state.currentTab) return;

      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const pane = document.getElementById(targetId);
      if (pane) pane.classList.add('active');

      state.currentTab = targetId;

      // Lazy fetch based on tab
      if (targetId === 'tab-explorer') {
        fetchLinks();
      } else if (targetId === 'tab-analytics') {
        fetchAnalytics();
      } else if (targetId === 'tab-observability') {
        fetchCloudWatchTelemetry();
      }
    });
  });

  // ==========================================
  // API Calls & Data Fetching
  // ==========================================

  // 1. Fetch Global Summary Metrics
  async function fetchSummaryMetrics() {
    try {
      const res = await fetch('/api/stats/report');
      if (!res.ok) throw new Error('Failed to load metrics');
      const data = await res.json();
      const s = data.summary || data;

      statTotalLinks.textContent = (s.total_links || s.total_urls || 0).toLocaleString();
      statTotalClicks.textContent = (s.total_clicks || 0).toLocaleString();
      statActiveLinks.textContent = (s.active_links || s.active_urls || 0).toLocaleString();
      statExpiredLinks.textContent = (s.expired_links || s.expired_urls || 0).toLocaleString();

      systemStatusIndicator.className = 'status-pill';
      systemStatusText.textContent = 'System Online';
    } catch (err) {
      console.warn('Metrics check:', err.message);
      systemStatusText.textContent = 'Degraded';
    }
  }

  // 2. Fetch All Links for Explorer Table
  async function fetchLinks() {
    urlsTableTbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--text-faint); padding: 2rem;">Loading persistent records from SQLite...</td>
      </tr>
    `;

    try {
      const res = await fetch('/api/urls?limit=200');
      if (!res.ok) throw new Error('Failed to fetch URLs');
      const data = await res.json();
      state.allUrls = data.urls || [];
      renderUrlsTable();
    } catch (err) {
      urlsTableTbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; color: var(--danger); padding: 2rem;">Error loading links: ${escapeHtml(err.message)}</td>
        </tr>
      `;
      showToast('Could not fetch links from database', 'error');
    }
  }

  // 3. Render Link Explorer Table with Search & Filter
  function renderUrlsTable() {
    const query = state.searchQuery.toLowerCase().trim();
    const filter = state.statusFilter;

    const filtered = state.allUrls.filter(item => {
      // Status filter
      if (filter === 'active' && !item.is_active) return false;
      if (filter === 'expired' && !item.is_expired) return false;

      // Text search
      if (!query) return true;
      const matchCode = (item.short_code || '').toLowerCase().includes(query);
      const matchUrl = (item.original_url || '').toLowerCase().includes(query);
      const matchDomain = (item.destination_domain || '').toLowerCase().includes(query);
      return matchCode || matchUrl || matchDomain;
    });

    if (filtered.length === 0) {
      urlsTableTbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; color: var(--text-faint); padding: 2rem;">No matching links found in database.</td>
        </tr>
      `;
      return;
    }

    const host = window.location.origin;

    urlsTableTbody.innerHTML = filtered.map(item => {
      const fullShortUrl = `${host}/${item.short_code}`;
      const statusBadge = item.is_expired
        ? `<span class="badge badge-danger">Expired</span>`
        : (item.is_active
          ? `<span class="badge badge-success">Active</span>`
          : `<span class="badge badge-warning">Inactive</span>`);

      return `
        <tr data-code="${escapeHtml(item.short_code)}">
          <td>
            <a href="${fullShortUrl}" target="_blank" class="table-short-code" title="Test Redirection">${escapeHtml(item.short_code)}</a>
          </td>
          <td>
            <div class="table-url-cell" title="${escapeHtml(item.original_url)}">
              ${escapeHtml(item.original_url)}
            </div>
          </td>
          <td>
            <span style="font-size: 0.82rem; color: var(--text-muted);">${escapeHtml(item.destination_domain || 'unknown')}</span>
          </td>
          <td>
            <span style="font-weight: 600; color: var(--accent-cyan);">${(item.click_count || 0).toLocaleString()}</span>
          </td>
          <td style="font-size: 0.82rem; color: var(--text-muted);">
            ${formatDate(item.created_at)}
          </td>
          <td>
            ${statusBadge}
          </td>
          <td style="text-align: right;">
            <div class="table-actions" style="justify-content: flex-end;">
              <button type="button" class="action-icon-btn btn-copy-link" data-url="${fullShortUrl}" title="Copy short URL">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </button>
              <a href="${fullShortUrl}" target="_blank" class="action-icon-btn btn-redirect-link" title="Test HTTP 307 Redirection">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                  <polyline points="15 3 21 3 21 9"></polyline>
                  <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
              </a>
              <button type="button" class="action-icon-btn btn-inspect-stats" data-code="${escapeHtml(item.short_code)}" title="View detailed stats">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="16" x2="12" y2="12"></line>
                  <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    // Attach event listeners for row actions
    attachTableRowActions();
  }

  function attachTableRowActions() {
    // Copy button
    urlsTableTbody.querySelectorAll('.btn-copy-link').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const url = btn.getAttribute('data-url');
        copyTextToClipboard(url, 'Short URL copied to clipboard');
      });
    });

    // Inspect stats modal button
    urlsTableTbody.querySelectorAll('.btn-inspect-stats').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const code = btn.getAttribute('data-code');
        openStatsModal(code);
      });
    });

    // Redirect link triggers background update
    urlsTableTbody.querySelectorAll('.btn-redirect-link').forEach(btn => {
      btn.addEventListener('click', () => {
        setTimeout(() => {
          fetchSummaryMetrics();
          fetchLinks();
        }, 800);
      });
    });
  }

  // 4. Fetch Analytics & Leaderboard
  async function fetchAnalytics() {
    try {
      const [topRes, domRes] = await Promise.all([
        fetch('/api/stats/top?limit=10'),
        fetch('/api/stats/domains'),
      ]);

      if (topRes.ok) {
        const topData = await topRes.json();
        renderTopLinks(topData.top_links || topData.top_urls || []);
      }

      if (domRes.ok) {
        const domData = await domRes.json();
        renderDomains(domData.domains || []);
      }
    } catch (err) {
      showToast('Error loading analytics metrics', 'error');
    }
  }

  function renderTopLinks(list) {
    if (!list || list.length === 0) {
      topLinksList.innerHTML = `<div style="color: var(--text-faint); font-size: 0.88rem;">No URL visits logged yet.</div>`;
      return;
    }

    const host = window.location.origin;

    topLinksList.innerHTML = list.map(item => {
      const rankClass = item.rank === 1 ? 'rank-1' : (item.rank === 2 ? 'rank-2' : (item.rank === 3 ? 'rank-3' : ''));
      const fullUrl = `${host}/${item.short_code}`;

      return `
        <div class="leaderboard-item">
          <div class="leaderboard-left">
            <span class="rank-badge ${rankClass}">${item.rank}</span>
            <div class="leaderboard-info">
              <a href="${fullUrl}" target="_blank" class="leaderboard-code">${escapeHtml(item.short_code)}</a>
              <div class="leaderboard-domain">${escapeHtml(item.destination_domain || item.original_url)}</div>
            </div>
          </div>
          <div class="leaderboard-clicks">
            <span>${(item.click_count || 0).toLocaleString()}</span>
            <span style="font-size: 0.72rem; color: var(--text-muted); font-weight: normal;">clicks</span>
          </div>
        </div>
      `;
    }).join('');
  }

  function renderDomains(domains) {
    if (!domains || domains.length === 0) {
      domainDistributionList.innerHTML = `<div style="color: var(--text-faint); font-size: 0.88rem;">No domains cataloged.</div>`;
      return;
    }

    const maxCount = Math.max(...domains.map(d => d.link_count || d.url_count || 1), 1);

    domainDistributionList.innerHTML = domains.slice(0, 8).map(d => {
      const linkCount = d.link_count || d.url_count || 0;
      const percentage = Math.round((linkCount / maxCount) * 100);
      return `
        <div class="domain-bar-item">
          <div class="domain-bar-header">
            <span style="font-weight: 500; color: var(--text-main); font-family: var(--font-mono); font-size: 0.82rem;">${escapeHtml(d.domain)}</span>
            <span style="color: var(--text-muted); font-size: 0.78rem;">${linkCount} links (${(d.total_clicks || 0)} clicks)</span>
          </div>
          <div class="domain-bar-track">
            <div class="domain-bar-fill" style="width: ${percentage}%;"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // 5. Single Shorten Submission
  formShorten.addEventListener('submit', async (e) => {
    e.preventDefault();

    const longUrl = inputLongUrl.value.trim();
    const customCode = inputCustomCode.value.trim();
    const expVal = selectExpiration.value;
    const expParams = parseExpirationValue(expVal);

    if (!longUrl) return;

    const payload = {
      url: longUrl,
      ...(customCode ? { custom_code: customCode } : {}),
      ...expParams,
    };

    try {
      const res = await fetch('/api/shorten', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to shorten URL');
      }

      // Display result box
      resultShortUrlText.textContent = data.short_url;
      resultCodeVal.textContent = data.short_code;
      resultDomainVal.textContent = (new URL(data.original_url)).hostname || '-';
      resultTypeVal.textContent = data.code_type || 'standard_base62';
      resultExpiresVal.textContent = formatDate(data.expires_at);

      btnVisitResult.href = data.short_url;

      resultBox.style.display = 'block';
      showToast('Short link generated successfully', 'success');

      // Refresh overview metrics
      fetchSummaryMetrics();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Copy result button
  btnCopyResult.addEventListener('click', () => {
    const text = resultShortUrlText.textContent;
    if (text && text !== '-') {
      copyTextToClipboard(text, 'Short URL copied to clipboard');
    }
  });

  // 6. Batch Shorten Submission
  formBatch.addEventListener('submit', async (e) => {
    e.preventDefault();

    const text = textareaBatchUrls.value.trim();
    if (!text) return;

    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    if (lines.length === 0) return;

    const expVal = selectBatchExpiration.value;
    const expParams = parseExpirationValue(expVal);

    const payload = {
      urls: lines,
      ...expParams,
    };

    try {
      const res = await fetch('/api/shorten/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Batch shortening failed');

      const items = data.items || [];
      batchCountVal.textContent = items.length;

      batchResultsTbody.innerHTML = items.map(item => `
        <tr>
          <td><span style="font-family: var(--font-mono); color: var(--primary); font-weight: 600;">${escapeHtml(item.short_code)}</span></td>
          <td><div class="table-url-cell" title="${escapeHtml(item.original_url)}">${escapeHtml(item.original_url)}</div></td>
          <td><a href="${item.short_url}" target="_blank" style="color: var(--accent-cyan); font-family: var(--font-mono); font-size: 0.85rem;">${escapeHtml(item.short_url)}</a></td>
          <td>
            <button type="button" class="btn btn-secondary btn-sm" onclick="navigator.clipboard.writeText('${item.short_url}')">
              Copy
            </button>
          </td>
        </tr>
      `).join('');

      batchResultsContainer.style.display = 'block';
      showToast(`Batch completed: ${items.length} links generated`, 'success');

      fetchSummaryMetrics();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // 7. Search & Filter Handlers for Table
  inputTableSearch.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    renderUrlsTable();
  });

  selectTableFilter.addEventListener('change', (e) => {
    state.statusFilter = e.target.value;
    renderUrlsTable();
  });

  btnRefreshTable.addEventListener('click', () => {
    fetchLinks();
    fetchSummaryMetrics();
    showToast('Table refreshed', 'success');
  });

  // 8. Observability & Maintenance Handlers
  btnTriggerCleanup.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/maintenance/cleanup-expired', { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Cleanup failed');

      showToast(`Cleanup executed: ${data.deactivated_count} links deactivated`, 'success');
      fetchSummaryMetrics();
      fetchLinks();
      fetchCloudWatchTelemetry();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  btnFetchCloudwatch.addEventListener('click', () => {
    fetchCloudWatchTelemetry();
    showToast('CloudWatch telemetry refreshed', 'success');
  });

  async function fetchCloudWatchTelemetry() {
    telemetryLog.textContent = 'Querying CloudWatch metrics & system report...';
    try {
      const [cwRes, repRes] = await Promise.all([
        fetch('/api/stats/cloudwatch'),
        fetch('/api/stats/report'),
      ]);

      const cwData = cwRes.ok ? await cwRes.json() : { error: 'CloudWatch fetch failed' };
      const repData = repRes.ok ? await repRes.json() : { error: 'Report fetch failed' };

      const combined = {
        cloud_provider: "AWS (Simulated)",
        architecture_tier: "Compute: ECS Fargate / Storage: SQLite / Monitoring: CloudWatch",
        timestamp: new Date().toISOString(),
        cloudwatch_metrics: cwData,
        system_report: repData,
      };

      telemetryLog.textContent = JSON.stringify(combined, null, 2);
    } catch (err) {
      telemetryLog.textContent = `Telemetry error: ${err.message}`;
    }
  }

  // 9. Stats Modal
  async function openStatsModal(shortCode) {
    statsModal.classList.add('active');
    modalCode.textContent = shortCode;
    modalUrl.textContent = 'Loading...';
    modalDomain.textContent = '-';
    modalClicks.textContent = '-';
    modalCreated.textContent = '-';
    modalAccessed.textContent = '-';
    modalExpires.textContent = '-';
    modalStatus.textContent = '-';

    try {
      const res = await fetch(`/api/urls/${shortCode}/stats`);
      if (!res.ok) throw new Error('Failed to load URL statistics');
      const data = await res.json();

      modalUrl.textContent = data.original_url || '-';
      modalDomain.textContent = data.destination_domain || '-';
      modalClicks.textContent = (data.click_count || 0).toLocaleString();
      modalCreated.textContent = formatDate(data.created_at);
      modalAccessed.textContent = formatDate(data.last_accessed_at);
      modalExpires.textContent = formatDate(data.expires_at);

      if (data.is_expired) {
        modalStatus.innerHTML = `<span class="badge badge-danger">Expired</span>`;
      } else if (data.is_active) {
        modalStatus.innerHTML = `<span class="badge badge-success">Active</span>`;
      } else {
        modalStatus.innerHTML = `<span class="badge badge-warning">Inactive</span>`;
      }
    } catch (err) {
      modalUrl.textContent = `Error: ${err.message}`;
    }
  }

  btnCloseModal.addEventListener('click', () => {
    statsModal.classList.remove('active');
  });

  statsModal.addEventListener('click', (e) => {
    if (e.target === statsModal) {
      statsModal.classList.remove('active');
    }
  });

  // ==========================================
  // Initialization
  // ==========================================
  fetchSummaryMetrics();
  fetchLinks();
});
