---
name: omni-scope
description: >
  Use when the user asks for comprehensive internet research that spans multiple platforms —
  全网调研, 深度调研, 全面调研, 跨平台研究, multi-source investigation.
  Use when the task demands: (1) broad discovery across web + social + video + code platforms,
  (2) penetrating anti-bot or JS-heavy sites that normal fetchers can't reach,
  (3) high-confidence verification where search summaries must be cross-checked against raw primary sources.
  Triggers on: 全面调研, 跨平台搜索, omni-research, omni, 全平台, 深度对比,
  "check this across Twitter Reddit and GitHub", "find everything about X".
  NOT for: single-platform lookups (use agent-reach directly),
  simple web page reads (use agent-reach web channel),
  one-off URL fetches without verification needs.
triggers:
  - omni:
    - 全面调研/全平台搜索/跨平台/全网搜索/全方位/omni/omni-scope
    - 所有平台都搜一下/多平台对比/到各个平台看看
    - 深度对比/find everything about/cross-platform research
    - 帮我彻底研究/深挖/全面了解/完整调研
---

# OmniScope — 全视研究

Three tools, one pipeline. **Scout** (Agent-Reach) discovers across 13 platforms. **Extract** (Scrapling) penetrates defenses. **Verify** (deep-research methodology) cross-references and scores reliability.

## Decision Flow

```
Research request arrives
        │
        ▼
┌─────────────────────────────────┐
│ 1. SCOUT: Agent-Reach           │
│    Multi-platform discovery     │
│    Web + Social + Video + Code  │
│    Parallel, independent queries│
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ 2. EXTRACT: Per-URL decision    │
│                                 │
│ Normal page → Agent-Reach web   │
│ Anti-bot page → Scrapling       │
│   StealthyFetcher               │
│ JS-heavy SPA → Scrapling        │
│   DynamicFetcher                │
│ Structured data → Scrapling     │
│   Selector (adaptive parsing)   │
│ Raw ground-truth → Obscura      │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ 3. VERIFY: Cross-reference      │
│    Compare search vs primary    │
│    Flag discrepancies           │
│    Score reliability per source │
│    Synthesize with source tags  │
│    EVERY tag MUST carry a URL   │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ 4. REVIEW: Content & Compliance │
│    Check regulatory red lines   │
│    Assess content safety        │
│    Flag ethical / legal risks   │
│    Privacy & data compliance    │
└─────────────────────────────────┘
```

## Phase 1 — Scout (Agent-Reach)

**REQUIRED:** Read `agent-reach` skill routing table first. Run `agent-reach doctor --json` before starting.

Cover at least 3 of these angles in parallel:

| Angle | Platform | Command pattern |
|-------|----------|----------------|
| Web search | Exa | `mcporter call 'exa.web_search_exa(query: "Q", numResults: 5)'` |
| Social (EN) | Twitter, Reddit | `twitter search "Q" -n 10` / `opencli reddit search "Q"` |
| Social (CN) | 小红书, B站, V2EX | `opencli xiaohongshu search "Q"` / `bili search "Q"` |
| Code | GitHub | `gh search repos "Q" --sort stars --limit 10` |
| Video | YouTube, B站 | `yt-dlp --write-sub --skip-download URL` (only YT) |
| Web pages | Jina Reader | `curl -s "https://r.jina.ai/URL"` |

Collect 5-15 candidate URLs/sources across all platforms.

## Phase 2 — Extract (Scrapling)

Route each URL by its defense level:

```python
from scrapling import Fetcher, StealthyFetcher, DynamicFetcher

# Level 0: Normal static page
page = Fetcher().get(url)
content = page.css('article').text()

# Level 1: Behind Cloudflare / anti-bot
stealth = StealthyFetcher()
page = stealth.get(url)
content = page.css('article').text()

# Level 2: JavaScript SPA (React/Vue)
dyn = DynamicFetcher()
page = dyn.get(url)
page.wait_for('.content-loaded')
content = page.css('.content-loaded').text()

# Level 3: Structured data extraction (survives site redesigns)
selector = page.css('.price')[0]
auto_css = page.generate_selector(selector)  # regenerates if layout changes
```

**When to use Scrapling instead of Agent-Reach web/Jina:**
- Page returns 403 / Cloudflare challenge
- Page is JS-rendered (empty body with `<div id="app">`)
- Need precise element extraction (not full-page text)
- Large-scale crawl (use Scrapling Spider)

**Parallelize**: crawl up to 4 URLs simultaneously across both tools.

## Phase 3 — Verify & Synthesize

**CRITICAL: Every source tag MUST carry a clickable URL.** Never output a bare tag without a link.

Source tag format: `[Platform Name](URL) [AR:source]`

