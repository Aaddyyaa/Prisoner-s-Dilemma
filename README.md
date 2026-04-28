# 🧠 Prisoner's Dilemma — Information-Theoretic Tournament

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

An advanced simulation of **Axelrod’s Prisoner's Dilemma Tournament** enhanced with:

* 📊 **Shannon Entropy**
* 🔗 **Mutual Information**

to build an **adaptive intelligent strategy (Info-Aware Agent)**.

---

## 🚀 Features

### 🎮 Classic Strategies

* Tit-for-Tat
* Always Defect / Always Cooperate
* Grim Trigger
* Pavlov (Win-Stay, Lose-Shift)
* Random

---

### 🧠 Info-Aware Strategy (🔥 Novel Contribution)

Uses **information theory** to classify opponents:

#### 📊 Signals Used

* **Shannon Entropy → Detect randomness**
* **Mutual Information → Detect reactivity**

#### ⚡ Adaptive Behavior

* Exploit deterministic players
* Cooperate with reactive players
* Defect against random players

---

## ⚙️ How It Works

* Round-robin tournament (every strategy vs every other)
* Noise: **5% random move flips**
* Metrics tracked:

  * Total score
  * Average score per round
  * Cooperation rate

---

## 📊 Payoff Matrix

```text
          Opponent
           C     D
        ┌─────┬─────┐
     C  │ 3,3 │ 0,5 │
        ├─────┼─────┤
     D  │ 5,0 │ 1,1 │
        └─────┴─────┘
```

---

## 🧠 Info-Aware Decision Logic

| Condition    | Interpretation         | Action      |
| ------------ | ---------------------- | ----------- |
| Low entropy  | Deterministic opponent | Exploit     |
| High MI      | Reactive opponent      | Cooperate   |
| High entropy | Random opponent        | Defect      |
| Otherwise    | Uncertain              | Tit-for-Tat |

---

## ▶️ Run the Project

```bash
python pd_tournament.py
```


---

## 📦 Dependencies

✅ None — pure Python (stdlib only)

---

## 📜 License

MIT License

---

## 💡 Why This Project Matters

This project combines:

* 🎲 Game Theory
* 📊 Information Theory
* 🤖 Adaptive AI

to go beyond classic fixed strategies into **intelligent decision-making systems**.

---

## 👨‍💻 Author

Built as a research-style simulation exploring **adaptive behavior in competitive environments**.
