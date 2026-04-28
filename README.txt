# 🧠 Prisoner's Dilemma — Information-Theoretic Tournament

An advanced simulation of **Axelrod’s Prisoner's Dilemma Tournament** enhanced with **Shannon Entropy** and **Mutual Information** to create an adaptive intelligent agent.

---

## 🚀 Features

* Classic strategies:

  * Tit-for-Tat
  * Always Defect / Cooperate
  * Grim Trigger
  * Pavlov
  * Random

* 🧠 **Info-Aware Strategy (Novel Contribution)**

  * Uses:

    * Shannon Entropy → Detect randomness
    * Mutual Information → Detect opponent reactivity
  * Dynamically switches behavior:

    * Exploit deterministic players
    * Cooperate with reactive players
    * Defect against random players

---

## 🧪 How It Works

* Each strategy plays against every other
* Payoff matrix:

|       | C   | D   |
| ----- | --- | --- |
| **C** | 3,3 | 0,5 |
| **D** | 5,0 | 1,1 |

* Noise: 5% random move flips
* Metrics:

  * Total score
  * Average score per round
  * Cooperation rate

---

## 🧠 Info-Aware Logic

| Condition    | Interpretation         | Action      |
| ------------ | ---------------------- | ----------- |
| Low entropy  | Deterministic opponent | Exploit     |
| High MI      | Reactive opponent      | Cooperate   |
| High entropy | Random opponent        | Defect      |
| Otherwise    | Uncertain              | Tit-for-Tat |

---

## ▶️ Run the Simulation

```bash
python pd_tournament.py
```

---

## 🌐 Interactive Dashboard

Open:

```bash
web/index.html
```

---


## 💡 Inspiration

Based on Axelrod’s Tournament and extended using **Information Theory**.

---

## 👨‍💻 Author

Built as a research-style simulation combining:

* Game Theory
* Information Theory
* Adaptive AI strategies