| Tag | Source | Required Link Format |
|-----|--------|---------------------|
| `[AR:web]` | Agent-Reach Jina Reader | `[文章标题](URL) [AR:web]` |
| `[AR:search]` | Web/Exa search result | `[来源名称](URL) [AR:search]` |
| `[AR:social]` | Twitter / Reddit / 小红书 / B站 / V2EX | `[@作者](URL) [AR:social]` |
| `[AR:code]` | GitHub search | `[repo/name](URL) [AR:code]` |
| `[AR:video]` | YouTube / B站 transcript | `[视频标题](URL) [AR:video]` |
| `[SP:stealth]` | Scrapling StealthyFetcher | `[页面标题](URL) [SP:stealth]` |
| `[SP:fetch]` | Scrapling Fetcher (HTTP) | `[页面标题](URL) [SP:fetch]` |
| `[SP:dynamic]` | Scrapling DynamicFetcher (JS) | `[页面标题](URL) [SP:dynamic]` |
| `[OB]` | Obscura raw crawl | `[页面标题](URL) [OB]` |
| `[AR→SP]` | Cross-tool verified | `[页面标题](URL) [AR→SP]` |

**Output format:**

```
## OmniScope 研究报告: [Topic]

### 多平台发现
| 平台 | 关键发现 | 来源链接 |
|------|---------|---------|
| Twitter | @cyrilXBT 列出Scrapling为10大采集神器 | [@cyrilXBT](https://x.com/cyrilXBT/status/xxx) [AR:social] |
| 36氪 | 9块9的AI文游在小红书火爆 | [36氪](https://www.36kr.com/p/3650102990692743) [AR:search] |
| GitHub | Spider_XHS 6.5k⭐ | [Spider_XHS](https://github.com/cv-cat/Spider_XHS) [AR:code] |

### 深度验证
> [Scrapling/Obscura 抓取的原文关键段落，附带抓取 URL]

#### 差异标记
- ⚠️ 搜索摘要遗漏: [...]
- ⚠️ 平台间矛盾: [来源A vs 来源B]
- ✅ 多源一致: [...]

### 可靠性矩阵
| 来源 | 类型 | 可靠性 | 理由 |
|------|------|--------|------|
| [文章标题](URL) | 一手页面 | 最高 | Scrapling 绕过反爬抓取 |
| [推文链接](URL) | 社交媒体 | 中 | 用户观点，需交叉验证 |
| [搜索摘要] | 聚合信息 | 低 | 可能遗漏关键上下文 |
```

## Phase 4 — Content & Compliance Review (MANDATORY)

**Every report MUST include a content review section** before closing. This is not optional.

Assess the following dimensions:

| 维度 | 检查项 |
|------|--------|
| **合规性** | 涉及行业是否有监管红线？平台政策是否允许？ |
| **内容安全** | 调研对象是否涉及灰色/黑色地带？数据来源是否合法？ |
| **伦理边界** | AI 生成内容是否有版权/偏见/误导风险？ |
| **商业道德** | 建议的商业模式是否有法律风险（如二清/支付牌照）？ |
| **数据隐私** | 抓取的数据是否涉及个人信息？是否符合 GDPR/个保法？ |

**Output format:**

```
## 内容审查与合规提醒

| 维度 | 评估 | 风险等级 | 建议 |
|------|------|---------|------|
| 合规性 | ... | 🟢/🟡/🔴 | ... |
| 内容安全 | ... | 🟢/🟡/🔴 | ... |
| 伦理边界 | ... | 🟢/🟡/🔴 | ... |
| 商业道德 | ... | 🟢/🟡/🔴 | ... |
| 数据隐私 | ... | 🟢/🟡/🔴 | ... |

> ⚠️ 本报告仅供研究参考，不构成商业建议。具体业务决策请咨询专业律师。
```

## Tool Paths

```
Agent-Reach CLI:  agent-reach
Agent-Reach src:  D:/myprogram/Agent-Reach
Scrapling:        python -c "from scrapling import ..."
Scrapling MCP:    scrapling mcp
Obscura:          D:/myprogram/obscura/target/release/obscura
```

## Common Mistakes

- **Bare source tags without URLs**: NEVER output `[AR:social]` without a clickable link. Every tag must be `[Name](URL) [AR:source]`.
- **Skipping Phase 4**: Every report MUST have a content/compliance review section. No exceptions.
- **Single-platform blind spot**: researching only via web search, missing social discussion (Twitter/XHS/Reddit often have more candid takes).
- **Trusting Jina Reader on anti-bot pages**: Jina gets blocked too. If `r.jina.ai` returns empty/error, escalate to Scrapling StealthyFetcher.
- **Using yt-dlp on B站**: blocked by B站风控. Use Agent-Reach's `bili search` instead (routed via bili-cli).
- **Sequential crawling**: Scrapling and Obscura both parallelize well. Never crawl URLs one at a time.
- **Not running doctor first**: Agent-Reach backends change. Run `agent-reach doctor --json` before every session to see active backends.
- **No platform diversity**: Chinese topics need 小红书/B站/V2EX, not just Twitter/Reddit. English topics vice versa. Match platforms to the topic's language and audience.
- **Skipping the diff**: the value is in what one source has and another doesn't. Always highlight discrepancies.
