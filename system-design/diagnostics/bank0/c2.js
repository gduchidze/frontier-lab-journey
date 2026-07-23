var PHASE0_BANK_C2 = [
  {
    topic: 'c2',
    q: 'What does the derivative of a function at a point fundamentally measure?',
    options: [
      'How sensitively the output changes when the input nudges slightly',
      'The total area accumulated under the curve before that point',
      'The average output value the function takes across its domain'
    ],
    answer: 0,
    explain: 'The derivative is local sensitivity: the slope of the best linear approximation, telling you how much output moves per tiny input nudge.'
  },
  {
    topic: 'c2',
    q: 'Why is backpropagation often described as just the chain rule applied to a computation graph?',
    options: [
      'It approximates derivatives numerically by evaluating the loss at many nearby points',
      'It multiplies local derivatives along each path of the network computation graph',
      'It replaces every nonlinear activation with a linear surrogate before computing gradients'
    ],
    answer: 1,
    explain: 'Backprop walks the graph backward multiplying each node local derivative, which is exactly the chain rule applied path by path.'
  },
  {
    topic: 'c2',
    q: 'In which direction does the gradient of a multivariable function point?',
    options: [
      'Toward the nearest local minimum of the function',
      'Along the contour line where the function flattens',
      'Toward the direction of steepest increase in output'
    ],
    answer: 2,
    explain: 'The gradient collects all partial derivatives into the direction of steepest ascent, which is why descent steps go the opposite way.'
  },
  {
    topic: 'c2',
    q: 'What does the partial derivative of f(x, y) with respect to x represent?',
    options: [
      'Sensitivity of f to x while holding y fixed',
      'Sensitivity of f when x and y change together',
      'The steepest slope of f across all possible directions'
    ],
    answer: 0,
    explain: 'A partial derivative freezes every other variable and asks how the output responds to nudging just that one input.'
  },
  {
    topic: 'c2',
    q: 'During training the loss bounces wildly and then grows without bound. What is the most likely cause?',
    options: [
      'The learning rate is too small to make progress',
      'The learning rate is too large, overshooting each step',
      'The gradient computation is disconnected from the loss function'
    ],
    answer: 1,
    explain: 'An oversized learning rate makes each step overshoot the valley, so updates bounce past the minimum and eventually diverge.'
  },
  {
    topic: 'c2',
    q: 'Loss decreases smoothly but after many epochs it has barely moved. What is the most likely fix?',
    options: [
      'Increase the learning rate a bit',
      'Decrease the learning rate a lot',
      'Restart training from the same weights'
    ],
    answer: 0,
    explain: 'Smooth but glacial progress is the classic too-small learning rate symptom, so nudging the step size up usually helps.'
  },
  {
    topic: 'c2',
    q: 'What is the derivative of f(x) = 3x^2 evaluated at x = 2?',
    options: [
      '6',
      '24',
      '12'
    ],
    answer: 2,
    explain: 'The power rule gives f\'(x) = 6x, and plugging in x = 2 yields 12.'
  },
  {
    topic: 'c2',
    q: 'Gradient descent uses learning rate 0.5 to update w = 4 where the gradient is 2. What is the new w?',
    options: [
      '5',
      '3',
      '2'
    ],
    answer: 1,
    explain: 'The update rule w - lr * grad gives 4 - 0.5 * 2 = 3.'
  },
  {
    topic: 'c2',
    q: 'A pipeline computes y from x, then z from y. A small change in x scales y by 3, and a change in y scales z by 2. How sensitive is z to x?',
    options: [
      'Factor 5, sensitivities add',
      'Factor 6, sensitivities multiply',
      'Factor 2, downstream dominates'
    ],
    answer: 1,
    explain: 'The chain rule multiplies sensitivities along the pipeline, so dz/dx = 2 * 3 = 6.'
  },
  {
    topic: 'c2',
    q: 'Why does gradient descent subtract the gradient rather than add it?',
    options: [
      'The negative gradient points toward the locally steepest decrease',
      'Subtraction keeps the weights positive throughout the training run',
      'Adding the gradient would make the update step undefined'
    ],
    answer: 0,
    explain: 'Since the gradient points uphill, stepping against it moves the parameters in the direction of fastest local loss decrease.'
  },
  {
    topic: 'c2',
    q: 'What does it mean for a loss function to be convex?',
    options: [
      'It has many local minima separated by high barriers',
      'Its gradient is constant everywhere across the parameter space',
      'Any local minimum found is also the global minimum'
    ],
    answer: 2,
    explain: 'A convex bowl has no misleading valleys, so wherever descent bottoms out is guaranteed to be the global optimum.'
  },
  {
    topic: 'c2',
    q: 'Neural network losses are non-convex, yet SGD trains them well in practice. Which observation best explains this?',
    options: [
      'High-dimensional losses have many good minima and noise helps escape traps',
      'SGD secretly converts the non-convex loss into an equivalent convex one',
      'Modern networks are actually convex once you add enough hidden layers'
    ],
    answer: 0,
    explain: 'In high dimensions most bad critical points are escapable saddles, plenty of minima generalize well, and SGD noise jostles past traps.'
  },
  {
    topic: 'c2',
    q: 'In high-dimensional loss landscapes, which critical point is far more common than a true local minimum?',
    options: [
      'A global maximum with flat curvature',
      'A saddle point with mixed curvature',
      'A discontinuity where gradients stop existing'
    ],
    answer: 1,
    explain: 'With millions of dimensions it is rare for curvature to be positive in every direction at once, so saddle points dominate.'
  },
  {
    topic: 'c2',
    q: 'What is the derivative of f(x) = e^(2x)?',
    options: [
      'e^(2x)',
      '2x*e^(2x)',
      '2e^(2x)'
    ],
    answer: 2,
    explain: 'The exponential reproduces itself and the chain rule multiplies by the inner derivative 2, giving 2e^(2x).'
  },
  {
    topic: 'c2',
    q: 'What is the gradient of f(x, y) = x^2 + y^2 at the point (1, 2)?',
    options: [
      '(1, 2)',
      '(2, 4)',
      '(4, 2)'
    ],
    answer: 1,
    explain: 'The partials are 2x and 2y, which evaluate to (2, 4) at the point (1, 2).'
  },
  {
    topic: 'c2',
    q: 'What is the derivative of f(x) = x^3 + x evaluated at x = 1?',
    options: [
      '4',
      '3',
      '2'
    ],
    answer: 0,
    explain: 'Differentiating gives f\'(x) = 3x^2 + 1, which equals 4 at x = 1.'
  },
  {
    topic: 'c2',
    q: 'Using the chain rule, what is the derivative of h(x) = (2x + 1)^2 at x = 1?',
    options: [
      '6',
      '9',
      '12'
    ],
    answer: 2,
    explain: 'The chain rule gives h\'(x) = 2(2x + 1) * 2 = 4(2x + 1), which is 12 at x = 1.'
  },
  {
    topic: 'c2',
    q: 'The gradient of the loss with respect to one weight is a large positive number. What does this tell you?',
    options: [
      'That weight has almost no influence on the loss',
      'Slightly increasing that weight would noticeably increase the loss',
      'That weight has already converged to its optimal value'
    ],
    answer: 1,
    explain: 'A large positive partial derivative means the loss is very sensitive to that weight and rises when the weight is nudged up.'
  },
  {
    topic: 'c2',
    q: 'Why is backpropagation efficient compared to numerically nudging each weight separately?',
    options: [
      'It reuses shared intermediate derivatives while sweeping the graph backward',
      'It skips computing gradients for layers close to the input',
      'It only ever computes gradients for one randomly chosen weight'
    ],
    answer: 0,
    explain: 'One backward sweep shares the chain rule intermediate products across all weights, instead of one full forward pass per weight.'
  },
  {
    topic: 'c2',
    q: 'Training stalls with the gradient near zero, but the loss is clearly not at a good minimum. What is a likely situation?',
    options: [
      'The loss function must be convex around this point',
      'The learning rate is too large for stable convergence',
      'Optimization is stuck near a saddle point or plateau'
    ],
    answer: 2,
    explain: 'A near-zero gradient at a poor loss value signals a saddle point or flat plateau, where SGD noise or momentum usually helps escape.'
  }
];
