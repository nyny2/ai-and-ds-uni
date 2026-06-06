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

### Student–Program Matching (Gale-Shapley + ILP)
`Gale–Shapley.zip` · Python · Combinatorial Optimisation · Game Theory

*Course: LU3IN025 — IA et Jeux*

A Parcoursup-style two-sided matching problem: assigning students to academic programmes with capacity constraints. Implements and compares five assignment strategies:

- **Gale-Shapley (student-proposing)**: students-optimal stable matching
- **Gale-Shapley (programme-proposing)**: programmes-optimal stable matching
- **ILP max-min** (Q11, Gurobi): maximises the minimum student utility — maximally fair
- **ILP max-sum** (Q12, Gurobi): maximises total bilateral utility
- **ILP k-first** (Q13/Q14, Gurobi): finds the smallest k such that every student is matched to one of their top-k choices

Stability of all assignments is verified against the preference lists. GS runtime is benchmarked across problem sizes (n = 200 → 2000, 10 runs each), with convergence curves plotted. All five solutions are compared on average utility, minimum utility, and number of unstable pairs.

**Stack:** Python, Gurobi (gurobipy), matplotlib

---

### CineCloud — Cinema Streaming Platform
`cinecloud-main.zip` · Python · JavaScript · Cloud / DevOps

*With Farah Belaidouni*

A full-stack cinema catalogue web application, designed from scratch with a microservices architecture and cloud-native deployment:

- **Movie catalogue**: real-time data from the TMDB API with normalisation
- **Redis cache** (Cache-Aside strategy): near-instant search and browsing
- **User system**: authentication and persistent favourites in PostgreSQL
- **Event-driven logging**: asynchronous user-activity journalling via Apache Kafka
- **UX**: dark mode, infinite scroll ("Load More"), bilingual interface (FR/EN)
- **Deployment**: full Kubernetes manifests (Deployments, Services, Ingress) for Minikube; one-command launch via `run.sh`
- **CI/CD**: GitLab CI pipeline using Kaniko for secure container builds

**Stack:** FastAPI (Python 3.11), React.js (Vite), PostgreSQL, Redis, Apache Kafka, Docker, Kubernetes

---

### G-Débat (V/S) — Online Debate Platform
`g-debat.zip` · Python · Web · Full-Stack

*Team project — Scrum Master: Nehir Yüksekkaya*

An online debate platform called **V/S** (V = against, / = neutral, S = for), allowing users to discuss structured topics across thematic categories:

- **Account creation**: email, phone, birthdate, preferred debate categories
- **Voting**: each debate offers three stances — for, against, neutral — with a configurable time limit
- **Debate creation**: any user can propose topics with a category and deadline
- **Results**: once closed, the platform tallies stance changes and declares a winner
- **Database**: relational schema in SQLite, with separate modules for users, debates, arguments, and votes (`db_fun.py`, `db_args_fun.py`, etc.)

**Stack:** Python, Flask, SQLite, HTML/CSS

---

### Fashion-MNIST Classification & Clustering
`projet-datascience.zip` · Python · Machine Learning · Data Science

*Course: LU3IN0226 — IA & Data Science · With Dalia Sadi*

End-to-end supervised and unsupervised learning project on the **Fashion-MNIST** dataset (60,000 train / ~5,000 test images, 784 pixel features, 10 clothing categories). Built on a custom `iads` library implemented throughout the course (`Classifiers.py`, `Clustering.py`, `evaluation.py`, `utils.py`).

**Supervised learning (binary & multi-class):**
- **Perceptron** with learning-rate sweep — reaches 96.7% on easy pair (Trouser vs Pullover)
- **K-NN** (k = 1 → 15) — best single-model accuracy on raw pixels
- **Decision trees** on PCA-50 features (88.5% variance retained) — epsilon-pruning study
- **Bagging** of decision trees — best multi-class accuracy (69.7%), reduces variance significantly
- 5-fold cross-validation comparison + confusion matrix analysis

**Unsupervised learning:**
- **PCA projection** (2D) reveals a natural split: footwear vs. upper-body garments
- **Hierarchical clustering (CHA)** with four linkage strategies — dendrograms show the two macro-groups
- **K-means** (k = 2 → 15) — elbow method + Dunn index; K=10 reaches ~50% global purity
- **Contingency matrix** to measure cluster–class alignment
- **Misclassification analysis**: errors cluster around visually similar pairs (Pullover/Coat/Shirt, Sneaker/Sandal/Ankle Boot)

Results presented with a poster (PDF) and an oral defence.

**Stack:** Python, numpy, pandas, matplotlib, scipy, custom `iads` library

---

## Tech at a glance

`Python` `numpy` `pandas` `scikit-learn` `pygame` `numba` `matplotlib` `Graphviz` `ASP / clingo` `Flask` `FastAPI` `React.js` `PostgreSQL` `Redis` `Kafka` `Docker` `Kubernetes` `Gurobi`
