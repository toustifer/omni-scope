---
name: omni-scope
description: >
  跨平台深度调研 pipeline：Scout 撒网（13+ 平台）→ Extract 攻坚（反反爬）→ Verify 验证 → Audit 审计。
  当用户要求全网调研/深度调研/全面调研/跨平台研究/multi-source investigation 时使用。
whenToUse: >
  触发词：全网调研, 深度调研, 全面调研, 跨平台研究, 全平台搜索, omni, omni-scope,
  所有平台都搜一下, 多平台对比, 深度对比, find everything about X,
  cross-platform research, "check this across Twitter Reddit and GitHub"。
  适用：需要跨 web + 社交 + 视频 + 代码平台的广度发现、需要穿透反爬/JS 站点、
  需要把搜索摘要与一手原始来源交叉验证的高置信调研。
  不适用：单一平台查询（直接用 agent-reach skill）、简单网页读取（agent-reach web 通道）、
  无验证需求的一次性 URL 抓取。
---

# OmniScope — 全视研究

Three tools, one pipeline. **Scout** (Agent-Reach) discovers across 13 platforms. **Extract** (Scrapling) penetrates defenses. **Verify** cross-references and scores reliability. **Audit** flags untrustworthy sources.

---

## 🖥️ DeepSeek Harness (DSH) 适配版

本分支（`deepseekdsh`）把 OmniScope 适配为 **DeepSeek Harness skill 插件**。DSH 从 `~/.agents/skills/<name>/SKILL.md` 加载 skill（也支持项目级 `.dsh/skills`、`.agents/skills` 与 `$DSH_HOME/skills`），frontmatter 使用 DSH 的 `name` / `description` / `whenToUse` 字段（无 Claude 专属 `triggers`）。

```powershell
# 安装（Windows，Git Bash 用户改用 ~/.agents/skills/omni-scope）
git clone -b deepseekdsh https://github.com/toustifer/omni-scope.git $env:USERPROFILE\.agents\skills\omni-scope
cd $env:USERPROFILE\.agents\skills\omni-scope

# 预检：检查各平台后端是否可用
python omni_scope_runner.py --doctor

# 实测查询（按需指定平台，输出 JSON 便于 agent 解析）
python omni_scope_runner.py "你的调研主题" -p web,github,hn,wikipedia —json

# 传统用法
python omni_scope_runner.py "你的调研主题" -p twitter,web,github -n 8 -o report.md
```

runner 环境变量（默认值与旧版硬编码一致）：

| 变量 | 默认 | 作用 |
|------|------|------|
| `OMNISCOPE_AGENT_REACH` | `D:/myprogram/Agent-Reach` | Agent-Reach 源码目录（mcporter / twitter / bili 在其中的工作目录） |
| `OMNISCOPE_OPENCLI_SESSION` | `dujdhsts` | OpenCLI 浏览器会话名（Twitter/Reddit/小红书/知乎/微博/百度百科走真实浏览器） |

在 DSH 中直接对模型说"帮我全网调研 X"即可触发本 skill；模型按下方 pipeline 执行（scout→extract→verify→audit），可调用 `pwsh` 工具运行 runner，或按 Phase 1 表逐平台并行执行。

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
│  □ 4. NEVER default to one web search alone — that's single-angle │
│  □ 5. If a platform backend is DOWN → skip it, log `[SKIP]`    │
│  □ 6. Minimum 3 platforms SUCCEED before moving to Phase 2      │
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
│  Built-in fetch 403 → Scrapling StealthyFetcher                 │
│  Built-in fetch 402 → Mark PAYWALLED, move on                   │
│  Page is blank/<div id="app"> → Scrapling DynamicFetcher      │
│  Search snippet only → NOT a primary source, flag it          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚫 ANTI-PATTERN #1 — Defaulting to a single built-in web search

**This is the most common failure mode.** Your muscle memory will reach for the built-in web search/fetch tools (`web_search` in DeepSeek Harness, `WebSearch`/`WebFetch` in Claude Code) because they're fast and need no setup. RESIST THIS.

Why it fails:
- A built-in web search covers ONE angle (search engine index). Social conversation, code repos, video transcripts, and anti-bot pages are all invisible to it.
- A built-in fetcher silently gives up on Cloudflare-protected pages. You get 403 and move on, losing the most valuable sources.
- Search snippets are the search engine's paraphrase, NOT the original page. They can be outdated, decontextualized, or flat wrong.

**The fix**: After the pre-flight checklist, your FIRST action should be a parallel fan-out across 3+ platforms. The built-in web search can be ONE of them — not all of them.

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
│ 1. SCOUT: Agent-Reach / built-in web search / gh / yt-dlp │
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
| Web search | Exa | `mcporter call 'exa.web_search_exa(query: "Q", numResults: 8)'` |
| Social (EN) | Twitter | **Primary:** OpenCLI browser bridge. See `twitter-browser.md` below. **Fallback:** `twitter search "Q" -n 10` |
| Social (EN) | Reddit | `opencli reddit search "Q"` / `rdt-cli search "Q"` |
| Social (CN) | 小红书, B站, V2EX | `opencli xiaohongshu search "Q"` / `bili search "Q"` |
| Code | GitHub | `gh search repos "Q" --sort stars --limit 10` |
| Video | YouTube, B站 | `youtube transcript "VIDEO_ID"` / `bili search "Q"` |
| Web pages | Jina Reader | `curl -s "https://r.jina.ai/URL"` |

