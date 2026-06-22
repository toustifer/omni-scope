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

Every claim tagged with origin:

| Tag | Source |
|-----|--------|
| `[AR:web]` | Agent-Reach Jina Reader |
| `[AR:search]` | Exa search result |
| `[AR:social]` | Twitter / Reddit / 小红书 / B站 / V2EX |
| `[AR:code]` | GitHub search |
| `[AR:video]` | YouTube / B站 transcript |
| `[SP:fetch]` | Scrapling Fetcher (HTTP) |
| `[SP:stealth]` | Scrapling StealthyFetcher (anti-bot bypass) |
| `[SP:dynamic]` | Scrapling DynamicFetcher (JS rendered) |
| `[OB]` | Obscura raw crawl |
| `[AR→SP]` | Agent-Reach discovered, Scrapling verified |
| `[AR→OB]` | Agent-Reach discovered, Obscura verified |

**Output format:**

```
## OmniScope 研究报告: [Topic]

### 多平台发现
| 平台 | 关键发现 | 来源 |
|------|---------|------|
| Twitter | ... | [AR:social] |
| Reddit | ... | [AR:social] |
| GitHub | ... | [AR:code] |

### 深度验证
> [Scrapling/Obscura 抓取的原文关键段落]

#### 差异标记
- ⚠️ 搜索摘要遗漏: [...]
- ⚠️ 平台间矛盾: [Twitter 说 X vs Reddit 说 Y]
- ✅ 多源一致: [...]

### 可靠性矩阵
| 来源 | 类型 | 可靠性 | 理由 |
|------|------|--------|------|
| [URL] | 一手页面 | 最高 | Scrapling 绕过反爬抓取 |
| [URL] | 社交媒体 | 中 | 用户观点，需交叉验证 |
| [search] | 搜索摘要 | 低 | 可能遗漏关键上下文 |
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

- **Single-platform blind spot**: researching only via web search, missing social discussion (Twitter/XHS/Reddit often have more candid takes).
- **Trusting Jina Reader on anti-bot pages**: Jina gets blocked too. If `r.jina.ai` returns empty/error, escalate to Scrapling StealthyFetcher.
- **Using yt-dlp on B站**: blocked by B站风控. Use Agent-Reach's `bili search` instead (routed via bili-cli).
- **Sequential crawling**: Scrapling and Obscura both parallelize well. Never crawl URLs one at a time.
- **Not running doctor first**: Agent-Reach backends change. Run `agent-reach doctor --json` before every session to see active backends.
- **No platform diversity**: Chinese topics need 小红书/B站/V2EX, not just Twitter/Reddit. English topics vice versa. Match platforms to the topic's language and audience.
- **Skipping the diff**: the value is in what one source has and another doesn't. Always highlight discrepancies.
