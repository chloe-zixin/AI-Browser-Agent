from __future__ import annotations

from typing import Any, Dict, List

import requests


API_BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 15


class APIClientError(Exception):
    pass


def _handle_response(response: requests.Response) -> Any:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        message = f"HTTP {response.status_code}: {response.text}"
        raise APIClientError(message) from e

    try:
        return response.json()
    except Exception as e:
        raise APIClientError("Failed to parse JSON response from backend.") from e


def get_health() -> Dict[str, Any]:
    response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
    return _handle_response(response)


def get_tasks() -> List[Dict[str, Any]]:
    response = requests.get(f"{API_BASE_URL}/tasks", timeout=TIMEOUT)
    return _handle_response(response)


def get_task_metrics_summary() -> Dict[str, Any]:
    response = requests.get(f"{API_BASE_URL}/tasks/metrics/summary", timeout=TIMEOUT)
    return _handle_response(response)


def get_task_detail(task_id: str, include_quotes: bool = False) -> Dict[str, Any]:
    response = requests.get(
        f"{API_BASE_URL}/tasks/{task_id}",
        params={"include_quotes": include_quotes},
        timeout=TIMEOUT,
    )
    return _handle_response(response)


def create_task(pages: int, mode: str) -> Dict[str, Any]:
    payload = {
        "pages": pages,
        "mode": mode,
    }
    response = requests.post(f"{API_BASE_URL}/tasks/run", json=payload, timeout=TIMEOUT)
    return _handle_response(response)