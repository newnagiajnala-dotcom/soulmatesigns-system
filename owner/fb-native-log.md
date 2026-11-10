# Facebook NATIVE uploads (Facebook web uploader in the VPS Chrome, or owner's phone) — API FB reels stopped 10 Nov
Method (owner session, VPS Chrome with Claude extension, logged in as the Soulmate Signs Page):
1. Pick yesterday's best IG reel (highest views in data/performance.csv, not yet in this log); video_url from promo/NNN/spec.json.
2. facebook.com/reels/create → in the FB tab add a 'message' listener, window.open(video_url) → in that tab fetch(location.href).arrayBuffer() and
   window.opener.postMessage({kind:'vid',buf},'*',[buf]) → back in FB tab build File, DataTransfer into input[type=file][accept*=video], dispatch change.
3. Next → Next → caption (IG caption, "Link in bio" → "Comment your …", no URL) → type a space to close hashtag suggestions → Post.
| Date (IST) | Reel | Source | By | Views (later) |
|---|---|---|---|---|
| 2026-11-09 21:40 | Soulmate check 1998−1971 (promo 003) | phone | owner | 465 after ~11 h |
| 2026-11-10 11:25 | Soulmate check birth day + month (promo 005) | VPS Chrome web upload | Claude | |
