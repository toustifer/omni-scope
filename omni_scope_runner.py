#!/usr/bin/env python3
"""
OmniScope Runner — multi-platform research pipeline.
DeepSeek Harness (dsh) 适配版: 路径/会话可用环境变量覆盖，支持 --doctor 预检与 --json 结构化输出。
Usage:
  python omni_scope_runner.py "your research query"
  python omni_scope_runner.py "query" --platforms twitter,web,bilibili
  python omni_scope_runner.py "query" -n 5 -o report.md
  python omni_scope_runner.py "query" --json          # agent 可解析的结构化结果
  python omni_scope_runner.py --doctor                # 预检各平台后端是否可用
  python omni_scope_runner.py --list-platforms
Env:
  OMNISCOPE_AGENT_REACH      Agent-Reach 源码目录 (默认 D:/myprogram/Agent-Reach)
  OMNISCOPE_OPENCLI_SESSION  OpenCLI 浏览器会话名 (默认 dujdhsts)
"""

import argparse, json, subprocess, sys, os, shutil, re, time, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

AGENT_REACH = os.environ.get("OMNISCOPE_AGENT_REACH", "D:/myprogram/Agent-Reach")
AGENT_REACH_BASH = "/d/myprogram/Agent-Reach"  # Git Bash / MSYS path
OPENCLI_SESSION = os.environ.get("OMNISCOPE_OPENCLI_SESSION", "dujdhsts")


@dataclass
class ScoutResult:
    platform: str
    status: str  # "ok" | "skip" | "error"
    data: list = field(default_factory=list)
    error: str = ""


