# AI & Data Science — University Projects

A collection of AI, data science, and algorithms projects from my Computer Science Bachelor's at Sorbonne Université.

---

## Projects

### Competitive Level-Based Foraging
`competitive-level-based-foraging/` · Python · Game Theory · Multi-Agent Systems

A competitive two-team resource-collection game where agents must coordinate to capture coloured vials under different capture rules. Implemented and benchmarked **7 strategies** across 5 maps:

- **Stationary**: random, stubborn, greedy, expert, coordination
- **History-based**: fictitious play, regret matching

Fictitious play proved the strongest overall, dominating on complex maps (`expert vs fictitious`: 0/13 on blue-map). Full results and analysis in [`docs/rapport.md`](competitive-level-based-foraging/docs/rapport.md).

**Stack:** Python, pygame, A\* pathfinding

---

### Robot AI — Paint Wars
`robots/` · Python · Robotics · Evolutionary Computation

A 2D robot simulator (Tetracomposibot) for a competitive paint-coverage game. Built progressively from Braitenberg vehicles through subsumption architecture to GA-optimised controllers:

- **Braitenberg vehicles**: wall-avoiding and bot-chasing reflexive controllers
- **Subsumption architecture**: layered priority-based behaviour (explore → avoid → attack)
- **(1+1)-Genetic Algorithm**: evolved sensor-weight arrays over 500 generations with numba JIT compilation for a **10× simulation speedup**
- **Random search baseline**: for ablation comparison

**Stack:** Python, pygame, numpy, numba

---

### CO₂ Emissions Prediction
`ARESD.ipynb` · Python · Machine Learning · Time Series

kNN-based regression model to predict CO₂ intensity of the French electricity grid from time-series features. Built a custom label encoder and modulo-distance function for cyclical time features (hour-of-day, day-of-week).

**Stack:** numpy, pandas, matplotlib, scikit-learn

---

### Discrete Mathematics — Finite Automata
`Discrete-Math/` · Python · Formal Languages

Implementation of finite automata from scratch: states, transitions, determinisation, and a custom parser for regular expressions. Includes Jupyter notebooks for interactive exploration.

**Stack:** Python, Graphviz

---

### Statistics & Probability
`Statistics/` · Python · Statistical Modelling

Three statistics projects covering probability distributions, inference, and applied modelling. Includes a **Reversi AI** built as part of project 1.

**Stack:** Python, numpy, scipy, matplotlib

---

### Continuous Optimisation — Models and Applications
`Continuous-Optimisation-Models-and-Applications/` · Python · Optimisation

Six lab sessions (TMEs) on continuous optimisation methods: gradient descent, evolutionary strategies, and constraint handling. Implemented in Python with Answer Set Programming exercises (`.lp` files).

**Stack:** Python, numpy, clingo (ASP)

---

## Additional Projects (archived as zip)

| File | Description |
|---|---|
| `Gale–Shapley.zip` | Implementation of the Gale-Shapley stable matching algorithm |
| `cinecloud-main.zip` | Cinema streaming web application |
| `g-debat.zip` | Debate platform website |
| `projet-DS.zip` | Data science analysis project |

---

## Tech at a glance

`Python` `numpy` `pandas` `scikit-learn` `pygame` `numba` `matplotlib` `Graphviz` `ASP / clingo`
