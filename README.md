# opentheory

中文互联网理论观察档案：整理**薄肌理论、大水理论、黄毛理论、孙学**的存量资料，每天跟踪观点更新，并发现新的理论或衍生话语。

这里的“理论”沿用网络讨论的名称。条目记录谁在什么来源说了什么，保留不同版本与争议；收录不代表认可。仓库名为 `opentheory`。

## 阅读入口

- [理论目录](indexes/theories.md)：四个初始主题与后续新主题。
- [每日更新](daily/README.md)：新增来源、观点变化、新理论线索及检索范围。
- [来源索引](indexes/sources.md)：原网址、来源类型、核读状态。
- [新理论候选](indexes/candidates.md)：尚未达到稳定主题收录条件的线索。
- [架构设计](docs/architecture.md) / [每日维护流程](docs/daily-update.md)。

首批资料为 2026-10-13 初始化索引，不是完整文献库。未取得视频正文的条目仅保存线索，不编造视频内容或起源。

## 存量与增量

```text
data/
  theories/       理论身份、当前摘要、观点与来源引用
  sources/        每份来源的元数据、自写摘要、核读状态
  events/        只追加的发现、观点变化、修订记录
  runs/          每次检索的范围、结果和失败（与内容增量分开）
knowledge/       自动生成的理论阅读页
daily/           自动生成的每日汇总，可包含同日多次运行
indexes/         自动生成的理论、来源、候选目录
config/          主题查询与发现策略
scripts/         校验、生成与一致性检查
tests/           引用完整性、去重与生成检查
docs/            架构、数据契约、采集及发布操作说明
```

## 每日更新

已约定每天北京时间 **09:00**，由本 Codex 聊天的定时任务检索公开资料、核读来源、合并重复转载、生成当日记录并提交 GitHub。同步搜索新理论，不局限于最初四个主题。

任务需要运行该聊天的电脑开机且 Codex 应用运行；离线后下一次运行按上次成功覆盖时间补查。GitHub Actions 只负责数据和生成产物校验，不冒充采集器。无新增时仍保存检索范围；平台访问失败记为部分完成，不推断“没有更新”。

## 本地维护

Python 3.11+，无第三方依赖：

```bash
python scripts/catalog.py validate
python scripts/catalog.py build
python scripts/catalog.py check
python -m unittest discover -s tests -v
```

修改 `data/` 后执行 `build`；提交结构化数据与生成页，不手改生成文件。首批来源多为二次研究与文字稿，后续优先补原作者的可核读材料。

## 内容使用

只保存来源元数据、自写摘要、必要短引文和链接。第三方原文、视频与图片权利归原作者，不批量转存第三方全文。代码按 [MIT](LICENSE) 使用；仓库原创整理文字按 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 使用，第三方材料不包含在授权范围内。
