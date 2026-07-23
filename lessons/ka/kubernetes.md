# Kubernetes და kind — მარტივად, ქართულად

---

# ნაწილი 1: რა არის Kubernetes

## მოკლედ

Kubernetes არის ღია კოდის (open source) პლატფორმა, რომელიც კონტეინერებში გაშვებულ აპლიკაციებს ავტომატურად მართავს — უშვებს, ამასშტაბებს და აღადგენს, როცა რამე იშლება.

სახელი ბერძნულიდან მოდის და „მესაჭეს" ნიშნავს. შემოკლება **K8s** ასე იშიფრება: „K"-სა და „s"-ს შორის 8 ასოა (u-b-e-r-n-e-t-e). პროექტი Google-მა 2014 წელს გახსნა და მასში ჩადო 15+ წლის გამოცდილება, რომელიც საკუთარი production სისტემების (Borg) მართვისას დააგროვა.

## რატომ გჭირდება

კონტეინერი (მაგ. Docker) კარგი გზაა აპლიკაციის შესაფუთად და გასაშვებად. მაგრამ production-ში ჩნდება კითხვები:

- თუ კონტეინერი „მოკვდა", ვინ გაუშვებს ახალს?
- თუ ტრაფიკი გაიზარდა, ვინ დაამატებს ასლებს?
- ვინ გადაანაწილებს დატვირთვას სერვერებზე?

