"""Ghosting probability model.

A small scikit-learn LogisticRegression that estimates the probability a job
application has been *ghosted* based on how long it has been since the last
contact and whether the company ever made contact at all.

The model is trained once at import time on a synthetic but realistic dataset
(recruiters typically respond within ~1-2 weeks), so the app has no external
data dependency. `predict_ghost_probability()` is the public entry point.
"""
import numpy as np

_model = None


def _build_training_data(n=2000, seed=42):
    """Generate synthetic (features, label) pairs.

    Features: [days_since_contact, had_contact]
      - days_since_contact: integer 0..45
      - had_contact: 1 if the company ever replied, else 0
    Label: 1 = ghosted, 0 = still active. Longer silence and never having had
    contact both push the probability of ghosting up; noise keeps it realistic.
    """
    rng = np.random.default_rng(seed)
    days = rng.integers(0, 46, size=n)
    had_contact = rng.integers(0, 2, size=n)
    # Latent score: silence is the dominant driver; no prior contact adds risk.
    score = (days - 12) / 4.0 + (1 - had_contact) * 1.5
    prob = 1 / (1 + np.exp(-score))
    labels = (rng.random(n) < prob).astype(int)
    X = np.column_stack([days, had_contact]).astype(float)
    return X, labels


def _get_model():
    global _model
    if _model is None:
        from sklearn.linear_model import LogisticRegression
        X, y = _build_training_data()
        clf = LogisticRegression()
        clf.fit(X, y)
        _model = clf
    return _model


def predict_ghost_probability(days_since_contact, had_contact):
    """Return P(ghosted) in [0, 1] as a float, or None if sklearn is unavailable."""
    try:
        model = _get_model()
        x = np.array([[float(days_since_contact), 1.0 if had_contact else 0.0]])
        return float(model.predict_proba(x)[0][1])
    except Exception:
        return None
