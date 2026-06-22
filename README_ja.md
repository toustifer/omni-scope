<h1 align="center">🔭 OmniScope · オムニスコープ</h1>

<p align="center">
  <strong>3つのツール、1つのパイプライン。Claude Code のための最も包括的なインターネット調査 Agent Skill。</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-skill-6C47FF?style=for-the-badge&logo=anthropic" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/プラットフォーム-13-00C853?style=for-the-badge" alt="13 Platforms">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <a href="README.md">中文</a> · <a href="README_en.md">English</a>
</p>

---

## OmniScope とは？

OmniScope は、3つの最高峰オープンソースツールを1つのシームレスな Agent Skill に統合する **3段階の調査パイプライン** です：

```
                    ┌──────────────────┐
                    │    🔭 OmniScope   │
                    │    全視調査エンジン │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   🔭 発見                ⛏️ 抽出               🔍 検証
  Agent-Reach           Scrapling            Obscura
  13プラットフォーム     アンチボット+         クロスリファレンス
  で情報収集             適応型パース          +信頼性スコア
```

| 段階 | ツール | 役割 |
|------|------|------|
| **発見** | [Agent-Reach](https://github.com/Panniantong/Agent-Reach) | 13チャンネルのマルチプラットフォーム並行発見（Twitter、Reddit、GitHub、YouTube、Bilibili、小紅書、V2EX…） |
| **抽出** | [Scrapling](https://github.com/D4Vinci/Scrapling) | アンチボット防御の突破 + サイト改版に強い適応型パース |
| **検証** | [Obscura](https://github.com/h4ckf0r0day/obscura) / deep-research 方法論 | 生ページクロール→検索サマリーと比較→矛盾を指摘→信頼性スコア |

## なぜ OmniScope なのか？

**課題：** AIエージェントはウェブ検索だけに頼りがちで、ソーシャルメディアの生の議論、コードリポジトリ、動画コンテンツを見逃します。クローリングを試みてもブロックされ、矛盾する情報を検証する能力がありません。

**解決策：** OmniScope は完全なインテリジェンスサイクルを自動化——プラットフォームを横断して広く網を張り、防御を突破して一次データを取得し、すべての主張を一次ソースとクロス検証します。

## クイックスタート

```bash
# OmniScope スキルをインストール
git clone https://github.com/toustifer/omni-scope.git ~/.claude/skills/omni-scope

# Claude Code で使用：
/omni-scope "XXXについて徹底調査して"
```

### 前提条件

OmniScope は3つの基盤ツールに依存します。各1回インストールすれば完了です：

```bash
# 1. Scrapling — アンチボット+適応型パース
pip install scrapling[fetchers,ai,shell]
playwright install chromium

# 2. Agent-Reach — 13プラットフォーム発見
git clone https://github.com/Panniantong/Agent-Reach.git
cd Agent-Reach && pip install -e ".[all]"

# 3. Obscura — 生ページクロール検証
cd your-path/obscura && cargo build --release
```

インストール後、`agent-reach doctor --json` で各プラットフォームの状態を確認してください。

## ソースタグ体系

| タグ | 意味 |
|------|------|
| `[AR:web]` | Agent-Reach Jina Reader |
| `[AR:social]` | Twitter / Reddit / 小紅書 / Bilibili / V2EX |
| `[AR:code]` | GitHub 検索 |
| `[AR:video]` | YouTube / Bilibili 字幕 |
| `[SP:stealth]` | Scrapling StealthyFetcher（アンチボット突破） |
| `[SP:dynamic]` | Scrapling DynamicFetcher（JSレンダリング） |
| `[OB]` | Obscura 生クロール |
| `[AR→SP]` | クロスツール検証済み |

## 対応プラットフォーム

| カテゴリ | プラットフォーム |
|----------|------------------|
| **ソーシャル（海外）** | Twitter/X、Reddit |
| **ソーシャル（中国）** | 小紅書（ベータ）、Bilibili、V2EX |
| **コード** | GitHub |
| **動画** | YouTube、Bilibili |
| **検索** | Exa（意味検索）、Jina Reader（ウェブ） |
| **コンテンツ** | RSS、任意のウェブページ |

---

## 🙏 謝辞

OmniScope は3つの卓越したオープンソースプロジェクトの上に成り立っています：

- **[Agent-Reach](https://github.com/Panniantong/Agent-Reach)** by [Neo Reid](https://github.com/Panniantong) — **発見層**：13プラットフォームのゼロコンフィグアクセスと自動バックエンドフェイルオーバー。

- **[Scrapling](https://github.com/D4Vinci/Scrapling)** by [Karim Shoair](https://github.com/D4Vinci) — **抽出層**：BeautifulSoup 比774倍高速、Cloudflare 突破、適応型セレクタ、MCPサーバー内蔵。

- **[Obscura](https://github.com/h4ckf0r0day/obscura)** & deep-research 方法論 — **検証層**：軽量クロール（30MBフットプリント）によるグラウンドトゥルース検証。

---

## ライセンス

MIT — オープンソースコミュニティへの感謝を込めて。