def run(cmd, timeout=30, cwd=None):
    """Run shell command. Uses cmd.exe with optional working directory."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd, encoding='utf-8', errors='replace')
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def _esc(s):
    """Escape for cmd.exe double-quote context."""
    return s.replace('"', '\\"')


def _has_cjk(s):
    """是否包含中日韩统一表意文字 (CJK)。"""
    return any('\u4e00' <= ch <= '\u9fff' for ch in s)

# ── Platform Scouts ──────────────────────────────────────────


def scout_web_exa(query, n=8):
    """Exa semantic web search."""
    cmd = f'mcporter call exa.web_search_exa query="{query}" numResults={n}'
    out = run(cmd, timeout=30, cwd=AGENT_REACH)
    if not out:
        return ScoutResult("web", "skip", error="Exa search failed")
    return ScoutResult("web", "ok", data=[{"raw": out}])


def scout_twitter_opencli(query, n=8):
    """Twitter via OpenCLI browser bridge (real browser session). Falls back to twitter-cli."""
    encoded = urllib.parse.quote(query)
    run("opencli browser " + OPENCLI_SESSION + " bind", timeout=5)
    r1 = run("opencli browser " + OPENCLI_SESSION + ' open "https://x.com/search?q=' + encoded + '&f=top"', timeout=15)
    if r1 is None:
        # Fallback to twitter-cli
        out = run('cd "' + AGENT_REACH + '" && twitter search "' + query + '" -n ' + str(n), timeout=30)
        return ScoutResult("twitter", "ok", data=[{"raw": out}]) if out else \
               ScoutResult("twitter", "skip", error="Both OpenCLI and twitter-cli failed")

    run('opencli browser ' + OPENCLI_SESSION + ' wait selector "[data-testid=\\"tweet\\"]" timeout 10', timeout=20)

    js_code = (
        "JSON.stringify(Array.from(document.querySelectorAll('[data-testid=\"tweet\"]'))"
        ".slice(0," + str(n) + ").map(t=>({"
        "author: t.querySelector('[data-testid=\"User-Name\"]')?.innerText?.split('@')[0]?.trim()||'',"
        "handle: t.querySelector('[data-testid=\"User-Name\"]')?.innerText?.match(/@\\w+/)?.toString()||'',"
        "text: t.querySelector('[data-testid=\"tweetText\"]')?.innerText||'',"
        "time: t.querySelector('time')?.getAttribute('datetime')||'',"
        "link: t.querySelector('a[href*=\"/status/\"]')?.href||'',"
        "})))"
    )
    out = run('opencli browser ' + OPENCLI_SESSION + ' eval "' + js_code + '"', timeout=15)
    if not out:
        out2 = run('cd "' + AGENT_REACH + '" && twitter search "' + query + '" -n ' + str(n), timeout=30)
        return ScoutResult("twitter", "ok", data=[{"raw": out2}]) if out2 else \
               ScoutResult("twitter", "skip", error="Tweet extraction failed")

    try:
        tweets = json.loads(out)
        return ScoutResult("twitter", "ok", data=tweets)
    except json.JSONDecodeError:
        return ScoutResult("twitter", "ok", data=[{"raw": out}])


def scout_bilibili(query, n=5):
    """B站视频搜索 (output is YAML)."""
    try:
        import yaml
    except ImportError:
        return ScoutResult("bilibili", "skip", error="yaml module missing")
    out = run("bili search " + _esc(query) + " 2>&1", timeout=20, cwd=AGENT_REACH)
    if not out:
        return ScoutResult("bilibili", "skip", error="Bili cmd failed")
    try:
        d = yaml.safe_load(out)
        if not d:
            return ScoutResult("bilibili", "skip", error="Empty output")
        data = d.get("data", [])
        if data and len(data) > 0:
            items = [{"name": v.get("name", ""), "id": str(v.get("id", "")), "fans": v.get("fans", 0), "sign": v.get("sign", "")} for v in data[:n]]
            return ScoutResult("bilibili", "ok", data=items)
        return ScoutResult("bilibili", "skip", error="No B站 results")
    except Exception as e:
        return ScoutResult("bilibili", "skip", error=str(e))


def scout_v2ex(query, n=5):
    """V2EX社区搜索."""
    encoded = urllib.parse.quote(query)
    out = run(
        'curl -s "https://www.v2ex.com/api/v2/search?q=' + encoded + '"'
        ' -H "User-Agent: Mozilla/5.0" 2>&1',
        timeout=15
    )
    if not out or out == "[]":
        return ScoutResult("v2ex", "skip", error="No results")
    return ScoutResult("v2ex", "ok", data=[{"raw": out}])


def scout_github(query, n=5):
    """GitHub仓库搜索（中文查询无结果时降级为保留的 ASCII 词条重试）。"""
    def _search(q):
        return run('gh search repos "' + q + '" --sort stars --limit ' + str(n) + ' 2>&1', timeout=20)

    out = _search(query)
    if not out and _has_cjk(query):
        # gh 对中文查询常返回空 → 去掉 CJK 词条，保留英文产品/模型名重试
        ascii_q = re.sub(r'[\u4e00-\u9fff]+', ' ', query).strip()
        if ascii_q and ascii_q != query:
            out = _search(ascii_q)
    if not out:
        return ScoutResult("github", "skip", error="GitHub search failed (中文查询已尝试 ASCII 降级)")
    return ScoutResult("github", "ok", data=[{"raw": out}])


def scout_youtube(query, n=5):
    """YouTube视频搜索 via yt-dlp."""
    import json
    out = run("yt-dlp --flat-playlist --dump-json \"ytsearch" + str(n) + ":" + _esc(query) + "\" 2>&1", timeout=30)
    if not out or "ERROR" in out:
        return ScoutResult("youtube", "skip", error="YouTube search failed")
    items = []
    for line in out.split("\n"):
        if not line.strip() or not line.startswith("{"):
            continue
        try:
            v = json.loads(line)
            items.append({"title": v.get("title", ""), "url": v.get("webpage_url", "") or v.get("url", ""), "channel": v.get("channel", "") or v.get("uploader", ""), "duration": v.get("duration", 0)})
        except:
            continue
    return ScoutResult("youtube", "ok", data=items) if items else ScoutResult("youtube", "skip", error="No videos")

# ── Pipeline ─────────────────────────────────────────────────



def scout_hn(query, n=8):
    """Hacker News - Algolia API, no key needed."""
    import urllib.request, json
    try:
        url = "https://hn.algolia.com/api/v1/search?query=" + urllib.parse.quote(query) + "&hitsPerPage=" + str(n) + "&tags=story"
        resp = urllib.request.urlopen(url, timeout=15)
        data = json.loads(resp.read())
        items = []
        for h in data.get("hits", []):
            items.append({"title": h.get("title",""), "url": h.get("url",""), "points": h.get("points",0), "author": h.get("author",""), "link": "https://news.ycombinator.com/item?id=" + h.get("objectID","")})
        return ScoutResult("hn", "ok", data=items)
    except Exception as e:
        return ScoutResult("hn", "skip", error=str(e))


def scout_wikipedia(query, n=5):
    """Wikipedia search."""
    import urllib.request, json
    try:
        url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=" + urllib.parse.quote(query) + "&format=json&srlimit=" + str(n)
        req = urllib.request.Request(url, headers={"User-Agent": "OmniScope/1.0 (research tool; contact@example.com)"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        items = []
        for r in data.get("query",{}).get("search",[]):
            title = r.get("title","")
            page_url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ","_"))
            items.append({"title": title, "snippet": r.get("snippet",""), "link": page_url})
        return ScoutResult("wikipedia", "ok", data=items)
    except Exception as e:
        return ScoutResult("wikipedia", "skip", error=str(e))


def scout_arxiv(query, n=5):
    """ArXiv academic papers."""
    import urllib.request, xml.etree.ElementTree as ET
    try:
        url = "https://export.arxiv.org/api/query?search_query=all:" + urllib.parse.quote(query) + "&max_results=" + str(n) + "&sortBy=relevance"
        resp = urllib.request.urlopen(url, timeout=20)
        root = ET.fromstring(resp.read())
        ns = {"a": "http://www.w3.org/2005/Atom"}
        items = []
        for entry in root.findall("a:entry", ns):
            title = entry.find("a:title", ns).text.strip().replace("\n"," ") if entry.find("a:title", ns) is not None else ""
            summary = entry.find("a:summary", ns).text.strip()[:200] if entry.find("a:summary", ns) is not None else ""
            link = entry.find("a:id", ns).text if entry.find("a:id", ns) is not None else ""
            items.append({"title": title, "summary": summary, "link": link})
        return ScoutResult("arxiv", "ok", data=items)
    except Exception as e:
        return ScoutResult("arxiv", "skip", error=str(e))


def scout_reddit(query, n=8):
    """Reddit via OpenCLI browser."""
    import json
    encoded = urllib.parse.quote(query)
    run("opencli browser " + OPENCLI_SESSION + " bind", timeout=5)
    run("opencli browser " + OPENCLI_SESSION + " open 'https://www.reddit.com/search/?q=" + encoded + "&type=link'", timeout=12)
    run("opencli browser " + OPENCLI_SESSION + " wait selector h3", timeout=15)
    js_code = 'JSON.stringify(Array.from(document.querySelectorAll("h3")).slice(0,' + str(8) + ').map(function(n){return n.innerText||""}).filter(Boolean))'
    out = run("opencli browser " + OPENCLI_SESSION + " eval " + chr(34) + js_code + chr(34), timeout=15)
    if not out:
        return ScoutResult("reddit", "skip", error="Reddit failed")
    try:
        items = json.loads(out)
        items = [{"title": t} for t in items if t]
        return ScoutResult("reddit", "ok", data=items) if items else ScoutResult("reddit", "skip", error="No results")
    except Exception as e:
        return ScoutResult("reddit", "skip", error=str(e))

def scout_duckduckgo(query, n=5):
    """DuckDuckGo instant answers."""
    import urllib.request, json
    try:
        url = "https://api.duckduckgo.com/?q=" + urllib.parse.quote(query) + "&format=json&no_html=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (OmniScope)"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        items = []
        if data.get("AbstractText"):
            items.append({"title": data.get("Heading",""), "text": data.get("AbstractText","")[:300], "source": data.get("AbstractSource",""), "link": data.get("AbstractURL","")})
        for topic in data.get("RelatedTopics",[]):
            if "Text" in topic:
                items.append({"text": topic.get("Text","")[:300]})
            if len(items) >= n:
                break
        return ScoutResult("duckduckgo", "ok", data=items) if items else ScoutResult("duckduckgo", "skip", error="No results")
    except Exception as e:
        return ScoutResult("duckduckgo", "skip", error=str(e))


def scout_stackoverflow(query, n=5):
    """Stack Overflow search."""
    import urllib.request, json
    try:
        url = "https://api.stackexchange.com/2.3/search/advanced?q=" + urllib.parse.quote(query) + "&site=stackoverflow&pagesize=" + str(n) + "&order=desc&sort=relevance"
        resp = urllib.request.urlopen(url, timeout=15)
        data = json.loads(resp.read())
        items = [{"title": q.get("title",""), "link": q.get("link",""), "score": q.get("score",0), "answers": q.get("answer_count",0)} for q in data.get("items",[])]
        return ScoutResult("stackoverflow", "ok", data=items) if items else ScoutResult("stackoverflow", "skip", error="No results")
    except Exception as e:
        return ScoutResult("stackoverflow", "skip", error=str(e))



def scout_xiaohongshu(query, n=8):
    """小红书 via OpenCLI browser bridge."""
    import json
    encoded = urllib.parse.quote(query)
    run("opencli browser " + OPENCLI_SESSION + " open \"https://www.xiaohongshu.com/search_result?keyword=" + encoded + "&source=web_search_result_notes\"", timeout=10)
    run("opencli browser " + OPENCLI_SESSION + " wait selector .note-item", timeout=15)
    js = "JSON.stringify(Array.from(document.querySelectorAll('.note-item')).slice(0," + str(n) + ").map(n=>({title:(n.querySelector('.title,.note-title')?.innerText||'').trim(),author:(n.querySelector('.author,.name,.username')?.innerText||'').trim().split('\\n')[0]||'',likes:(n.querySelector('.like-wrapper,.like,.count')?.innerText||'').trim(),link:n.querySelector('a')?.href||'',desc:(n.querySelector('.desc,.note-desc')?.innerText||'').trim()})))"
    out = run("opencli browser " + OPENCLI_SESSION + " eval \"" + js + "\"", timeout=15)
    if not out:
        return ScoutResult("xiaohongshu", "skip", error="小红书 extract failed")
    try:
        items = json.loads(out)
        items = [i for i in items if i.get("title") or i.get("author")]
        return ScoutResult("xiaohongshu", "ok", data=items) if items else ScoutResult("xiaohongshu", "skip", error="No valid notes")
    except json.JSONDecodeError:
        return ScoutResult("xiaohongshu", "skip", error="JSON parse failed")

def scout_zhihu(query, n=8):
    """知乎 - via OpenCLI browser bridge."""
    import json
    encoded = urllib.parse.quote(query)
    run("opencli browser " + OPENCLI_SESSION + " open \"https://www.zhihu.com/search?type=content&q=" + encoded + "\"", timeout=10)
    run("opencli browser " + OPENCLI_SESSION + " wait selector .ContentItem", timeout=15)
    js = "JSON.stringify(Array.from(document.querySelectorAll('.ContentItem')).slice(0," + str(n) + ").map(n=>({title:(n.querySelector('h2')?.innerText||'').trim(),link:n.querySelector('a')?.href||'',excerpt:(n.querySelector('.RichText')?.innerText||'').slice(0,300)})))"
    out = run("opencli browser " + OPENCLI_SESSION + " eval \"" + js + "\"", timeout=15)
    if not out:
        return ScoutResult("zhihu", "skip", error="知乎 extract failed")
    try:
        items = json.loads(out)
        items = [i for i in items if i.get("title")]
        return ScoutResult("zhihu", "ok", data=items) if items else ScoutResult("zhihu", "skip", error="No items")
    except json.JSONDecodeError:
        return ScoutResult("zhihu", "ok", data=[{"raw": out}])

def scout_baike(query, n=5):
    """百度百科 via OpenCLI browser."""
    import json
    encoded = urllib.parse.quote(query)
    # Try direct item page first
    run("opencli browser " + OPENCLI_SESSION + " open \"https://baike.baidu.com/item/" + encoded + "\"", timeout=10)
    run("opencli browser " + OPENCLI_SESSION + " wait selector .mainContent_R5LPd, .para, .J-lemma-content, .J-summary, .body-wrapper", timeout=12)
    js_item = "JSON.stringify({title:document.title,url:location.href,summary:(document.querySelector('.J-summary')?.innerText||document.querySelector('.lemma-summary')?.innerText||document.querySelector('.mainContent_R5LPd .para')?.innerText||document.querySelector('.para')?.innerText||'').slice(0,500)})"
    out = run("opencli browser " + OPENCLI_SESSION + " eval \"" + js_item + "\"", timeout=12)
    if out:
        try:
            d = json.loads(out)
            if d.get("summary") and len(d["summary"]) > 20:
                return ScoutResult("baike", "ok", data=[d])
        except:
            pass
    # Fallback: search page
    run("opencli browser " + OPENCLI_SESSION + " open \"https://baike.baidu.com/s?wd=" + encoded + "\"", timeout=10)
    run("opencli browser " + OPENCLI_SESSION + " wait selector .search-list, .list, .result", timeout=12)
    js_search = "JSON.stringify(Array.from(document.querySelectorAll('.search-list a, .list-item, .result-op')).slice(0," + str(n) + ").map(n=>({title:n.innerText.split('\\n')[0]||'',link:n.href||''})))"
    out = run("opencli browser " + OPENCLI_SESSION + " eval \"" + js_search + "\"", timeout=12)
    if not out:
        return ScoutResult("baike", "skip", error="百度百科 no results")
    try:
        items = json.loads(out)
        items = [i for i in items if i.get("title") and i.get("link")]
        return ScoutResult("baike", "ok", data=items) if items else ScoutResult("baike", "skip", error="No baike results")
    except:
        return ScoutResult("baike", "skip", error="Parse failed")

def scout_weibo(query, n=8):
    """微博 - via OpenCLI browser bridge. Requires user to be logged into weibo.com in their browser."""
    import json
    encoded = urllib.parse.quote(query)
    run("opencli browser " + OPENCLI_SESSION + " open \"https://s.weibo.com/weibo?q=" + encoded + "&xsort=hot\"", timeout=10)
    js_check = "location.href"
    current_url = run("opencli browser " + OPENCLI_SESSION + " eval \"" + js_check + "\"", timeout=8)
    if current_url and "passport" in current_url:
        return ScoutResult("weibo", "skip", error="微博需要在浏览器中登录")
    run("opencli browser " + OPENCLI_SESSION + " wait selector .card-wrap, .weibo-item, [class*=\"Feed_body\"]", timeout=12)
    js = "JSON.stringify(Array.from(document.querySelectorAll('.card-wrap, .weibo-item, [class*=\"Feed_body\"]')).slice(0," + str(n) + ").map(n=>({text:(n.querySelector('.txt, .card-text, [class*=\"Feed_body\"]')?.innerText||n.innerText||'').slice(0,300),author:(n.querySelector('.name, .username, [class*=\"Feed_name\"]')?.innerText||'').trim(),link:n.querySelector('a')?.href||''})))"
    out = run("opencli browser " + OPENCLI_SESSION + " eval \"" + js + "\"", timeout=12)
    if not out:
        return ScoutResult("weibo", "skip", error="微博 no results")
    try:
        items = json.loads(out)
        items = [i for i in items if i.get("text")]
        return ScoutResult("weibo", "ok", data=items) if items else ScoutResult("weibo", "skip", error="微博无内容")
    except:
        return ScoutResult("weibo", "skip", error="Parse failed")

def scout_devto(query, n=5):
    """Dev.to developer articles."""
    import urllib.request, json
    try:
        url = "https://dev.to/api/articles?q=" + urllib.parse.quote(query) + "&per_page=" + str(n)
        req = urllib.request.Request(url, headers={"User-Agent": "OmniScope/1.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        items = [{"title": a.get("title",""), "author": a.get("user",{}).get("name",""), "tags": a.get("tag_list",[]), "url": a.get("url",""), "comments": a.get("comments_count",0), "reactions": a.get("positive_reactions_count",0)} for a in data]
        return ScoutResult("devto", "ok", data=items) if items else ScoutResult("devto", "skip", error="No results")
    except Exception as e:
        return ScoutResult("devto", "skip", error=str(e))

def scout_googlenews(query, n=5):
    """Google News RSS."""
    import urllib.request, xml.etree.ElementTree as ET
    try:
        encoded = urllib.parse.quote(query)
        url = "https://news.google.com/rss/search?q=" + encoded + "&hl=zh-CN&gl=CN"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        root = ET.fromstring(resp.read())
        items = []
        for item in root.findall(".//item")[:n]:
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            source = item.find("source").text if item.find("source") is not None else ""
            items.append({"title": title, "source": source, "link": link})
        return ScoutResult("googlenews", "ok", data=items) if items else ScoutResult("googlenews", "skip", error="No news")
    except Exception as e:
        return ScoutResult("googlenews", "skip", error=str(e))


def scout_36kr(query, n=5):
    import urllib.request, xml.etree.ElementTree as ET
    try:
        req = urllib.request.Request('https://36kr.com/feed')
        r = urllib.request.urlopen(req, timeout=15)
        root = ET.fromstring(r.read())
        items = []
        for item in root.findall('.//item')[:n]:
            t = item.find('title')
            l = item.find('link')
            if t is not None:
                items.append({"title":('' if t is None else t.text)[:200],"link":('' if l is None else l.text)})
        if items: return ScoutResult('36kr','ok',data=items)
        return ScoutResult('36kr','skip',error='No items')
    except Exception as e:
        return ScoutResult('36kr','skip',error=str(e))
PLATFORMS = {
    "web":          ("Exa 语义搜索", scout_web_exa),
    "xiaohongshu": ("小红书", scout_xiaohongshu),
    "zhihu":        ("知乎", scout_zhihu),
    "baike":        ("百度百科", scout_baike),
    "weibo":        ("微博", scout_weibo),
    "devto":        ("Dev.to", scout_devto),
    "googlenews":   ("谷歌新闻", scout_googlenews),
    "36kr":         ("36氪", scout_36kr),
    "twitter":      ("Twitter/X", scout_twitter_opencli),
    "reddit":       ("Reddit", scout_reddit),
    "hn":           ("Hacker News", scout_hn),
    "wikipedia":    ("Wikipedia", scout_wikipedia),
    "arxiv":        ("ArXiv论文", scout_arxiv),
    "duckduckgo":   ("DuckDuckGo", scout_duckduckgo),
    "stackoverflow": ("Stack Overflow", scout_stackoverflow),
    "bilibili":     ("B站视频", scout_bilibili),
    "v2ex":         ("V2EX社区", scout_v2ex),
    "github":       ("GitHub仓库", scout_github),
}


def run_pipeline(query, platforms=None, max_results=8):
    """Run parallel multi-platform scout. Returns dict of platform->ScoutResult."""
    if platforms is None:
        platforms = list(PLATFORMS.keys())

    results = {}
    with ThreadPoolExecutor(max_workers=min(6, len(platforms))) as executor:
        futures = {
            executor.submit(PLATFORMS[p][1], query, max_results): p
            for p in platforms if p in PLATFORMS
        }
        for future in as_completed(futures):
            platform = futures[future]
            try:
                result = future.result()
            except Exception as e:
                result = ScoutResult(platform, "error", error=str(e))
            results[platform] = result
            status_icon = "OK" if result.status == "ok" else "SKIP"
            print(f"  [{status_icon}] {platform}: {result.status} ({len(result.data)} items)", file=sys.stderr)
    return results


def format_report(query, results):
    """Generate Markdown research report."""
    ok_platforms = {p: r for p, r in results.items() if r.status == "ok"}
    skip_platforms = {p: r for p, r in results.items() if r.status != "ok"}

    lines = [
        f"# OmniScope 研究报告: {query}",
        "",
        f"*生成: {time.strftime('%Y-%m-%d %H:%M')} | 平台: {len(ok_platforms)}/{len(results)} 成功*",
        "",
    ]

    if skip_platforms:
        lines.append("## 已跳过平台")
        for p, r in skip_platforms.items():
            lines.append(f"- **{p}**: {r.error}")
        lines.append("")

    lines.append("## 多平台发现")
    lines.append("")
    lines.append("| 平台 | 类型 | 结果数 |")
    lines.append("|------|------|--------|")
    for p, r in ok_platforms.items():
        name = PLATFORMS.get(p, (p,))[0]
        lines.append(f"| {name} | {p} | {len(r.data)} |")

    for p, r in ok_platforms.items():
        name = PLATFORMS.get(p, (p,))[0]
        lines.append(f"")
        lines.append(f"### {name}")
        lines.append("")
        for item in r.data[:10]:
            if isinstance(item, dict) and "text" in item:
                author = item.get("author", "?")
                handle = item.get("handle", "")
                text = item.get("text", "")[:300]
                link = item.get("link", "")
                lines.append(f"- **@{handle}** ({author}): {text}")
                if link:
                    lines.append(f"  {link}")
            elif isinstance(item, dict) and "raw" in item:
                raw = item["raw"]
                if len(raw) > 500:
                    raw = raw[:500] + "..."
                lines.append(f"```\n{raw}\n```")
            else:
                lines.append(f"- {str(item)[:300]}")
        if len(r.data) > 10:
            lines.append(f"\n*...还有 {len(r.data) - 10} 条结果未展示*")

    return "\n".join(lines)


DOCTOR_TOOLS = [
    ("agent-reach", "Agent-Reach CLI (13平台发现)", "bin"),
    ("opencli", "OpenCLI (浏览器桥: Twitter/Reddit/小红书/知乎/微博/百度百科)", "bin"),
    ("mcporter", "mcporter (Exa 语义搜索 MCP)", "bin"),
    ("gh", "GitHub CLI (仓库搜索)", "bin"),
    ("yt-dlp", "yt-dlp (YouTube 搜索)", "bin"),
    ("bili", "bili (B站搜索)", "bin"),
    ("scrapling", "Scrapling Python 库 (反反爬攻坚)", "python"),
    ("curl", "curl (Jina Reader / V2EX)", "bin"),
]


def _backend_ok(cmd, kind):
    """bin → PATH 查找；python → import 检测。"""
    if kind == "python":
        try:
            r = subprocess.run(
                [sys.executable, "-c", "import " + cmd],
                capture_output=True, timeout=15,
            )
            return r.returncode == 0, None
        except Exception:
            return False, None
    path = shutil.which(cmd)
    return path is not None, path


def run_doctor():
    """Pre-flight: 检查各平台后端是否可用 (DSH 启动调研前调用)。"""
    print("OmniScope Doctor — 平台后端检查\n")
    rows = []
    for cmd, desc, kind in DOCTOR_TOOLS:
        ok, where = _backend_ok(cmd, kind)
        rows.append((cmd, ok))
        status = "OK" if ok else "XX"
        if ok and kind == "bin":
            note = f" -> {where}"
        elif ok:
            note = "  (python 库已安装)"
        else:
            note = "  (未安装，对应平台将 [SKIP])"
        print(f"  [{status}] {cmd:12s} {desc}{note}")
    print(f"\n  Agent-Reach src : {AGENT_REACH} (存在: {os.path.isdir(AGENT_REACH)})")
    print(f"  OpenCLI session : {OPENCLI_SESSION}")
    missing = [cmd for cmd, ok in rows if not ok]
    if missing:
        print(f"\n⚠ 缺失 {len(missing)} 个后端: {', '.join(missing)} — 对应平台会被 [SKIP]，不影响其余平台")
    else:
        print("\n✅ 全部后端就绪")


def main():
    parser = argparse.ArgumentParser(
        description="OmniScope - 多平台研究管线",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python omni_scope_runner.py "Bybit 注册教程"
  python omni_scope_runner.py "AI 最新进展" -p twitter,web,github
  python omni_scope_runner.py "react 19" --output report.md
        """
    )
    parser.add_argument("query", nargs="?", default="", help="搜索关键词")
    parser.add_argument("--platforms", "-p", help="逗号分隔的平台列表 (默认:全部)")
    parser.add_argument("--max-results", "-n", type=int, default=8, help="每平台最大结果数")
    parser.add_argument("--output", "-o", help="输出Markdown文件路径")
    parser.add_argument("--list-platforms", action="store_true", help="列出可用平台")
    parser.add_argument("--doctor", action="store_true", help="预检各平台后端是否可用")
    parser.add_argument("--json", dest="as_json", action="store_true", help="以 JSON 输出结构化结果 (供 agent 解析)")

    args = parser.parse_args()

    if args.doctor:
        run_doctor()
        return

    if args.list_platforms:
        print("可用平台:")
        for k, (name, _) in PLATFORMS.items():
            print(f"  {k:12s} {name}")
        return

    platforms = args.platforms.split(",") if args.platforms else None
    if platforms:
        unknown = [p for p in platforms if p not in PLATFORMS]
        if unknown:
            print(f"未知平台: {unknown}", file=sys.stderr)
            print(f"可用: {list(PLATFORMS.keys())}", file=sys.stderr)
            sys.exit(1)

    print(f"\nOmniScope: {args.query}", file=sys.stderr)
    print(f"平台: {platforms or list(PLATFORMS.keys())}\n", file=sys.stderr)

    start = time.time()
    results = run_pipeline(args.query, platforms, args.max_results)
    elapsed = time.time() - start

    ok_count = sum(1 for r in results.values() if r.status == "ok")
    print(f"\n耗时 {elapsed:.1f}s | {ok_count}/{len(results)} 平台成功\n", file=sys.stderr)

    report = format_report(args.query, results)

    if args.as_json:
        payload = {
            "query": args.query,
            "elapsed_s": round(elapsed, 1),
            "ok_platforms": ok_count,
            "total_platforms": len(results),
            "results": {
                p: {"status": r.status, "error": r.error, "data": r.data}
                for p, r in results.items()
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"报告已保存: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
