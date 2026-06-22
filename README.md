<h1 align="center">🔭 OmniScope</h1>

<p align="center">
  <strong>Three tools, one pipeline. The most comprehensive internet research Agent Skill.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-skill-6C47FF?style=for-the-badge&logo=anthropic" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/platforms-13-00C853?style=for-the-badge" alt="13 Platforms">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="MIT License">
</p>

---

## What is OmniScope?

OmniScope is a **3-phase research pipeline** that orchestrates three best-in-class open-source tools into one seamless Agent Skill:

```
                    ┌──────────────────┐
                    │    🔭 OmniScope   │
                    │    全视研究引擎    │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   🔭 Scout             ⛏️ Extract            🔍 Verify
  Agent-Reach           Scrapling           deep-research
  13 platforms          Anti-bot +          Cross-ref +
  discovery             adaptive parse      reliability
```

| Phase | Tool | Role |
|-------|------|------|
| **Scout** | [Agent-Reach](https://github.com/Panniantong/Agent-Reach) | Multi-platform discovery across 13 channels (Twitter, Reddit, GitHub, YouTube, B站, 小红书, V2EX…) |
| **Extract** | [Scrapling](https://github.com/D4Vinci/Scrapling) | Penetrate anti-bot defenses + adaptive parsing that survives site redesigns |
| **Verify** | [Obscura](https://github.com/) / deep-research methodology | Cross-reference search summaries against raw primary sources, flag discrepancies, score reliability |

## Why OmniScope?

**The Problem:** AI agents default to web search only, missing candid social discussions, code repositories, and video content. When they do scrape, they get blocked. When they find conflicting info, they can't verify.

**The Solution:** OmniScope automates the full intelligence cycle — cast a wide net across platforms, penetrate defenses to get ground-truth data, then cross-verify every claim against primary sources.

## Quick Start

```bash
# Install OmniScope skill
git clone https://github.com/toustifer/omni-scope.git ~/.claude/skills/omni-scope

# Then in Claude Code:
/omni-scope "research X across all platforms"
```

### Prerequisites

OmniScope requires all three underlying tools. Install each once:

```bash
# 1. Scrapling
pip install scrapling[fetchers,ai,shell]
playwright install chromium

# 2. Agent-Reach
git clone https://github.com/Panniantong/Agent-Reach.git
cd Agent-Reach && pip install -e ".[all]"

# 3. Obscura
cd D:/myprogram/obscura && cargo build --release
```

Run `agent-reach doctor --json` to see which platforms are available, then configure as needed.

## Research Output Example

Every claim is tagged with its origin:

```
## OmniScope 研究报告: Xiaohongshu Scraping Methods

### 多平台发现
| 平台 | 关键发现 | 来源 |
|------|---------|------|
| GitHub | Spider_XHS 6.5k⭐ | [AR:code] |
| Reddit | XHS anti-bot stricter than Twitter | [AR:social] |
| Twitter | Scrapling recommended for stealth | [AR:social] |

### 深度验证
> [Scrapling/Obscura 抓取的原文段落]

#### 差异标记
- ✅ 多源一致: Residential proxies required
- ⚠️ WebSearch 遗漏: Signatures change monthly

### 可靠性矩阵
| 来源 | 可靠性 | 理由 |
|------|--------|------|
| GitHub repo | 最高 | Open source, auditable |
| Social media | 中 | Needs cross-validation |
| Search snippet | 低 | Missing context |
```

## Source Tags

| Tag | Meaning |
|-----|---------|
| `[AR:web]` | Agent-Reach Jina Reader |
| `[AR:social]` | Twitter / Reddit / 小红书 / B站 / V2EX |
| `[AR:code]` | GitHub search |
| `[AR:video]` | YouTube / B站 transcript |
| `[SP:stealth]` | Scrapling StealthyFetcher (anti-bot) |
| `[SP:dynamic]` | Scrapling DynamicFetcher (JS-rendered) |
| `[OB]` | Obscura raw crawl |
| `[AR→SP]` | Cross-tool verified |

## Supported Platforms

| Category | Platforms |
|----------|-----------|
| **Social (EN)** | Twitter/X, Reddit |
| **Social (CN)** | 小红书 (BETA), B站, V2EX |
| **Code** | GitHub |
| **Video** | YouTube, B站 |
| **Search** | Exa (semantic), Jina Reader (web) |
| **Content** | RSS, Web pages |

---

## 🙏 Acknowledgments

OmniScope stands on the shoulders of three incredible open-source projects:

### 🔭 [Agent-Reach](https://github.com/Panniantong/Agent-Reach) — by [Neo Reid](https://github.com/Panniantong)

> "Give your AI Agent eyes to see the entire internet."

Agent-Reach is the **scout layer** — it handles the hard problem of routing across 13 platforms with multi-backend failover. When yt-dlp gets blocked by B站, Agent-Reach silently switches to bili-cli. When Reddit's anonymous API dies, it routes through rdt-cli. This is the kind of infrastructure work that saves agents from platform fragmentation hell.

**Why we chose it:** No other tool provides zero-config multi-platform access with automatic backend failover. The `agent-reach doctor` diagnostic system makes platform health transparent.

### 🕷️ [Scrapling](https://github.com/D4Vinci/Scrapling) — by [Karim Shoair](https://github.com/D4Vinci)

> "An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl."

Scrapling is the **extract layer** — when normal fetchers get blocked, Scrapling's StealthyFetcher bypasses Cloudflare Turnstile. When sites change their layout, its adaptive Selector automatically relocates elements. With 65k+ GitHub stars, it's the fastest-growing scraping framework in open source.

**Why we chose it:** 774x faster than BeautifulSoup for text extraction, built-in MCP server for AI integration, and the only framework that combines anti-bot evasion with adaptive parsing in one package.

### 📡 [Obscura](https://github.com/) & deep-research methodology

> Ground-truth verification through raw page crawling.

The **verify layer** — Obscura crawls pages at the HTTP level (30MB footprint, no browser overhead), providing raw ground-truth content to cross-check against search engine summaries. The deep-research methodology ensures every claim carries an explicit source tag and reliability score.

**Why we chose it:** Search snippets omit critical context. Obscura's lightweight footprint enables parallel crawling of 4+ URLs simultaneously, making verification fast and thorough.

---

## License

MIT — Built with gratitude to the open-source community.

---

<p align="center">
  <sub>If OmniScope helps your research, ⭐ the three projects it depends on.</sub>
</p>
