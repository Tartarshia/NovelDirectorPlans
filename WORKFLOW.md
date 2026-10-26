# 维护流程

本仓库是导演规划的持久版本库，NovelVoice 的本地工作目录保留私有正文和精读中间状态。每批阅读完成并通过本地原文校验后，将结果导出到本仓库，再审查、提交与推送。Git 历史代替上传临时检查点；不要直接把整个 output 目录加入 Git。

1. 在本地工作副本中按 `progress.json` 的 `next_chapter_id` 顺读正文，全文未读不能计入完成；只做规划，不调用音频或外部模型。
2. 更新角色、卷内阶段、章节草案及证据，并同步受影响的 characters 阶段卡、句内归属和 reviews 语义复核记录。归属必须人工判定说话人、内心、叙述及公开伪装，脚本只分区间和查覆盖。无法确定的留 open_question，不自动猜人。区分原文明述、人物猜测、导演建议；人物当下所知不得混入后期真相。稳定音色与成长表演分离。
3. 在 NovelVoice 中运行 `python scripts/validate_long_novel_director.py output/director/yishizhizun`，核对正文哈希和引用。
4. 在本仓库运行以下命令（按实际相对目录调整）：

```console
python scripts/package.py export --source ../NovelVoice/output/director/yishizhizun
python scripts/package.py validate
git diff --stat
git diff --check
git add books manifest.json
git commit -m "Update sequential reading and director drafts"
git push
```

导出只允许明确列出的文档与结构化数据，正文仅转为章节元数据和段落数量；发现本地绝对路径、常见凭据或100字以上完整原文段落时中止。自动检查不能替代人工隐私与内容审查。不会自动提交或上传。

卷末或重要里程碑用 `archive` 生成包，作为 GitHub Release 附件。阶段版本必须标注草案，不得将目录索引数量误当精读数量。导出器不会删除未知旧文件；修改目录布局时必须单独审查迁移。

恢复时先克隆本仓库，再自行准备与 `source_sha256` 匹配的原书并使用 NovelVoice 的本地索引工具生成私有阅读副本。不要从云端角色百科补写成已读原文；本包未提供小说全文，无法单独执行全文复核。

补充归属校验：`python scripts/validate_attribution.py --source ../NovelVoice/output/director/yishizhizun`。此命令只在有本地正文时校验字符偏移及段落哈希；不带 source 可查发布包覆盖。新复核章节须同步 reviews/attribution-summary.json，不得用结构通过替代逐段语义审查。

## 每章完成后的五小时额度检查与刷新后自动续读

用户要求：每完成一章（全文精读、导演分场、角色状态、句内归属、语义复核、校验和提交推送均完成），必须检查当前 Codex 五小时 usage limit，再决定是否开始下一章。不得累积多章后再查。恢复阅读前也检查一次。

在本仓库运行 `python scripts/check_usage.py`；从 NovelVoice 运行时可用 `python ../NovelDirectorPlans/scripts/check_usage.py --record output/director/yishizhizun/usage-checks/章节ID.json` 保存本地检查回执。脚本通过已登录 Codex 的 `account/rateLimits/read` 只读获取额度，不开启模型回合，不读取或打印凭据。按 `windowDurationMins == 300` 选取五小时窗口，剩余比例为 `100 - usedPercent`，不以累计 token、费用、周额度或上下文剩余量替代。

- 返回 `continue`（退出码0）：剩余至少15%，可继续；恰好15%不触发本规则。
- 返回 `pause`（退出码2）：剩余不足15%。不开始下一章，保留当前完整成果，等待五小时额度刷新后自动续读，不因这一条件将 goal 设为 `paused`。优先使用接口返回的五小时窗口刷新时间安排等待；到时必须重新查询并确认剩余至少15%才开始下一章。若无法取得可靠刷新时间，每30分钟重新查询一次；刷新时间已过而额度仍不足15%时也每30分钟复查。用户另行要求停止或暂停时服从用户指令。
- 返回 `unknown`（退出码3）：本次无法核实额度。保留已完成成果，不假报比例或默认充足，不开始下一章，每30分钟重新查询；不能以查询失败推断额度已经刷新。

额度回执仅保存在本地 `usage-checks/`，不导出或提交账户额度、重置时间等个人使用记录。额度等待不改动全书目标、阅读进度或下一章，不将项目标记为完成；刷新后先复查再自动续读。也不自动消耗重置权益、购买额度或切换账号。
