"""
Prisoner's Dilemma Information-Theoretic Tournament
====================================================
Axelrod's classic tournament + Shannon entropy & mutual information
as a memory/compression mechanism for an adaptive agent.

Strategies
----------
- Tit-for-Tat       : Mirror opponent's last move
- Always Defect     : Always D
- Always Cooperate  : Always C
- Grim Trigger      : Cooperate until first defection, then D forever
- Pavlov            : Win-stay, lose-shift
- Random            : 50/50 each round
- Info-Aware        : Uses H(opponent) and I(my_move; their_next) to decide

Payoff matrix  (row=me, col=opponent)
    C   D
C  3,3  0,5
D  5,0  1,1
"""

from __future__ import annotations
import math
import random
import itertools
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import sys

# ── Payoff ────────────────────────────────────────────────────────────────────
PAYOFF: dict[str, Tuple[int, int]] = {
    "CC": (3, 3),
    "CD": (0, 5),
    "DC": (5, 0),
    "DD": (1, 1),
}

Move = str  # 'C' or 'D'


# ── Information-theoretic helpers ─────────────────────────────────────────────

def shannon_entropy(history: List[Move]) -> float:
    """H(X) in bits for a binary sequence of C/D moves."""
    if not history:
        return 0.0
    n = len(history)
    c = history.count("C") / n
    d = 1.0 - c

    def xlogx(p: float) -> float:
        return 0.0 if p <= 0 or p >= 1 else -p * math.log2(p)

    return xlogx(c) + xlogx(d)


def mutual_information(my_history: List[Move],
                       their_history: List[Move],
                       window: int = 8) -> float:
    """
    I(my_move_t ; their_move_{t+1}) estimated over the last `window` rounds.

    High MI  → opponent is reactive (my moves predict their next move).
    Low MI   → opponent is indifferent to what I do.
    """
    n = min(len(my_history), len(their_history), window)
    if n < 4:
        return 0.0

    pairs: Counter = Counter()
    offset = len(my_history) - n
    for i in range(offset, len(my_history) - 1):
        x = my_history[i]
        y = their_history[i + 1] if (i + 1) < len(their_history) else "C"
        pairs[(x, y)] += 1

    total = sum(pairs.values())
    if total == 0:
        return 0.0

    p_xy = {k: v / total for k, v in pairs.items()}
    p_x: dict[str, float] = {}
    p_y: dict[str, float] = {}
    for (x, y), p in p_xy.items():
        p_x[x] = p_x.get(x, 0.0) + p
        p_y[y] = p_y.get(y, 0.0) + p

    mi = 0.0
    for (x, y), pxy in p_xy.items():
        if pxy > 0:
            mi += pxy * math.log2(pxy / (p_x[x] * p_y[y]))
    return max(0.0, mi)


def compress_history(history: List[Move], window: int = 8,
                     eps: float = 0.05) -> List[Move]:
    """
    Keep only the last `window` moves; within that window discard
    moves that contribute < eps bits of incremental entropy.
    Returns the compressed (informative) suffix.
    """
    win = history[-window:]
    if len(win) <= 2:
        return win
    kept: List[Move] = [win[0]]
    for m in win[1:]:
        trial = kept + [m]
        if shannon_entropy(trial) - shannon_entropy(kept) >= eps:
            kept.append(m)
    return kept


# ── Strategy base class ───────────────────────────────────────────────────────

class Strategy:
    name: str = "Abstract"
    short: str = "???"

    def move(self,
             my_history: List[Move],
             their_history: List[Move],
             window: int = 8) -> Move:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.name


# ── Classic strategies ────────────────────────────────────────────────────────

class TitForTat(Strategy):
    name, short = "Tit-for-Tat", "TFT"

    def move(self, my_history, their_history, window=8):
        return their_history[-1] if their_history else "C"


class AlwaysDefect(Strategy):
    name, short = "Always Defect", "ALLD"

    def move(self, my_history, their_history, window=8):
        return "D"


class AlwaysCooperate(Strategy):
    name, short = "ALLC", "ALLC"

    def move(self, my_history, their_history, window=8):
        return "C"


class GrimTrigger(Strategy):
    name, short = "Grim Trigger", "GRIM"

    def move(self, my_history, their_history, window=8):
        return "D" if "D" in their_history else "C"


