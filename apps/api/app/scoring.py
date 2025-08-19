import math
from typing import List, Dict, Tuple

LABEL_SAFE = "safe"
LABEL_SUSPICIOUS = "suspicious"
LABEL_DANGER = "danger"


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def compose_score(S: float, C: float, T: float, U: float) -> float:
    # S/C/T/U in [0,1]
    z = 0.4 * S + 0.25 * C + 0.15 * T + 0.2 * U
    return round(sigmoid(3 * z - 1.5) * 100, 1)


def compose_score_dynamic(S: float, C: float, T: float, U: float, include_u: bool) -> float:
    weights = {"S": 0.4, "C": 0.25, "T": 0.15, "U": 0.2}
    if not include_u:
        total = weights["S"] + weights["C"] + weights["T"]
        S_w = weights["S"] / total
        C_w = weights["C"] / total
        T_w = weights["T"] / total
        z = S_w * S + C_w * C + T_w * T
    else:
        z = weights["S"] * S + weights["C"] * C + weights["T"] * T + weights["U"] * U
    return round(sigmoid(3 * z - 1.5) * 100, 1)


def compute_u_adjusted(u_raw: float, n_votes: int, baseline: float = 0.5, ramp_n: int = 10) -> Tuple[float, float]:
    """Blend community U toward a neutral baseline when votes are few, and return a ramp factor.

    Returns (u_adjusted, u_factor) where u_factor in [0,1] can be used to scale U's weight.
    Example: with ramp_n=10, 1 vote -> factor=0.1; 5 votes -> 0.5; >=10 votes -> 1.0.
    """
    if n_votes <= 0:
        return baseline, 0.0
    alpha = min(1.0, max(0.0, n_votes / float(ramp_n)))
    u_adj = alpha * u_raw + (1.0 - alpha) * baseline
    return max(0.0, min(1.0, u_adj)), alpha


def compose_score_weighted(S: float, C: float, T: float, U: float, u_factor: float) -> float:
    """Compose score with a dynamic weight for U.

    Base weights: S=0.4, C=0.25, T=0.15, U=0.2. We scale U by u_factor in [0,1],
    then re-distribute the remaining weight across S/C/T proportionally to their
    base weights so total remains 1 before sigmoid mapping.
    """
    base = {"S": 0.4, "C": 0.25, "T": 0.15}
    w_u = 0.2 * max(0.0, min(1.0, u_factor))
    rem = 1.0 - w_u
    base_sum = base["S"] + base["C"] + base["T"]
    S_w = rem * (base["S"] / base_sum)
    C_w = rem * (base["C"] / base_sum)
    T_w = rem * (base["T"] / base_sum)
    z = S_w * S + C_w * C + T_w * T + w_u * U
    return round(sigmoid(3 * z - 1.5) * 100, 1)


def classify_level(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "amber"
    return "red"


def wilson_lower_bound(pos: float, n: float, z: float = 1.96) -> float:
    """
    Wilson score lower bound for a Bernoulli parameter.
    pos: positive count (can be fractional when weighting)
    n: total trials
    returns value in [0,1]
    """
    if n <= 0:
        return 0.5
    phat = pos / n
    denom = 1 + z * z / n
    center = phat + z * z / (2 * n)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)
    return max(0.0, min(1.0, (center - margin) / denom))


def compute_u_from_votes(votes: List[Dict]) -> Tuple[float, Dict[str, int]]:
    """Map votes to Wilson lower bound with suspicious as 0.5 weight.
    Returns (U, counts_by_label)
    """
    counts = {LABEL_SAFE: 0, LABEL_SUSPICIOUS: 0, LABEL_DANGER: 0}
    for v in votes:
        label = v.get("label")
        if label in counts:
            counts[label] += 1
    n = sum(counts.values())
    pos = counts[LABEL_SAFE] + 0.5 * counts[LABEL_SUSPICIOUS]
    u = wilson_lower_bound(pos, n) if n > 0 else 0.5
    return u, counts


def compute_breakdown(votes: List[Dict]) -> Dict[str, float]:
    # TODO: Replace S/C/T placeholders with real signals extraction.
    # For MVP bootstrap, assume moderately safe defaults.
    S = 0.8
    C = 0.6
    T = 0.6
    U, _ = compute_u_from_votes(votes)
    return {"S": S, "C": C, "T": T, "U": U}
