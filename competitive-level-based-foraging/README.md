# Competitive Level-Based Foraging

A competitive two-team resource-collection game implemented for the *AI & Games* course (LU3IN025) at Sorbonne Université.

**Team:** Nehir Yüksekkaya & Kathy Vo

## Game Rules

Two teams of 8 players compete over 5 vials per round. Vial capture rules depend on colour:

| Colour | Condition to capture |
|---|---|
| Yellow | ≥ 1 player; majority team wins |
| Red | ≥ 2 players from same team; majority wins |
| Green | ≥ 3 players total; majority team wins |
| Blue | Like Red, but a lone player beats a team that meets the condition |

Ties leave the vial uncaptured. Teams move simultaneously with full observability.

## Strategies Implemented

### Stationary
- **Random** — uniform random vial selection (baseline)
- **Stubborn** — always targets the same vial
- **Greedy** — targets the least-contested vial each round
- **Expert** — samples from a hand-crafted set of fixed allocations
- **Coordination** — probabilistically concentrates the team on one vial (p=0.7)

### History-Based
- **Fictitious Play** — models the opponent's empirical distribution and greedily allocates players to minimise cost-to-win per vial
- **Regret Matching** — tracks counterfactual regret per vial and samples proportionally to positive regret (converges to correlated equilibrium)

## Results Highlight

Compared across all 5 maps (`yellow`, `red`, `green`, `blue`, `mixed`), 20 episodes each:

- **Fictitious play** is the strongest overall strategy, especially on complex maps (`expert vs fictitious`: 0/13 on blue-map)
- **Regret matching** is competitive and beats fictitious play on blue-map and mixed-map
- **Greedy** dominates stationary strategies but collapses on blue-map (loses 14/1 to random) due to its dispersion logic conflicting with the lone-player rule
- **Blue-map** inverts most strategy rankings, exposing structural weaknesses

Full results table and analysis: [`docs/rapport.md`](docs/rapport.md)

## Implementation Notes

- Team assignment uses spawn-row detection (`x == 2` → team 0, `x == 18` → team 1) rather than list-index splitting, for robustness across map variants
- Priority alternates each episode to prevent first-mover advantage
- `compare_all()` runs every strategy pair on every map automatically and prints a summary table

## Stack

Python · pygame · pySpriteWorld · A\* pathfinding (`search` module)

## Running

```bash
cd src
python main.py
```

To change the map, edit the `name` variable in `main.py`'s `init()` function (options: `yellow-map`, `red-map`, `green-map`, `blue-map`, `mixed-map`).
