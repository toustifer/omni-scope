<h1 align="center">🔭 OmniScope · 全视研究引擎</h1>

<p align="center">
  <strong>三个工具，一条流水线。为 Claude Code 打造的跨平台深度调研 Agent Skill。</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-skill-6C47FF?style=for-the-badge&logo=anthropic" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/DeepSeek_Harness-skill-blue?style=for-the-badge" alt="DeepSeek Harness Skill">
  <img src="https://img.shields.io/badge/平台-13-00C853?style=for-the-badge" alt="13 Platforms">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <a href="README_en.md">English</a> · <a href="README_ja.md">日本語</a>
</p>

---

## 这是什么？

OmniScope 是一个**三阶段调研流水线**，把三个顶尖开源工具整合成一个无缝的 Agent Skill：

```
                    ┌──────────────────┐
                    │    🔭 OmniScope   │
                    │    全视研究引擎    │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   🔭 撒网                ⛏️ 攻坚               🔍 验证
  Agent-Reach           Scrapling            Obscura
  13平台发现           反反爬+自适应解析      交叉对比+可靠性打分
```

| 阶段 | 工具 | 职责 |
|------|------|------|
| **撒网** | [Agent-Reach](https://github.com/Panniantong/Agent-Reach) | 13 个平台并行发现（Twitter、Reddit、GitHub、YouTube、B站、小红书、V2EX…） |
| **攻坚** | [Scrapling](https://github.com/D4Vinci/Scrapling) | 绕过 Cloudflare/反爬 + 自适应解析（网站改版也不怕） |
| **验证** | [Obscura](https://github.com/h4ckf0r0day/obscura) / deep-research 方法论 | 原始页面抓取 → 跟搜索摘要对比 → 标记矛盾 → 可靠性打分 |

## 为什么需要 OmniScope？

**痛点：** AI Agent 只会用搜索引擎，错过了社交媒体的真实讨论、代码仓库、视频内容。就算去爬，也会被反爬拦住。找到矛盾信息？它没能力验证。

**解法：** OmniScope 自动化完整情报循环——跨平台广撒网 → 穿透防御拿一手数据 → 每条结论跟原始来源交叉验证。

## 快速上手

```bash
# 安装 OmniScope skill
git clone https://github.com/toustifer/omni-scope.git ~/.claude/skills/omni-scope

# 在 Claude Code 中使用：
/omni-scope "帮我全面调研 XXX"
```

> 💙 **DeepSeek Harness 用户**：本仓库 `deepseekdsh` 分支提供 DSH 适配版 ——
> DSH 格式 frontmatter（`whenToUse`）、`--doctor` 预检、`--json` 结构化输出、环境变量配置。
> 安装 & 使用见 **[README.dsh.md](README.dsh.md)**：
> `git clone -b deepseekdsh https://github.com/toustifer/omni-scope.git ~/.agents/skills/omni-scope`

### 安装底层依赖

OmniScope 依赖三个底层工具，各装一次即可：

```bash
# 1. Scrapling — 反反爬 + 自适应解析
pip install scrapling[fetchers,ai,shell]
playwright install chromium

# 2. Agent-Reach — 13 平台发现
git clone https://github.com/Panniantong/Agent-Reach.git
cd Agent-Reach && pip install -e ".[all]"

# 3. Obscura — 原始页面抓取验证
cd D:/myprogram/obscura && cargo build --release
```

装完后运行 `agent-reach doctor --json` 查看各平台状态。

## 调研输出示例

每条结论都带来源标签：

```
## OmniScope 研究报告: 小红书抓取方法

### 多平台发现
| 平台 | 关键发现 | 来源 |
|------|---------|------|
| GitHub | Spider_XHS 6.5k⭐ | [AR:code] |
| Reddit | XHS 反爬比 Twitter 更狠 | [AR:social] |
| Twitter | Scrapling 被推荐用于隐身抓取 | [AR:social] |

### 深度验证
> [Scrapling/Obscura 抓取的原文段落]

#### 差异标记
- ✅ 多源一致: 必须用住宅代理
- ⚠️ 搜索摘要遗漏: 签名算法每月变更

### 可靠性矩阵
| 来源 | 可靠性 | 理由 |
|------|--------|------|
| GitHub 源码 | 最高 | 开源可审计 |
| 社交媒体 | 中 | 用户观点，需交叉验证 |
| 搜索摘要 | 低 | 遗漏关键上下文 |
```

## 来源标签体系

| 标签 | 含义 |
|------|------|
| `[AR:web]` | Agent-Reach Jina Reader 网页 |
| `[AR:social]` | Twitter / Reddit / 小红书 / B站 / V2EX |
| `[AR:code]` | GitHub 搜索 |
| `[AR:video]` | YouTube / B站 字幕 |
| `[SP:stealth]` | Scrapling StealthyFetcher（绕过反爬） |
| `[SP:dynamic]` | Scrapling DynamicFetcher（JS 渲染页面） |
| `[OB]` | Obscura 原始抓取 |
| `[AR→SP]` | 跨工具交叉验证 |

## 支持平台

| 类别 | 平台 |
|------|------|
| **社交（海外）** | Twitter/X、Reddit |
| **社交（国内）** | 小红书 (测试中)、B站、V2EX |
| **代码** | GitHub |
| **视频** | YouTube、B站 |
| **搜索** | Exa（语义搜索）、Jina Reader（网页） |
| **内容** | RSS、任意网页 |

---

## 🙏 致谢

OmniScope 站在三个杰出开源项目的肩膀上：

### 🔭 [Agent-Reach](https://github.com/Panniantong/Agent-Reach) — by [Neo Reid](https://github.com/Panniantong)

> 「给你的 AI Agent 一键装上互联网能力。」

Agent-Reach 是 **撒网层**——它解决了 13 个平台的多后端路由难题。yt-dlp 被 B站封了？自动切换到 bili-cli。Reddit 匿名接口挂了？自动走 rdt-cli。这种基础设施级别的容错，让 Agent 从此告别平台碎片化噩梦。

**选择理由：** 唯一提供零配置多平台接入 + 自动后端故障转移的工具。`agent-reach doctor` 诊断系统让平台健康状态一目了然。

### 🕷️ [Scrapling](https://github.com/D4Vinci/Scrapling) — by [Karim Shoair](https://github.com/D4Vinci)

> 「一个自适应的 Web 抓取框架，从单次请求到大规模爬取，应有尽有。」

Scrapling 是 **攻坚层**——普通抓取被拦时，StealthyFetcher 绕过 Cloudflare Turnstile。网站改版时，自适应 Selector 自动重新定位元素。65k+ GitHub Stars，开源抓取框架中增长最快。

**选择理由：** 文本提取比 BeautifulSoup 快 774 倍，内置 MCP Server 用于 AI 集成，唯一同时具备反反爬 + 自适应解析的框架。

### 📡 [Obscura](https://github.com/h4ckf0r0day/obscura) · deep-research 方法论

> 「通过原始页面抓取实现地面真相验证。」

**验证层**——Obscura 以 HTTP 级别爬取页面（仅 30MB 内存，无浏览器开销），提供一手原始内容，与搜索引擎摘要交叉对比。deep-research 方法论确保每条结论都有明确来源和可靠性评分。

**选择理由：** 搜索摘要省略关键上下文。Obscura 轻量级架构支持 4+ URL 并行抓取，让验证又快又彻底。

---

## 开源协议

MIT — 心怀感恩，回馈开源社区。

---

<p align="center">
  <sub>如果 OmniScope 对你的调研有帮助，请给三个底层项目各点一颗 ⭐</sub>
</p>
