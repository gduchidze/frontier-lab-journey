var PHASE0_BANK_A4 = [
  {
    topic: 'a4',
    q: 'In the TCP 3-way handshake, what sequence of segments do client and server exchange?',
    options: [
      'SYN, then ACK, then SYN-ACK',
      'SYN, then SYN-ACK, then ACK',
      'ACK, then SYN, then SYN-ACK'
    ],
    answer: 1,
    explain: 'The client sends SYN, the server replies with SYN-ACK, and the client completes the handshake with an ACK.'
  },
  {
    topic: 'a4',
    q: 'What is the fundamental difference between TCP flow control and congestion control?',
    options: [
      'Flow control protects the receiver; congestion control protects the network',
      'Flow control protects the network; congestion control protects the receiver',
      'Flow control limits retransmissions; congestion control limits the receive buffer'
    ],
    answer: 0,
    explain: 'Flow control (receive window) keeps the sender from overrunning the receiver, while congestion control (cwnd) keeps it from overrunning the network path.'
  },
  {
    topic: 'a4',
    q: 'On a lossy network, an HTTP/2 page load stalls across all resources even though streams are multiplexed. What is the most likely cause?',
    options: [
      'The server has exhausted its connection pool of idle sockets',
      'The browser is opening too many parallel TCP connections simultaneously',
      'A lost TCP segment blocks every multiplexed stream behind it'
    ],
    answer: 2,
    explain: 'HTTP/2 multiplexes all streams over one TCP connection, so one lost segment stalls every stream until retransmission (TCP-level head-of-line blocking).'
  },
  {
    topic: 'a4',
    q: 'You are building a real-time multiplayer game where stale position updates are useless. Which transport fits best?',
    options: [
      'TCP, because reliable ordered delivery guarantees every update eventually arrives',
      'UDP, because retransmitting stale updates only delays newer useful data',
      'TCP, because congestion control automatically prevents any packet loss occurring'
    ],
    answer: 1,
    explain: 'For latency-sensitive data with fast-expiring value, UDP avoids TCP retransmission and ordering delays; a lost update is simply superseded by the next one.'
  },
  {
    topic: 'a4',
    q: 'Which features does UDP itself provide beyond raw IP delivery?',
    options: [
      'Port-based demultiplexing and an optional checksum, nothing more',
      'Ordering guarantees and congestion control, but no retransmission',
      'Retransmission of lost datagrams and per-packet delivery acknowledgments'
    ],
    answer: 0,
    explain: 'UDP adds only ports for demultiplexing and a checksum; reliability, ordering, and congestion control are left to the application.'
  },
  {
    topic: 'a4',
    q: 'A cold HTTPS request needs: DNS lookup (1 RTT), TCP handshake (1 RTT), TLS 1.2 handshake (2 RTTs), then the HTTP request/response itself. How many round trips before the response arrives?',
    options: [
      '3 RTTs',
      '4 RTTs',
      '5 RTTs'
    ],
    answer: 2,
    explain: '1 (DNS) + 1 (TCP) + 2 (TLS 1.2) + 1 (HTTP request/response) = 5 round trips before the first response byte.'
  },
  {
    topic: 'a4',
    q: 'With 100 ms RTT to a server, roughly how long do the TCP handshake plus a full TLS 1.3 handshake take before the first HTTP byte can be sent?',
    options: [
      'About 200 ms',
      'About 300 ms',
      'About 100 ms'
    ],
    answer: 0,
    explain: 'TCP costs 1 RTT and a full TLS 1.3 handshake costs 1 RTT, so setup takes roughly 2 x 100 ms = 200 ms.'
  },
  {
    topic: 'a4',
    q: 'What problem does HTTP/1.1 keep-alive solve, and what limitation remains?',
    options: [
      'It multiplexes concurrent requests but cannot reuse an existing connection',
      'It reuses one connection but requests still complete strictly sequentially',
      'It compresses request headers but leaves the connection setup unchanged'
    ],
    answer: 1,
    explain: 'Keep-alive avoids a new TCP handshake per request, but each connection still serves one request at a time, causing application-level head-of-line blocking.'
  },
  {
    topic: 'a4',
    q: "Why is HTTP/3's QUIC built on top of UDP rather than as a brand-new transport protocol?",
    options: [
      'UDP provides built-in stream multiplexing and ordering that QUIC just reuses directly',
      'UDP always guarantees strictly lower latency than any other protocol atop IP',
      'Middleboxes and kernels widely pass UDP, while new IP protocols get dropped'
    ],
    answer: 2,
    explain: 'A new IP-level protocol would be blocked by middleboxes and need OS kernel support, so QUIC rides on UDP and implements reliability and streams in user space.'
  },
  {
    topic: 'a4',
    q: 'A microservice makes thousands of short HTTPS calls per second to the same backend and latency spikes. Why does adding a connection pool help most?',
    options: [
      'It amortizes TCP and TLS handshake costs across many requests',
      "It increases the backend's CPU capacity for processing request payloads",
      'It compresses payloads so each individual request transfers fewer bytes'
    ],
    answer: 0,
    explain: 'Pooling reuses already-established connections, so each call skips the multi-RTT TCP and TLS setup and avoids socket churn.'
  },
  {
    topic: 'a4',
    q: 'With an empty cache, in what order does a recursive resolver contact servers to resolve api.example.com?',
    options: [
      'Authoritative server, then TLD server, then the root server',
      'Root server, then TLD server, then the authoritative server',
      'TLD server, then root server, then the authoritative server'
    ],
    answer: 1,
    explain: 'The resolver walks the hierarchy: root servers point to the .com TLD servers, which point to the authoritative servers for example.com.'
  },
  {
    topic: 'a4',
    q: 'A week before a planned failover you lower a DNS record TTL from 24 hours to 60 seconds. What trade-off are you accepting?',
    options: [
      'Slower failover propagation in exchange for far fewer authoritative DNS queries',
      'Higher query load on authoritative servers in exchange for faster failover',
      'Lower cache hit rates everywhere in exchange for stronger DNS security'
    ],
    answer: 1,
    explain: 'Short TTLs make caches expire quickly so the new record propagates fast, at the cost of many more queries hitting the authoritative servers.'
  },
  {
    topic: 'a4',
    q: 'How does TLS session resumption reduce connection setup cost on reconnect?',
    options: [
      'It skips the TCP handshake by reusing the prior socket',
      "It caches the server's response bytes and replays them locally",
      'It reuses prior session secrets, skipping the full key exchange'
    ],
    answer: 2,
    explain: 'Resumption (session tickets or PSK in TLS 1.3) reuses previously established secrets, cutting handshake round trips and expensive asymmetric crypto.'
  },
  {
    topic: 'a4',
    q: 'A client without keep-alive fetches 20 small resources, each needing a fresh TCP handshake (1 RTT) plus request/response (1 RTT), at 50 ms RTT. Roughly how long in total?',
    options: [
      'About 2000 ms',
      'About 1000 ms',
      'About 4000 ms'
    ],
    answer: 0,
    explain: '20 resources x 2 RTTs x 50 ms = 2000 ms; connection reuse would roughly halve this by removing the handshake RTT per resource.'
  },
  {
    topic: 'a4',
    q: 'A mobile user switches from Wi-Fi to cellular mid-download. Why can HTTP/3 continue the transfer while HTTP/2 must reconnect?',
    options: [
      "HTTP/3 servers always ignore the client's source address entirely anyway",
      'HTTP/2 forbids downloads from resuming after any network interface change',
      'QUIC identifies connections by connection ID, not the IP 4-tuple'
    ],
    answer: 2,
    explain: "QUIC's connection IDs survive address changes, whereas a TCP connection is bound to the source/destination IP-and-port 4-tuple and dies when it changes."
  },
  {
    topic: 'a4',
    q: 'A service opening a new outbound connection per request starts failing with address-in-use errors under heavy load. What is the most likely cause?',
    options: [
      'The server ran out of file descriptors for its listening socket',
      'Ephemeral client ports are exhausted by connections lingering in TIME_WAIT state',
      'DNS resolution is failing because the local resolver cache expired completely'
    ],
    answer: 1,
    explain: 'Closed connections sit in TIME_WAIT and hold their ephemeral ports, so high connection churn exhausts the port range; pooling avoids this.'
  },
  {
    topic: 'a4',
    q: 'What does HTTP/2 multiplexing provide that HTTP/1.1 keep-alive does not?',
    options: [
      'Many concurrent request-response streams interleaved on one single TCP connection',
      'A separate fresh TCP connection automatically opened for every request',
      'Guaranteed delivery of responses even across network failures or restarts'
    ],
    answer: 0,
    explain: 'HTTP/2 frames multiple streams onto one connection concurrently, removing HTTP/1.1 per-request serialization and the need for many parallel connections.'
  },
  {
    topic: 'a4',
    q: 'At 80 ms RTT, how much handshake time does TLS 1.3 (1-RTT) save versus TLS 1.2 (2-RTT) on each fresh connection?',
    options: [
      '80 ms',
      '160 ms',
      '40 ms'
    ],
    answer: 0,
    explain: 'TLS 1.3 removes one full round trip from the handshake, saving exactly 1 RTT = 80 ms per fresh connection.'
  },
  {
    topic: 'a4',
    q: "A record's TTL is 300 seconds, but some users still reach the old IP an hour after you change it. What is the most plausible explanation?",
    options: [
      'Root servers keep serving the old record for 24 hours',
      'TTL only applies to browsers, never to recursive resolver caches',
      'Some resolvers or applications ignore TTLs and cache records longer'
    ],
    answer: 2,
    explain: 'TTL is advisory: some resolvers, OS caches, and applications (e.g. JVMs, long-lived processes) cache beyond it, so stragglers hit the old address.'
  },
  {
    topic: 'a4',
    q: 'For repeat HTTPS visitors, which mechanism removes the most round trips before the first application byte?',
    options: [
      'Increasing the TCP initial congestion window on the server',
      'TLS 1.3 0-RTT resumption combined with a reused connection',
      'Switching the DNS record to a much longer TTL'
    ],
    answer: 1,
    explain: 'Connection reuse plus TLS 1.3 0-RTT resumption eliminates the TCP and TLS handshake round trips entirely, letting data ride the first flight.'
  }
];
