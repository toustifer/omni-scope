<h1 align="center">🔭 OmniScope</h1>

<p align="center">
  <strong>Three tools, one pipeline. The most comprehensive internet research Agent Skill for Claude Code.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-skill-6C47FF?style=for-the-badge&logo=anthropic" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/platforms-13-00C853?style=for-the-badge" alt="13 Platforms">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">中文</a> · <a href="README_ja.md">日本語</a>
</p>

---

## What is OmniScope?

OmniScope is a **3-phase research pipeline** that orchestrates three best-in-class open-source tools into one seamless Agent Skill:

```
                    ┌──────────────────┐
                    │    🔭 OmniScope   │
                    │   Research Engine │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   🔭 Scout             ⛏️ Extract            🔍 Verify
  Agent-Reach           Scrapling            Obscura
  13-platform           Anti-bot +           Cross-ref +
  discovery             adaptive parse       reliability
```

| Phase | Tool | Role |
|-------|------|------|
| **Scout** | [Agent-Reach](https://github.com/Panniantong/Agent-Reach) | Multi-platform discovery across 13 channels (Twitter, Reddit, GitHub, YouTube, B站, 小红书, V2EX…) |
| **Extract** | [Scrapling](https://github.com/D4Vinci/Scrapling) | Penetrate anti-bot defenses + adaptive parsing that survives site redesigns |
| **Verify** | [Obscura](https://github.com/h4ckf0r0day/obscura) / deep-research methodology | Cross-reference search summaries against raw primary sources, flag discrepancies, score reliability |

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
# 1. Scrapling — Anti-bot + adaptive parsing
pip install scrapling[fetchers,ai,shell]
playwright install chromium

# 2. Agent-Reach — 13-platform discovery
git clone https://github.com/Panniantong/Agent-Reach.git
cd Agent-Reach && pip install -e ".[all]"

# 3. Obscura — Raw page crawling for verification
cd your-path/obscura && cargo build --release
```

Run `agent-reach doctor --json` to see which platforms are available, then configure as needed.

## Source Tags

| Tag | Meaning |
|------|------|
| `[AR:web]` | Agent-Reach Jina Reader |
| `[AR:social]` | Twitter / Reddit / 小红书 / B站 / V2EX |
| `[AR:code]` | GitHub search |
| `[AR:video]` | YouTube / B站 transcript |
| `[SP:stealth]` | Scrapling StealthyFetcher (anti-bot bypass) |
| `[SP:dynamic]` | Scrapling DynamicFetcher (JS-rendered pages) |
| `[OB]` | Obscura raw crawl |
| `[AR→SP]` | Cross-tool verified |

---

## 🙏 Acknowledgments

OmniScope stands on the shoulders of three incredible open-source projects:

- **[Agent-Reach](https://github.com/Panniantong/Agent-Reach)** by [Neo Reid](https://github.com/Panniantong) — The scout layer: zero-config multi-platform access with automatic backend failover across 13 platforms.

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** by [Karim Shoair](https://github.com/D4Vinci) — The extract layer: 774x faster than BeautifulSoup, Cloudflare bypass, adaptive selectors, built-in MCP server.

- **[Obscura](https://github.com/h4ckf0r0day/obscura)** & deep-research methodology — The verify layer: lightweight raw page crawling (30MB footprint) for ground-truth cross-referencing.

---

## License

MIT — Built with gratitude to the open-source community.
