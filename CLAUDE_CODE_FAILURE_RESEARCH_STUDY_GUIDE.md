# Claude Code Failure Research 学习与面试指南

规则核查日：2026-10-03；研究更新日：2026-10-04；固定版本：2.1.288。本项目是社区研究。
**目前包含框架、28 个已有报告筛查、离线验证与无需账号的真实客户端契约
实验；没有 Claude 模型 coding trials、确认生产 failure、Anthropic issue 或
修复。** 面试时首先说清楚这个证据边界。

免费研究使用官方 `claude plugin test` 和公开内置 mod 源码。真实引擎负责
hooks/UI 分发，测试脚本应答下层世界；部分测试直接调用公开源码函数。
这能够研究组件契约，不能推断 Claude 模型的指令保留或长任务能力。
Windows 的 `/work/.git` 虚拟路径曾制造测试假阳性：引擎请求 `C:\work\.git`，
原 stub 未匹配。对照只调整模拟路径；实测记录见 [免费研究报告](docs/no-cost-research.md)。

两项旧测试超时已完成[专项调查](docs/timeout-investigation.md)：默认 5 秒与
15 秒时限的隔离原用例各 20/20 通过，完整默认派发仍重现超时；采样观察到
CLI 子进程并发峰值 27。逐文件派发在默认 5 秒时限下 210/210 通过。
这支持测试派发与套件上下文敏感性判断，但内部原因未隔离，不能说生产 bug 已修复。

## 从一次 coding run 读懂系统

用户任务与项目指令进入上下文，模型选择工具；Claude Code 负责工具、权限、
hooks、会话与结果交付。MCP 扩展外部工具，plugin 可以组合 hooks、skills、
agents 等组件。工具返回以后模型继续推理，最终描述结果。每一层都可能出错，
所以“结果不对”不能直接确定责任层。

