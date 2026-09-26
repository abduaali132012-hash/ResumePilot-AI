"""
Shared test helpers for SpecCheck tests.

FakeClient, sample data, and other utilities used across test modules.
"""
from __future__ import annotations


class FakeClient:
    """Drop-in for GeminiClient that never touches the network."""

    available = True  # agents check this

    def __init__(self, response_data):
        self._data = response_data

    def generate_json(self, prompt: str, **kwargs):
        return self._data

    def generate(self, prompt: str, **kwargs):
        import json
        return json.dumps(self._data)


# ------------------------------------------------------------------ #
# Sample resume / JD text reused across many tests.
# ------------------------------------------------------------------ #
SAMPLE_JD = (
    "We are hiring a Python backend engineer. "
    "The candidate should have strong experience with Python, FastAPI, PostgreSQL, and Docker. "
    "Experience with Kubernetes or AWS is a plus but not required."
)

SAMPLE_RESUME = (
    "Senior Software Engineer\n\n"
    "Built APIs with Python and FastAPI for internal business tools. "
    "Managed PostgreSQL databases and containerized services with Docker. "
    "Worked with cloud infrastructure and deployment workflows in a production environment.\n\n"
    "Key accomplishments:\n"
    "- Developed Python automation scripts for ETL and backend integrations.\n"
    "- Built FastAPI services for reporting and customer dashboards.\n"
    "- Managed PostgreSQL schemas and query optimization.\n"
    "- Deployed containerized services using Docker.\n\n"
    "Skills: Python, FastAPI, PostgreSQL, Docker\n\n"
    "Education: B.S. in Computer Science."
)