class Pavlov(Strategy):
    """Win-stay, lose-shift."""
    name, short = "Pavlov", "PAV"

    def move(self, my_history, their_history, window=8):
        if not my_history:
            return "C"
        m, o = my_history[-1], their_history[-1]
        key = m + o
        if key in ("CC", "DC"):   # won last round → repeat
            return m
        return "D" if m == "C" else "C"   # lost → switch


class RandomStrategy(Strategy):
    name, short = "Random", "RND"

    def move(self, my_history, their_history, window=8):
        return random.choice(["C", "D"])


# ── Information-aware agent ───────────────────────────────────────────────────

@dataclass
class InfoDiagnostics:
    entropy: float = 0.0
    mutual_info: float = 0.0
    regime: str = "bootstrap"
    compressed_len: int = 0
    raw_len: int = 0
    decision: Move = "C"


class InfoAwareStrategy(Strategy):
    """
    Adaptive strategy using Shannon entropy H(opponent) and mutual
    information I(my_move ; their_next) over a sliding window.

    Decision rules
    ──────────────
    H < 0.30 bits  → deterministic opponent  → exploit (mirror their mode)
    MI > 0.40 bits → reactive opponent       → cooperate (induce cooperation)
    H > 0.70 bits  → random/unpredictable   → defect (can't be exploited)
    else           → adaptive TFT fallback
    """
    name, short = "Info-Aware", "INFO"

    H_DETERMINISTIC = 0.30
    H_RANDOM        = 0.70
    MI_REACTIVE     = 0.40

    def __init__(self):
        self.last_diag = InfoDiagnostics()

    def move(self, my_history: List[Move],
             their_history: List[Move],
             window: int = 8) -> Move:

        compressed = compress_history(their_history, window)
        H  = shannon_entropy(compressed)
        MI = mutual_information(my_history, their_history, window)

        diag = InfoDiagnostics(
            entropy=H, mutual_info=MI,
            compressed_len=len(compressed), raw_len=len(their_history)
        )

        # Bootstrap: too little data
        if len(their_history) < 3:
            diag.regime = "bootstrap"
            diag.decision = "C"

        elif H < self.H_DETERMINISTIC:
            # Deterministic opponent → mirror their dominant move
            mode = "C" if compressed.count("C") > len(compressed) / 2 else "D"
            diag.regime = "deterministic-exploit"
            diag.decision = mode

        elif MI > self.MI_REACTIVE:
            # Reactive opponent → cooperate to induce cooperation
            diag.regime = "reactive-induce-coop"
            diag.decision = "C"

        elif H > self.H_RANDOM:
            # Random → defect (can't coordinate, protect score)
            diag.regime = "random-defect"
            diag.decision = "D"

        else:
            # Adaptive TFT fallback
            diag.regime = "adaptive-TFT"
            diag.decision = their_history[-1] if their_history else "C"

        self.last_diag = diag
        return diag.decision


# ── Match engine ──────────────────────────────────────────────────────────────

@dataclass
class MatchResult:
    strategy_a: str
    strategy_b: str
    score_a: int
    score_b: int
    history_a: List[Move]
    history_b: List[Move]
    rounds: int

    @property
    def avg_a(self) -> float:
        return self.score_a / self.rounds

    @property
    def avg_b(self) -> float:
        return self.score_b / self.rounds

    @property
    def coop_rate_a(self) -> float:
        return self.history_a.count("C") / self.rounds

    @property
    def coop_rate_b(self) -> float:
        return self.history_b.count("C") / self.rounds


def play_match(strategy_a: Strategy,
               strategy_b: Strategy,
               rounds: int = 100,
               noise: float = 0.05,
               window: int = 8,
               seed: Optional[int] = None) -> MatchResult:
    """Play one match; noise flips a move with probability `noise`."""
    if seed is not None:
        random.seed(seed)

    hist_a: List[Move] = []
    hist_b: List[Move] = []
    score_a = score_b = 0

    def apply_noise(m: Move) -> Move:
        if noise > 0 and random.random() < noise:
            return "D" if m == "C" else "C"
        return m

    for _ in range(rounds):
        ma = apply_noise(strategy_a.move(hist_a, hist_b, window))
        mb = apply_noise(strategy_b.move(hist_b, hist_a, window))
        pa, pb = PAYOFF[ma + mb]
        score_a += pa
        score_b += pb
        hist_a.append(ma)
        hist_b.append(mb)

    return MatchResult(strategy_a.name, strategy_b.name,
                       score_a, score_b, hist_a, hist_b, rounds)