CLAUDE.md 是行为上下文，不能保证硬性禁止操作。`.claude/rules/` 可按路径加载。
当前原生 AGENTS 支持有版本、fallback 和可用性条件；同时存在 CLAUDE.local.md
时，默认选择可能改变。先核实加载，再研究保留。见 [官方 memory 文档](https://code.claude.com/docs/en/memory)。

Hook 是运行时事件处理机制。PreToolUse 在工具执行前，PostToolUse 在成功后，
PostToolUseFailure 处理失败，Stop、SessionStart、SubagentStop 对应不同生命周期。
同名注册、父子 session 或不同 tool ID 可以产生多个合法调用。事件、注册与
调用实体必须同时对齐。见 [hooks](https://code.claude.com/docs/en/hooks)。

权限 deny → ask → allow 的优先级先于你对“应该允许”的直觉；auto mode 还有
classifier，managed policy 也可能覆盖普通设置。原生 Windows 的 Bash sandbox
不受支持，应采用官方支持的 WSL2 等环境。权限设置不能被说成 OS sandbox。
见 [permissions](https://code.claude.com/docs/en/permissions)、[sandbox](https://code.claude.com/docs/en/sandboxing)。

Subagent 拥有自己的上下文与工具设置，不能假定继承所有父会话内容。Compaction
重构会话上下文，需要观察实际 boundary。Git 状态应从 git 命令与时间点确认，
不能把模型记忆当作最新 diff。MCP 则要分开服务器、协议、传输、认证及客户端。
见 [subagents](https://code.claude.com/docs/en/sub-agents)、[MCP](https://code.claude.com/docs/en/mcp)、
[agent loop](https://code.claude.com/docs/en/how-claude-code-works)。

## Classification：面试时怎样说明归类

如果模型看到明确要求，工具与权限正常，却多次选择不测试并声称全量测试通过，
应优先报告 model behavior。如果实际进程完成、hook 调用或 tool result 交付
被客户端错误重复/遗漏，且有固定条件复现，则可能是 software bug。单纯 gateway
报错、用户规则冲突或第三方插件异常，首先是 environment/configuration 诊断。
真正越过安全边界的行为进入私密安全渠道，不能公开 issue。

当前 `github_connection` 是 claude.ai 连接 GitHub 的表单，不能机械套到所有
Action/@claude/PR 故障。模板核查与归因细节见 [issue routing](docs/issue-routing.md)。

## 30 个面试问题与参考答案

1. **为什么一次失败不足？** 一次运行混合了模型采样、任务难度、工具与服务状态。
   它只能形成 E1 候选。重复运行估计频率，对照排除解释；确定性软件缺陷另用最小复现。

2. **怎么做 control？** 固定任务、初始 repo、模型、模式、预算、平台，只改变目标因素。
   V01 主对照把同一约束放在 prompt 或 CLAUDE.md。随机运行顺序减少时间漂移，
   但不能替代控制模型/加载条件。

3. **Ablation 是什么？** 移除或替换某机制，观察症状是否仍出现。重申约束、关闭插件、
   更换指令来源都有诊断用途。Safe mode 同时改变多项机制，不能当单因素因果识别。

4. **怎样减少 confounding？** 每次 fresh fixture，固定 CLI/模型与权限，排除用户
   gateway、插件和 MCP，核对实际加载。保留中断与反例，并检查不同组的 dropout。
   外层命令串行也不能保证测试引擎内部 worker 串行；须分开测试时限、派发方式、
   解析器错误和功能断言失败。逐文件对照通过也不能自动识别具体资源瓶颈。

5. **为什么预注册 failure criteria？** 防止看完结果才定义“失败”，同时让负结果可解释。
   需要修改时先版本化新协议，再开始新 run；不能悄悄改变已有数据的标签规则。

6. **Goal drift 是什么？** 原始必需目标被遗漏、优先级被替换或扩大为无关重构。
   预先列出 required/optional/out-of-scope，才能区分正常探索与偏离。

7. **Verification omission 是什么？** 明确要求的验证没有完成。例如只写出测试命令、
   在旧代码上跑过，或只跑了子集。代码最后正确也不能补足 agent 没执行验证的事实。

8. **False completion claim 是什么？** 明确的完成/通过声明被可对齐的事实证据反驳。
   未执行但宣称通过是 unsupported；同一最终状态的全量测试失败而宣称通过是 false。
   这两类应分别计数。

9. **Instruction retention 怎样测？** 把可验证工程约束前置，改变正常任务长度，
   分别确认指令是否加载和之后是否遵守。路径/API 可自动测，阅读顺序可能需人工 trace。

10. **Long-horizon 为什么难？** 工具结果、分支假设、未完成任务、错误恢复不断积累，
    上下文压缩和并行协作可能改变显著性。用实际 tool count 和时间暴露分层，
    不能靠 prompt 写“100 steps”来声称观察到长任务。

11. **Hook 和 plugin 的关系？** Hook 是事件机制，plugin 是分发组件的载体。
    本地与 plugin 注册可以并存。研究核心问题时必须提供不依赖自制插件的 clean repro。

12. **CLAUDE.md 怎样影响 agent？** 它向模型提供项目行为上下文，不是强制权限策略。
    指令清晰与加载位置影响遵循，但“加载了”不等于“必然遵守”。

13. **Permissions 怎样影响工具？** 决策结合 deny/ask/allow、mode 和管理策略。
    未批准的工具无法完成验证。先确认有效配置，才能区分模型没选工具与客户端拒绝执行。

14. **Subagents 会产生哪些 failure？** 子任务丢失、失败被父会话说成成功、重复修改、
    文件冲突、父子约束不同。验证子会话记录、错误与编辑所有权，不能只看父总结。

15. **Compaction 的风险是什么？** 会话证据、优先级或待办可能在摘要中改变；
    但长期会话本身就更难。自动 compaction 的发生是内生的，单纯前后差异不能证明因果。

16. **MCP 错误怎样分类？** 先复核 schema、server response、连接和认证。可重现
    的客户端结果交付问题是 software；第三方 server 错误归 owning component；
    模型没读错误再重复调用可能是 behavior。

17. **Model failure 与 harness failure 的区别？** 前者是给定可用信息后的选择，
    后者是信息/工具/状态交付实现。不同模型与 surface 对照能提供诊断，
    但公共仓库看不到的内部原因仍必须写 unknown。

18. **怎样排除 environment failure？** 检查 shell/PATH、repo、有效 settings、
    权限、插件和 provider。隔离网关后没有官方认证，是实验前提不足，不能叫 Claude bug。

19. **为什么 clean baseline 重要？** 研究仪器可能自己改变行为。先去掉自制 plugin、
    hook 与外部 MCP，保留相同任务/模型条件，再添加仪器，才能诊断其影响。

20. **怎样做 minimum repro？** 缩减为触发症状必需的文件、配置与步骤，每次缩减都重测。
    保持现实任务与可公开 MIT fixture；删掉真实用户数据、私有 repo 与不必要依赖。

21. **如何把 failure 变成 eval？** 固定 initial state、task、constraint、objective
    verifier 和 outcome schema，并保留触发条件与反例。Eval 应对未来版本可执行，
    而不是只记一次坏输出。

22. **怎样设计 programmatic verifier？** 直接核对 exit code、测试数量、文件/API
    与最终 source hash。Agent 验证和 observer 验证必须分开；任何测试改动使
    原验证证据失去可信度。当前 fixture 审计与 tool marker 交叉核对，仍非防篡改证明。

23. **什么时候需要 LLM judge？** 难以编码的语义 scope、摘要忠实度或可读性可能需要。
    客观路径、测试和 API 不应完全依赖它。Judge 应盲于组别、校准到人工标注并报告一致性。

24. **False positive 怎样处理？** 逐条复核范围、否定、条件句、不同代码版本和子集测试。
    不明确就 abstain。用人工标注估计 precision/recall，不把解析器没抓到当成没有问题。

25. **如何比较版本？** 固定 fixture 与 protocol，记录 CLI 和实际 model ID/date，
    重复相同条件。客户端 patch 与模型后端更新可能同时发生，不能把所有变化归给版本号。

26. **哪些 failure 适合 RL？** 可客观验证的工具选择、修复策略和验证纪律可形成反馈。
    先判断任务覆盖与奖励是否正确，防止奖励只鼓励说“测试通过”而不要求真实证据。

27. **哪些必须改 runtime？** 确定性事件重复、permission 实现、tool result 丢失
    或会话状态错误，应从运行时修复。训练模型去补偿稳定客户端缺陷不是可靠修复路径。

28. **怎样构造 training trajectory？** 使用获授权、去敏的任务、工具观察与实际结果，
    标记纠错和验证节点，保留失败与反例。公共最小 fixture 可复现，不应收集私人 transcript。

29. **Reward 怎样设计？** 分开任务正确、约束、验证和声明一致性，并设置不可补偿的
    硬约束。测试篡改不应被正确代码奖励抵消；单纯更长、更频繁 tool use 也不应得分。

30. **加入团队后怎样继续研究？** 先验证仪器与真实任务代表性，再扩展到长期任务和
    版本回归，形成可重复 bug→eval→fix→retest 闭环。跨 agent 比较应固定能力、预算和
    工具条件。当前已执行免费客户端契约实验，但还未完成 Claude 模型 coding pilot。

## 简历表述：随事实升级

目前可用的英文 bullet：

> Built a preregistered Claude Code reliability framework and executed 110 local
> client test-case runs using the official test engine and public module helpers;
> isolated a Windows virtual-fixture path mismatch through controlled comparisons,
> with explicit separation from unexecuted Claude model coding trials.

只有实际完成报告后，才能写 reported a reproducible failure。只有官方修复并在
原 fixture 上验证，才能写 independently verified an Anthropic fix。
本项目所有状态均以 [技术报告](docs/technical-report.md) 与 run 数据为准。
