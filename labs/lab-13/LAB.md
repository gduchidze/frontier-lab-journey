# Lab 13 — Lock the Stack: NetworkPolicy, Quotas, Engine Auth

Lesson: [0013-security-multitenancy.html](../../lessons/0013-security-multitenancy.html) · Time: ~2 h · **ADVANCED**

## Prereq

Cilium cluster from lab 11 (kindnet would silently ignore every policy — the whole point).

## Objectives

- Default-deny ingress in `llm`; feel the outage; then allow exactly the drawn graph
- Prove isolation from an attacker pod (screenshot the timeout)
- ResourceQuota + LimitRange on `llm`; hit the quota wall deliberately
- `--api-key` on engines from a Secret; 401 without, 200 with; RBAC audit

## Steps (condensed — solutions in `../solutions/k8s-advanced/netpol.yaml`, `quota.yaml`)

```bash
kubectl apply -f k8s/netpol.yaml        # deny-all first — watch UI die (intended!)
# add the allow policies (ui→router, router→engines, monitoring→engines, ingress→ui/router)
kubectl run attacker --rm -it --image=curlimages/curl -- \
  curl -m 5 http://vllm.llm.svc.cluster.local:8000/health   # must TIMEOUT
kubectl apply -f k8s/quota.yaml
kubectl scale deployment vllm -n llm --replicas=5            # quota says no (Events)
# engine auth:
kubectl create secret generic vllm-api-key -n llm --from-literal=key="$(openssl rand -hex 16)"
# chart: env VLLM_API_KEY from secret + --api-key flag; update UI's OPENAI_API_KEY
```

## Checkpoints — `./verify.sh`

- [ ] Default-deny policy present in `llm`
- [ ] ≥3 allow policies; UI + scraping work again (targets still UP!)
- [ ] Attacker pod times out against engines
- [ ] Quota + LimitRange active; over-scale rejected
- [ ] Engine 401s without key, 200s with; UI still chats
- [ ] RBAC audit output saved to `docs/rbac-audit.md`

## If stuck

| Symptom | Move |
|---|---|
| Policies "applied" but nothing blocked | You're not on the Cilium cluster — `kubectl get pods -n kube-system -l k8s-app=cilium` |
| Prometheus targets DOWN after allow rules | Forgot monitoring→engines ingress rule (port 8000, from ns monitoring) |
| UI broken after allow rules | Ingress controller ns needs a path to ui/router too — the edge is a client now |
| 401 even with key in UI | Key must match EXACTLY; check Secret b64 vs UI env |
| Quota blocks the HPA later | Quota must leave headroom for maxReplicas — size it consciously |

## Stretch

Cilium Hubble (`cilium hubble enable`, `hubble observe`) — watch your allow/deny decisions live. Network observability for free.
