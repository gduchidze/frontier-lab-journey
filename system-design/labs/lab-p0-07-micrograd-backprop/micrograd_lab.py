"""Lab p0-07 — Micrograd Backprop.

A ~60-line scalar autograd engine (a tiny clone of Karpathy's micrograd),
then four experiments that make Lesson p0-07's claims measurable.
Run:  python3 micrograd_lab.py

Then do the exercises in README.md — predict, edit CONFIG, re-run, compare.
"""

from __future__ import annotations

import math
import random

# ---------------------------------------------------------------- CONFIG
CONFIG = {
    "SEED": 7,              # rng seed (same init for every optimizer race)
    "HIDDEN": 4,            # neurons in the XOR net's hidden layer
    "MAX_STEPS": 4000,      # training step budget per optimizer
    "TARGET_LOSS": 0.01,    # "converged" means mean-squared error below this
    "LR_SGD": 0.1,          # learning rates per optimizer (E2 asks you to sweep)
    "LR_MOMENTUM": 0.1,
    "MOMENTUM": 0.9,
    "LR_ADAM": 0.05,
    "DEPTH": 8,             # layers in the deep-chain experiment 4
    "WIDTH": 8,             # neurons per layer in experiment 4
    "INIT_SCALES": [0.1, 0.61, 2.0],   # weight init scales to compare (E4)
    "GRAD_CHECK_H": 1e-6,   # finite-difference step for experiment 1
}
# -----------------------------------------------------------------------


class Value:
    """A scalar with a gradient. The whole engine is ~60 lines."""

    __slots__ = ("data", "grad", "_backward", "_prev")

    def __init__(self, data: float, _prev: tuple = ()):
        self.data = data
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = _prev

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other))

        def _backward():
            self.grad += out.grad          # += : gradients ACCUMULATE
            other.grad += out.grad
        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other))

        def _backward():
            self.grad += other.data * out.grad   # local deriv × upstream grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __pow__(self, k: float):
        out = Value(self.data ** k, (self,))

        def _backward():
            self.grad += k * (self.data ** (k - 1)) * out.grad
        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,))

        def _backward():
            self.grad += (1.0 - t * t) * out.grad
        out._backward = _backward
        return out

    def backward(self):
        topo, visited = [], set()

        def build(v):
            if id(v) not in visited:
                visited.add(id(v))
                for child in v._prev:
                    build(child)
                topo.append(v)
        build(self)
        self.grad = 1.0
        for v in reversed(topo):               # reverse topological order
            v._backward()

    __radd__ = __add__
    __rmul__ = __mul__

    def __neg__(self):
        return self * -1.0

    def __sub__(self, other):
        return self + (-other if isinstance(other, Value) else -other)


# ------------------------------------------------------------ tiny MLP

class Neuron:
    def __init__(self, n_in: int, rng: random.Random):
        self.w = [Value(rng.uniform(-1, 1)) for _ in range(n_in)]
        self.b = Value(0.0)

    def __call__(self, x: list) -> Value:
        act = self.b
        for wi, xi in zip(self.w, x):
            act = act + wi * xi
        return act.tanh()

    def parameters(self):
        return self.w + [self.b]


class MLP:
    def __init__(self, sizes: list[int], rng: random.Random):
        self.layers = [
            [Neuron(sizes[i], rng) for _ in range(sizes[i + 1])]
            for i in range(len(sizes) - 1)
        ]

    def __call__(self, x: list) -> Value:
        for layer in self.layers:
            x = [n(x) for n in layer]
        return x[0]

    def parameters(self):
        return [p for layer in self.layers for n in layer for p in n.parameters()]


XOR_DATA = [([-1.0, -1.0], -1.0), ([-1.0, 1.0], 1.0),
            ([1.0, -1.0], 1.0), ([1.0, 1.0], -1.0)]


def xor_loss(net: MLP) -> Value:
    total = Value(0.0)
    for x, y in XOR_DATA:
        total = total + (net(x) - y) ** 2
    return total * 0.25


def fresh_net() -> MLP:
    rng = random.Random(CONFIG["SEED"])
    return MLP([2, CONFIG["HIDDEN"], 1], rng)


# ------------------------------------------------------------ experiments

def experiment_1_grad_check() -> None:
    print("=" * 78)
    print("EXPERIMENT 1 — do not trust autograd: check it against finite differences")
    print("=" * 78)
    h = CONFIG["GRAD_CHECK_H"]
    print(f"f(a,b,c) = tanh(a*b + c)**2, at a=2, b=-3, c=10   (fd step h={h:g})\n")

    def f(a: float, b: float, c: float) -> float:
        return math.tanh(a * b + c) ** 2

    a, b, c = Value(2.0), Value(-3.0), Value(10.0)
    loss = (a * b + c).tanh() ** 2
    loss.backward()

    point = (2.0, -3.0, 10.0)
    print(f"  {'param':<8}{'autograd':>16}{'finite diff':>16}{'abs error':>14}")
    for i, (name, v) in enumerate(zip("abc", (a, b, c))):
        lo, hi = list(point), list(point)
        lo[i] -= h
        hi[i] += h
        fd = (f(*hi) - f(*lo)) / (2 * h)
        print(f"  {name:<8}{v.grad:>16.9f}{fd:>16.9f}{abs(v.grad - fd):>14.2e}")
    print("\n  -> same numbers to ~9 digits: backprop IS the chain rule, "
          "executed by bookkeeping.\n")


