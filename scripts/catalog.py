"""Validate the source graph and generate a deterministic Markdown catalog."""
import argparse
from collections import defaultdict
from datetime import date, datetime
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def load(root):
    result = {}
    for kind in ("theories", "sources", "events", "runs"):
        entries = {}
        for path in sorted((root / "data" / kind).glob("*.json")):
            item = json.loads(path.read_text(encoding="utf-8"))
            assert item["id"] == path.stem and ID.fullmatch(item["id"]), f"Invalid ID: {path}"
            entries[item["id"]] = item
        result[kind] = entries
    return result


def day(value):
    assert date.fromisoformat(value).isoformat() == value, f"Invalid date: {value}"


def instant(value):
    parsed = datetime.fromisoformat(value)
    assert parsed.tzinfo is not None, f"Missing timezone: {value}"
    return parsed


def validate(data):
    theories, sources, events, runs = (data[k] for k in ("theories", "sources", "events", "runs"))
    assert theories, "Catalog requires theories"
    seen = set()
    for source in sources.values():
        for key in ("id", "url", "title", "author", "kind", "published_at", "discovered_at", "checked_at", "verification", "summary", "limitation", "supersedes"):
            assert key in source, f"Missing source field: {key}"
        url = urlsplit(source["url"])
        assert url.scheme in {"https", "http"} and url.hostname and not url.username, "Invalid source URL"
        assert source["kind"] in {"primary", "secondary", "transcript"}
        assert source["verification"] in {"read", "metadata_only", "unavailable"}
        day(source["discovered_at"])
        instant(source["checked_at"])
        if source["published_at"] is not None:
            instant(source["published_at"]) if "T" in source["published_at"] else day(source["published_at"])
        fingerprint = (source["url"], source["summary"], source["verification"])
        assert fingerprint not in seen, "Duplicate source snapshot"
        seen.add(fingerprint)
        if source["supersedes"]:
            old = sources[source["supersedes"]]
            assert old["url"] == source["url"] and old["id"] != source["id"]
            assert instant(old["checked_at"]) <= instant(source["checked_at"])
            visited = {source["id"]}
            while old:
                assert old["id"] not in visited, "Cyclic source history"
                visited.add(old["id"])
                old = sources.get(old["supersedes"]) if old["supersedes"] else None
    for theory in theories.values():
        assert theory["status"] in {"tracked", "candidate", "archived"}
        assert theory["name"] and theory["summary"] and theory["source_ids"]
        assert isinstance(theory["aliases"], list) and isinstance(theory["open_questions"], list)
        day(theory["updated_at"])
        assert len(theory["source_ids"]) == len(set(theory["source_ids"]))
        assert set(theory["source_ids"]) <= sources.keys(), "Dangling theory source"
        for claim in theory["claims"]:
            assert claim["text"] and claim["source_ids"], "Unsourced claim"
            assert set(claim["source_ids"]) <= set(theory["source_ids"])
            assert claim["attribution"] in {"author_statement", "secondary_summary", "editorial_analysis"}
            assert all(sources[s]["verification"] == "read" for s in claim["source_ids"]), "Unread source cannot support a claim"
            if claim["attribution"] == "author_statement":
                assert all(sources[s]["kind"] == "primary" for s in claim["source_ids"]), "Secondary source cannot be an author statement"
    for event in events.values():
        day(event["date"])
        assert event["summary"] and event["type"] in {"seed", "source_added", "claim_updated", "theory_added", "candidate_found", "correction"}
        assert event["theory_ids"] and set(event["theory_ids"]) <= theories.keys()
        assert event["source_ids"] and set(event["source_ids"]) <= sources.keys()
        for theory_id in event["theory_ids"]:
            assert set(event["source_ids"]) & set(theories[theory_id]["source_ids"]), "Event source not attached to theory"
        run = runs[event["run_id"]]
        assert event["id"] in run["event_ids"] and event["date"] == run["date"], "Broken run/event reference"
    for run in runs.values():
        day(run["date"])
        start, end = instant(run["started_at"]), instant(run["completed_at"])
        assert start <= end
        assert instant(run["coverage_from"]) <= instant(run["coverage_to"]) <= end
        assert run["status"] in {"seed", "complete", "partial", "failed"}
        assert run["checks"] and all(c["query"] and c["outcome"] in {"ok", "failed"} and c["note"] for c in run["checks"])
        assert len(run["event_ids"]) == len(set(run["event_ids"]))
        assert all(events[e]["run_id"] == run["id"] for e in run["event_ids"])
        if run["status"] == "complete":
            assert not run["failures"] and all(c["outcome"] == "ok" for c in run["checks"]), "Complete run contains failures"
        if run["status"] in {"partial", "failed"}:
            assert run["failures"], "Failed coverage requires explanation"


