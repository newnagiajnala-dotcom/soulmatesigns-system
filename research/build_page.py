import csv, json, html
rows = list(csv.DictReader(open("research/top-reels.csv")))
for r in rows: r["views"] = int(r["views"])
data = json.dumps(rows, ensure_ascii=False)

page = """<title>Soulmate Niche Reel Atlas</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one column — summary of formats, key lessons, then a filterable ledger of every reel */
:root{
  --bg:#f5f4fa; --surface:#ffffff; --ink:#1d1a33; --muted:#625e7d; --line:#dcd9ea;
  --accent:#6b4fd8; --gold:#b07d12; --chip:#ece8fb;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;
  --body:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#12101f;--surface:#1b1830;--ink:#ece9fb;--muted:#a7a2c6;--line:#2f2a4b;--accent:#a893ff;--gold:#e3b84f;--chip:#2a2547;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12101f;--surface:#1b1830;--ink:#ece9fb;--muted:#a7a2c6;--line:#2f2a4b;--accent:#a893ff;--gold:#e3b84f;--chip:#2a2547;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.55 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 56px}
.wrap{max-width:1180px;margin:0 auto;display:grid;gap:32px}
h1{font:800 clamp(28px,4.5vw,44px)/1.05 var(--display);margin:0;text-wrap:balance;letter-spacing:-.01em}
h2{font:600 22px/1.2 var(--display);margin:0 0 12px;text-wrap:balance}
.lede{color:var(--muted);max-width:68ch;margin:10px 0 0}
.kpis{display:flex;flex-wrap:wrap;gap:28px;margin-top:18px}
.kpi b{display:block;font:600 26px/1 var(--mono);font-variant-numeric:tabular-nums;color:var(--ink)}
.kpi span{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.formats{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
.fmt{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:6px;min-width:0}
.fmt .name{font-weight:600}
.fmt .meta{font:13px var(--mono);color:var(--muted);font-variant-numeric:tabular-nums}
.bar{height:6px;background:var(--chip);border-radius:3px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--accent)}
.lessons{display:grid;gap:10px;margin:0;padding:0;list-style:none;max-width:80ch}
.lessons li{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:baseline}
.lessons li::before{content:"✶";color:var(--gold)}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px}
.controls input{flex:1 1 220px;min-width:0;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);font:inherit}
.chip{border:1px solid var(--line);background:var(--surface);color:var(--ink);padding:6px 11px;border-radius:999px;font:13px var(--body);cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.chip:focus-visible,.controls input:focus-visible,th button:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.tablebox{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
table{border-collapse:collapse;width:100%;min-width:980px;font-size:13.5px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font:600 11px var(--body);letter-spacing:.07em;text-transform:uppercase;color:var(--muted);position:sticky;top:0;background:var(--surface)}
th button{all:unset;cursor:pointer}
td.v{font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:500}
td a{color:var(--accent);text-decoration:none;font-family:var(--mono);font-size:12.5px}
td a:hover{text-decoration:underline}
.tag{display:inline-block;background:var(--chip);border-radius:6px;padding:2px 7px;font-size:12px;white-space:nowrap}
.seen{font-size:11px;color:var(--muted)}
.seen.y{color:var(--gold)}
.foot{color:var(--muted);font-size:13px;max-width:80ch}
</style>
<div class="wrap">
<header>
  <h1>Soulmate Niche Reel Atlas</h1>
  <p class="lede">What makes soulmate, zodiac and love reels reach 100K+ views on Instagram. Scanned 31 Oct 2026 from public account grids. Hooks and thumbnails are described in our own words, and each row ends with an original idea we can make for @soulmatesigns.daily.</p>
  <div class="kpis" id="kpis"></div>
</header>
<section><h2>Views by format</h2><div class="formats" id="formats"></div></section>
<section>
  <h2>What the winners have in common</h2>
  <ul class="lessons">
    <li><span><b>Split all 12 signs.</b> The biggest reels (40.9M, 25.4M, 6.9M) put six signs on one side and six on the other, so every viewer is included and sends it to someone on "the other side".</span></li>
    <li><span><b>One big text box on frame 1.</b> A short question or label in a solid box ("Two types of wives", "Who will you marry?"). That frame is also the thumbnail.</span></li>
    <li><span><b>A share or comment trigger, never a sales line.</b> "Send this to your bestie", "Choose your birth month", "Comment to get your sketch". Comment-bait reels hit 27K to 71K comments.</span></li>
    <li><span><b>Short and silent-friendly.</b> Most winners run about 7 to 15 seconds and read fine with the sound off.</span></li>
    <li><span><b>Repeat what worked.</b> The 898K sketch hook was posted again and pulled 253K. Top accounts reuse their best template every week.</span></li>
    <li><span><b>Faceless works.</b> AI cinematic images with bold yellow and white captions (363K, 306K) and moving b-roll with a text box (170K) need no presenter.</span></li>
  </ul>
</section>
<section>
  <h2>Every reel</h2>
  <div class="controls">
    <input id="q" type="search" placeholder="Search hooks, accounts, ideas" aria-label="Search reels">
    <div id="chips" style="display:flex;flex-wrap:wrap;gap:8px"></div>
  </div>
  <div class="tablebox"><table>
    <thead><tr>
      <th><button data-k="views" id="sortv">Views ↓</button></th><th>Account</th><th>Format</th><th>Hook pattern</th><th>Thumbnail</th><th>CTA</th><th>Why it worked</th><th>Our original idea</th><th>Reel</th>
    </tr></thead>
    <tbody id="tb"></tbody>
  </table></div>
  <p class="foot">Rows marked "studied" were opened and analysed one by one. Others share their account's proven template and are listed for their view counts. View counts are Instagram's rounded play counts at the time of the scan.</p>
</section>
</div>
<script>
const D=__DATA__;
const fmtN=n=>n>=1e6?(n/1e6).toFixed(1).replace(/\\.0$/,'')+'M':Math.round(n/1e3)+'K';
const group=f=>f.replace(/ \\(account template\\)/,'').replace(/ \\(birth (month|date)\\)/,'');
const total=D.reduce((s,r)=>s+r.views,0);
document.getElementById('kpis').innerHTML=[[D.length,'reels at 100K+'],[D.filter(r=>r.views>=1e6).length,'over 1M views'],[D.filter(r=>r.viewed_individually==='yes').length,'studied one by one'],[fmtN(total),'combined views']].map(([b,s])=>`<div class="kpi"><b>${b}</b><span>${s}</span></div>`).join('');
const G={};D.forEach(r=>{const g=group(r.format);(G[g]=G[g]||{n:0,v:0,max:0});G[g].n++;G[g].v+=r.views;G[g].max=Math.max(G[g].max,r.views)});
const gs=Object.entries(G).sort((a,b)=>b[1].v-a[1].v);const top=gs[0][1].v;
document.getElementById('formats').innerHTML=gs.map(([g,s])=>`<div class="fmt"><div class="name">${g}</div><div class="meta">${s.n} reels · ${fmtN(s.v)} total · best ${fmtN(s.max)}</div><div class="bar"><i style="width:${Math.max(2,s.v/top*100)}%"></i></div></div>`).join('');
let active='All',asc=false;
const chips=['All',...gs.map(g=>g[0])];
const cbox=document.getElementById('chips');
cbox.innerHTML=chips.map(c=>`<button class="chip" aria-pressed="${c==='All'}" data-c="${c}">${c}</button>`).join('');
cbox.addEventListener('click',e=>{const b=e.target.closest('.chip');if(!b)return;active=b.dataset.c;cbox.querySelectorAll('.chip').forEach(x=>x.setAttribute('aria-pressed',x===b));render()});
document.getElementById('q').addEventListener('input',render);
document.getElementById('sortv').addEventListener('click',e=>{asc=!asc;e.target.textContent='Views '+(asc?'↑':'↓');render()});
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function render(){const q=document.getElementById('q').value.toLowerCase();
 const rs=D.filter(r=>(active==='All'||group(r.format)===active)&&(!q||Object.values(r).join(' ').toLowerCase().includes(q))).sort((a,b)=>asc?a.views-b.views:b.views-a.views);
 document.getElementById('tb').innerHTML=rs.map(r=>`<tr><td class="v">${fmtN(r.views)}</td><td>${esc(r.account)}<div class="seen ${r.viewed_individually==='yes'?'y':''}">${r.viewed_individually==='yes'?'studied':'template'}</div></td><td><span class="tag">${esc(group(r.format))}</span></td><td>${esc(r.hook_pattern)}</td><td>${esc(r.thumbnail_style)}</td><td>${esc(r.cta)}</td><td>${esc(r.why_it_worked)}</td><td>${esc(r.our_original_idea)}</td><td><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.reel_id)}</a></td></tr>`).join('');}
render();
</script>
"""
open("research/reel-atlas.html","w").write(page.replace("__DATA__", data))
print("ok", len(rows))
