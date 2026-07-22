// Shared quiz component. Usage in a lesson:
// <div class="quiz" data-quiz>
//   <h3>Check yourself</h3>
//   <div class="q">
//     <p class="stem">Question text?</p>
//     <button class="opt" data-correct>Right answer</button>
//     <button class="opt">Wrong answer</button>
//     <p class="explain">Why the right answer is right.</p>
//   </div>
// </div>
(function () {
  document.querySelectorAll("[data-quiz] .q").forEach(function (q) {
    q.querySelectorAll(".opt").forEach(function (opt) {
      opt.addEventListener("click", function () {
        if (q.classList.contains("answered")) return;
        q.classList.add("answered");
        if (opt.hasAttribute("data-correct")) {
          opt.classList.add("correct");
        } else {
          opt.classList.add("wrong");
          var right = q.querySelector("[data-correct]");
          if (right) right.classList.add("correct");
        }
      });
    });
  });
})();
