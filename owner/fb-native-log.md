- OVERRIDE 14 Nov 13:40 IST (owner: copy what FB winners do — Dante Caruso 12.3K comments = question hook; 'Type YES' = most common CTA): chart videos now have an intro card "Who's the first person that came to your mind?" and an end card "Type YES if you want to see your soulmate's face" (reelgen/chart_reel.py cards=True; chart1,3–8 rebuilt). Caption must START with "Who's the first person that came to your mind? 👀 Type YES 👇" and end with "💌 Message us SKETCH and we'll send you the link ✨". First comment: "Type YES 👇 and message us SKETCH — we'll send you the link to see your soulmate's face 💌". Auto reply (owner turned ON 14 Nov) answers every new message with the link.
- OVERRIDE 14 Nov: the comment-to-message automation does NOT fire on reels (13 Nov, Sarah's 'Sketch' got nothing). CTA is now MESSAGE-based: caption ending "💌 Message us SKETCH and we'll send you the link ✨", first comment "💌 Want the link to see your soulmate's face? Send us a message with SKETCH and we'll send it to you ✨". Do NOT reply to people's comments (owner 13 Nov: "dont reply"). 20:30 upload on 13 Nov skipped (Chrome unreachable).
- OVERRIDE 13 Nov 11:40 IST (OWNER: "where is the link") — the ONLY first comment from now on: "💌 Want the link to see your soulmate's face? Comment SKETCH below and we'll send it to you in Messenger ✨". Caption ending: "💌 Comment SKETCH and we'll send you the link ✨". OWNER 13 Nov: NO "(affiliate link · for fun)" tag in captions or comments ("i hate it") — the affiliate disclosure lives where the link actually is: the Messenger auto-reply text and the sketch page. Never use the 'Tap Soulmate Signs → Learn more' wording again. Messenger automation (keywords SKETCH/LINK/YES) DMs the clickable https://soulmatesigns.org/sketch?src=fbdm. Still NO raw URL in reel comments/captions (not clickable).
# OVERRIDE 11 Nov (owner): URLs in REEL COMMENTS are NOT clickable on Facebook (checked: no <a> tag). Do NOT post the URL comment any more.
- OVERRIDE 12 Nov 23:40 IST — ADD MUSIC to every FB upload: after the video loads, in the 'Edit reel' step click Music → search an English upbeat/romantic royalty-free track (proven: "Sunny Day" – Jonny Houlihan; vary it) → click it → Done → Next. Chart reels (promo-chart) are silent files and MUST get music. Prefer chart reels for FB uploads now (IG chart reel 018 had our best watch time).
# Instead the first comment is: "👉 Want to see your soulmate's face? Tap Soulmate Signs above → the Learn more button (or the pinned post) ✨ (affiliate link · for fun)"
# Clickable paths: Page "Learn more" action button → https://soulmatesigns.org/sketch?src=fbbtn (tid fbbtna); pinned post (src=fbpin); Messenger comment-to-message (owner sets up, src=fbdm).
# Caption ending: "See your soulmate sketch → tap our Page name ✨" (instead of "Link in the first comment").

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
| 2026-11-11 06:25 | Love number check num2 (promo 013, retention-fix version) FB reel 2194567124812162 | VPS Chrome web upload + link comment | Claude (owner asked) | 107 at +5 h; 201 at +14 h |
| 2026-11-11 11:32 | Soulmate check age2 (promo 010) FB reel 1605287307589530 | VPS Chrome web upload | Claude (daily 11:30) | 35 at +45 min; 279 at +9 h; 459 at +24 h; link comment 12:20 (not clickable) |
| 2026-11-11 20:32 | Initial heart A (promo 012) FB reel 1439832341044089 | VPS Chrome web upload, caption → Page name (no URL) | Claude (evening) | 3 at +1 h; Learn-more comment 21:15; 222 at +14 h; 223 at +24 h |
| 2026-11-12 11:33 | Soulmate check init W (promo 016, retention-fix) FB reel 4290452254432425 | VPS Chrome web upload, caption → Page name | Claude (daily 11:30) | Learn-more comment 11:36; 184 at +9 h |
| 2026-11-12 20:32 | Initial heart S (promo 015) FB reel 1831354797898730 | VPS Chrome web upload, caption → Page name | Claude (evening) | Learn-more comment 20:36; 76 at +3 h |
| 2026-11-12 23:40 | Chart 'Your first initial' (promo 018) + Music 'Sunny Day' – Jonny Houlihan FB reel 1876210400204839 | VPS Chrome web upload, caption → Page name | Claude (owner test) | Learn-more comment 23:44; 516 at +10 h; 744 at +12 h; **4.2K at +36 h** (20 reactions, 4 comments, 1 share) |
| 2026-11-13 11:35 | Chart 'birth month → month you meet' (chart2) + Music 'Let Me Love You (feat. Ariza)' – Julia Gartha FB reel 1130488976440671 | VPS Chrome web upload, caption → Page name | Claude (daily 11:30) | Learn-more comment 11:40; only 4 views at +24 h |
| 2026-11-14 11:35 | Chart 'zodiac → soulmate's sign' (chart3) + Music 'Good Morning Sun' – Jonny Houlihan FB reel 2338941796644862 | VPS Chrome web upload, caption → 'Message us SKETCH' | Claude (daily 11:30) | first comment 'Send us a message with SKETCH' |
## 12 Nov 10:20 IST — Messenger "Comment to message" automation LIVE (keywords SKETCH/LINK/YES → DM https://soulmatesigns.org/sketch?src=fbdm, tid fbdma; Messenger channel only). Switching captions/comments to "Comment SKETCH" awaits owner OK.
## 10 Nov 16:50 IST — sales push on Facebook (owner: "get me sales as soon as possible, do whatever")
- Link comment (src=fbc → tid fbca) added under both native reels (839 + 274 views). Replied to commenters Estrella (1958, 1989).
- New Page post with the sketch link (src=fbpin → tid fbpina), PINNED as Featured at the top of the Page.
- Comment-to-message automation: owner sets it up himself in Meta Business Suite (automation clicks blocked for Claude).

- 2026-11-13 12:30 IST: owner banned "(affiliate link · for fun)" everywhere. Removed from FB: 4 reel captions edited, 9 old Learn-more/link comments deleted and replaced with "Comment SKETCH" comments (reels 1876210400204839, 1130488976440671, 1831354797898730, 4290452254432425, 1439832341044089, 1605287307589530, 2194567124812162, 1148978397709236, 1600136254752587, 1454575703550907), pinned post edited. Messenger DM text now ends "(affiliate link)". IG old captions not edited (no IG login here; API cannot edit captions).
