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

Three tools, one pipeline. **Scout** (Agent-Reach) discovers across 13 platforms. **Extract** (Scrapling) penetrates defenses. **Verify** cross-references and scores reliability. **Audit** flags untrustworthy sources.

---

## ⚡ QUICK-REFERENCE CARD

> Read this first. Every time. Before ANY tool call.

```
┌──────────────────────────────────────────────────────────────┐
│                    PRE-FLIGHT CHECKLIST                       │
│                                                              │
│  □ 1. Run `agent-reach doctor --json`                        │
│  □ 2. Pick 3+ platforms from the routing table                │
│  □ 3. Scout ALL platforms in PARALLEL (not sequential)        │
│  □ 4. NEVER default to WebSearch alone — that's single-angle  │
│                                                              │
│                    PHASE GATES (self-check)                   │
│                                                              │
│  After Scout:  3+ platforms covered? 5-15 URLs collected?    │
│  After Extract: Any 403/402 left? → escalate or flag dead     │
│  After Verify:  Discrepancies between sources found?          │
│  After Audit:   Any source flagged RED? → DISCARD it          │
│                                                              │
│                    ESCALATION RULES                           │
│                                                              │
│  WebFetch returns 403 → Scrapling StealthyFetcher             │
│  WebFetch returns 402 → Mark PAYWALLED, move on               │
│  Page is blank/<div id="app"> → Scrapling DynamicFetcher      │
│  Search snippet only → NOT a primary source, flag it          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚫 ANTI-PATTERN #1 — Defaulting to WebSearch + WebFetch

**This is the most common failure mode.** Your muscle memory will reach for `WebSearch` and `WebFetch` because they're built-in, fast, and don't need permission prompts. RESIST THIS.

Why it fails:
- WebSearch covers ONE angle (search engine index). Social conversation, code repos, video transcripts, and anti-bot pages are all invisible to it.
- WebFetch silently gives up on Cloudflare-protected pages. You get 403 and move on, losing the most valuable sources.
- Search snippets are the search engine's paraphrase, NOT the original page. They can be outdated, decontextualized, or flat wrong.

**The fix**: After the pre-flight checklist, your FIRST action should be a parallel fan-out across 3+ platforms. WebSearch can be ONE of them — not all of them.

---

## Decision Flow

```
Research request arrives
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│ ⚡ PRE-FLIGHT (30 seconds, before any tool call)          │
│   1. agent-reach doctor --json                           │
│   2. Pick 3-6 platforms matched to topic language/domain │
│   3. Plan parallel queries (write them out, don't run)   │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ 1. SCOUT: Agent-Reach / WebSearch / gh / yt-dlp │
│    Multi-platform discovery, PARALLEL queries    │
│    Target: 5-15 candidate URLs across platforms  │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ ⚡ GATE 1: ≥3 platforms covered? ≥5 URLs found? │
│    Any 403/402? → tag for escalation             │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ 2. EXTRACT: Route each URL by defense level      │
│    200 OK + static → Agent-Reach web / Jina      │
│    403 + Cloudflare → Scrapling StealthyFetcher  │
│    JS SPA (empty body) → Scrapling DynamicFetcher│
│    402 / auth wall → Mark PAYWALLED, skip        │
│    Structured data → Scrapling Selector           │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ ⚡ GATE 2: All 403 pages tried via Scrapling?    │
│    Paywalled pages tagged and abandoned?          │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ 3. VERIFY: Cross-reference search vs primary     │
│    Flag discrepancies between sources            │
│    Search snippet ≠ primary source — check origin │
│    EVERY source tag MUST carry a clickable URL   │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ ⚡ GATE 3: Any contradictions between sources?   │
│    Any search-snippet-only claims flagged?        │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ 4. AUDIT: Source credibility matrix              │
│    ⭐⭐⭐ Authority / Originality / Verifiability │
│    🟢 Trust directly  🟡 Keep with caution       │
│    🔴 DISCARD — do not cite                      │
│    Mark unverifiable claims explicitly            │
└───────────────────────┬─────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│ ⚡ GATE 4: ≥1 source flagged RED and discarded?  │
│    Unverifiable claims marked in report?          │
└───────────────────────┘
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

## Phase 4 — Source Credibility Audit (MANDATORY)

**Every report MUST include a source credibility audit** before closing. This is the final quality gate — flag every source that doesn't hold up.

Audit each source across five dimensions:

| 维度 | 检查项 | 低可信信号 |
|------|--------|-----------|
| **权威性** | 谁发布的？有机构背书吗？ | 个人博客、匿名账号、无署名 |
| **一手性** | 是原始来源还是转载？ | 转载、聚合、引用引用、搜​​索引擎摘要 |
| **可验证性** | 数据/结论能被独立验证吗？ | 无数据来源、模糊说辞、"据说""据悉" |
| **时效性** | 信息是什么时候的？ | 无日期、超过 2 年的市场数据 |
| **动机/偏见** | 发布者有没有利益相关？ | 软文、竞品报告、创业 BP 自我美化 |

**Output format:**

```
## 来源可信度审计

| 来源 | 权威性 | 一手性 | 可验证 | 时效 | 偏见 | 综合 |
|------|--------|--------|--------|------|------|------|
| [名称](URL) | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 🟢 可信 |
| [名称](URL) | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐ | 🔴 弃用 |

### 审计结论
- 🟢 直接引用：N 条（高可信来源）
- 🟡 保留参考：N 条（需交叉验证）
- 🔴 不可引用：N 条（列出原因）
```

## Escalation Decision Tree

When `WebFetch` fails, don't silently skip — escalate:

```
WebFetch result?
        │
        ├── 200 OK + content ──→ Use it ✓
        │
        ├── 403 Forbidden ──→ Scrapling StealthyFetcher
        │   └── Still blocked? → Scrapling DynamicFetcher (headless browser)
        │       └── Still blocked? → Flag [UNREACHABLE], note what was lost
        │
        ├── 402 Payment Required ──→ Flag [PAYWALLED], move on
        │
        ├── 307/308 Redirect ──→ Follow redirect with new URL
        │   └── Redirected host blocked? → Escalate per above
        │
        ├── Empty body / <div id="app"> ──→ Scrapling DynamicFetcher
        │
        └── Jina Reader empty/error ──→ Scrapling StealthyFetcher (Jina gets blocked too)
```

**Critical rule**: Don't silently skip a blocked page. Either escalate to Scrapling, or explicitly flag it as `[UNREACHABLE]` so the user knows what's missing.

---

## Common Mistakes (ranked by frequency)

| # | Mistake | Why it happens | Fix |
|---|---------|---------------|-----|
| **1** | **Defaulting to WebSearch + WebFetch** | Built-in tools are fastest; muscle memory | Force parallel fan-out FIRST; WebSearch is ONE angle, not all of them |
| **2** | **Skipping the pre-flight** | Rushing to "get results" | `agent-reach doctor --json` takes 5 seconds, changes which platforms are available |
| **3** | **Silently dropping blocked pages** | 403 feels like dead end | Escalate to Scrapling, or flag `[UNREACHABLE]` — never pretend it doesn't exist |
| **4** | **Treating search snippets as primary sources** | Search results feel authoritative | Snippets are search engine paraphrase — verify against original page or flag as `[AR:search]` |
| **5** | **Skipping Phase 4 (Audit)** | Report "feels done" after Verify | Every report MUST have a credibility matrix with at least one 🔴 discarded source |
| **6** | **Single-platform blind spot** | Topic-language/platform mismatch | Chinese topics → 小红书/B站/V2EX; English → Twitter/Reddit; Code → GitHub |
| **7** | **Bare source tags without URLs** | Sloppy output formatting | `[Source Name](URL) [AR:source]` — every tag carries a clickable link |
| **8** | **No discrepancies highlighted** | Taking all sources at equal weight | The value is in what source A has that source B doesn't — call out the diff |
| **9** | **Sequential crawling** | Habit | Scrapling parallelizes 4 URLs; WebSearch + social + code can all fire simultaneously |

---

## Tool Paths

```
Agent-Reach CLI:  agent-reach
Agent-Reach src:  D:/myprogram/Agent-Reach
Scrapling:        python -c "from scrapling import ..."
Scrapling MCP:    scrapling mcp
Obscura:          D:/myprogram/obscura/target/release/obscura
```
