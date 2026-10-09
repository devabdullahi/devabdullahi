"""Builds dark_mode.svg / light_mode.svg for the GitHub profile README.
Run with ACCESS_TOKEN set (a GitHub token with read:user + repo) to pull live stats."""
import os, json, html, datetime, urllib.request

USER = "devabdullahi"
TOKEN = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")

def gql(query, variables=None):
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if "errors" in out: raise RuntimeError(out["errors"])
    return out["data"]

def fetch_stats():
    d = gql("""query($login:String!){ user(login:$login){
        createdAt followers{totalCount}
        repositories(ownerAffiliations:OWNER, first:100){ totalCount nodes{ stargazerCount } }
        repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY], includeUserRepositories:true){ totalCount }
        contributionsCollection{ contributionYears } } }""", {"login": USER})["user"]
    commits = 0
    for y in d["contributionsCollection"]["contributionYears"]:
        c = gql("""query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){
            contributionsCollection(from:$from,to:$to){ totalCommitContributions restrictedContributionsCount } } }""",
            {"login": USER, "from": f"{y}-01-01T00:00:00Z", "to": f"{y}-12-31T23:59:59Z"})
        cc = c["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    return dict(created=d["createdAt"][:10], followers=d["followers"]["totalCount"],
                repos=d["repositories"]["totalCount"],
                stars=sum(n["stargazerCount"] for n in d["repositories"]["nodes"]),
                contributed=d["repositoriesContributedTo"]["totalCount"], commits=commits)

def uptime(since):
    a = datetime.date.fromisoformat(since); b = datetime.date.today()
    y = b.year - a.year; m = b.month - a.month; d = b.day - a.day
    if d < 0:
        m -= 1
        prev = (b.replace(day=1) - datetime.timedelta(days=1))
        d += prev.day
    if m < 0: y -= 1; m += 12
    s = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return f"{s(y,'year')}, {s(m,'month')}, {s(d,'day')}"

def build(st, freeze=None):
    """freeze=i renders message i statically (for previews); None = animated."""
    art = open("cat.txt").read().split("\n")
    f = lambda n: f"{n:,}"
    msgs = [
        ("meow! welcome to abdullahi's github.", "make yourself at home and look around."),
    ]
    BW = 46                      # bubble inner width (chars)
    SEC = 4                      # seconds per message
    total = SEC * len(msgs)
    term = [
        [("prompt", "~ $ "), ("cmd", "cat ~/.profile")],
        [("key", "name"), ("cc", " ........ "), ("value", "Abdullahi Khalafalla")],
        [("key", "now"), ("cc", " ......... "), ("value", "AI Software Engineer Intern @ IBM")],
        [("key", "prev"), ("cc", " ........ "), ("value", "Apple (Siri) · Ford (FordPass)")],
        [("key", "school"), ("cc", " ...... "), ("value", "B.S. Computer Science @ UT Arlington")],
        [("key", "email"), ("cc", " ....... "), ("value", "abdulahikhalafalla@gmail.com")],
        [],
        [("prompt", "~ $ "), ("cursor", "\u2588")],
    ]
    themes = {
        "dark":  dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f", prompt="#3fb950", bubble="#e6edf3"),
        "light": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", cc="#8c959f", prompt="#1a7f37", bubble="#1f2328"),
    }
    LH, ALH, TOP, ART_X, X, WPX = 20, 12, 26, 18, 392, 985
    H = TOP + max(len(art) * ALH, 23 * LH)
    BY = TOP + 70                # bubble top (tail lines up with the cat's face)
    TY = BY + 5 * LH + 28        # terminal top
    for name, t in themes.items():
        css = (f'.key{{fill:{t["key"]};}}.value{{fill:{t["value"]};}}.cc{{fill:{t["cc"]};}}'
               f'.prompt{{fill:{t["prompt"]};}}.cmd{{fill:{t["text"]};}}.bubble{{fill:{t["bubble"]};}}'
               'text,tspan{white-space:pre;}')
        if freeze is None:
            css += (f'.type{{clip-path:inset(0 100% 0 0);animation:type 2.5s steps({BW}) 0.6s forwards;}}'
                    '@keyframes type{to{clip-path:inset(0 0 0 0)}}'
                    '.cursor{fill:' + t["text"] + ';animation:blink 1s steps(1) infinite;}@keyframes blink{50%{opacity:0}}'
                    '.tail{animation:wag 2s ease-in-out infinite;}@keyframes wag{50%{opacity:.35}}')
        else:
            css += '.cursor{fill:' + t["text"] + ';}'
        o = ['<?xml version="1.0" encoding="utf-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" font-family="ConsolasFallback,Consolas,Menlo,DejaVu Sans Mono,Courier New,monospace" width="{WPX}px" height="{H}px" font-size="16px">',
             '<style>@font-face{src:local("Consolas"),local("Consolas Bold");font-family:"ConsolasFallback";font-display:swap;-webkit-size-adjust:109%;size-adjust:109%;}' + css + '</style>',
             f'<rect width="{WPX}px" height="{H}px" fill="{t["bg"]}" rx="15"/>',
             f'<text x="{ART_X}" y="{TOP}" fill="{t["text"]}" font-size="11px">']
        o += [f'<tspan x="{ART_X}" y="{TOP + i * ALH}">{html.escape(l)}</tspan>' for i, l in enumerate(art)]
        o.append("</text>")
        # speech bubble frame
        frame = [" ." + "-" * (BW + 2) + ".", " |" + " " * (BW + 2) + "|", "<|" + " " * (BW + 2) + "|",
                 " |" + " " * (BW + 2) + "|", " '" + "-" * (BW + 2) + "'"]
        o.append(f'<text class="cc">')
        for i, l in enumerate(frame):
            cls = ' class="tail"' if l.startswith("<") else ""
            o.append(f'<tspan x="{X - 5}" y="{BY + i * LH}"{cls}>{html.escape(l)}</tspan>')
        o.append("</text>")
        for i, (a, b) in enumerate(msgs):
            if freeze is not None and i != freeze:
                continue
            style = ""
            o.append(f'<g class="msg"{style}><g class="type"{style}><text class="bubble">'
                     f'<tspan x="{X + 22}" y="{BY + 1.5 * LH}">{html.escape(a)}</tspan>'
                     f'<tspan x="{X + 22}" y="{BY + 2.5 * LH}">{html.escape(b)}</tspan></text></g></g>')
        o.append(f'<text x="{X}" y="{TY}">')
        for i, line in enumerate(term):
            parts = "".join(f'<tspan class="{c}">{html.escape(s)}</tspan>' for c, s in line)
            o.append(f'<tspan x="{X}" y="{TY + i * LH}">{parts}</tspan>')
        o.append("</text></svg>")
        out = f"{name}_mode.svg" if freeze is None else f"/home/claude/profile/frame_{name}_{freeze}.svg"
        open(out, "w").write("\n".join(o))

if __name__ == "__main__":
    if TOKEN:
        st = fetch_stats()
    else:
        st = json.load(open("stats.json")) if os.path.exists("stats.json") else \
             dict(created="2021-01-01", followers=0, repos=0, stars=0, contributed=0, commits=0)
    json.dump(st, open("stats.json", "w"), indent=2)
    build(st)
