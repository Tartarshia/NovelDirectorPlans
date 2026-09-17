# 小说导演规划包

独立于 NovelVoice 音频引擎维护的导演文档与证据记录。目前收录《一世之尊》，以本地提供版本为依据，由当前 Codex 顺序分批精读编写。仓库为私有。

**当前为进行中草案：精读至第四卷第147章，647 / 1410 个目录条目，约212.2万字。第一至三卷已有卷末汇总；全书复核与逐句归属尚未完成。** 最新状态以 [progress.json](books/yishizhizun/progress.json) 为准。文档包含已读范围剧透；历史记录不代表最终事实。

续读以 [progress.json](books/yishizhizun/progress.json) 为准；维护步骤见 [WORKFLOW.md](WORKFLOW.md)。

## 阅读入口

- [角色阶段索引](books/yishizhizun/characters/README.md)：按角色归纳前三卷成长和当前阶段，可直接查阅表演边界。
- [第147章复核](books/yishizhizun/reviews/review-v04-0147.md)：修旗两次、重返九乡与清源身份，80段、126个句内单元。
- [第146章复核](books/yishizhizun/reviews/review-v04-0146.md)：共享珍食、辅助计划与牵扯警告，76段、118个句内单元。
- [第145章复核](books/yishizhizun/reviews/review-v04-0145.md)：归琴与玉书突破、挥旗代价及答谢，99段、113个句内单元。
- [第144章复核](books/yishizhizun/reviews/review-v04-0144.md)：两敌逃遁、九指实名与宝物使用边界，78段、87个句内单元。
- [第143章复核](books/yishizhizun/reviews/review-v04-0143.md)：大日变清蛊与两邪魔阻路，63段、77个句内单元。
- [第142章复核](books/yishizhizun/reviews/review-v04-0142.md)：四宗师牵制与孟奇出刀，96段、116个句内单元。
- [第141章复核](books/yishizhizun/reviews/review-v04-0141.md)：阮承德舍命唤琴与归属未决，106段、115个句内单元。
- [第140章复核](books/yishizhizun/reviews/review-v04-0140.md)：何高胜负、乾元线索与探子撤离，73段、83个句内单元。
- [第139章复核](books/yishizhizun/reviews/review-v04-0139.md)：联攻破阵与剑蛊旧怨，66段、87个句内单元。
- [第138章复核](books/yishizhizun/reviews/review-v04-0138.md)：首梯四重确认与三家揭局，92段、131个句内单元。
- [第137章复核](books/yishizhizun/reviews/review-v04-0137.md)：何九高空切磋与突破临界，97段、106个句内单元，尚未确认晋阶完成。
- [第136章复核](books/yishizhizun/reviews/review-v04-0136.md)：三次拜访、83段138个句内单元，何九到观未战。
- [第135章复核](books/yishizhizun/reviews/review-v04-0135.md)：宁台切磋与阮门受冷，93段、137个句内单元。
- [第134章复核](books/yishizhizun/reviews/review-v04-0134.md)：潜修后秋海与宁台初登场，74段、112个句内单元。
- [第133章复核](books/yishizhizun/reviews/review-v04-0133.md)：回岸与严冲切磋，81段、111个句内单元。
- [第130–132章复核](books/yishizhizun/reviews/review-v04-0130-0132.md)：本轮新增256段、299个句内单元，观刀解债及出岛收束。
- [第127–129章复核](books/yishizhizun/reviews/review-v04-0127-0129.md)：本轮按用户要求止于129章，新增203段、280个句内单元，1处传音歧义。
- [最近六章补充复核](books/yishizhizun/reviews/review-v04-0121-0126.md)：435段、663个句内单元的归属，保留七处疑问；早期620条目的逐句归属仍待补。
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
python scripts/validate_attribution.py
python scripts/package.py archive
```

压缩包生成在 `dist/`，也可从 GitHub Releases 下载阶段快照。`manifest.json` 列出所有数据文件 SHA-256。校验覆盖文件完整性、章节连续性、场景段落覆盖及证据范围；不声称完成语义复核。无正文环境不能重新验证原文内容；对照原文需自行持有同一版本。

后续精读按 [维护流程](WORKFLOW.md) 更新并提交 Git，保留每批差异与历史。
