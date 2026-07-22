# Lab 12 — Ingress, TLS, and the Streaming Fix

Lesson: [0012-production-edge.html](../../lessons/0012-production-edge.html) · Time: ~2 h · **ADVANCED**

## Objectives

- ingress-nginx (kind manifest) on the advanced cluster
- Host routing with LLM-tuned annotations: `chat.llm.local` → UI, `api.llm.local` → router
- cert-manager + self-signed CA ClusterIssuer → HTTPS on both hosts
- Buffering ON vs OFF streaming demo (the war story)

## Steps (condensed — solution in `../solutions/k8s-advanced/ingress.yaml`)

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait -n ingress-nginx --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=180s
sudo sh -c 'echo "127.0.0.1 chat.llm.local api.llm.local" >> /etc/hosts'
# apply ingress.yaml (hosts + annotations), test http, then:
helm repo add jetstack https://charts.jetstack.io && helm repo update
helm install cert-manager jetstack/cert-manager -n cert-manager --create-namespace --set crds.enabled=true
# apply cluster-issuer.yaml, annotate ingress, watch Certificates become Ready
curl -k https://api.llm.local/v1/models
```

Streaming demo: `curl -sN https://api.llm.local/v1/chat/completions -k -d '{...,"stream":true}'` with `proxy-buffering` on vs off.

## Checkpoints — `./verify.sh`

- [ ] ingress-nginx controller Ready
- [ ] Ingress routes both hosts (http 200)
- [ ] cert-manager Ready; Certificates Ready; HTTPS answers on both hosts
- [ ] Timeout + buffering annotations present
- [ ] By hand: tokens lump vs flow demo — describe the difference in one sentence to your teacher

## If stuck

| Symptom | Move |
|---|---|
| Controller Pending | Advanced kind config missing 80/443 mappings or the ingress-ready node label — check `k8s/kind-advanced.yaml` vs solution |
| 404 from nginx | Host header mismatch — curl with `-H "Host: api.llm.local"` to isolate /etc/hosts vs Ingress rule |
| Certificate stuck NotReady | `kubectl describe certificate` → Issuer events; CA issuer needs its root Secret first |
| Stream still lumps with buffering off | Annotation typo (`nginx.ingress.kubernetes.io/proxy-buffering: "off"` — string!) |

## Stretch

Gateway API: install the CRDs, express the same routing as `Gateway` + 2 `HTTPRoute`s with a 90/10 weight split between… the same backend twice (canary plumbing, next lesson gives it purpose).
