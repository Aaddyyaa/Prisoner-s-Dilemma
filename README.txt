# 🧠 Prisoner's Dilemma — Information-Theoretic Tournament

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=flat" alt="Status" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License" />
</p>

An advanced simulation of **Axelrod’s Prisoner's Dilemma Tournament** enhanced with information-theoretic metrics to build an **adaptive intelligent strategy (Info-Aware Agent)**.

---

## 🚀 Features

### 🎮 Classic Strategies
* **Tit-for-Tat**: Reciprocates the opponent's previous move.
* **Always Defect / Always Cooperate**: Fixed behavior patterns.
* **Grim Trigger**: Cooperates until the opponent defects once, then defects forever.
* **Pavlov (Win-Stay, Lose-Shift)**: Repeats move if successful, switches if not.
* **Random**: Moves are determined by a 50/50 probability.

### 🧠 Info-Aware Strategy (🔥 Novel Contribution)
Uses **Information Theory** to classify and counter opponents dynamically:

#### 📊 Signals Used
* **Shannon Entropy ($H$):** Measures the unpredictability of an opponent's moves.
* **Mutual Information ($I$):** Quantifies the dependency between your moves and the opponent’s reactions.

#### ⚡ Adaptive Behavior
* **Exploit** deterministic players (Low Entropy).
* **Cooperate** with reactive players (High Mutual Information).
* **Defect** against random players (High Entropy).

---

## ⚙️ How It Works

* **Format**: Round-robin tournament (every strategy vs. every other).
* **Noise**: 5% probability of random move flips to test robustness.
* **Metrics Tracked**:
  * Total & Average Score
  * Cooperation Rate
  * Convergence to Nash Equilibrium

---

## 📊 Payoff Matrix

```text
          Opponent
            C     D
         ┌─────┬─────┐
      C  │ 3,3 │ 0,5 │
         ├─────┼─────┤
      D  │ 5,0 │ 1,1 │
         └─────└─────┘
