# Windows merge-state fixture 独立提交审查

审查日期：2026-10-05。结论：**approve-to-submit-as-test-fixture**。

现有草稿可作为官方 `mods/diff/tests/register.test.ts` 的原生 Windows 路径匹配缺陷提交。没有发现需要阻断提交的证据或隐私问题。此结论仅批准该测试 fixture 的报告范围，不批准将它计为生产 merge bug、模型 failure、原生 test worker 故障或跨平台一般失败率。

审查者未参与本轮实验设计。本次仅只读检查指定草稿、报告、五份 qualification 数据、最小 wrapper、wrapper 验证和随附去重记录，并检查 wrapper 直接使用的 runner 函数。未设计或执行新实验，未调用 Claude 模型，未发布 issue/comment，未更改登录、设置或原有文件。此文件是本次唯一写入。

## 证据与结论边界

| 检查对象 | 审查结果 |
|---|---|
| 原始整个 register 文件 | 三次均为 40 个唯一 test case；各 37 pass / 3 fail，9 次失败均属于同一组三个 merge-state 用例，分类为 assertion；均完整、有退出码 1、无 outer timeout。原始与执行 register 的 SHA256 相同。 |
| portable register | 三次均为 40 个唯一 test case、40 pass / 0 fail、完整、退出码 0、无 outer timeout；上游 pin、二进制 SHA256、5000 ms case deadline、dispatch 与原始组一致。 |
| 路径诊断 | 三个预期契约均通过。literal/portable 两条记录均观测到合成 `C:\work\.git`；literal 的 `before_unavailable=false`，portable 的 `before_unavailable=true`，二者 `after_changed=true`。第三个用例为无 merge marker 时展示普通 diff 的控制。 |
| portable serial | 30 个单文件 native invocation 汇总 210/210；每个文件均完整、退出码 0、无 timeout；汇总与 210 条唯一 case 记录一致，`overlay_restored=true`。这不是一次默认全套并行 dispatch 的 210/210。 |
| 新最小 wrapper 验证 | 两臂各 40 个 case：literal 37/3、portable 40/0，均完整。执行树 SHA256 分别与主原始/portable register 组相同；当前 wrapper SHA256 与验证记录一致。它是另一次 wrapper 复现，不应添加到主要三次重复的分母。 |
| 不完整全套尝试 | 有 115 个 pass 标签和 2 个 case-timeout 标签，`tests_run=null`、`complete=false`、`timed_out=true`。草稿和报告正确将其单列；不能当成完整 117-case 失败率或完整全套结果。 |

`prepare_portable_control` 对固定 pin 要求原始比较式只出现一次，语义上仅替换 `e.path === '/work/.git'`，不删除断言或放宽 timeout。`prepare` 在两臂中均只保留整个 register test 文件；wrapper 检查 production hooks 树哈希一致。上述静态机制、相同三个断言的重复表现，以及已观测合成路径的控制，共同支持“literal fixture 未送达 merge marker”的解释。

三种 merge delay 和三次重复是确定性稳定性检查，不是独立模型样本或随机化因果估计。运行顺序、文件隔离、单机与单一当前引擎限制仍然存在，但在已有的 fixture 机制证据下，不构成该狭窄缺陷报告的阻断混杂。portable serial 也没有证明原始全套超时的内部调度原因。研究 copytree 长路径错误是测试前的 harness setup 失败，报告已正确分开，不能归因于所报断言缺陷。

草稿标题、开头、版本与回归字段均保持了这个边界；未主张真实用户仓库 merge 刷新失败，未主张模型指令遵循失败，也未把未执行的 portable full-dispatch 重复算作完成。归类为 test-fixture bug 合适。

## 复现充分性

对本次固定版本/固定源码的狭窄结论，复现材料充分。README 给出官方 source pin、二进制 SHA256、两臂命令与 0/1/2 退出码约定；代码校验原生 Windows、官方 origin、固定 commit、相关源码和 license 的 clean 状态，以及固定二进制哈希/版本。其私有副本保留 license；两臂没有生产 hook 改动。公开 wrapper 依赖本研究 checkout 内的 runner，不是单文件独立脚本，README 已说明从本研究 checkout 执行。

本次没有重新运行 wrapper，也没有检查私有 raw logs 或重新校验二进制签名。因此对具体 assertion 文本、签名 provenance 和当前远端 HEAD 的评价依据是所提供的既有记录；日志 SHA256 提供追踪点，不等于本审查重新验证了日志内容。已有完整 wrapper 验证和可读静态实现足以支持提交 fixture issue，而不足以扩大运行或生产结论。

## 重复风险

去重记录按具体 matcher、register 文件、merge timing 和 plugin-test 症状检索，并记录相关 PR 与大型 mods 讨论的区别；没有记录到同一 literal matcher/Windows merge-state fixture 的现存报告。引入 merge-completion tests 的 PR 与 first-edit PR 已被分别识别，不能仅因涉及同一个文件就视为本缺陷的重复。

这是“现有去重记录未识别精确重复”，不是新颖性证明。`/work/.git` 查询的 1280 个宽泛结果没有穷尽性价值，记录明确保留了这一限制。本次未独立重跑远端搜索或重读其全部评论；无法排除未索引、之后新增或维护者已知的报告。该残余风险可接受；若维护者指出重复，应将此处证据转入既有条目。

## 隐私与公开范围

指定公开草稿、报告、fixture 和数据只含合成路径、测试名称、版本、时间、哈希与公开 GitHub 链接。只读模式检查未发现 token 常见格式、个人 home 路径或凭据赋值。没有真实仓库内容、模型输出、账号/订阅信息或完整 raw log；`C:\work\.git` 是合成测试路径。凭据文件和登录状态未被访问。该检查不构成对未提供私有日志的发布批准。

## 必要修改与非阻断建议

**必要修改：无。** 可以按当前准确限定的 test-fixture 草稿提交。

两项小幅澄清可在提交整理时完成，均不影响审查结论：

- 将复现步骤中的 `claude plugin test mods/diff` 明确标为直接全套入口；将 wrapper 两臂比较标为本次已完整验证的 40-case 复现入口。当前结尾已披露原始全套 outer timeout，但在步骤旁说明会减少读者误以为该全套命令应直接返回 37/3 的可能。
- README 的“40 assertions”宜写为“40 test cases, with all original assertions retained”。数据证明的是 40 个 case，并没有给出断言语句总数。

后续若改变 matcher、fixture、执行树、版本或报告主张，应重新核查相应改变；当前批准不延伸到新的研究结论。
