var PHASE0_BANK_C1 = [
  {
    topic: 'c1',
    q: 'Why do embedding systems typically use cosine similarity to compare vectors?',
    options: [
      'It is always faster to compute than dot products',
      'It measures direction alignment while ignoring differences in magnitude',
      'It guarantees every similarity score is exactly zero centered'
    ],
    answer: 1,
    explain: 'Cosine similarity normalizes out vector length, so it compares only direction, which is what carries semantic meaning in embeddings.'
  },
  {
    topic: 'c1',
    q: 'What is the dot product of [1, 2, 3] and [4, 0, -1]?',
    options: ['1', '7', '12'],
    answer: 0,
    explain: 'Multiply matching components and sum: 1*4 + 2*0 + 3*(-1) = 4 + 0 - 3 = 1.'
  },
  {
    topic: 'c1',
    q: 'A is 4x8, B is 8x2, C is 2x5; what shape is the product (AB)C?',
    options: ['8x5', '4x2', '4x5'],
    answer: 2,
    explain: 'AB is 4x2 because the inner dimension 8 cancels, and multiplying by the 2x5 matrix C leaves 4x5.'
  },
  {
    topic: 'c1',
    q: 'In the 3Blue1Brown view, what does the matrix product AB represent?',
    options: [
      'Adding the two transformations elementwise into one map',
      'Applying transformation B first, then applying transformation A',
      'Averaging the two transformations into a blended map'
    ],
    answer: 1,
    explain: 'Matrix multiplication composes linear maps, and in AB the right-hand matrix B acts on the vector first.'
  },
  {
    topic: 'c1',
    q: 'Using the 2mnp rule, how many FLOPs does a 100x200 times 200x50 matmul take?',
    options: ['2,000,000', '1,000,000', '4,000,000'],
    answer: 0,
    explain: 'Each of the 100x50 outputs needs 200 multiplies and 200 adds, giving 2*100*200*50 = 2,000,000 FLOPs.'
  },
  {
    topic: 'c1',
    q: 'Why does AB generally not equal BA for matrices?',
    options: [
      'Matrix entries are stored in different memory layouts',
      'Matrix products are only defined for square inputs',
      'Applying transformations in a different order changes results'
    ],
    answer: 2,
    explain: 'Matrix multiplication is composition of transformations, and rotating then shearing is generally not the same as shearing then rotating.'
  },
  {
    topic: 'c1',
    q: 'What does taking the transpose of a matrix do?',
    options: [
      'It flips the matrix across its main diagonal',
      'It reverses the sign of every matrix entry',
      'It inverts the transformation that the matrix represents'
    ],
    answer: 0,
    explain: 'Transposing swaps rows and columns, so the entry at position (i, j) moves to position (j, i).'
  },
  {
    topic: 'c1',
    q: 'Why does attention use dot products between query and key vectors?',
    options: [
      'Dot products always produce probability values between zero and one',
      'Dot products score how well each key matches the query',
      'Dot products guarantee the attention weights sum exactly to one'
    ],
    answer: 1,
    explain: 'A dot product measures alignment between two vectors, so query-key dot products give raw relevance scores that softmax later normalizes.'
  },
  {
    topic: 'c1',
    q: 'What is the L2 norm of the vector [3, 4]?',
    options: ['7', '1', '5'],
    answer: 2,
    explain: 'The L2 norm is sqrt(3^2 + 4^2) = sqrt(25) = 5, while 7 would be the L1 norm.'
  },
  {
    topic: 'c1',
    q: 'How is the L1 norm of a vector computed?',
    options: [
      'Sum the absolute values of all its components',
      'Take the square root of the summed squares',
      'Take the largest absolute value among its components'
    ],
    answer: 0,
    explain: 'The L1 norm adds up absolute values of components, while L2 squares them, sums, and takes the square root.'
  },
  {
    topic: 'c1',
    q: 'You compare document embeddings whose lengths vary with document size; which metric is usually preferred?',
    options: [
      'Euclidean distance, because it accounts for embedding magnitude directly',
      'Cosine similarity, because it ignores magnitude and compares direction',
      'Manhattan distance, because it sums coordinate differences more robustly'
    ],
    answer: 1,
    explain: 'When magnitude reflects irrelevant factors like document length, cosine similarity compares only direction, which carries the meaning.'
  },
  {
    topic: 'c1',
    q: 'A 3x7 matrix multiplies a 7x4 matrix; what is the result shape?',
    options: ['7x7', '3x7', '3x4'],
    answer: 2,
    explain: 'The inner dimension 7 must match and cancels, leaving the outer dimensions 3 and 4.'
  },
  {
    topic: 'c1',
    q: 'What is special about an eigenvector of a transformation?',
    options: [
      'It always has a length of exactly one',
      'It stays on its own span, only scaled',
      'It always points along a coordinate axis direction'
    ],
    answer: 1,
    explain: 'An eigenvector is only stretched or flipped by its eigenvalue, never knocked off its own line by the transformation.'
  },
  {
    topic: 'c1',
    q: 'What does the rank of a matrix intuitively measure?',
    options: [
      'The number of independent directions the output spans',
      'The number of nonzero entries in the matrix',
      'The number of rows minus number of columns'
    ],
    answer: 0,
    explain: 'Rank counts the dimensions of the output space, so it reflects how much independent information the transformation preserves.'
  },
  {
    topic: 'c1',
    q: 'Why can LoRA represent a weight update with two small matrices A and B?',
    options: [
      'Because weight updates are always exactly diagonal matrices anyway',
      'Because small matrices multiply faster than sparse matrices do',
      'Because fine-tuning updates are approximately low rank in practice'
    ],
    answer: 2,
    explain: 'LoRA factors the update as BA with a tiny inner dimension, which works because fine-tuning changes have low effective rank.'
  },
  {
    topic: 'c1',
    q: 'A 1000x1000 weight uses rank-8 LoRA factors of shape 1000x8 and 8x1000; how many LoRA parameters are trained?',
    options: ['8,000', '16,000', '64,000'],
    answer: 1,
    explain: 'The two factors contribute 1000*8 plus 8*1000 parameters, totaling 16,000 instead of the original 1,000,000.'
  },
  {
    topic: 'c1',
    q: 'What is the L1 norm of the vector [-2, 3, -1]?',
    options: ['6', '0', '14'],
    answer: 0,
    explain: 'The L1 norm sums absolute values: 2 + 3 + 1 = 6, whereas summing raw signed values would wrongly give 0.'
  },
  {
    topic: 'c1',
    q: 'In attention, what does softmax do to the raw dot-product scores?',
    options: [
      'It converts scores into binary select-or-ignore mask decisions',
      'It sorts scores so the largest key wins',
      'It turns scores into weights summing to one'
    ],
    answer: 2,
    explain: 'Softmax exponentiates and normalizes the scores, producing a positive probability-like weighting over the value vectors.'
  },
  {
    topic: 'c1',
    q: 'A batch of 32 activation vectors of size 512 (a 32x512 matrix) multiplies a weight matrix to produce size-2048 outputs; what shape must the weight be?',
    options: ['2048x512', '512x2048', '32x2048'],
    answer: 1,
    explain: 'With the 32x512 activations on the left, the weight must start with 512 to match, giving 512x2048 and a 32x2048 output.'
  },
  {
    topic: 'c1',
    q: 'Geometrically, what does a positive dot product between two vectors indicate?',
    options: [
      'They point in broadly the same direction',
      'They have exactly the same vector length',
      'They are perpendicular to each other exactly'
    ],
    answer: 0,
    explain: 'The dot product is positive when the angle between the vectors is under 90 degrees, meaning they roughly align.'
  }
];
