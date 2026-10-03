# Claude Code Failure Research

可复现的 Coding Agent 可靠性实验。社区研究项目，与 Anthropic 无隶属关系。

**截至 2026-10-03：公开框架阶段。28 个已有报告完成筛查；真实 Claude coding
trial 为 0，确认 failure 为 0，Anthropic issue 为 0。** 本机 CLI 已从 2.1.169
更新至 2.1.288。隔离自定义网关后，官方访问探针要求登录，未调用模型。
按照研究者的选择，真实实验待官方登录后再执行。不能把这次访问诊断计入
行为失败，也不能据此判断 Claude 的可靠性。

当前可用交付物：

- [实验方法](docs/methodology.md)、[分类路由](docs/issue-routing.md)、[技术报告](docs/technical-report.md)。
- [28 个候选的筛查及评分](reports/candidate-screening.md)，全部保留已有 issue 链接。
- [V01 预注册场景](scenarios/verification-retention.json)：修复发票舍入 bug、保留 API、
  不改测试、修改前后验证；prompt 与 CLAUDE.md 为主要对照，另有三种消融。
- 七文件自创 MIT fixture，初始 10 个测试中 4 个失败；已用已知正确修复验证 oracle。
- 干净 repo runner、声明与证据一致性分析、路径/API/测试完整性检查、脱敏、JSON Schema 和离线 CI。
- [学习与面试指南](CLAUDE_CODE_FAILURE_RESEARCH_STUDY_GUIDE.md)，含 30 题参考答案。

本地离线检查：

```powershell
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python -m runners.validate_repository
python -m runners.run_study --repetitions 1
```

最后一条仅生成计划，不调用模型。登录后先运行官方访问探针和 N=1 pilot，
确认 resolved model、权限、指令加载和日志格式，再按预注册计划运行每组 N=10。
具体命令与费用上限见 [英文 README](README.md)。整个仓库没有自动提交 issue 的代码。

[42 项离线检查](results/offline-validation.json)已通过。
[独立审查](reports/independent-review.md)发现共用文档重复投递约束，已在任何
真实 run 前修正为 V01 1.0.1；原设计与修订理由均已保存。审查允许公开框架，
不批准提交尚无实测证据的 issue。

原始日志留在被 Git 忽略的 `.private/`；公开结果只导出审阅过的元数据，
不发布完整 transcript。访问中断单列为 blocked，不进入有效行为 trial 分母。
不明确的“tests passed”范围交给人工复核，不能擅自解释为全量测试通过。

长任务、compaction、subagents、MCP、IDE 和 Remote Control 尚未完成实测。
当前没有可报告 case，故没有 issue、Anthropic 回复或 v0.1.0 release。
将来达到 E3/E4、排除重复且独立审查通过后，才进入正式报告。

求职材料目前可写：搭建了受控可靠性研究框架、程序化 verifier 与可复现 fixture。
不能写“发现并报告了 Claude bug”或“Anthropic 已修复”。
