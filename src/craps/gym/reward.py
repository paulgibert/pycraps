from typing import Tuple
from numpy.typing import NDArray
import numpy as np

def cpt_utility(x: NDArray[np.float32], ref: float, n_bins: int=10) -> np.float32:
    outcomes, probs = _get_outcomes_and_probs(x, ref, n_bins)
    return _cpt_evaluate(outcomes, probs)

def cpt_utility_from_returns(returns: NDArray[np.float32], n_bins: int=10) -> np.float32:
    outcomes, probs = _get_outcomes_and_probs_from_returns(returns, n_bins)
    return _cpt_evaluate(outcomes, probs)

def _cpt_evaluate(
    outcomes: NDArray[np.float32],
    probs: NDArray[np.float32]
) -> np.float32:
    outcomes_gain = outcomes[outcomes >= 0]
    probs_gain = probs[outcomes >= 0]

    outcomes_loss = outcomes[outcomes < 0]
    probs_loss = probs[outcomes < 0]

    values_gain = _cpt_values(outcomes_gain)
    pis_gain = _gain_decision_weights(probs_gain)

    values_loss = _cpt_values(outcomes_loss)
    pis_loss = _loss_decision_weights(probs_loss)

    utility_gain = np.sum(values_gain * pis_gain)
    utility_loss = np.sum(values_loss * pis_loss)

    return utility_gain + utility_loss

def _get_outcomes_and_probs(
    x: NDArray[np.float32],
    ref: float,
    n_bins: int
) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
    counts, edges = np.histogram(x, bins=n_bins)
    outcomes = (0.5 * (edges[:-1] + edges[1:]) - ref) / ref

    mask = counts != 0
    counts = counts[mask]
    outcomes = outcomes[mask]

    probs = counts / counts.sum()

    idx = np.argsort(outcomes)
    outcomes = outcomes[idx]
    probs = probs[idx]

    return outcomes, probs

def _get_outcomes_and_probs_from_returns(
    returns: NDArray[np.float32],
    n_bins: int
) -> Tuple[NDArray[np.float32], NDArray[np.float32]]:
    counts, edges = np.histogram(returns, bins=n_bins)
    outcomes = 0.5 * (edges[:-1] + edges[1:])

    mask = counts != 0
    counts = counts[mask]
    outcomes = outcomes[mask]

    probs = counts / counts.sum()

    idx = np.argsort(outcomes)
    outcomes = outcomes[idx]
    probs = probs[idx]

    return outcomes, probs

def _cpt_values(
        x: NDArray[np.float32],
        alpha: float=0.88,
        beta: float=0.88,
        lamb: float=2.25
) -> NDArray[np.float32]:
    y = x.copy()
    y[y >= 0] = y[y >= 0] ** alpha
    y[y < 0] = -lamb * (-y[y < 0]) ** beta
    return y

def _gain_decision_weights(
    probs: NDArray[np.float32]
) -> NDArray[np.float32]:
    """
    Note: We assume probs is sorted.
    """
    pis = []
    cumsum = 0.0
    for p in probs[::-1]:      # largest gain first
        pi = _weigh_probs(cumsum + p) - _weigh_probs(cumsum)
        pis.insert(0, pi)
        cumsum += p
    return np.array(pis)


def _loss_decision_weights(
    probs: NDArray[np.float32]
) -> NDArray[np.float32]:
    """
    Note: We assume probs is sorted.
    """
    pis = []
    cumsum = 0.0
    for p in probs:
        pi = _weigh_probs(cumsum + p) - _weigh_probs(cumsum)
        pis.append(pi)
        cumsum += p
    return np.array(pis)

def _weigh_probs(
        probs: NDArray[np.float32],
        gamma: float=0.61
) -> NDArray[np.float32]:
    probs = np.clip(probs, 0.0, 1.0)
    a = probs ** gamma
    b = (1-probs) ** gamma
    return a / ((a + b) ** (1 / gamma))