"""Content-based personalization and adaptive UI recommendation logic."""
from collections import Counter
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROLE_DEFAULTS = {
    "Hospital Administrator": ["KPI summary", "Hospital comparison", "State overview"],
    "Healthcare Data Analyst": ["Measure trends", "Detailed data table", "Measure distribution"],
}
VIEW_DESCRIPTIONS = {
    "KPI summary": "high-level summary key performance indicators overview for administrators",
    "Hospital comparison": "compare hospital performance measures across facilities and states",
    "State overview": "summarize healthcare quality records by state and location",
    "Measure trends": "analyze trends over reporting dates and quality measures",
    "Detailed data table": "inspect detailed records, columns, samples, footnotes, and download data",
    "Measure distribution": "explore distribution and spread of numeric measure scores",
}

def recommend_views(role: str, interaction_history: Iterable[str] | None = None, limit: int = 3) -> list[str]:
    """Recommend views using TF-IDF content similarity, role context, and interaction frequency.

    This is a lightweight content-based recommender; it is not a generative model.
    """
    history = [x for x in (interaction_history or []) if x in VIEW_DESCRIPTIONS]
    defaults = ROLE_DEFAULTS.get(role, ROLE_DEFAULTS["Healthcare Data Analyst"])
    if not history:
        return defaults[:max(1, limit)]
    names = list(VIEW_DESCRIPTIONS)
    descriptions = [VIEW_DESCRIPTIONS[name] for name in names]
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(descriptions)
    profile_text = " ".join([role] + [VIEW_DESCRIPTIONS[x] for x in history] + [VIEW_DESCRIPTIONS[x] for x in defaults])
    profile = vectorizer.transform([profile_text])
    similarity = cosine_similarity(profile, matrix).ravel()
    counts = Counter(history)
    scores = {}
    for i, name in enumerate(names):
        scores[name] = float(similarity[i]) + 0.35 * counts[name] + (1.0 if name in defaults else 0.0)
    return sorted(names, key=lambda n: (-scores[n], names.index(n)))[:max(1, limit)]

def choose_layout(role: str, simplified: bool = False) -> dict:
    """Return a declarative layout profile used by the UI."""
    if simplified:
        return {"show_kpis": True, "show_charts": True, "show_table": False, "columns": 1}
    if role == "Hospital Administrator":
        return {"show_kpis": True, "show_charts": True, "show_table": False, "columns": 2}
    return {"show_kpis": True, "show_charts": True, "show_table": True, "columns": 2}

def log_interaction(history: list[str], view_name: str, max_items: int = 50) -> list[str]:
    """Append an interaction to an in-memory, bounded history."""
    return (list(history) + [view_name])[-max_items:]