ამ ყველაფრის ხელით კეთება არარეალურია. Kubernetes სწორედ ეს სისტემაა — შენ უწერ **სასურველ მდგომარეობას** („მინდა ამ აპის 3 ასლი მუშაობდეს"), ის კი მუდმივად ზრუნავს, რომ რეალობა ამ აღწერას დაემთხვეს.

## რას გაძლევს Kubernetes

1. **Service discovery და load balancing** — კონტეინერს ანიჭებს DNS სახელს ან IP მისამართს და მაღალი ტრაფიკის დროს მოთხოვნებს ასლებზე ანაწილებს.
2. **Storage-ის ორკესტრაცია** — ავტომატურად აერთებს სასურველ საცავს: ლოკალურ დისკს, cloud provider-ის storage-ს და ა.შ.
3. **ავტომატური rollout/rollback** — აღწერ ახალ ვერსიას და Kubernetes კონტროლირებული ტემპით ანაცვლებს ძველ კონტეინერებს ახლებით; პრობლემისას უკან აბრუნებს.
4. **Bin packing** — ეუბნები, რამდენი CPU და RAM სჭირდება თითო კონტეინერს, და ის ოპტიმალურად ალაგებს მათ კვანძებზე (node), რომ რესურსი არ დაიკარგოს.
5. **Self-healing** — გაფუჭებულ კონტეინერს გადატვირთავს, health check-ჩავარდნილს კლავს და ცვლის, ხოლო სანამ კონტეინერი მზად არ არის, ტრაფიკს არ უშვებს მასზე.
6. **Secret-ებისა და კონფიგურაციის მართვა** — პაროლებს, ტოკენებსა და SSH გასაღებებს ინახავს ისე, რომ image-ის გადაბილდვა და კონფიგში მათი გამჟღავნება არ დაგჭირდეს.
7. **Batch სამუშაოები** — სერვისების გარდა ერთჯერად და CI ტიპის ამოცანებსაც უშვებს.
8. **ჰორიზონტალური მასშტაბირება** — ერთი ბრძანებით, UI-დან ან ავტომატურად (მაგ. CPU დატვირთვის მიხედვით) ზრდი/ამცირებ ასლების რაოდენობას.
9. **IPv4/IPv6 dual-stack** — Pod-ებსა და Service-ებს ორივე ტიპის მისამართს ანიჭებს.
10. **გაფართოებადობა** — კლასტერს ახალ ფუნქციებს უმატებ ისე, რომ Kubernetes-ის კოდი არ შეცვალო.

## რა **არ** არის Kubernetes

- **არ არის PaaS** (Heroku-ს ტიპის „ყველაფერი ჩართული" პლატფორმა). აძლევს სამშენებლო ბლოკებს, მაგრამ არჩევანს შენ გიტოვებს.
- **არ ზღუდავს აპლიკაციის ტიპს** — stateless, stateful, data processing... თუ კონტეინერში ეშვება, Kubernetes-შიც იმუშავებს.
- **არ აბილდებს კოდს** — CI/CD შენი საზრუნავია.
- **არ მოყვება ჩაშენებული DB, message bus, cache** — ესენი Kubernetes-ზე *შეგიძლია* გაუშვა, მაგრამ პლატფორმის ნაწილი არ არის.
- **არ გაძალებს კონკრეტულ logging/monitoring გადაწყვეტას** — თავად ირჩევ ინსტრუმენტებს.
- **არ არის უბრალო „ორკესტრატორი"** — ორკესტრაცია ნიშნავს ფიქსირებულ workflow-ს (ჯერ A, მერე B, მერე C). Kubernetes სხვანაირად მუშაობს: დამოუკიდებელი კონტროლ-პროცესები მუდმივად აახლოებენ მიმდინარე მდგომარეობას სასურველთან, გზას კი თავად პოულობენ.

## ისტორიული კონტექსტი: რატომ მივედით აქამდე

**ფიზიკური სერვერების ეპოქა.** აპლიკაციები პირდაპირ სერვერებზე ეშვებოდა. რესურსების საზღვრები არ არსებობდა — ერთი აპი მთელ CPU-ს ჭამდა და დანარჩენები ზარალდებოდნენ. გამოსავალი „თითო აპს თითო სერვერი" ძვირი და არაეფექტიანი იყო.

**ვირტუალიზაციის ეპოქა.** ერთ ფიზიკურ სერვერზე რამდენიმე ვირტუალური მანქანა (VM) გაეშვა. აპლიკაციები იზოლირებულია, რესურსი უკეთ გამოიყენება. მინუსი: თითო VM სრული მანქანაა საკუთარი ოპერაციული სისტემით — მძიმეა.

**კონტეინერების ეპოქა.** კონტეინერი VM-ს ჰგავს, მაგრამ ოპერაციულ სისტემას სხვა კონტეინერებს უზიარებს, ამიტომ მსუბუქია. აქვს საკუთარი ფაილური სისტემა, CPU-სა და მეხსიერების წილი, მაგრამ ინფრასტრუქტურას არ არის მიბმული — ლეპტოპზეც ისე ეშვება, როგორც cloud-ში. სწორედ ამ კონტეინერების მასობრივად სამართავად გაჩნდა Kubernetes.

---

# ნაწილი 2: kind — Quick Start

## რა არის kind

**kind** (Kubernetes IN Docker) ლოკალურ Kubernetes კლასტერს უშვებს ისე, რომ „კვანძებად" (node) Docker კონტეინერებს იყენებს. იდეალურია სასწავლოდ, ლოკალური დეველოპმენტისთვის და CI-სთვის — ცალკე VM-ები არ გჭირდება.

> `kubectl` kind-ისთვის სავალდებულო არ არის, მაგრამ კლასტერთან სამუშაოდ დაგჭირდება — ცალკე დააინსტალირე.

## ინსტალაცია

მიმდინარე სტაბილური ვერსიაა **v0.32.0**.

**Linux (მზა ბინარით):**

```bash
# AMD64 / x86_64
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.32.0/kind-linux-amd64
# ARM64
[ $(uname -m) = aarch64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.32.0/kind-linux-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

**macOS:**

```bash
brew install kind
```

**Windows:**

```powershell
choco install kind
# ან
winget install Kubernetes.kind
```

**Go დეველოპერებისთვის:**

```bash
go install sigs.k8s.io/kind@v0.32.0
```

`go install` ბინარს `$(go env GOPATH)/bin`-ში დებს — თუ `kind: command not found` მიიღე, ეს დირექტორია `$PATH`-ში დაამატე.

ნებისმიერ ბრძანებაზე დახმარებას მიიღებ `kind --help`-ით.

## კლასტერის შექმნა

```bash
kind create cluster
```

ესაა და ეს — kind ჩამოტვირთავს მზა node image-ს (`kindest/node`) და წამებში აგიწყობს კლასტერს.

სასარგებლო ფლაგები:

- `--name my-cluster` — კლასტერს სახელს არქმევს (ნაგულისხმევად ჰქვია `kind`)
- `--image kindest/node:v1.xx.x` — Kubernetes-ის კონკრეტულ ვერსიას ირჩევ (შესაბამისი image-ები kind-ის release notes-შია ჩამოთვლილი)
- `--wait 30s` / `--wait 5m` — ბრძანება დაელოდება, სანამ control plane მზად არ იქნება

kind ავტომატურად ამოიცნობს, რომელი runtime გაქვს: Docker, Podman თუ nerdctl. ხელით არჩევა შეგიძლია გარემოს ცვლადით, მაგ. `KIND_EXPERIMENTAL_PROVIDER=podman` (Podman/nerdctl ნაგულისხმევად rootless რეჟიმში მუშაობს და დამატებითი გამართვა სჭირდება).

## კლასტერთან მუშაობა

kind ავტომატურად წერს კონფიგურაციას `~/.kube/config`-ში, ასე რომ `kubectl` პირდაპირ მუშაობს.

ორი კლასტერი რომ შექმნა:

```bash
kind create cluster            # კონტექსტი: kind
kind create cluster --name kind-2

kind get clusters              # ჩამონათვალი: kind, kind-2
```

კონკრეტულთან სამუშაოდ კონტექსტს უთითებ (kind პრეფიქსად `kind-`-ს უმატებს):

```bash
kubectl cluster-info --context kind-kind
kubectl cluster-info --context kind-kind-2
```

## კლასტერის წაშლა

```bash
kind delete cluster            # შლის ნაგულისხმევ "kind" კლასტერს
kind delete cluster --name kind-2
```

არარსებული კლასტერის წაშლა შეცდომას **არ** აბრუნებს — ეს განზრახაა, რომ cleanup სკრიპტები იდემპოტენტური იყოს.

## ლოკალური image-ის ჩატვირთვა კლასტერში

kind-ის კლასტერი შენს ლოკალურ Docker image-ებს ავტომატურად ვერ ხედავს — ხელით უნდა ჩატვირთო:

```bash
kind load docker-image my-app:latest
kind load docker-image my-app:latest my-db:latest    # რამდენიმე ერთად
kind load docker-image my-app:latest --name test-cluster   # სახელიან კლასტერში
kind load image-archive /my-image-archive.tar        # tar არქივიდან
```

ტიპური workflow:

```bash
docker build -t my-custom-image:unique-tag ./my-image-dir
kind load docker-image my-custom-image:unique-tag
kubectl apply -f my-manifest.yaml
```

**მნიშვნელოვანი ხაფანგი:** თუ image-ის ტეგი `:latest`-ია (ან საერთოდ არ აქვს), Kubernetes-ის pull policy `Always` ხდება — კვანძი შეეცდება image-ის registry-დან გადმოწერას და შენს ჩატვირთულს იგნორს გაუკეთებს. გამოსავალი:

- ნუ იყენებ `:latest` ტეგს, ან
- მანიფესტში მიუთითე `imagePullPolicy: IfNotPresent` ან `Never`

კვანძზე არსებული image-ების ნახვა:

```bash
docker exec -it kind-control-plane crictl images
```

## კონფიგურაციის ფაილი (Advanced)

კონფიგი YAML ფაილით გადაეცემა:

```bash
kind create cluster --config my-config.yaml
```

**მრავალკვანძიანი კლასტერი** (1 control-plane + 2 worker):

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
```

**HA control plane** — უბრალოდ რამდენიმე `control-plane` როლს წერ.

**პორტების გადამისამართება host-ზე** (NodePort სერვისებისთვის გამოსადეგი):

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
```

**Kubernetes ვერსიის დაფიქსირება** — კვანძს image-ს sha256-ით უთითებ:

```yaml
nodes:
- role: control-plane
  image: kindest/node:v1.16.4@sha256:b91a2c...
```

**Feature gate-ების ჩართვა** (ალფა/ექსპერიმენტული ფუნქციები):

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
featureGates:
  FeatureGateName: true
```

## ლოგების ექსპორტი

დებაგისთვის kind მთელი კლასტერის ლოგებს ერთად ამოიღებს:

```bash
kind export logs           # დროებით დირექტორიაში
kind export logs ./somedir # კონკრეტულ ადგილას
```

მიიღებ Docker host-ის ინფოს, `kubelet.log`-ს, `journal.log`-ს, pod-ების ლოგებს და ა.შ.

## Docker Desktop-ის შენიშვნა (macOS/Windows)

თუ node image-ს თავად აბილდებ (`kind build node-image`), Docker-ის VM-ს მინიმუმ **6 GB RAM** სჭირდება, რეკომენდებულია **8 GB** — Settings → Advanced-ში შეცვლი. ადგილის გასათავისუფლებლად `docker system prune`-იც გამოგადგება.

---

წყაროები: [kubernetes.io/docs/concepts/overview](https://kubernetes.io/docs/concepts/overview/) და [kind.sigs.k8s.io/docs/user/quick-start](https://kind.sigs.k8s.io/docs/user/quick-start/) (ორივე CC BY 4.0 ლიცენზიით).