def experiment_2_train_xor() -> None:
    print("=" * 78)
    print("EXPERIMENT 2 — train a 2-{}-1 tanh MLP on XOR with plain SGD".format(
        CONFIG["HIDDEN"]))
    print("=" * 78)
    net = fresh_net()
    params = net.parameters()
    lr = CONFIG["LR_SGD"]
    print(f"params={len(params)}  lr={lr}\n")
    for step in range(1, CONFIG["MAX_STEPS"] + 1):
        loss = xor_loss(net)
        for p in params:
            p.grad = 0.0                      # forget this line -> E5's bug
        loss.backward()
        for p in params:
            p.data -= lr * p.grad
        if step % 200 == 0 or step == 1:
            print(f"  step {step:>5}   loss={loss.data:.6f}")
        if loss.data < CONFIG["TARGET_LOSS"]:
            print(f"  step {step:>5}   loss={loss.data:.6f}   <- converged")
            break
    print("\n  predictions after training:")
    for x, y in XOR_DATA:
        print(f"    xor({x[0]:+.0f},{x[1]:+.0f}) = {net(x).data:+.3f}   target {y:+.0f}")
    print("\n  -> note the long PLATEAU near loss=1.0: saturated tanh units pass"
          "\n     almost no gradient (lesson sections 4 and 7). Experiment 3 shows"
          "\n     how momentum and Adam punch through the same plateau faster.\n")


def make_optimizer(name: str, params: list):
    """Returns update(step) closure. All state lives here."""
    if name == "sgd":
        lr = CONFIG["LR_SGD"]

        def update(_t):
            for p in params:
                p.data -= lr * p.grad
    elif name == "momentum":
        lr, mu = CONFIG["LR_MOMENTUM"], CONFIG["MOMENTUM"]
        vel = [0.0] * len(params)

        def update(_t):
            for i, p in enumerate(params):
                vel[i] = mu * vel[i] - lr * p.grad
                p.data += vel[i]
    elif name == "adam":
        lr, b1, b2, eps = CONFIG["LR_ADAM"], 0.9, 0.999, 1e-8
        m = [0.0] * len(params)
        v = [0.0] * len(params)

        def update(t):
            for i, p in enumerate(params):
                m[i] = b1 * m[i] + (1 - b1) * p.grad
                v[i] = b2 * v[i] + (1 - b2) * p.grad * p.grad
                m_hat = m[i] / (1 - b1 ** t)
                v_hat = v[i] / (1 - b2 ** t)
                p.data -= lr * m_hat / (math.sqrt(v_hat) + eps)
    else:
        raise ValueError(name)
    return update


def experiment_3_optimizer_race() -> None:
    print("=" * 78)
    print("EXPERIMENT 3 — optimizer race on XOR (identical init, target loss "
          f"{CONFIG['TARGET_LOSS']})")
    print("=" * 78)
    print(f"  {'optimizer':<12}{'steps to target':>16}{'final loss':>14}")
    for name in ("sgd", "momentum", "adam"):
        net = fresh_net()                     # same seed -> same starting weights
        params = net.parameters()
        update = make_optimizer(name, params)
        steps, final = None, None
        for t in range(1, CONFIG["MAX_STEPS"] + 1):
            loss = xor_loss(net)
            for p in params:
                p.grad = 0.0
            loss.backward()
            update(t)
            final = loss.data
            if loss.data < CONFIG["TARGET_LOSS"]:
                steps = t
                break
        shown = str(steps) if steps else f">{CONFIG['MAX_STEPS']}"
        print(f"  {name:<12}{shown:>16}{final:>14.6f}")
    print("\n  -> adaptive per-parameter step sizes (Adam) buy convergence speed;"
          "\n     plain SGD needs more steps or a hand-tuned schedule.\n")


def experiment_4_depth_and_scale() -> None:
    print("=" * 78)
    print("EXPERIMENT 4 — gradients through {} linear layers: init scale decides "
          "vanish/explode".format(CONFIG["DEPTH"]))
    print("=" * 78)
    width, depth = CONFIG["WIDTH"], CONFIG["DEPTH"]
    print(f"width={width}  stable scale ~ sqrt(3/width) = {math.sqrt(3 / width):.2f}\n")
    print(f"  {'init scale':<12}{'|last activation|':>18}{'|input grad|':>16}"
          f"{'update/weight @L1':>18}")
    for scale in CONFIG["INIT_SCALES"]:
        rng = random.Random(CONFIG["SEED"])
        x = [Value(rng.uniform(-1, 1)) for _ in range(width)]
        h = x
        layers = []
        for _ in range(depth):
            w = [[Value(rng.uniform(-scale, scale)) for _ in range(width)]
                 for _ in range(width)]
            layers.append(w)
            nh = []
            for row in w:
                acc = Value(0.0)
                for wi, hi in zip(row, h):
                    acc = acc + wi * hi
                nh.append(acc)
            h = nh
        loss = Value(0.0)
        for o in h:
            loss = loss + o * o
        loss.backward()

        fwd = sum(abs(o.data) for o in h) / width          # forward signal size
        bwd = sum(abs(xi.grad) for xi in x) / width        # backward signal size
        l1 = [w for row in layers[0] for w in row]
        upd = (sum(abs(w.grad) for w in l1) / len(l1)) / \
              (sum(abs(w.data) for w in l1) / len(l1))     # grad relative to weight
        print(f"  {scale:<12}{fwd:>18.3e}{bwd:>16.3e}{upd:>18.3e}")
    print("\n  -> backprop multiplies one factor per layer: scale too small and"
          "\n     early layers learn nothing (vanishing); too big and updates blow"
          "\n     up (exploding). Careful init + normalization keep the ratio ~1.\n")


def main() -> None:
    experiment_1_grad_check()
    experiment_2_train_xor()
    experiment_3_optimizer_race()
    experiment_4_depth_and_scale()
    print("Done. Now do the README exercises: predict, edit CONFIG, re-run, compare.")


if __name__ == "__main__":
    main()
