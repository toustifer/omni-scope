# 🔭 OmniScope · DeepSeek Harness (DSH) 适配版

> 分支 `deepseekdsh` — 把 OmniScope 从 Claude Code skill 适配为 **DeepSeek Harness skill 插件**。

## 与 master（Claude 版）的差异

| 维度 | master (Claude) | deepseekdsh (DSH) |
|------|-----------------|-------------------|
| frontmatter | `name` + `description` + Claude 专属 `triggers` | DSH 格式 `name` + `description` + `whenToUse` |
| 安装路径 | `~/.claude/skills/omni-scope` | `~/.agents/skills/omni-scope`（或项目 `.dsh/skills`、`$DSH_HOME/skills`） |
| 工具措辞 | 内置 `WebSearch`/`WebFetch` | 泛化 + 点名 DSH `web_search` 工具 |
| runner | 路径/会话硬编码 | 环境变量可覆盖 + `--doctor` 预检 + `--json` 结构化输出 |
| 文档 | README.md / README_en.md / README_ja.md | 新增 README.dsh.md |

DSH 的 skill 加载器（`@deepseek-ai/dsh-skill-filesystem`）按以下根目录发现 skill：
`<workspace>/.dsh/skills`、`<workspace>/.agents/skills`、`$DSH_HOME/skills`、`$DSH_AGENTS_HOME 或 ~/.agents/skills`。

## 安装（Windows / PowerShell）

```powershell
# 方式 A：全新 clone 到 DSH 的 skill 目录
git clone -b deepseekdsh https://github.com/toustifer/omni-scope.git $env:USERPROFILE\.agents\skills\omni-scope

# 方式 B：已有副本切到该分支
git -C $env:USERPROFILE\.agents\skills\omni-scope fetch origin
git -C $env:USERPROFILE\.agents\skills\omni-scope checkout deepseekdsh
```

装好后在 DSH 会话里直接说“帮我全网调研 X”，模型会自动加载本 skill。

## 使用

### 1. 预检（每次大调研前）

```powershell
python $env:USERPROFILE\.agents\skills\omni-scope\omni_scope_runner.py --doctor
```

输出各平台后端（agent-reach / opencli / mcporter / gh / yt-dlp / bili / scrapling / curl）的可用状态；
缺失的后端对应平台会被 `[SKIP]`，其余照常跑。

### 2. 单次调研

```powershell
# 传统 Markdown 报告
python omni_scope_runner.py "调研主题" -p twitter,web,github -n 8 -o report.md

# agent 友好：JSON 结构化结果（stdout 只有 JSON，进度走 stderr）
python omni_scope_runner.py "调研主题" -p web,github,hn,wikipedia --json

# 全部平台
python omni_scope_runner.py "调研主题"
```

### 3. 平台列表

```powershell
python omni_scope_runner.py --list-platforms
```

## 环境变量

| 变量 | 默认 | 作用 |
|------|------|------|
| `OMNISCOPE_AGENT_REACH` | `D:/myprogram/Agent-Reach` | Agent-Reach 源码目录（mcporter / twitter / bili 的 cwd） |
| `OMNISCOPE_OPENCLI_SESSION` | `dujdhsts` | OpenCLI 浏览器会话名 |

## 底层依赖

与 master 相同：Agent-Reach（13 平台发现）、Scrapling（反反爬）、Obscura（验证），
另需 `opencli`、`mcporter`、`gh`、`yt-dlp`、`bili`、`curl`。用 `--doctor` 一键核对。