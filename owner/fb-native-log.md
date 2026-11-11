# Facebook NATIVE uploads (Facebook web uploader in the VPS Chrome, or owner's phone) — API FB reels stopped 10 Nov
Method (owner session, VPS Chrome with Claude extension, logged in as the Soulmate Signs Page):
1. Pick yesterday's best IG reel (highest views in data/performance.csv, not yet in this log); video_url from promo/NNN/spec.json.
2. facebook.com/reels/create → in the FB tab add a 'message' listener, window.open(video_url) → in that tab fetch(location.href).arrayBuffer() and
   window.opener.postMessage({kind:'vid',buf},'*',[buf]) → back in FB tab build File, DataTransfer into input[type=file][accept*=video], dispatch change.
3. Next → Next → caption (IG caption with "Link in bio ✨" → "Link in the first comment 👇", NO URL) → type a space to close hashtag suggestions → Post.
4. (10 Nov, owner: ~70% of buyers are on FB) ~1 hour after posting (or at the next run) add the FIRST COMMENT as the Page:
   "See what your soulmate looks like ✨ https://soulmatesigns.org/sketch?src=fbc (just for fun · affiliate link)". Tracking id = fbca.
5. Schedule: 2 native uploads a day, 11:30 and 20:30 IST. Prefer the newest retention-fix versions; facebook-only hooks in promo/fb_hooks.json when built.
| Date (IST) | Reel | Source | By | Views (later) |
|---|---|---|---|---|
| 2026-11-09 21:40 | Soulmate check 1998−1971 (promo 003) | phone | owner | 465 after ~11 h |
| 2026-11-10 11:25 | Soulmate check birth day + month (promo 005) FB reel 1600136254752587 | VPS Chrome web upload | Claude | 233 after ~5 h; 316 after ~10 h; 377 after ~19 h |

| 2026-11-10 20:32 | Initial heart M (promo 006) FB reel 1148978397709236 | VPS Chrome web upload | Claude | 7 at +1 h; 220 at +10 h; link comment 21:35 |
| 2026-11-11 06:25 | Love number check num2 (promo 013, retention-fix version) FB reel 2194567124812162 | VPS Chrome web upload + link comment | Claude (owner asked) | 107 at +5 h |
| 2026-11-11 11:32 | Soulmate check age2 (promo 010, 394 IG views) | VPS Chrome web upload | Claude (daily 11:30) | link comment +45 min |
## 10 Nov 16:50 IST — sales push on Facebook (owner: "get me sales as soon as possible, do whatever")
- Link comment (src=fbc → tid fbca) added under both native reels (839 + 274 views). Replied to commenters Estrella (1958, 1989).
- New Page post with the sketch link (src=fbpin → tid fbpina), PINNED as Featured at the top of the Page.
- Comment-to-message automation: owner sets it up himself in Meta Business Suite (automation clicks blocked for Claude).
