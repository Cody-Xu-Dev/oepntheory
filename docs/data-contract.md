# 数据契约 v1

所有 JSON 文件 UTF-8；ID 仅小写英文、数字和连字符，文件名必须等于 ID。日期用 `YYYY-MM-DD`，时间用带时区的 ISO 8601；未知发布时间为 `null`，不能填搜索索引的爬取时间。

## Theory (`data/theories/{id}.json`)

`id, name, aliases[], status, summary, source_ids[], claims[], open_questions[], updated_at`。

状态：`tracked`（持续跟踪）、`candidate`（新理论线索）、`archived`（停止跟踪，保留历史）。
观点：`text, source_ids[], attribution`；attribution 为 `author_statement`（核读的原作者表达）、`secondary_summary`（二次资料概括）、`editorial_analysis`（编者分析）。摘要不能比引用所支持的范围更大。

## Source (`data/sources/{id}.json`)

`id, url, title, author, kind, published_at, discovered_at, checked_at, verification, summary, limitation, supersedes`。

kind：`primary`、`secondary`、`transcript`；verification：`read`（可核读正文）、`metadata_only`（仅元数据）、`unavailable`（访问失败）。
只有 `read` 可以支持实质观点，`primary + read` 才能支持 author_statement。转载文字稿标为 transcript，其表述仍需对照原视频。版本变化新增记录，supersedes 必须指向同 URL 的旧记录。

## Event (`data/events/{id}.json`)

`id, date, type, theory_ids[], source_ids[], summary, run_id`。
type：`seed`、`source_added`、`claim_updated`、`theory_added`、`candidate_found`、`correction`。所有事件必须关联理论、来源和一次运行。

## Run (`data/runs/{id}.json`)

`id, date, started_at, completed_at, status, coverage_from, coverage_to, checks[], failures[], event_ids[]`。
status：`seed`、`complete`、`partial`、`failed`。
check：`query, outcome, note`；outcome 为 `ok`、`failed`。每次运行至少一个 check；complete 要求全部查询成功、failures 为空。seed 不能作为完整检索水位。没有发现允许 event_ids 为空，但要说明查了哪里。Run 与 Event 双向引用。

## 去重

URL 去掉跟踪参数与无意义锚点，保留真实内容标识。相同来源 ID 不重复添加；同 URL 同摘要同状态拒绝重复。实质内容变更使用新 Source ID、supersedes 和 correction/claim_updated 事件；不因 checked_at 改变就制造新版本。
