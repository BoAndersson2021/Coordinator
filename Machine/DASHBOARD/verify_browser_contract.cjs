// Deterministic DOM/clock/network contract tests of the actual dashboard script.
// This is a maintenance harness, not a browser rendering or runtime qualification.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(__dirname + '/candidate/src/dashboard_assets/dashboard.js', 'utf8');
class Element {
  constructor() {
    this.children = []; this.attributes = {}; this.classes = new Set();
    this.classList = {add: name => this.classes.add(name), remove: name => this.classes.delete(name)};
  }
  set innerHTML(_) { throw Error('Unsafe HTML injection'); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(key, value) { this.attributes[key] = value; }
}
function harness(token = true) {
  const elements = new Map();
  const intervals = [];
  const callbacks = new Map();
  const state = {now: Date.now(), mono: 1, mode: 'ok', instance: 'first', requests: []};
  const element = id => { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); };
  const body = new Element();
  const document = {body, hidden: false, getElementById: element, createElement: () => new Element(), addEventListener: (event, fn) => callbacks.set(event, fn)};
  class ClockDate extends Date { static now() { return state.now; } }
  const observation = () => ({workflow_invariant: {workflow_ready: state.mode === 'false-ready' ? true : false}, observation_scope: 'local_ledger_only', observed_at: new Date(state.now).toISOString(), stale_seconds: 8,
    counts: {tasks: 1, live_receivers_proven: 0, reports_retained: 0, reviews_retained: 0},
    service: {pid: 123, instance: state.instance, supervisor: 'launchd'},
    tasks: [{id: '<img src=x onerror=bad()>', project: 'project', agent: 'role', ledger_state: 'delivered', attempts: 1, delivery: 'Receipt retained; execution not established', receiver: 'Live execution not established', report_retained: false, review_retained: false, evidence_at: '2020-01-01T00:00:00Z', evidence_source: 'Historical ledger', attempt_id: 'exact-attempt'}]});
  vm.runInNewContext(source, {document, location: {hash: token ? '#token=private-test-token' : ''}, URLSearchParams, Date: ClockDate, performance: {now: () => state.mono}, AbortController,
    setInterval: (fn, milliseconds) => intervals.push({fn, milliseconds}), setTimeout: () => 1, clearTimeout() {},
    window: {addEventListener: (event, fn) => callbacks.set(event, fn)},
    fetch: async (url, options) => {
      state.requests.push({url, options});
      if (state.mode === 'offline') throw Error('Connection lost');
      return {ok: state.mode !== 'corrupt', status: state.mode === 'corrupt' ? 503 : 200, json: async () => observation()};
    }
  });
  return {state, element, intervals, callbacks, body};
}
const flush = () => new Promise(resolve => setImmediate(resolve));
(async () => {
  const h = harness(); await flush();
  assert.equal(h.element('connection').textContent, 'LEDGER CONNECTED');
  assert.equal(h.element('receivers-count').textContent, '0');
  assert.equal(h.element('reports-count').textContent, '0');
  assert.equal(h.state.requests[0].options.headers['X-Machine-Token'], 'private-test-token');
  assert.equal(h.state.requests[0].options.redirect, 'error');
  assert.equal(h.element('tasks').children[0].children[0].children[0].children[0].textContent, '<img src=x onerror=bad()>');
  const repeat = h.intervals.find(t => t.milliseconds === 2000).fn;
  const watchdog = h.intervals.find(t => t.milliseconds === 500).fn;
  h.state.now += 9000; h.state.mono += 9000; watchdog();
  assert.equal(h.element('connection').textContent, 'STALE / DISCONNECTED');
  assert.equal(h.element('refresh-error').hidden, false);
  h.state.instance = 'second'; await repeat();
  assert.equal(h.element('connection').textContent, 'LEDGER CONNECTED');
  assert.match(h.element('service').textContent, /1 reconnection restart observed/);
  for (const mode of ['offline', 'corrupt', 'false-ready']) {
    h.state.mode = mode; await repeat();
    assert.equal(h.element('connection').textContent, 'STALE / DISCONNECTED');
    assert.equal(h.element('refresh-error').hidden, false);
  }
  h.state.mode = 'ok'; await repeat();
  assert.equal(h.element('connection').textContent, 'LEDGER CONNECTED');
  const noToken = harness(false); await flush();
  assert.equal(noToken.state.requests.length, 0);
  assert.match(noToken.element('refresh-error').textContent, /authorization is missing/);
  console.log('PASS: actual dashboard JavaScript refresh, stale watchdog, disconnect, 503, invalid readiness, automatic reconnect, restart indication, missing auth, and literal-text rendering.');
})().catch(error => { console.error(error); process.exit(1); });
