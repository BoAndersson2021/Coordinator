'use strict';
(() => {
  const token = new URLSearchParams(location.hash.slice(1)).get('token');
  const $ = id => document.getElementById(id);
  let lastSuccess = 0;
  let lastObservation = 0;
  let staleSeconds = 8;
  let busy = false;
  let lastInstance = null;
  let restartCount = 0;
  let failed = false;

  function text(tag, value, className) {
    const element = document.createElement(tag);
    element.textContent = value;
    if (className) element.className = className;
    return element;
  }

  function disconnected(reason) {
    failed = true;
    document.body.classList.add('disconnected');
    $('observations').classList.add('stale');
    $('observations').setAttribute('aria-busy', 'true');
    $('connection').className = 'connection offline';
    $('connection').textContent = 'STALE / DISCONNECTED';
    $('refresh-error').hidden = false;
    $('refresh-error').textContent = reason + ' Displayed records are stale. Workflow execution remains blocked. Automatic reconnection continues.';
  }

  function gauge(name, count, total) {
    $(name + '-count').textContent = String(count);
    const fraction = total > 0 ? Math.max(0, Math.min(1, count / total)) : 0;
    $(name + '-ring').setAttribute('stroke-dashoffset', String(263.894 * (1 - fraction)));
  }

  function taskCard(task) {
    const card = text('article', '', 'task');
    const heading = text('div', '', 'task-heading');
    const identity = text('div', '');
    identity.append(text('h3', task.id), text('p', task.project + ' / ' + task.agent, 'project'));
    heading.append(identity, text('span', 'ledger: ' + task.ledger_state, 'ledger-state'));
    const facts = text('dl', '', 'task-facts');
    for (const [label, value, warning] of [
      ['DELIVERY', task.delivery, false],
      ['RECEIVING EXECUTION', task.receiver, true],
      ['COMPLETION EVIDENCE', task.report_retained ? 'Historical report retained' : 'No completed report retained', !task.report_retained],
      ['VERIFICATION', task.review_retained ? 'Historical review retained · ' + (task.historical_verdict || 'verdict not summarized') : 'No review retained', !task.review_retained]
    ]) {
      const fact = text('div', '', 'fact');
      fact.append(text('dt', label), text('dd', value, warning ? 'warning' : ''));
      facts.append(fact);
    }
    const evidence = text('div', '', 'task-evidence');
    evidence.append(text('span', 'EVIDENCE TIME · ' + (task.evidence_at ? new Date(task.evidence_at).toLocaleString() : 'Not recorded')),
      text('span', 'ATTEMPTS · ' + task.attempts), text('span', 'SOURCE · ' + task.evidence_source));
    if (task.attempt_id) evidence.append(text('span', 'ATTEMPT · ' + task.attempt_id));
    card.append(heading, facts, evidence);
    return card;
  }

  function render(body) {
    if (body.workflow_invariant?.workflow_ready !== false || body.observation_scope !== 'local_ledger_only' || !Array.isArray(body.tasks)) {
      throw new Error('Unexpected observation contract');
    }
    const observed = Date.parse(body.observed_at);
    if (!Number.isFinite(observed) || Math.abs(Date.now() - observed) > 8000) throw new Error('Observation is stale or has an invalid timestamp');
    const counts = body.counts;
    if (lastInstance && lastInstance !== body.service.instance) restartCount++;
    lastInstance = body.service.instance;
    staleSeconds = body.stale_seconds;
    gauge('tasks', counts.tasks, counts.tasks);
    gauge('receivers', counts.live_receivers_proven, counts.tasks);
    gauge('reports', counts.reports_retained, counts.tasks);
    gauge('reviews', counts.reviews_retained, counts.tasks);
    $('receivers-note').textContent = 'Live runtime is not observed · ' + counts.tasks + ' retained tasks';
    $('tasks').replaceChildren(...body.tasks.map(taskCard));
    if (!body.tasks.length) $('tasks').append(text('div', 'No assignments in this ledger. This does not establish workflow readiness.', 'empty'));
    $('task-total').textContent = counts.tasks + ' retained assignment' + (counts.tasks === 1 ? '' : 's');
    $('last-read').textContent = new Date(observed).toLocaleString();
    $('service').textContent = 'PID ' + body.service.pid + ' · ' + restartCount + ' reconnection restart' + (restartCount === 1 ? '' : 's') + ' observed';
    $('supervision').textContent = 'Dashboard · ' + body.service.supervisor + ' · automatic refresh every 2s';
    $('connection').className = 'connection online';
    $('connection').textContent = 'LEDGER CONNECTED';
    $('refresh-error').hidden = true;
    $('observations').classList.remove('stale');
    $('observations').setAttribute('aria-busy', 'false');
    document.body.classList.remove('disconnected');
    failed = false;
    lastObservation = observed;
    lastSuccess = performance.now();
  }

  async function refresh() {
    if (busy) return;
    if (!token) { disconnected('Dashboard authorization is missing.'); return; }
    busy = true;
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 4000);
      let response;
      try { response = await fetch('/api/snapshot', {headers: {'X-Machine-Token': token}, cache: 'no-store', signal: controller.signal, redirect: 'error'}); }
      finally { clearTimeout(timeout); }
      if (!response.ok) throw new Error('Local observation failed (HTTP ' + response.status + ')');
      render(await response.json());
    } catch (error) {
      disconnected(error.name === 'AbortError' ? 'Local observation timed out.' : error.message + '.');
    } finally { busy = false; }
  }

  setInterval(() => {
    if (lastSuccess && (performance.now() - lastSuccess > staleSeconds * 1000 || Date.now() - lastObservation > staleSeconds * 1000) && !failed) {
      disconnected('The last successful ledger observation is older than ' + staleSeconds + ' seconds.');
    }
  }, 500);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      if (lastSuccess && Date.now() - lastObservation > staleSeconds * 1000) disconnected('The page resumed with stale observations.');
      refresh();
    }
  });
  window.addEventListener('online', refresh);
  setInterval(refresh, 2000);
  refresh();
})();
