var PHASE0_BANK_B1 = [
  {
    topic: 'b1',
    q: 'What defines self-supervised learning, as used to pretrain large language models?',
    options: [
      'Labels are derived automatically from the input data itself',
      'Labels are assigned manually by human annotators before training',
      'Labels are absent entirely and clusters emerge without supervision'
    ],
    answer: 0,
    explain: 'Self-supervised learning creates its own labels from the raw data, as in next-token prediction for language models.'
  },
  {
    topic: 'b1',
    q: 'Why is cross-entropy loss preferred over MSE for training softmax classifiers?',
    options: [
      'It always guarantees convergence to the global loss minimum',
      'It gives strong gradients when predicted probabilities are wrong',
      'It runs faster because it avoids computing any squares'
    ],
    answer: 1,
    explain: 'With softmax outputs, cross-entropy yields large gradients for confident wrong predictions, while MSE gradients vanish and stall learning.'
  },
  {
    topic: 'b1',
    q: 'Which regularizer tends to drive many weights exactly to zero, producing sparse models?',
    options: [
      'L2, whose squared penalty shrinks weights smoothly toward zero',
      'Dropout, whose random unit removal forces weights toward zero',
      'L1, whose constant-magnitude gradient snaps small weights to zero'
    ],
    answer: 2,
    explain: 'The L1 penalty has constant gradient magnitude everywhere, so it pushes small weights exactly to zero and yields sparse models.'
  },
  {
    topic: 'b1',
    q: 'What does dropout actually do during training?',
    options: [
      'Randomly zeroes activations, preventing units from co-adapting too strongly',
      'Randomly deletes training examples, preventing the model from memorizing',
      'Randomly shrinks learning rates, preventing the optimizer from overshooting'
    ],
    answer: 0,
    explain: 'Dropout randomly zeroes unit activations on each forward pass, preventing co-adaptation and acting as a regularizer.'
  },
  {
    topic: 'b1',
    q: 'Why does a smaller SGD batch size often improve generalization?',
    options: [
      'Smaller batches compute exact gradients that avoid sharp minima',
      'Gradient noise from small batches helps escape sharp minima',
      'Smaller batches raise effective learning rates, guaranteeing flatter minima'
    ],
    answer: 1,
    explain: 'Small-batch gradient noise perturbs the optimization trajectory enough to escape sharp minima, which correlates with better generalization.'
  },
  {
    topic: 'b1',
    q: 'A binary classifier has AUC-ROC of 0.9. What does that number mean?',
    options: [
      'The model classifies 90 percent of all examples correctly',
      'The model achieves 90 percent precision at every threshold',
      'Random positives outscore random negatives 90 percent of time'
    ],
    answer: 2,
    explain: 'AUC-ROC is the probability that a randomly chosen positive receives a higher score than a randomly chosen negative.'
  },
  {
    topic: 'b1',
    q: 'Which quantity should early stopping monitor to decide when training halts?',
    options: [
      'Training loss, halting once it stops decreasing between epochs',
      'Validation loss, halting once it stops improving between epochs',
      'Test loss, halting once it stops improving between epochs'
    ],
    answer: 1,
    explain: 'Early stopping halts when held-out validation performance stops improving; using the test set for this decision would leak test information.'
  },
  {
    topic: 'b1',
    q: 'Training loss keeps falling while validation loss falls, bottoms out, then climbs after epoch ten. Diagnosis and fix?',
    options: [
      'Overfitting; add regularization or stop training around epoch ten',
      'Underfitting; increase model capacity and train for far longer',
      'Leakage; validation examples are contaminating the training data split'
    ],
    answer: 0,
    explain: 'Diverging train and validation loss is the classic overfitting signature; regularize or stop near the validation minimum.'
  },
  {
    topic: 'b1',
    q: 'Both training and validation losses plateau at similarly high values. What is the right move?',
    options: [
      'Add dropout and stronger L2 so the model generalizes',
      'Collect more training data so the model generalizes better',
      'Increase model capacity or features since it is underfitting'
    ],
    answer: 2,
    explain: 'High loss on both splits means the model cannot even fit the training data, so add capacity or better features rather than regularization.'
  },
  {
    topic: 'b1',
    q: 'You fit a StandardScaler on the full dataset, then split into train and test. What went wrong?',
    options: [
      'Nothing; scaling is deterministic so split order never matters',
      'Test statistics leaked into preprocessing, inflating measured test performance',
      'The scaler destroyed feature variance, deflating measured test performance'
    ],
    answer: 1,
    explain: 'Fitting the scaler on all data lets test-set means and variances influence preprocessing, a subtle form of leakage.'
  },
  {
    topic: 'b1',
    q: 'For churn prediction you randomly shuffle three years of user events into train and test splits. Main risk?',
    options: [
      'Future information leaks backward, so offline metrics overstate production performance',
      'Class imbalance worsens sharply, so offline metrics understate production performance',
      'Gradient variance increases, so training diverges before reaching production performance'
    ],
    answer: 0,
    explain: 'Random splits on temporal data let the model train on events that happen after test events, leaking the future.'
  },
  {
    topic: 'b1',
    q: 'A fraud model scores 99.8 percent accuracy on data with 0.2 percent fraud cases. What should you check first?',
    options: [
      'Its AUC-ROC, since accuracy ignores ranking quality on positives',
      'Its calibration curve, since accuracy ignores probability estimates entirely',
      'Its precision and recall, since predicting all-negative scores identically'
    ],
    answer: 2,
    explain: 'With 0.2 percent positives, a model that always predicts negative also scores 99.8 percent accuracy, so precision and recall on fraud cases reveal real skill.'
  },
  {
    topic: 'b1',
    q: 'For an initial cancer screening test where missed cases are catastrophic, which metric should dominate?',
    options: [
      'Recall, because false negatives cost far more than false positives',
      'Precision, because false positives cost far more than false negatives',
      'Accuracy, because balanced errors matter more than either failure mode'
    ],
    answer: 0,
    explain: 'A missed cancer case is far worse than an unnecessary follow-up test, so screening prioritizes recall over precision.'
  },
  {
    topic: 'b1',
    q: 'An email spam filter where flagging real mail as spam is very costly should primarily optimize which metric?',
    options: [
      'Recall, so nearly every spam message gets caught reliably',
      'Precision, so nearly every flagged message is truly spam',
      'Accuracy, so nearly every message gets the correct label'
    ],
    answer: 1,
    explain: 'When false positives are the costly error, precision measures exactly how trustworthy each spam flag is.'
  },
  {
    topic: 'b1',
    q: 'Training loss oscillates wildly and occasionally explodes to NaN within the first few epochs. Most likely cause?',
    options: [
      'Batch size too large, making the gradient estimates unstable',
      'Excessive dropout regularization, making the gradient estimates numerically unstable',
      'Learning rate too high, making the update steps overshoot'
    ],
    answer: 2,
    explain: 'Oscillating or exploding loss early in training is the textbook sign of a learning rate that is too high.'
  },
  {
    topic: 'b1',
    q: 'After fifty rounds of tuning hyperparameters against the test set, test accuracy looks excellent. Why should you distrust it?',
    options: [
      'Fifty rounds is insufficient tuning, so accuracy remains badly underestimated',
      'Repeated test-set evaluation overfits selection, so accuracy is optimistically biased',
      'Hyperparameter tuning always harms generalization, so accuracy is pessimistically biased'
    ],
    answer: 1,
    explain: 'Selecting hyperparameters by repeatedly peeking at the test set overfits to it, so the estimate is no longer an unbiased measure of generalization.'
  },
  {
    topic: 'b1',
    q: 'A classifier produces TP=40, FP=10, FN=20, TN=930. What is its precision?',
    options: [
      '0.80',
      '0.67',
      '0.95'
    ],
    answer: 0,
    explain: 'Precision is TP / (TP + FP) = 40 / 50 = 0.80.'
  },
  {
    topic: 'b1',
    q: 'Same classifier: TP=40, FP=10, FN=20, TN=930. What is its recall, roughly?',
    options: [
      '0.80',
      '0.67',
      '0.33'
    ],
    answer: 1,
    explain: 'Recall is TP / (TP + FN) = 40 / 60, which is about 0.67.'
  },
  {
    topic: 'b1',
    q: 'You raise the decision threshold of a binary classifier from 0.5 to 0.8. What typically happens?',
    options: [
      'Precision rises while recall falls as fewer positives get flagged',
      'Recall rises while precision falls as fewer positives get flagged',
      'Both metrics rise together since fewer borderline positives get flagged'
    ],
    answer: 0,
    explain: 'A higher threshold flags fewer but more confident positives, which usually raises precision and lowers recall.'
  },
  {
    topic: 'b1',
    q: 'On 1000 samples with 10 positives, a model predicts everything negative. Its accuracy and recall are?',
    options: [
      'Accuracy 0.90 and recall 0.10',
      'Accuracy 0.99 and recall 1.00',
      'Accuracy 0.99 and recall 0.00'
    ],
    answer: 2,
    explain: 'It gets 990 of 1000 correct for 0.99 accuracy while catching zero of ten positives, so recall is 0.00.'
  }
];
