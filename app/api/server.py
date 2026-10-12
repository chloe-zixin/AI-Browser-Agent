from __future__ import annotations

import traceback
from typing import Any, Dict, List, Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.analyzer.llm_analyzer import analyze_quote_with_llm
from app.analyzer.quotes_analyzer import analyze_quotes
from app.crawler.quotes_spider import SOURCE_ID, SOURCE_URL, crawl_quotes, deduplicate_quotes
from app.task.task_manager import task_manager


app = FastAPI(
    title="AI Browser Agent Workflow Platform API",
    description="""
A task-driven AI browser workflow backend for structured crawling,
semantic enrichment, task lifecycle orchestration, and dashboard monitoring.
""".strip(),
    version="2.0.0",
    contact={
        "name": "Catherine",
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRunRequest(BaseModel):
    pages: int = Field(default=3, ge=1, le=20, description="Number of pages to crawl")
    mode: Literal["local"] = Field(default="local", description="Analysis mode")


class TaskRunResponse(BaseModel):
    task_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    response_model=HealthResponse,
)
def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "AI Browser Agent Workflow Platform API",
        "version": "2.0.0",
    }


@app.get(
    "/tasks",
    tags=["Tasks"],
    summary="List all tasks",
)
def list_tasks() -> List[Dict[str, Any]]:
    return task_manager.list_tasks()


@app.get(
    "/tasks/metrics/summary",
    tags=["Tasks"],
    summary="Get dashboard summary metrics",
)
def get_task_metrics_summary() -> Dict[str, Any]:
    return task_manager.get_metrics_summary()


@app.get(
    "/tasks/{task_id}",
    tags=["Tasks"],
    summary="Get task detail by task_id",
)
def get_task_detail(task_id: str, include_quotes: bool = Query(default=False)) -> Dict[str, Any]:
    task = task_manager.get_task(task_id, include_quotes=include_quotes)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return task


@app.post(
    "/tasks/run",
    tags=["Tasks"],
    summary="Create and run a new task",
    response_model=TaskRunResponse,
)
def run_task(payload: TaskRunRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    task = task_manager.create_task(pages=payload.pages, mode=payload.mode)
    task_id = task["task_id"]
    task_manager.update_task(
        task_id,
        {
            "source_id": SOURCE_ID,
            "source_url": SOURCE_URL,
            "provenance_version": 1,
        },
    )

    background_tasks.add_task(execute_pipeline_task, task_id, payload.pages, payload.mode)

    return {
        "task_id": task_id,
        "status": "pending",
        "message": "Task created successfully and scheduled for background execution.",
    }


def execute_pipeline_task(task_id: str, pages: int, mode: str) -> None:
    try:
        task_manager.mark_running(task_id)

        crawled_quotes = crawl_quotes(pages=pages, headless=True)
        raw_quotes = [item for item in crawled_quotes if str(item.get("quote") or "").strip()]
        quotes_to_analyze = deduplicate_quotes(raw_quotes)
        duplicate_count = len(raw_quotes) - len(quotes_to_analyze)
        if not quotes_to_analyze:
            raise RuntimeError("The crawler returned no quotes.")
        for item in quotes_to_analyze:
            source_url = str(item.get("source_url") or "")
            if (
                item.get("source_id") != SOURCE_ID
                or not source_url.startswith(SOURCE_URL)
                or not item.get("captured_at")
                or not item.get("record_id")
            ):
                raise RuntimeError("A crawled quote is missing valid source provenance metadata.")

        quotes: List[Dict[str, Any]] = []
        for item in quotes_to_analyze:
            quote_text = str(item.get("quote") or "").strip()
            author = str(item.get("author") or "").strip()
            raw_tags = item.get("tags")
            tags: List[Any] = list(raw_tags) if isinstance(raw_tags, list) else []
            enrichment = analyze_quote_with_llm(
                quote=quote_text,
                author=author,
                tags=[str(tag) for tag in tags],
            )
            quotes.append(
                {
                    "text": quote_text,
                    "author": author,
                    "tags": tags,
                    "source_page": item.get("page"),
                    "source_id": item.get("source_id", SOURCE_ID),
                    "source_url": item.get("source_url", SOURCE_URL),
                    "captured_at": item.get("captured_at"),
                    "record_id": item.get("record_id"),
                    **enrichment,
                    "analysis_method": "local_keyword_rules",
                }
            )

        report = analyze_quotes(quotes_to_analyze)
        report.update(
            {
                "summary": f"Crawled and locally analyzed {len(quotes)} quotes.",
                "quote_count": len(quotes),
                "unique_authors": len({quote["author"] for quote in quotes if quote["author"]}),
                "total_tags": sum(len(quote.get("tags") or []) for quote in quotes),
                "mode": mode,
                "analysis_method": "local_keyword_rules",
                "provenance_version": 1,
                "source_id": SOURCE_ID,
                "source_url": SOURCE_URL,
                "duplicate_count": duplicate_count,
                "requested_pages": pages,
                "crawled_pages": len({item.get("page") for item in quotes_to_analyze}),
            }
        )

        task_manager.mark_success(task_id, quotes=quotes, report=report)

    except Exception as e:
        error_message = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        task_manager.mark_failed(task_id, error=error_message)
