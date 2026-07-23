var PHASE0_BANK_A2 = [
  {
    topic: 'a2',
    q: 'Two threads in the same process share which of the following by default?',
    options: [
      'Only the code segment, never heap',
      'Heap, globals, and open file descriptors',
      'Nothing at all, each is isolated'
    ],
    answer: 1,
    explain: 'Threads share the address space and process resources such as heap, globals, and the file descriptor table, while stacks and registers stay private.'
  },
  {
    topic: 'a2',
    q: 'A worker occasionally segfaults due to a buggy native extension. To keep one crash from taking down all workers, you should run workers as what?',
    options: [
      'Separate processes, since address spaces are isolated',
      'Separate threads, since scheduling makes crashes recoverable',
      'Green threads, since runtimes always catch segfaults'
    ],
    answer: 0,
    explain: 'A segfault kills the entire process, so isolating workers in separate processes confines the blast radius to a single worker.'
  },
  {
    topic: 'a2',
    q: 'A process maps a 2 GB region with 4 KB pages. Roughly how many page-table entries are needed to cover it?',
    options: [
      'About 512 entries',
      'About 52,000 entries',
      'About 524,000 entries'
    ],
    answer: 2,
    explain: '2 GB divided by 4 KB yields 524,288 pages needing one entry each, which is exactly why huge pages exist.'
  },
  {
    topic: 'a2',
    q: 'What is the TLB in a modern CPU?',
    options: [
      'A disk cache holding recently evicted pages',
      'A hardware cache of virtual-to-physical address translations',
      'A kernel buffer of pending page faults'
    ],
    answer: 1,
    explain: 'The translation lookaside buffer caches recent virtual-to-physical mappings so most memory accesses avoid a full page-table walk.'
  },
  {
    topic: 'a2',
    q: 'A host shows constant disk I/O, high CPU wait, and every process crawls despite doing little real compute. Memory is oversubscribed. The most likely diagnosis is what?',
    options: [
      'Thrashing: the working sets exceed physical RAM',
      'Deadlock: the processes hold locks awaiting others',
      'Starvation: the scheduler favors one runnable process'
    ],
    answer: 0,
    explain: 'Continuous paging traffic with little useful compute means combined working sets do not fit in RAM, the classic thrashing signature.'
  },
  {
    topic: 'a2',
    q: 'Why does OS-style paging inspire PagedAttention for LLM KV caches?',
    options: [
      'Pages let the GPU swap tensors onto disk transparently',
      'Pages compress the cache so attention reads fewer bytes',
      'Fixed-size blocks avoid fragmentation and allow non-contiguous cache growth'
    ],
    answer: 2,
    explain: 'Like virtual memory, allocating KV cache in fixed blocks behind an indirection table eliminates the fragmentation caused by contiguous reservations.'
  },
  {
    topic: 'a2',
    q: 'What happens on a page fault for a valid but non-resident page?',
    options: [
      'The kernel loads the page, updates mappings, and resumes execution',
      'The process is terminated immediately because the access was illegal',
      'The CPU retries the instruction repeatedly until the page appears'
    ],
    answer: 0,
    explain: 'A fault on a valid mapping is a minor or major fault that the kernel services by loading data and updating the page table before resuming.'
  },
  {
    topic: 'a2',
    q: 'Two containers on one host both see PID 1 inside themselves. What mechanism makes this possible?',
    options: [
      'Hypervisor traps fully virtualizing each guest kernel',
      'PID namespaces giving each container private numbering',
      'Cgroups limiting how many total processes exist'
    ],
    answer: 1,
    explain: 'Namespaces virtualize the kernel resource view, including PID numbering, while cgroups only meter and limit resource consumption.'
  },
  {
    topic: 'a2',
    q: 'In Linux containers, what do cgroups primarily provide?',
    options: [
      'Isolated views of PIDs, mounts, and network stacks',
      'Cryptographic isolation of container image layers at rest',
      'Resource limits and accounting for CPU, memory, IO'
    ],
    answer: 2,
    explain: 'Cgroups meter and cap resource usage per group of processes; isolated resource views come from namespaces instead.'
  },
  {
    topic: 'a2',
    q: 'A security team asks why a container escape is generally scarier than a VM escape from a guest application bug. The core reason is what?',
    options: [
      'Containers share the host kernel, exposing its full syscall surface',
      'Containers always run as privileged, granting root on every host',
      'Container images carry more vulnerabilities than typical VM disk images'
    ],
    answer: 0,
    explain: 'A container attacker talks directly to the shared host kernel, while a VM guest must additionally breach the hypervisor boundary.'
  },
  {
    topic: 'a2',
    q: 'Assume a TLB hit costs 1 ns and a miss adds 100 ns extra. Moving the hit rate from 99 percent to 99.9 percent changes average translation cost roughly how?',
    options: [
      'From 101 ns down to nearly 51 ns',
      'From about 2 ns down to 1.1 ns',
      'From about 100 ns down to 10 ns'
    ],
    answer: 1,
    explain: 'Average cost is 1 ns plus miss rate times 100 ns, so 1 + 0.01x100 = 2 ns falls to 1 + 0.001x100 = 1.1 ns.'
  },
  {
    topic: 'a2',
    q: 'Relative to a 0.3 ns CPU cycle, a process context switch including cache and TLB effects typically costs on the order of what?',
    options: [
      'Tens of nanoseconds, roughly a hundred cycles',
      'Several whole milliseconds, roughly ten million cycles',
      'A few microseconds, roughly ten thousand cycles'
    ],
    answer: 2,
    explain: 'The direct switch takes about a microsecond and cache plus TLB pollution adds more, so the scale is microseconds, not nanoseconds or milliseconds.'
  },
  {
    topic: 'a2',
    q: 'You are building an in-memory cache server where request handlers must share one large hash table with minimal latency. Which concurrency model fits best?',
    options: [
      'Forked processes communicating through pipes for every lookup',
      'Threads in one process sharing the table directly',
      'Separate processes each holding a full table copy'
    ],
    answer: 1,
    explain: 'Threads share the address space, so handlers reach the table without copying or IPC, at the cost of needing synchronization.'
  },
  {
    topic: 'a2',
    q: 'Order these storage layers from fastest to slowest access latency.',
    options: [
      'L1 cache, DRAM, NVMe SSD, spinning disk',
      'DRAM, L1 cache, spinning disk, NVMe SSD',
      'L1 cache, NVMe SSD, DRAM, spinning disk'
    ],
    answer: 0,
    explain: 'Latency climbs from about a nanosecond in L1, to roughly 100 ns for DRAM, tens of microseconds for NVMe, and milliseconds for spinning disks.'
  },
  {
    topic: 'a2',
    q: 'A 30 GB in-memory database process calls fork() to snapshot itself, like Redis does. Why does the child not immediately consume another 30 GB?',
    options: [
      'The kernel compresses child memory pages until first use',
      'The child receives only stack pages, never heap pages',
      'Pages are shared copy-on-write and duplicated only when written'
    ],
    answer: 2,
    explain: 'fork marks pages copy-on-write, so parent and child share the same physical memory until either side writes to a page.'
  },
  {
    topic: 'a2',
    q: 'After that fork, the parent keeps taking heavy writes across its whole dataset while the child snapshots. What happens to host memory usage?',
    options: [
      'It stays flat because snapshots never touch parent memory',
      'It grows because each written page gets physically duplicated',
      'It halves because the kernel deduplicates the identical pages'
    ],
    answer: 1,
    explain: 'Every parent write to a still-shared page triggers a physical copy, so worst-case usage approaches double the dataset size.'
  },
  {
    topic: 'a2',
    q: 'What is a file descriptor in Unix?',
    options: [
      'A per-process integer indexing into a kernel open-file table',
      'A global filesystem path string cached inside the kernel',
      'A checksum the kernel uses to verify file integrity'
    ],
    answer: 0,
    explain: 'An fd is a small per-process integer that indexes into the kernel-maintained table of open file descriptions for that process.'
  },
  {
    topic: 'a2',
    q: 'A proxy under load starts failing with EMFILE (too many open files) even though the disk is nearly empty. What is the actual problem?',
    options: [
      'The filesystem ran out of inodes for new files',
      'The disk quota blocked the process from writing logs',
      'The process hit its descriptor limit, likely leaking sockets'
    ],
    answer: 2,
    explain: 'Sockets consume file descriptors, so EMFILE under load usually means the per-process fd limit was reached, often via leaked connections.'
  },
  {
    topic: 'a2',
    q: 'Why do OS schedulers use preemptive time slicing instead of letting each process run to completion?',
    options: [
      'It maximizes total throughput by eliminating all context switches',
      'It bounds response time so interactive tasks stay responsive',
      'It removes the need for locks between cooperating processes'
    ],
    answer: 1,
    explain: 'Preemption trades some switching overhead for bounded latency, preventing long CPU-bound jobs from starving interactive work.'
  },
  {
    topic: 'a2',
    q: 'A service performs 200,000 context switches per second at roughly 5 microseconds each including cache effects. Approximately what fraction of one core is lost?',
    options: [
      'Around 100 percent, an entire core',
      'Around 10 percent of one core',
      'Around 1 percent, effectively negligible overhead'
    ],
    answer: 0,
    explain: '200,000 switches times 5 microseconds equals one full second of overhead per second, consuming an entire core.'
  }
];