**Twitter via OpenCLI Browser Bridge (no cookie/API issues):**
```bash
# Step 1: Open search page in existing browser session (use doctor output for session name)
opencli browser SESSION open "https://x.com/search?q=URL_ENCODED_QUERY&f=top"

# Step 2: Wait for tweets to load
opencli browser SESSION wait selector "[data-testid=\"tweet\"]" timeout 10

# Step 3: Extract structured data
opencli browser SESSION eval "
JSON.stringify(Array.from(document.querySelectorAll('[data-testid=\"tweet\"]')).slice(0,N).map(t=>({
  author: t.querySelector('[data-testid=\"User-Name\"]')?.innerText?.split('@')[0]?.trim()||'',
  handle: t.querySelector('[data-testid=\"User-Name\"]')?.innerText?.match(/@\w+/)?.toString()||'',
  text: t.querySelector('[data-testid=\"tweetText\"]')?.innerText||'',
  time: t.querySelector('time')?.getAttribute('datetime')||'',
  link: t.querySelector('a[href*=\"/status/\"]')?.href||'',
})))"
```

Collect 5-15 candidate URLs/sources across all platforms.

### Platform Resilience: Handle Backend Failures Gracefully

**When a platform backend returns an error (exit code non-zero, API unavailable, rate limited), do NOT block the entire pipeline.** Log it and move on:

```
Error patterns to recognize as SKIP-worthy:
  "Twitter API temporarily unavailable" → [SKIP:twitter]
  "opencli: command not found"          → [SKIP:reddit]
  "bili search" returns empty           → [SKIP:bilibili]
  "xiaohongshu status: off"             → [SKIP:xiaohongshu]
  Any exit code ≠ 0 from agent-reach    → [SKIP:platform_name]
```

**Rules:**
1. If a platform fails, log `[SKIP:platform] — <reason>` and **immediately move on**
2. Do NOT retry the same platform in the same turn — wasted time
3. Do NOT wait for failed platforms before starting Phase 2 — proceed with what you have
4. The minimum gate is **3 successful platforms** (not 3 attempted)
5. If fewer than 3 platforms succeed after the first fan-out, try 1-2 alternative platforms not in the original batch
6. In the final report, note skipped platforms: `已跳过: Twitter (API 不可用), Reddit (CLI 未安装)`

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

When a built-in page fetch (or `WebFetch` in Claude) fails, don't silently skip — escalate:

```
Fetch result?
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
| **1** | **Defaulting to a single built-in web search** | Built-in tools are fastest; muscle memory | Force parallel fan-out FIRST; built-in search is ONE angle, not all of them |
| **2** | **Skipping the pre-flight** | Rushing to "get results" | `agent-reach doctor --json` takes 5 seconds, changes which platforms are available |
| **3** | **Silently dropping blocked pages** | 403 feels like dead end | Escalate to Scrapling, or flag `[UNREACHABLE]` — never pretend it doesn't exist |
| **4** | **Treating search snippets as primary sources** | Search results feel authoritative | Snippets are search engine paraphrase — verify against original page or flag as `[AR:search]` |
| **5** | **Skipping Phase 4 (Audit)** | Report "feels done" after Verify | Every report MUST have a credibility matrix with at least one 🔴 discarded source |
| **6** | **Single-platform blind spot** | Topic-language/platform mismatch | Chinese topics → 小红书/B站/V2EX; English → Twitter/Reddit; Code → GitHub |
| **7** | **Bare source tags without URLs** | Sloppy output formatting | `[Source Name](URL) [AR:source]` — every tag carries a clickable link |
| **8** | **No discrepancies highlighted** | Taking all sources at equal weight | The value is in what source A has that source B doesn't — call out the diff |
| **9** | **Sequential crawling** | Habit | Scrapling parallelizes 4 URLs; web search + social + code can all fire simultaneously |
| **10** | **Blocking on one failed backend** | One platform errors → entire scout stalls | Log `[SKIP:platform]`, move on immediately; gate is 3 SUCCEEDED, not 3 attempted |

---

## Tool Paths

```
Agent-Reach CLI:  agent-reach
Agent-Reach src:  D:/myprogram/Agent-Reach (env: OMNISCOPE_AGENT_REACH)
Scrapling:        python -c "from scrapling import ..."
Scrapling MCP:    scrapling mcp
Obscura:          D:/myprogram/obscura/target/release/obscura
OmniScope (DSH):  $env:USERPROFILE/.agents/skills/omni-scope
Runner:           python omni_scope_runner.py "query" -p twitter,web,github -n 8 [--json|--doctor]
OpenCLI session:  dujdhsts (env: OMNISCOPE_OPENCLI_SESSION)
```