# ── Tournament ────────────────────────────────────────────────────────────────

@dataclass
class TournamentResult:
    strategies: List[str]
    total_scores: dict[str, int]
    match_counts: dict[str, int]
    coop_rates: dict[str, float]
    matrix: dict[Tuple[str, str], float]   # avg score per round
    matches: List[MatchResult]

    @property
    def leaderboard(self) -> List[Tuple[str, int, float, float]]:
        """Returns [(name, total_score, avg_per_round, coop_rate)] sorted desc."""
        return sorted(
            [(n, self.total_scores[n],
              self.total_scores[n] / (self.match_counts[n] * 1),
              self.coop_rates[n])
             for n in self.strategies],
            key=lambda x: -x[1]
        )


def run_tournament(strategies: List[Strategy],
                   rounds: int = 100,
                   noise: float = 0.05,
                   window: int = 8,
                   seed: Optional[int] = 42) -> TournamentResult:
    """Round-robin tournament: every pair plays once."""
    names = [s.name for s in strategies]
    total_scores: dict[str, int]   = {n: 0 for n in names}
    match_counts: dict[str, int]   = {n: 0 for n in names}
    coop_totals:  dict[str, float] = {n: 0.0 for n in names}
    matrix:       dict[Tuple[str, str], float] = {}
    all_matches:  List[MatchResult] = []

    pairs = list(itertools.permutations(strategies, 2))
    for i, (sa, sb) in enumerate(pairs):
        r_seed = (seed + i) if seed is not None else None
        res = play_match(sa, sb, rounds=rounds, noise=noise,
                         window=window, seed=r_seed)
        total_scores[sa.name] += res.score_a
        match_counts[sa.name] += rounds   # per-round denominator
        coop_totals[sa.name]  += res.coop_rate_a
        matrix[(sa.name, sb.name)] = res.avg_a
        all_matches.append(res)

    # Normalise cooperation rate
    pair_counts = {n: sum(1 for sa, sb in pairs if sa.name == n)
                   for n in names}
    coop_rates = {n: coop_totals[n] / pair_counts[n] for n in names}

    return TournamentResult(names, total_scores, match_counts,
                            coop_rates, matrix, all_matches)


# ── Pretty-printing helpers ───────────────────────────────────────────────────

def _bar(val: float, max_val: float, width: int = 20) -> str:
    filled = int(round(val / max_val * width)) if max_val else 0
    return "█" * filled + "░" * (width - filled)


def print_leaderboard(result: TournamentResult) -> None:
    lb = result.leaderboard
    max_score = lb[0][1] if lb else 1
    print("\n" + "═" * 72)
    print("  TOURNAMENT LEADERBOARD")
    print("═" * 72)
    print(f"  {'#':<3} {'Strategy':<18} {'Total':>7} {'Avg/rnd':>8} "
          f"{'Coop%':>7}  Score")
    print("─" * 72)
    for rank, (name, total, avg, coop) in enumerate(lb, 1):
        bar = _bar(total, max_score)
        marker = " ← WINNER" if rank == 1 else ""
        print(f"  {rank:<3} {name:<18} {total:>7} {avg:>8.2f} "
              f"{coop*100:>6.0f}%  {bar}{marker}")
    print("═" * 72)


def print_matrix(result: TournamentResult) -> None:
    names = result.strategies
    shorts = {s: s[:6] for s in names}
    col_w = 7
    print("\n  HEAD-TO-HEAD MATRIX  (avg score per round for row player)")
    print("  " + " " * 18 + "  ".join(f"{shorts[n]:>{col_w}}" for n in names))
    print("  " + "─" * (18 + (col_w + 2) * len(names)))
    for na in names:
        row = f"  {na:<18}"
        for nb in names:
            if na == nb:
                row += f"{'—':>{col_w}}  "
            else:
                v = result.matrix.get((na, nb), 0.0)
                row += f"{v:>{col_w}.2f}  "
        print(row)


