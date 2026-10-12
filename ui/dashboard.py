from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd
import streamlit as st

from api_client import create_task, get_task_detail, get_tasks
from console_theme import inject_console_theme


st.set_page_config(
    page_title="AI Browser Agent | Collection Console",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def quote_tags(quote: dict[str, Any]) -> list[Any]:
    tags = quote.get("tags")
    return tags if isinstance(tags, list) else []


def main() -> None:
    inject_console_theme()
    st.title("Collection Console")
    st.caption("Quotes to Scrape · Browser collection · Local rule-based analysis")

    if st.button("刷新任务", icon=":material/refresh:"):
        st.rerun()

    tasks: list[dict[str, Any]] | None = None
    try:
        with st.spinner("正在读取任务记录…"):
            payload = get_tasks()
        if not isinstance(payload, list):
            raise ValueError("后端返回的任务数据格式无效。")
        tasks = [item for item in payload if isinstance(item, dict)]
    except Exception as error:
        st.error(f"任务服务暂不可用：{error}。启动 FastAPI 后可以重试。")

    last_created_id = st.session_state.get("last_created_task_id")
    last_created_task = next(
        (task for task in tasks or [] if task.get("task_id") == last_created_id),
        None,
    )
    if last_created_task:
        st.info(
            f"最近创建：{last_created_id} · {last_created_task.get('status', 'unknown')}。"
            "完成后刷新即可查看结果。"
        )

    with st.form("create_crawl_task"):
        input_col, button_col = st.columns([1, 2], vertical_alignment="bottom")
        with input_col:
            pages = st.number_input("采集页数", min_value=1, max_value=10, value=1, step=1)
        with button_col:
            submitted = st.form_submit_button(
                "开始真实采集",
                type="primary",
                width="stretch",
            )

    if submitted:
        try:
            with st.spinner("正在提交采集任务…"):
                created = create_task(pages=int(pages), mode="local")
            st.session_state["last_created_task_id"] = created.get("task_id")
            st.rerun()
        except Exception as error:
            st.error(f"任务提交失败：{error}")

    if tasks is None:
        st.info("没有显示缓存或演示数据。确认 API 服务后点击刷新任务。")
        return
    if not tasks:
        st.info("还没有采集任务。选择页数并开始一次真实采集。")
        return

    verified_tasks = [task for task in tasks if task.get("provenance_version") == 1]
    unverified_tasks = [task for task in tasks if task.get("provenance_version") != 1]
    successful_tasks = [task for task in verified_tasks if task.get("status") == "success"]
    verified_quotes = sum(int(task.get("quote_count") or 0) for task in successful_tasks)

    metric_columns = st.columns(4, gap="small")
    metric_columns[0].metric("可信采集任务", len(verified_tasks))
    metric_columns[1].metric("成功任务", len(successful_tasks))
    metric_columns[2].metric("真实记录", verified_quotes)
    metric_columns[3].metric("历史待核验", len(unverified_tasks))

    if unverified_tasks:
        st.warning(
            f"{len(unverified_tasks)} 条旧任务缺少当前来源版本信息，保留但不纳入可信指标。"
        )

    provenance_col, status_col = st.columns(2)
    with provenance_col:
        provenance_filter = st.selectbox(
            "来源状态",
            ["全部", "可信采集", "来源待核验"],
            key="provenance_filter",
        )
    with status_col:
        status_filter = st.selectbox(
            "任务状态",
            ["全部", *sorted({str(task.get("status", "unknown")) for task in tasks})],
            key="status_filter",
        )

    visible_tasks = tasks
    if provenance_filter == "可信采集":
        visible_tasks = verified_tasks
    elif provenance_filter == "来源待核验":
        visible_tasks = unverified_tasks
    if status_filter != "全部":
        visible_tasks = [task for task in visible_tasks if task.get("status") == status_filter]

    task_rows = [
        {
            "任务 ID": task.get("task_id", "--"),
            "来源": "已验证" if task.get("provenance_version") == 1 else "待核验",
            "状态": task.get("status", "--"),
            "页数": task.get("pages", "--"),
            "记录数": task.get("quote_count", 0),
            "创建时间": task.get("created_at", "--"),
            "摘要 / 错误": task.get("summary") or task.get("error") or "--",
        }
        for task in visible_tasks
    ]
    st.subheader("任务历史")
    if task_rows:
        st.dataframe(pd.DataFrame(task_rows), width="stretch", hide_index=True)
    else:
        st.info("当前筛选下没有任务。")
        return

    task_by_id = {
        str(task["task_id"]): task
        for task in visible_tasks
        if task.get("task_id")
    }
    if not task_by_id:
        st.info("筛选结果没有可打开的任务 ID。")
        return

    latest_visible_task_id = next(iter(task_by_id))
    selected_task_id = st.selectbox(
        "查看任务结果",
        list(task_by_id),
        format_func=lambda task_id: (
            f"{task_id} · {task_by_id[task_id].get('status', 'unknown')}"
        ),
        key=f"selected_task_id_{latest_visible_task_id}",
    )
    if not isinstance(selected_task_id, str):
        st.info("请选择一个有效任务。")
        return
    selected_task = task_by_id[selected_task_id]

    try:
        with st.spinner("正在载入任务结果…"):
            detail = get_task_detail(selected_task_id, include_quotes=True)
    except Exception as error:
        st.error(f"无法读取任务详情：{error}")
        return

    task_status = detail.get("status")
    if task_status == "failed":
        st.error("采集任务失败。")
        with st.expander("查看错误详情"):
            st.code(detail.get("error") or detail.get("summary") or "未提供错误信息")
        if st.button("按相同页数重新尝试", key=f"retry_{selected_task_id}"):
            try:
                retry = create_task(pages=int(selected_task.get("pages") or 1), mode="local")
                st.session_state["last_created_task_id"] = retry.get("task_id")
                st.rerun()
            except Exception as error:
                st.error(f"重试任务提交失败：{error}")
        return
    if task_status in {"pending", "running"}:
        st.info("采集仍在进行。完成后刷新任务状态即可查看结果。")
        return

    quote_payload = detail.get("quotes", [])
    quotes = [item for item in quote_payload if isinstance(item, dict)] if isinstance(quote_payload, list) else []
    if not quotes:
        st.info("该任务没有可显示的采集记录。")
        return

    provenance_verified = selected_task.get("provenance_version") == 1
    if not provenance_verified:
        st.warning("该历史任务缺少来源版本标记。可检查原始记录，但不生成可信统计图。")

    st.subheader("采集记录")
    search_col, tag_col = st.columns([2, 1])
    with search_col:
        search_text = st.text_input("搜索文本或作者", key=f"search_{selected_task_id}")
    available_tags = sorted({str(tag) for quote in quotes for tag in quote_tags(quote)})
    with tag_col:
        selected_tag = st.selectbox(
            "按标签筛选",
            ["全部标签", *available_tags],
            key=f"tag_{selected_task_id}",
        )

    filtered_quotes = [
        quote
        for quote in quotes
        if (
            not search_text
            or search_text.casefold()
            in f"{quote.get('text', '')} {quote.get('author', '')}".casefold()
        )
        and (selected_tag == "全部标签" or selected_tag in quote_tags(quote))
    ]
    if not filtered_quotes:
        st.info("没有符合当前筛选条件的记录。")
        return

    if provenance_verified:
        author_counts = pd.DataFrame(
            Counter(str(quote.get("author") or "未知作者") for quote in filtered_quotes)
            .most_common(10),
            columns=["作者", "记录数"],
        )
        tag_counts = pd.DataFrame(
            Counter(str(tag) for quote in filtered_quotes for tag in quote_tags(quote))
            .most_common(10),
            columns=["标签", "出现次数"],
        )
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.caption("作者分布 · 当前筛选记录")
            if not author_counts.empty:
                st.bar_chart(author_counts.set_index("作者"), horizontal=True)
        with chart_col2:
            st.caption("标签频次 · 当前筛选记录")
            if not tag_counts.empty:
                st.bar_chart(tag_counts.set_index("标签"))

    record_rows = [
        {
            "作者": quote.get("author") or "--",
            "内容": quote.get("text") or "--",
            "标签": ", ".join(map(str, quote_tags(quote))),
            "采集时间 (UTC)": quote.get("captured_at") or "不可用",
            "来源 ID": quote.get("source_id") or "不可用",
        }
        for quote in filtered_quotes
    ]
    st.dataframe(pd.DataFrame(record_rows), width="stretch", hide_index=True)

    record_indexes = list(range(len(filtered_quotes)))
    selected_record_index = st.selectbox(
        "记录详情",
        record_indexes,
        format_func=lambda index: (
            f"{filtered_quotes[index].get('author') or '未知作者'} · "
            f"{str(filtered_quotes[index].get('text') or '')[:90]}"
        ),
        key=f"record_{selected_task_id}",
    )
    if not isinstance(selected_record_index, int):
        return
    selected_record = filtered_quotes[selected_record_index]
    st.markdown(f"> {selected_record.get('text') or ''}")
    st.caption(
        f"{selected_record.get('author') or '未知作者'} · "
        f"{', '.join(map(str, quote_tags(selected_record))) or '无标签'} · "
        f"{selected_record.get('captured_at') or '采集时间不可用'} UTC"
    )
    source_url = selected_record.get("source_url")
    if source_url:
        with st.container(key="source-page-link"):
            st.link_button("打开来源页面", source_url)
    else:
        st.caption("该历史记录未保存来源链接。")
    report: dict[str, Any] = {}
    report_payload = detail.get("report")
    if isinstance(report_payload, dict):
        report = report_payload
    st.caption(
        f"分析方式：{selected_record.get('analysis_method', '旧记录 / 未标记')} · "
        f"当前结果记录：{len(quotes)} · 本次去重数：{report.get('duplicate_count', '不可用')}"
    )


if __name__ == "__main__":
    main()