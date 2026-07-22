/**
 * Reusable quiz component. Immediate per-question feedback + running score.
 *
 * Usage in a lesson:
 *   <div class="quiz" id="quiz"></div>
 *   <script src="../assets/quiz.js"></script>
 *   <script>
 *     renderQuiz(document.getElementById('quiz'), {
 *       title: 'Check yourself',
 *       questions: [
 *         {
 *           q: 'Question text?',
 *           options: ['A', 'B', 'C'],   // keep answers the same word count
 *           answer: 1,                  // index into options
 *           explain: 'Why B is right.'
 *         },
 *       ],
 *     });
 *   </script>
 */
function renderQuiz(root, config) {
  const state = { answered: 0, correct: 0 };

  const heading = document.createElement('h3');
  heading.textContent = config.title || 'Check yourself';
  root.appendChild(heading);

  config.questions.forEach((item, qi) => {
    const qEl = document.createElement('p');
    qEl.className = 'q';
    qEl.textContent = (qi + 1) + '. ' + item.q;
    root.appendChild(qEl);

    const optsEl = document.createElement('div');
    optsEl.className = 'options';

    const explainEl = document.createElement('div');
    explainEl.className = 'explain';
    explainEl.textContent = item.explain || '';

    item.options.forEach((text, oi) => {
      const btn = document.createElement('button');
      btn.className = 'opt';
      btn.type = 'button';
      btn.textContent = text;
      btn.addEventListener('click', () => {
        const buttons = optsEl.querySelectorAll('button.opt');
        buttons.forEach((b) => (b.disabled = true));
        const isRight = oi === item.answer;
        btn.classList.add(isRight ? 'correct' : 'wrong');
        if (!isRight) buttons[item.answer].classList.add('correct');
        explainEl.classList.add('show');
        state.answered += 1;
        if (isRight) state.correct += 1;
        updateScore();
      });
      optsEl.appendChild(btn);
    });

    root.appendChild(optsEl);
    root.appendChild(explainEl);
  });

  const scoreEl = document.createElement('div');
  scoreEl.className = 'score';
  root.appendChild(scoreEl);

  function updateScore() {
    const total = config.questions.length;
    scoreEl.textContent = 'Score: ' + state.correct + '/' + state.answered + ' answered (' + total + ' total)';
    if (state.answered === total) {
      scoreEl.textContent += state.correct === total
        ? ' — perfect. Tell your teacher: ready for the next lesson.'
        : ' — review the explanations above, then ask your teacher about the ones you missed.';
    }
  }
  updateScore();
}