def print_info_diagnostics(result: TournamentResult,
                           strategies: List[Strategy]) -> None:
    info_strat = next((s for s in strategies
                       if isinstance(s, InfoAwareStrategy)), None)
    if not info_strat:
        return

    print("\n  INFO-AWARE AGENT — FINAL MATCH DIAGNOSTICS")
    print("─" * 60)
    for m in result.matches:
        if m.strategy_a != "Info-Aware":
            continue
        H  = shannon_entropy(m.history_b)
        MI = mutual_information(m.history_a, m.history_b)
        cr = m.history_b.count("C") / m.rounds
        print(f"  vs {m.strategy_b:<18}  H={H:.3f} bits  "
              f"MI={MI:.3f} bits  opp_coop={cr:.0%}")


def print_match_detail(res: MatchResult, n_show: int = 40) -> None:
    print(f"\n  MATCH DETAIL: {res.strategy_a}  vs  {res.strategy_b}")
    print(f"  Final scores: {res.score_a} — {res.score_b}  "
          f"({'A wins' if res.score_a > res.score_b else 'B wins' if res.score_b > res.score_a else 'Tie'})")
    print(f"  Coop rates: A={res.coop_rate_a:.0%}  B={res.coop_rate_b:.0%}")
    shown = min(n_show, res.rounds)
    print(f"\n  First {shown} moves:")
    print("  A: " + " ".join(res.history_a[:shown]))
    print("  B: " + " ".join(res.history_b[:shown]))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    random.seed(0)

    # ── Parameters ──
    ROUNDS   = 150
    NOISE    = 0.05   # 5% move-flip probability
    WINDOW   = 8      # sliding window for MI / entropy

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  PRISONER'S DILEMMA — INFORMATION-THEORETIC TOURNAMENT          ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print(f"║  Rounds/match: {ROUNDS:<4}  Noise: {NOISE*100:.0f}%  MI window: {WINDOW}              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    strategies: List[Strategy] = [
        TitForTat(),
        AlwaysDefect(),
        AlwaysCooperate(),
        GrimTrigger(),
        Pavlov(),
        RandomStrategy(),
        InfoAwareStrategy(),
    ]

    print(f"\n  Running {len(strategies)} strategies × {len(strategies)-1} opponents "
          f"× {ROUNDS} rounds each …\n")

    result = run_tournament(strategies, rounds=ROUNDS,
                            noise=NOISE, window=WINDOW, seed=42)

    print_leaderboard(result)
    print_matrix(result)
    print_info_diagnostics(result, strategies)

    # ── Spotlight: Info-Aware vs TFT and vs AlwaysDefect ──
    print("\n" + "═" * 72)
    print("  SPOTLIGHT MATCHES")
    print("═" * 72)
    for opponent in strategies:
        if opponent.name in ("Tit-for-Tat", "Always Defect", "Grim Trigger"):
            res = play_match(InfoAwareStrategy(), opponent,
                             rounds=ROUNDS, noise=NOISE,
                             window=WINDOW, seed=7)
            print_match_detail(res)

    # ── Entropy probe demo ──
    print("\n" + "═" * 72)
    print("  INFORMATION-THEORETIC PROBE DEMO")
    print("═" * 72)
    test_seqs = {
        "Always Cooperate  ": list("C" * 20),
        "Always Defect     ": list("D" * 20),
        "Tit-for-Tat echo  ": list("CDCDCDCD" * 3)[:20],
        "Random opponent   ": [random.choice("CD") for _ in range(20)],
        "Mostly Cooperate  ": list("CCCCD" * 4),
    }
    print(f"  {'Sequence type':<22} {'H (bits)':>9} {'MI (bits)':>10} {'Regime':<28} {'INFO would'}")
    print("  " + "─" * 80)
    dummy_my = [random.choice("CD") for _ in range(20)]
    for label, seq in test_seqs.items():
        agent = InfoAwareStrategy()
        # Feed history step by step to get realistic MI
        for i in range(len(seq) - 1):
            agent.move(dummy_my[:i+1], seq[:i+1])
        decision = agent.move(dummy_my, seq)
        H  = shannon_entropy(seq)
        MI = mutual_information(dummy_my, seq)
        print(f"  {label:<22} {H:>9.3f} {MI:>10.3f}  {agent.last_diag.regime:<28} {decision}")

    print("\n  Done.\n")


if __name__ == "__main__":
    main()