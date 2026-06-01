# Robot AI — Paint Wars

A 2D robot simulator for a competitive paint-coverage game (Paint Wars), developed as part of the *Introduction to AI* course (LU3IN025) at Sorbonne Université.

## Overview

The project progresses through three stages of increasing sophistication:

**1. Braitenberg Vehicles**
Reactive controllers wired directly from sensors to motors. Implemented wall-avoiders, bot-chasers, and wall-lovers as building blocks.

**2. Subsumption Architecture**
Priority-layered behaviour system:
- Layer 0 (lowest): random exploration / wandering
- Layer 1: wall avoidance
- Layer 2 (highest): aggressive paint coverage / opponent interaction

Higher layers suppress lower ones when their activation conditions are met.

**3. Evolutionary Optimisation**
A **(1+1)-Genetic Algorithm** evolves the sensor weight arrays of a Braitenberg-based controller over 500 generations. Each individual is evaluated across 3 fixed starting orientations to reduce variance. Numba JIT compilation (`@njit`) brings a **>10× speedup** in headless simulation mode (~2300 fps vs ~230 fps on an M3 MacBook Air).

A **random search** baseline is also implemented for ablation comparison (`robot_randomsearch.py`).

## Key Files

| File | Description |
|---|---|
| `tetracomposibot.py` | Main simulator (arena, sensor model, display) |
| `robot.py` | Base `Robot` class |
| `robot_sub_FINAL.py` | Final subsumption architecture controller |
| `genetic_algorithms.py` | (1+1)-GA optimiser |
| `robot_randomsearch.py` | Random search baseline |
| `robot_braitenberg_*.py` | Individual Braitenberg behaviour modules |
| `arenas.py` / `arenas_eval.py` | Arena definitions for training and evaluation |
| `config_*.py` | Experiment configurations |

## Running

```bash
python tetracomposibot.py --config config_fin.py
```

Display modes: `0` = full pygame, `1` = lightweight, `2` = headless (fastest, for optimisation runs).

## Stack

Python · pygame · numpy · numba
