# 小说导演规划包

独立于 NovelVoice 音频引擎维护的导演文档与证据记录。目前收录《一世之尊》，以本地提供版本为依据，由当前 Codex 顺序分批精读编写。仓库为私有。

**当前为进行中草案：精读至第三卷第325章，473 / 1410 个目录条目，约154.3万字。第一、二卷已有卷末汇总；全书复核与逐句归属尚未完成。** 最新状态以 [progress.json](books/yishizhizun/progress.json) 为准。文档包含已读范围剧透；历史记录不代表最终事实。

## 阅读入口

- [角色 wiki](books/yishizhizun/wiki.md)：人物、关系、身份揭示、阶段变化及原文证据。当前仍含连续增补记录，后续全书汇总会进一步整理。
- [分卷指导](books/yishizhizun/volumes)：卷内成长阶段、情绪与表演走向。
- [章节导演草案](books/yishizhizun/chapter_direction)：视角、场景范围、节奏与归属提醒。
- [身份事件](books/yishizhizun/identity-events.json) / [原文疑点](books/yishizhizun/source-issues.json)。
- [阅读批次](books/yishizhizun/batches) / [阅读记录](books/yishizhizun/reading_receipts)：可追溯的顺读进度，不是独立证明理解质量的凭证。
- [证据索引](books/yishizhizun/evidence-index.json)：章节与段落编号、字符数、哈希，不含正文。

这里只做导演规划，未生成音频，也不是已审核的逐句 TTS 输入。原书及相关权利归原权利人；本包不包含 EPUB、全书正文、音频、模型、密钥、个人路径或旧临时备份。文档可能有为分析保留的简短引文。

## 校验与下载

需要 Python 3.10 或更高版本，无第三方依赖。

```console
python scripts/package.py validate
python scripts/package.py archive
```

压缩包生成在 `dist/`，也可从 GitHub Releases 下载阶段快照。`manifest.json` 列出所有数据文件 SHA-256。校验覆盖文件完整性、章节连续性、场景段落覆盖及证据范围；不声称完成语义复核。无正文环境不能重新验证原文内容；对照原文需自行持有同一版本。

后续精读按 [维护流程](WORKFLOW.md) 更新并提交 Git，保留每批差异与历史。