def line(value):
    return str(value).replace("\n", " ").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def render(data):
    theories, sources, events, runs = (data[k] for k in ("theories", "sources", "events", "runs"))
    out = {}
    source_link = lambda s: f"[{line(sources[s]['title'])}]({sources[s]['url']})"
    theory_index = ["# 理论目录", "", "本页由结构化数据生成。", "", "| 名称 | 状态 | 更新日 |", "| --- | --- | --- |"]
    for theory_id, theory in sorted(theories.items()):
        theory_index.append(f"| [{line(theory['name'])}](../knowledge/{theory_id}.md) | {theory['status']} | {theory['updated_at']} |")
        page = [f"# {theory['name']}", "", f"状态：{theory['status']} · 更新：{theory['updated_at']}", "", theory["summary"], "", "## 观点与版本", ""]
        if not theory["claims"]:
            page.append("尚无足够可核读证据支持实质观点，当前仅保存来源线索。")
        for claim in theory["claims"]:
            page.extend([f"- {claim['text']}（{claim['attribution']}）", "  来源：" + "；".join(source_link(s) for s in claim["source_ids"])])
        page.extend(["", "## 来源", ""])
        for s in theory["source_ids"]:
            source = sources[s]
            page.extend([f"- {source_link(s)} · {source['kind']} / {source['verification']}", f"  限制：{source['limitation']}"])
        page.extend(["", "## 待补资料", ""] + ["- " + q for q in theory["open_questions"]])
        page.extend(["", "## 更新历史", ""])
        for event in sorted(events.values(), key=lambda e: (e["date"], e["id"]), reverse=True):
            if theory_id in event["theory_ids"]:
                page.append(f"- [{event['date']}](../daily/{event['date'][:4]}/{event['date']}.md)：{event['summary']}")
        out[f"knowledge/{theory_id}.md"] = "\n".join(page) + "\n"
    out["indexes/theories.md"] = "\n".join(theory_index) + "\n"
    source_index = ["# 来源索引", "", "状态描述能核读到什么，不代表观点正确。发布时间未知时不猜测。", ""]
    for source_id, s in sorted(sources.items()):
        source_index.extend([f"## {source_id}", "", source_link(source_id), "", f"作者：{s['author'] or '待核实'} · 类别：{s['kind']} · 核读：{s['verification']}", f"发布时间：{s['published_at'] or '未知'} · 首次发现：{s['discovered_at']}", "", s["summary"], "", "限制：" + s["limitation"], ""])
    out["indexes/sources.md"] = "\n".join(source_index) + "\n"
    candidates = [f"- [{t['name']}](../knowledge/{i}.md)" for i, t in sorted(theories.items()) if t["status"] == "candidate"]
    out["indexes/candidates.md"] = "# 新理论候选\n\n" + ("\n".join(candidates) if candidates else "暂无已登记候选；发现查询仍会每日执行。") + "\n"
    grouped = defaultdict(list)
    for run in runs.values():
        grouped[run["date"]].append(run)
    days = ["# 每日更新", "", "按发现日期归档；初始化记录不代表完整采集。", ""]
    for d in sorted(grouped, reverse=True):
        days.append(f"- [{d}]({d[:4]}/{d}.md)")
        page = [f"# {d} 理论观察", "", "日期采用北京时间；发现时间与原始发布时间分开记录。", ""]
        for run in sorted(grouped[d], key=lambda r: r["started_at"]):
            page.extend([f"## {run['id']} · {run['status']}", "", f"执行：{run['started_at']} → {run['completed_at']}", f"检索窗口：{run['coverage_from']} → {run['coverage_to']}", "", "### 内容变化", ""])
            if not run["event_ids"]:
                page.append("本次未登记内容增量；结论范围以以下查询及访问结果为准。")
            for event_id in run["event_ids"]:
                e = events[event_id]
                page.extend([f"- **{e['type']}**：{e['summary']}", "  来源：" + "；".join(source_link(s) for s in e["source_ids"])])
            page.extend(["", "### 检索记录", ""])
            page.extend(f"- `{c['query']}` · {c['outcome']}：{c['note']}" for c in run["checks"])
            page.extend(["", "### 失败与覆盖限制", ""] + (["- " + f for f in run["failures"]] or ["无已登记失败。注意：公开搜索不能保证覆盖全网。"]) + [""])
        out[f"daily/{d[:4]}/{d}.md"] = "\n".join(page) + "\n"
    out["daily/README.md"] = "\n".join(days) + "\n"
    return out


def check(root, out):
    actual = {str(p.relative_to(root)).replace("\\", "/") for folder in ("knowledge", "daily", "indexes") for p in (root / folder).rglob("*.md")}
    assert actual == out.keys(), "Generated file list differs; run build"
    for path, content in out.items():
        assert (root / path).read_text(encoding="utf-8") == content, f"Stale generated page: {path}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "build", "check"))
    args = parser.parse_args()
    data = load(ROOT)
    validate(data)
    if args.command != "validate":
        out = render(data)
        if args.command == "check":
            check(ROOT, out)
        else:
            for path, content in out.items():
                target = ROOT / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8", newline="\n")
    print(f"{args.command}: OK ({len(data['theories'])} theories, {len(data['sources'])} sources, {len(data['runs'])} runs)")


if __name__ == "__main__":
    main()
