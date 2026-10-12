# AI Browser Agent

一个可复现的公开网页采集与分析作品集项目。通过 Playwright 抓取 [Quotes to Scrape](https://quotes.toscrape.com/)，保存有来源、有时间戳的记录，用本地规则生成轻量文本分析，并在 Streamlit 控制台中检索和查看结果。

![采集控制台](assets/09-verified-data-dashboard.png)

![真实采集记录与统计图](assets/10-verified-record-details.png)

## 功能

- 配置采集页数，在 FastAPI 后台创建 Playwright 任务。
- 为每条记录保存稳定记录 ID、来源 ID、实际页面 URL、UTC 采集时间、页码、作者、文本和标签。
- 按规范化后的文本与作者跨页去重，并在任务报告记录重复数量。
- 使用本地关键词规则生成主题、情绪、语气和摘要，不调用外部 LLM。
- 将任务、结果和分析报告按任务 ID 保存为 JSON。
- 在仪表盘筛选任务来源与状态、搜索文本或作者、按标签筛选，并查看来源链接和由当前筛选记录生成的统计图。
- 历史上缺少当前来源版本信息的任务仍可查看，但会标为待核验并排除在可信指标外。

## 技术栈与数据流

```text
Streamlit UI -> FastAPI -> Background Task -> Playwright -> Quotes to Scrape
                                              -> Local rule analyzer
                                              -> JSON task storage -> Task detail API -> UI
```

主要组件：Python 3.11+、FastAPI、Pydantic、Playwright、Streamlit、Pandas 和本地 JSON 文件存储。当前不需要数据库、LLM 密钥、Docker 或登录凭证。

每个任务存于 `data/tasks/<task_id>/`：

- `task.json`：状态、时间、来源版本和聚合计数。
- `quotes_all.json`：去重后的采集记录及逐条来源元数据。
- `report.json`：统计、重复数、分析方法和来源版本。
- `meta.json`：任务创建参数。

只有含 `provenance_version: 1` 的任务纳入可信统计。旧任务文件不会被自动迁移或覆盖。

## 环境配置

Windows PowerShell：

```powershell
py -3.11 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m playwright install chromium
```

Playwright 浏览器需单独安装。首次采集需要本机可访问 `quotes.toscrape.com`；页面无法访问或结构不匹配时，任务会标为失败并保留错误信息，不会生成伪造结果。

## 启动

在项目根目录打开两个 PowerShell 窗口，先分别启动 API 和 UI：

```powershell
venv\Scripts\Activate.ps1
uvicorn app.api.server:app --reload
```

```powershell
venv\Scripts\Activate.ps1
streamlit run ui/dashboard.py
```

打开 Streamlit 显示的本机地址（默认 `http://localhost:8501`）。API 文档位于 `http://127.0.0.1:8000/docs`，健康检查位于 `/health`。

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/health` | 服务健康状态 |
| `POST` | `/tasks/run` | 创建采集任务，JSON 参数为 `{"pages": 1, "mode": "local"}` |
| `GET` | `/tasks` | 按创建时间倒序列出任务 |
| `GET` | `/tasks/metrics/summary` | 可信来源版本的任务统计，另列未验证任务数 |
| `GET` | `/tasks/{task_id}` | 任务、报告及最多 10 条结果预览 |
| `GET` | `/tasks/{task_id}?include_quotes=true` | 任务及完整采集结果 |

任务创建返回后端队列状态；通过任务详情轮询 `pending`、`running`、`success` 或 `failed`。页面提供手动刷新。

## 测试与本地检查

```powershell
python -m unittest discover -s tests -v
python -m py_compile app/api/server.py app/crawler/quotes_spider.py app/task/task_manager.py ui/dashboard.py
```

单元测试使用替身数据验证转换、来源校验、去重和任务状态，不访问外网。手动端到端验证可在启动两项服务后，从仪表盘创建一页任务，并检查任务详情里的 `source_url`、`captured_at`、`record_id` 和 `analysis_method`。

## 项目结构

```text
app/
  analyzer/       本地规则分析与任务统计
  api/server.py   FastAPI 路由和后台任务管线
  crawler/        Playwright 采集器
  task/           JSON 任务生命周期与持久化
ui/
  dashboard.py    Streamlit 采集控制台
  api_client.py   本机 FastAPI 客户端
data/tasks/       按任务隔离的本地 JSON 结果
assets/           项目截图
tests/            离线单元测试
```

## 作品集说明

数据源是用于演示浏览器采集流程的公开测试网站，并非客户业务系统或真实商业成果。仪表盘中的可信指标只来自当前 provenance 版本的任务；旧历史记录与真实指标分开显示。发布前请使用新环境执行环境配置、单元测试和一次手动公开站点采集，并更新当前界面截图。