# Claude Code Failure Research

可复现的 Coding Agent 可靠性实验。社区研究项目，与 Anthropic 无隶属关系。

**截至 2026-10-04：正在开展无需账号、无需付费模型的客户端研究。** 官方
Claude Code 2.1.288 提供 `claude plugin test`，已用真实客户端测试引擎执行
指令加载契约和 Git pane 的受控诊断。28 个已有报告完成筛查；真实 Claude
模型 coding trial 为 0，确认生产 failure 为 0，Anthropic issue 为 0。
实测数量与证据边界见 [免费研究记录](docs/no-cost-research.md)。

两项超时的[专项调查](docs/timeout-investigation.md)已完成：隔离原用例后，
5 秒与 15 秒时限下分别 20/20 通过；完整套件默认派发仍有超时。采样观察到
原生 CLI 的子进程并发峰值为 27；按文件逐个派发，在原来的 5 秒时限下
完成 **210/210 通过**。这支持测试派发与套件上下文敏感性诊断，不构成生产 bug
或修复证明；旧失败与无效解析器批次均保留。

新增的[三个候选筛查](docs/free-candidate-screen.md)使用两批全新真实文件/Git
fixture，18 个自创用例共 **36/36 次执行通过**，无功能失败信号。采集结果送入
组件测试，生产文件／进程传输仍未验证。官方已新增 2.1.289 变更记录；本轮实测
引擎仍是 2.1.288，不宣称验证了最新引擎。

当前可用交付物：

- [实验方法](docs/methodology.md)、[分类路由](docs/issue-routing.md)、[技术报告](docs/technical-report.md)。
- [28 个候选的筛查及评分](reports/candidate-screening.md)，全部保留已有 issue 链接。
- [V01 预注册场景](scenarios/verification-retention.json)：修复发票舍入 bug、保留 API、
  不改测试、修改前后验证；prompt 与 CLAUDE.md 为主要对照，另有三种消融。
- 七文件自创 MIT fixture，初始 10 个测试中 4 个失败；已用已知正确修复验证 oracle。
- 干净 repo runner、声明与证据一致性分析、路径/API/测试完整性检查、脱敏、JSON Schema 和离线 CI。
- 免费客户端运行器、自创指令契约测试、Windows 虚拟 Git fixture 的路径对照；公开结果不包含 Anthropic 实现源码。
- [禁止付费调用的执行策略](research-policy.json)：旧访问探针与模型 runner 均在调用前阻断。
- [学习与面试指南](CLAUDE_CODE_FAILURE_RESEARCH_STUDY_GUIDE.md)，含 30 题参考答案。

本地离线检查：

```powershell
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python -m runners.validate_repository
python -m runners.run_study --repetitions 1
```

最后一条仅生成历史协议计划，不调用模型。免费研究使用单独下载、固定版本的
官方源码与已有 CLI，命令见 [英文 README](README.md)。外层命令顺序执行也
不能保证引擎内部 worker 串行；完整套件可用 `upstream-serial-files` 逐文件复测。
当前不要求登录，也不运行模型；`--execute`
无法绕过研究策略。整个仓库没有自动提交 issue 的代码。

[离线检查](results/offline-validation.json)已通过。
[独立审查](reports/independent-review.md)发现共用文档重复投递约束，已在任何
真实 run 前修正为 V01 1.0.1；原设计与修订理由均已保存。审查允许公开框架，
不批准提交尚无实测证据的 issue。

原始日志留在被 Git 忽略的 `.private/`；公开结果只导出审阅过的元数据，
不发布完整 transcript。访问中断单列为 blocked，不进入有效行为 trial 分母。
不明确的“tests passed”范围交给人工复核，不能擅自解释为全量测试通过。

官方 mod 测试在真实引擎中运行，但下层文件、Git、时钟等交互由脚本应答。
它能检验客户端契约与公开源码函数，不能替代 Claude 模型的指令保留实验。
长任务、compaction、subagents、MCP、IDE 和 Remote Control 尚未完成实测。
当前没有可报告 case，故没有 issue、Anthropic 回复或 v0.1.0 release。
将来达到 E3/E4、排除重复且独立审查通过后，才进入正式报告。
当前剩余免费工作和原目标的条件门槛见 [待办记录](reports/remaining-work.json)。

求职材料目前可写：搭建受控可靠性研究框架，并用官方客户端测试引擎开展免费
组件实验、程序化 verifier 和可复现 fixture，识别并控制 Windows 测试路径混杂。
不能写“发现并报告了 Claude bug”或“Anthropic 已修复”。
