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

def build(st):
    art = open("cat.txt").read().split("\n")
    W = 58
    def dots(n): return " " + "." * max(n, 1) + " "
    def kv(key, val): return [("cc", ". "), ("key", key), ("cc", ":"), ("cc", dots(W - len(key) - len(val) - 5)), ("value", val)]
    def hdr(t): return [("cc", "- "), ("key", t), ("cc", " " + "—" * (W - len(t) - 7) + "-—-")]
    blank = [("cc", ". ")]
    f = lambda n: f"{n:,}"
    left1 = f"Repos: .... {f(st['repos'])} {{Contributed: {f(st['contributed'])}}}"
    left2 = f"Commits: .......... {f(st['commits'])}"
    info = [
        [("key", "abdullahi@khalafalla"), ("cc", " " + "—" * (W - 25) + "-—-")],
        kv("OS", "macOS, iOS, Linux"),
        kv("Uptime", uptime(st["created"])),
        kv("Host", "IBM"),
        kv("Kernel", "AI Software Engineer Intern"),
        kv("Education", "B.S. Computer Science @ UT Arlington"),
        kv("IDE", "Xcode, VS Code"),
        blank,
        kv("Languages.Programming", "Swift, Python, Kotlin, Java"),
        kv("Languages.Computer", "HTML, CSS, JSON, YAML"),
        kv("Languages.Real", "English"),
        blank,
        kv("Prev.Experience", "Apple (Siri), Ford (FordPass)"),
        kv("Projects", "CarCare AI, Sorghum Detector"),
        kv("Interests", "Quant, Multi-Agent AI, On-Device ML"),
        blank,
        hdr("Contact"),
        kv("Email.Personal", "abdulahikhalafalla@gmail.com"),
        kv("GitHub", USER),
        blank,
        hdr("GitHub Stats"),
        [("cc", ". "), ("key", "Repos"), ("cc", ": .... "), ("value", f(st["repos"])), ("cc", " {"), ("key", "Contributed"),
         ("cc", ": "), ("value", f(st["contributed"])), ("cc", "} | "), ("key", "Stars"),
         ("cc", ":" + dots(W - len(left1) - 13 - len(f(st['stars'])))), ("value", f(st["stars"]))],
        [("cc", ". "), ("key", "Commits"), ("cc", ": .......... "), ("value", f(st["commits"])), ("cc", " | "), ("key", "Followers"),
         ("cc", ":" + dots(W - len(left2) - 17 - len(f(st['followers'])))), ("value", f(st["followers"]))],
    ]
    themes = {
        "dark":  dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff", cc="#616e7f"),
        "light": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069", cc="#c2cfde"),
    }
    LH, TOP, ART_X, INFO_X, WPX = 20, 30, 18, 395, 985
    ALH = 12  # art line height (art uses a smaller font for more detail)
    H = TOP + max(len(art) * ALH, len(info) * LH)
    for name, t in themes.items():
        o = ['<?xml version="1.0" encoding="utf-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" font-family="ConsolasFallback,Consolas,Menlo,DejaVu Sans Mono,Courier New,monospace" width="{WPX}px" height="{H}px" font-size="16px">',
             '<style>@font-face{src:local("Consolas"),local("Consolas Bold");font-family:"ConsolasFallback";font-display:swap;-webkit-size-adjust:109%;size-adjust:109%;}'
             f'.key{{fill:{t["key"]};}}.value{{fill:{t["value"]};}}.cc{{fill:{t["cc"]};}}text,tspan{{white-space:pre;}}</style>',
             f'<rect width="{WPX}px" height="{H}px" fill="{t["bg"]}" rx="15"/>',
             f'<text x="{ART_X}" y="{TOP - 4}" fill="{t["text"]}" font-size="11px" class="ascii">']
        o += [f'<tspan x="{ART_X}" y="{TOP - 4 + i * ALH}">{html.escape(l)}</tspan>' for i, l in enumerate(art)]
        o += ["</text>", f'<text x="{INFO_X}" y="{TOP}" fill="{t["text"]}">']
        for i, line in enumerate(info):
            parts = "".join(f'<tspan class="{c}">{html.escape(s)}</tspan>' for c, s in line)
            o.append(f'<tspan x="{INFO_X}" y="{TOP + i * LH}">{parts}</tspan>')
        o.append("</text></svg>")
        open(f"{name}_mode.svg", "w").write("\n".join(o))

if __name__ == "__main__":
    if TOKEN:
        st = fetch_stats()
    else:
        st = json.load(open("stats.json")) if os.path.exists("stats.json") else \
             dict(created="2021-01-01", followers=0, repos=0, stars=0, contributed=0, commits=0)
    json.dump(st, open("stats.json", "w"), indent=2)
    build(st)
