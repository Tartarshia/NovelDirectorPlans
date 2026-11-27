# 《一世之尊》维护与校验流程

[返回本书目录](README.md) · [项目维护](../../WORKFLOW.md)。以下命令从仓库根目录运行，另有说明的除外。

## 下载包校验

需要 Python 3.10 或更新版本。从解压后的根目录运行下列命令。

```console
python scripts/package.py validate
python scripts/validate_attribution.py
```

在仓库根目录运行 `python scripts/package.py archive` 可将当前版本打包到 `dist/`。根目录的 `manifest.json` 保存每个数据文件的 SHA-256。对照原文需要自行准备同版本底本。

## 精读与导出

本仓库是导演规划的持久版本库，NovelVoice 的本地工作目录保留私有正文和精读中间状态。每批阅读完成并通过本地原文校验后，将结果导出到本仓库，再审查、提交与推送。Git 历史代替上传临时检查点；不要直接把整个 output 目录加入 Git。

1. 在本地工作副本中按 `progress.json` 的 `next_chapter_id` 顺读正文，全文未读不能计入完成；只做规划，不调用音频或外部模型。
2. 更新角色、卷内阶段、章节草案及证据，并同步受影响的 characters 阶段卡、句内归属和 reviews 语义复核记录。归属必须人工判定说话人、内心、叙述及公开伪装，脚本只分区间和查覆盖。无法确定的留 open_question，不自动猜人。区分原文明述、人物猜测、导演建议；人物当下所知不得混入后期真相。稳定音色与成长表演分离。
3. 在 NovelVoice 中运行 `python scripts/validate_long_novel_director.py output/director/yishizhizun`，核对正文哈希和引用。
4. 从本仓库根目录运行以下命令，按实际位置调整底本目录。

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

卷末草案和回补里程碑用 Git 提交和阶段标签追溯。正式对外发布时，可用 `archive` 生成 GitHub Release 的 ZIP 附件。导出器不会删除未知旧文件；修改目录布局时必须单独审查迁移。

恢复时先克隆本仓库，再自行准备与 `source_sha256` 匹配的原书并使用 NovelVoice 的本地索引工具生成私有阅读副本。不要从云端角色百科补写成已读原文；本包未提供小说全文，无法单独执行全文复核。

补充归属校验：`python scripts/validate_attribution.py --source ../NovelVoice/output/director/yishizhizun`。此命令只在有本地正文时校验字符偏移及段落哈希；不带 source 可查发布包覆盖。新复核章节须同步 reviews/attribution-summary.json，不得用结构通过替代逐段语义审查。

## 每章完成后的五小时额度检查与工作时间停止规则

每完成一章（全文精读、导演分场、角色状态、句内归属、语义复核、校验和提交推送均完成），检查当前 Codex 五小时 usage limit；恢复阅读前也检查一次。不得累积多章后再查。

完成一章或一批（包括三章）只表示该批已落档，不是停止条件。目标处于 active 且未触发下述停止规则时，继续下一章；不得仅因批次完成就结束任务或将目标暂停。

使用 `python scripts/check_usage.py`，或在 NovelVoice 中用 `python ../NovelDirectorPlans/scripts/check_usage.py --record output/director/yishizhizun/usage-checks/章节ID.json`。脚本通过 `account/rateLimits/read` 只读获取五小时窗口，不启动模型回合，不读取或打印凭据。

- 使用 America/New_York 时区，以当地09:00（含）至17:00（不含）为15%保护时段；其余时段不因低于15%而停止。用户未限定工作日，不额外推定仅周一至周五。
- 保护时段内剩余至少15%：可继续，恰好15%不触发停止。
- 保护时段内剩余不足15%：不开始下一章，保存已完成成果，将 goal 设为 `paused` 并停止。不得启动额度等待进程、定时复查、轮询进程或自动等待刷新；由用户明确要求后再恢复。
- 保护时段外仍按章检查记录额度，但忽略15%门槛；实际限流或服务错误不能当成额度已恢复。
- 无法核实额度：不假报充足，不开始下一章，保存成果并停止，等待用户处理或明确要求重试；不得自动每半小时查询。

用户已取消此前的刷新后自动续读、未知时每30分钟查询和重复等待提示规则。只延长提示间隔不能避免自动续跑的模型额度消耗，不能以静默轮询替代停止。

额度回执仅留本地，不导出账户使用记录。停止不改动全书目标与阅读进度，不标记项目完成，不购买额度或切换账号。
