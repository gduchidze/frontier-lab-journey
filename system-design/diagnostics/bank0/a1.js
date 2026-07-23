var PHASE0_BANK_A1 = [
  {
    topic: 'a1',
    q: 'Why is hash table insertion described as amortized O(1) despite occasional O(n) resizes?',
    options: [
      'Resizes never happen if the table load factor stays low',
      'Doubling spreads resize cost so average per insert stays constant',
      'Hardware caches hide the resize cost from all timing measurements'
    ],
    answer: 1,
    explain: 'Doubling capacity makes total resize work O(n) over n inserts, so the average cost per insert is constant.'
  },
  {
    topic: 'a1',
    q: 'Your service p99 latency spikes periodically while average latency stays flat, and the hot path inserts into a growing in-memory hash map. What is the most likely cause?',
    options: [
      'Occasional full rehashes when the map doubles capacity',
      'Constant hash collisions on every single insert operation',
      'Garbage collection triggered by each individual key insertion'
    ],
    answer: 0,
    explain: 'Amortized O(1) hides rare O(n) rehash pauses, which surface as periodic tail latency spikes while the average stays flat.'
  },
  {
    topic: 'a1',
    q: 'Why do databases use B-trees instead of binary search trees for on-disk indexes?',
    options: [
      'Binary trees cannot store string keys on disk reliably',
      'B-trees guarantee perfectly balanced height without any rebalancing work',
      'High branching factor matches page size and minimizes seeks'
    ],
    answer: 2,
    explain: 'Each B-tree node fills a disk page, so a lookup touches a handful of pages instead of tens of pointer hops.'
  },
  {
    topic: 'a1',
    q: 'A B-tree stores one million keys with branching factor 1000. Roughly how many levels does a lookup traverse?',
    options: [
      'Roughly twenty levels',
      'Roughly ten levels',
      'Roughly two levels'
    ],
    answer: 2,
    explain: 'Height is about log base 1000 of one million, which is 2, so a lookup reads only a couple of pages.'
  },
  {
    topic: 'a1',
    q: 'A dynamic array doubles capacity starting from 8, copying all elements at each resize. After appending 1024 elements into an initially empty array, roughly how many element copies occurred?',
    options: [
      'Roughly one million copies',
      'Roughly one thousand copies',
      'Roughly ten thousand copies'
    ],
    answer: 1,
    explain: 'Copy work sums as 8+16+...+512, roughly 1000 total, which is why the amortized cost per append is constant.'
  },
  {
    topic: 'a1',
    q: 'What does a binary min-heap guarantee about its stored elements?',
    options: [
      'Every parent is less than or equal to its children',
      'All the elements are kept in fully sorted ascending order',
      'The left subtree always holds keys smaller than the right'
    ],
    answer: 0,
    explain: 'A heap enforces only the parent-child ordering invariant, not a total order across the whole structure.'
  },
  {
    topic: 'a1',
    q: 'You must repeatedly fetch the request with the earliest deadline from a changing set of pending requests. Which structure fits best?',
    options: [
      'A sorted array, rebuilt continuously',
      'A min-heap keyed by deadline',
      'A hash map of deadlines'
    ],
    answer: 1,
    explain: 'A min-heap gives O(log n) insert and O(log n) extract-min, which is exactly the scheduling access pattern.'
  },
  {
    topic: 'a1',
    q: 'You are building autocomplete over millions of strings and need all entries sharing a typed prefix. Which structure serves this most directly?',
    options: [
      'A hash table of complete strings',
      'A min-heap ordered by string length',
      'A trie walked down the prefix'
    ],
    answer: 2,
    explain: 'A trie reaches the prefix node in O(prefix length) steps and every descendant below it is a completion.'
  },
  {
    topic: 'a1',
    q: 'Which statement correctly describes bloom filter query answers?',
    options: [
      'Maybe present answers can be wrong; absent cannot',
      'Absent answers can be wrong; present answers cannot',
      'Both possible answers carry equal probability of error'
    ],
    answer: 0,
    explain: 'Bits are never cleared, so an inserted element always finds its bits set, meaning only false positives occur.'
  },
  {
    topic: 'a1',
    q: 'A storage engine checks a bloom filter before reading an SSTable from disk. What benefit does this provide?',
    options: [
      'Most reads for missing keys skip disk entirely',
      'Every read for present keys avoids disk access',
      'The filter stores the values for hot keys'
    ],
    answer: 0,
    explain: 'A negative filter answer is definitive, so lookups for absent keys avoid the expensive disk read.'
  },
  {
    topic: 'a1',
    q: 'A bloom filter uses about 10 bits per element with an optimal number of hash functions. What false positive rate should you roughly expect?',
    options: [
      'Around ten percent',
      'Around one percent',
      'Around zero percent'
    ],
    answer: 1,
    explain: 'Roughly 10 bits per element with about 7 hash functions yields a false positive rate near 1 percent.'
  },
  {
    topic: 'a1',
    q: 'Why do distributed caches use consistent hashing instead of hashing keys modulo the server count?',
    options: [
      'Modulo hashing cannot distribute keys evenly across many servers',
      'Consistent hashing guarantees every server holds identical key counts',
      'Adding a node remaps only a small key fraction'
    ],
    answer: 2,
    explain: 'With modulo, changing the server count remaps nearly all keys, while consistent hashing moves only about 1/n of them.'
  },
  {
    topic: 'a1',
    q: 'What problem do virtual nodes solve in a consistent hashing ring?',
    options: [
      'They stop hash collisions between different keys',
      'They smooth uneven load across physical nodes',
      'They remove the need for any rehashing'
    ],
    answer: 1,
    explain: 'Placing many virtual points per server evens out the random arc sizes each physical node owns.'
  },
  {
    topic: 'a1',
    q: 'For a few thousand small integer keys, a linear scan over an array often beats a hash map lookup in practice. Why?',
    options: [
      'Sequential access exploits caches and avoids hashing overhead',
      'Linear scans have better asymptotic complexity than hashing',
      'Hash maps must always sort keys before lookup'
    ],
    answer: 0,
    explain: 'Big-O ignores constants, and prefetch-friendly sequential scans over small data beat pointer chasing plus hash computation.'
  },
  {
    topic: 'a1',
    q: 'In a chained hash table, what happens when two distinct keys hash to the same bucket?',
    options: [
      'The second insert fails and reports an error',
      'The older key is overwritten by the newer',
      'Both keys are stored in that buckets list'
    ],
    answer: 2,
    explain: 'Chaining keeps all colliding entries in a per-bucket list, and lookups walk that list comparing full keys.'
  },
  {
    topic: 'a1',
    q: 'An attacker sends requests whose keys all collide in your hash table. What does lookup performance degrade to?',
    options: [
      'Amortized constant time still',
      'Linear in stored keys',
      'Logarithmic in stored keys'
    ],
    answer: 1,
    explain: 'All entries pile into one bucket, so each lookup scans a chain of length n, which is why languages use randomized seeds.'
  },
  {
    topic: 'a1',
    q: 'You need the top 100 scores from a stream of one billion events using minimal memory. Which approach works?',
    options: [
      'Keep a size-100 min-heap of best scores',
      'Sort all events then take the head',
      'Store every event inside a balanced BST'
    ],
    answer: 0,
    explain: 'A bounded min-heap holds the current top 100 and evicts its smallest root in O(log 100) per event.'
  },
  {
    topic: 'a1',
    q: 'Compared with a red-black tree in memory, a B-tree node holds many keys. What is the main benefit of this design?',
    options: [
      'Individual key comparisons become asymptotically faster inside each single node',
      'Insertions never split nodes because nodes have such large capacity',
      'Fewer node visits are needed because the tree is shallower'
    ],
    answer: 2,
    explain: 'Wide nodes shrink the height to log base B of n, cutting the number of expensive page or cache-line fetches.'
  },
  {
    topic: 'a1',
    q: 'You will insert exactly ten million entries into a hash map on a latency-sensitive startup path. What cheap optimization avoids rehash pauses?',
    options: [
      'Preallocate capacity for all expected entries',
      'Lower the load factor after inserting',
      'Use a cryptographic hash function instead'
    ],
    answer: 0,
    explain: 'Reserving the final capacity up front means no incremental doublings and no rehash pauses during the insert burst.'
  },
  {
    topic: 'a1',
    q: 'A bloom filter sized for 1 percent false positives at one million elements now holds two million elements. What happens to the false positive rate?',
    options: [
      'It stays near 1 percent',
      'It rises far above target',
      'It drops as bits saturate'
    ],
    answer: 1,
    explain: 'Overfilling raises the fraction of set bits, so the false positive rate grows well beyond the design target.'
  }
];
