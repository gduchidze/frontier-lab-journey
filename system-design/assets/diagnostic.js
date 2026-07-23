/**
 * Diagnostic quiz component. Questions carry a `topic` tag; the results
 * panel scores per topic, shows verdicts as soon as a topic is complete
 * (one-topic-per-sitting friendly), sorts weakest-first, and emits a
 * copy-paste summary. Progress persists in localStorage when a
 * `storageKey` is provided (survives closing the tab; Reset clears it).
 *
 * Usage:
 *   renderDiagnostic(rootEl, {
 *     topics: { t1: { label, lesson, lab }, ... },
 *     questions: [ { topic, q, options, answer, explain }, ... ],
 *     storageKey: 'phase1-diag-v2',
 *   });
 */
function renderDiagnostic(root, config) {
  var state = {};
  Object.keys(config.topics).forEach(function (key) {
    state[key] = { correct: 0, answered: 0, total: 0 };
  });
  config.questions.forEach(function (item) { state[item.topic].total += 1; });

  var answeredTotal = 0;
  var saved = loadSaved();
  var answerLog = {};   // qi -> chosen option index
  var appliers = [];    // qi -> function(oi) applying an answer without re-saving

  var progress = document.createElement('div');
  progress.className = 'score';
  root.appendChild(progress);

  var lastTopic = null;
  config.questions.forEach(function (item, qi) {
    if (item.topic !== lastTopic) {
      lastTopic = item.topic;
      var head = document.createElement('h3');
      head.textContent = config.topics[item.topic].label;
      root.appendChild(head);
    }

    var qEl = document.createElement('p');
    qEl.className = 'q';
    qEl.textContent = (qi + 1) + '. ' + item.q;
    root.appendChild(qEl);

    var optsEl = document.createElement('div');
    optsEl.className = 'options';

    var explainEl = document.createElement('div');
    explainEl.className = 'explain';
    explainEl.textContent = item.explain || '';

    function apply(oi, persist) {
      var buttons = optsEl.querySelectorAll('button.opt');
      if (buttons[0] && buttons[0].disabled) return; // already answered
      buttons.forEach(function (b) { b.disabled = true; });
      var isRight = oi === item.answer;
      buttons[oi].classList.add(isRight ? 'correct' : 'wrong');
      if (!isRight) buttons[item.answer].classList.add('correct');
      explainEl.classList.add('show');
      state[item.topic].answered += 1;
      if (isRight) state[item.topic].correct += 1;
      answeredTotal += 1;
      answerLog[qi] = oi;
      if (persist) save();
      update();
    }
    appliers[qi] = apply;

    item.options.forEach(function (text, oi) {
      var btn = document.createElement('button');
      btn.className = 'opt';
      btn.type = 'button';
      btn.textContent = text;
      btn.addEventListener('click', function () { apply(oi, true); });
      optsEl.appendChild(btn);
    });

    root.appendChild(optsEl);
    root.appendChild(explainEl);
  });

  var results = document.createElement('div');
  results.className = 'score';
  root.appendChild(results);

  var resetBtn = document.createElement('button');
  resetBtn.className = 'opt';
  resetBtn.type = 'button';
  resetBtn.textContent = 'Reset all progress';
  resetBtn.style.marginTop = '1rem';
  resetBtn.addEventListener('click', function () {
    if (!window.confirm('Wipe saved answers and start over?')) return;
    try { if (config.storageKey) localStorage.removeItem(config.storageKey); } catch (e) {}
    window.location.reload();
  });
  root.appendChild(resetBtn);

  function verdict(pct) {
    if (pct >= 0.8) return 'STRONG';
    if (pct >= 0.5) return 'SHAKY';
    return 'GAP';
  }

  function update() {
    progress.textContent = 'Answered ' + answeredTotal + '/' + config.questions.length +
      (config.storageKey ? ' (progress saved — safe to close the tab)' : '');

    var done = [], pending = [];
    Object.keys(config.topics).forEach(function (key) {
      var s = state[key];
      var row = { key: key, label: config.topics[key].label,
                  correct: s.correct, answered: s.answered, total: s.total,
                  pct: s.total ? s.correct / s.total : 0 };
      (s.answered === s.total ? done : pending).push(row);
    });
    done.sort(function (a, b) { return a.pct - b.pct; });

    var html = '';
    if (done.length) {
      html += '<h3>Results so far — weakest first</h3><table><tr>' +
        '<th>Topic</th><th>Score</th><th>Verdict</th><th>Deep-dive</th></tr>';
      var summaryLines = ['PHASE 1 DIAGNOSTIC RESULTS (' + done.length + '/' +
        Object.keys(config.topics).length + ' topics complete):'];
      done.forEach(function (r) {
        var v = verdict(r.pct);
        var t = config.topics[r.key];
        html += '<tr><td>' + r.label + '</td><td>' + r.correct + '/' + r.total +
          '</td><td>' + v + '</td><td>' +
          (v === 'STRONG' ? '—'
            : '<a href="' + t.lesson + '">lesson</a> · <a href="' + t.lab + '">lab</a>') +
          '</td></tr>';
        summaryLines.push(v + '  ' + r.correct + '/' + r.total + '  ' + r.label);
      });
      html += '</table><p><strong>Paste this to your teacher</strong> to plan deep-dives:</p>' +
        '<pre><code>' + summaryLines.join('\n') + '</code></pre>';
    }
    if (pending.length) {
      html += '<p>In progress: ' + pending.map(function (r) {
        return r.label + ' (' + r.answered + '/' + r.total + ')';
      }).join(' · ') + '</p>';
    }
    results.innerHTML = html || 'Answer a full topic block to see its verdict.';
  }

  function save() {
    if (!config.storageKey) return;
    try { localStorage.setItem(config.storageKey, JSON.stringify(answerLog)); } catch (e) {}
  }
  function loadSaved() {
    if (!config.storageKey) return {};
    try { return JSON.parse(localStorage.getItem(config.storageKey) || '{}'); } catch (e) { return {}; }
  }

  Object.keys(saved).forEach(function (qi) {
    var i = parseInt(qi, 10);
    if (appliers[i]) appliers[i](saved[qi], false);
  });
  update();
}
