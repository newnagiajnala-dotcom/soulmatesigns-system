# Autopilot runbook — @soulmatesigns.daily

Every scheduled run follows these steps exactly. Owner: Malkiat. He approved automatic publishing of
reels made by this system to @soulmatesigns.daily (max 2 per day), following the rules below.

## Constants
- Instagram API: https://graph.facebook.com/v21.0  (the environment's network secret adds the token; never print or log tokens)
- IG user id: 17841459940404036
- Repo: newnagiajnala-dotcom/soulmatesigns-system (branch main). Public raw base:
  https://raw.githubusercontent.com/newnagiajnala-dotcom/soulmatesigns-system/main/
- Bio link (quiz landing page): https://soulmatesigns.org/ (old github.io URL redirects here)  → hoplink affiliate=abhi10k

## Steps each run
1. `git pull`. Read playbook.md, data/performance.csv, research/top-reels.csv (skim), and the last 10 reels/*/spec.json.
2. Update stats: for every row in data/performance.csv posted in the last 30 days, GET
   `/{media_id}/insights?metric=views,reach,likes,comments,shares,saved` (fall back to `plays` if `views` errors)
   and write the numbers into that row. Also GET `/17841459940404036?fields=followers_count` and append
   `date,followers` to data/followers.csv.
3. Decide what to make, using the weekly mix in playbook.md (count what was posted in the last 7 days and fill the
   biggest gap). From day 7 on, lean toward the format with the best views per reel over the last 14 days.
4. Write reels/NNN/spec.json (next number). Hook must be NEW (not used in any earlier spec). Rules:
   - F0 meme → template "split" (reelgen/split_reel.py): title, incoming, left{head,reply,signs[6]}, right{head,seen,reply,signs[6]}, cta. All 12 signs used exactly once.
   - F1/F2/F3/F5/F6 → template "cards" (reelgen/cards_reel.py): hook (≤ 6 words), sub, items (3–6, each ≤ 30 characters), cta.
   - Selling reels (F1, F2, F4) put "link in bio" in the caption, not in the video.
   - Honest only: entertainment framing, no guarantees, no fake testimonials, no income/health claims, no copying other creators' text or footage.
   - Caption: 1–2 short lines + 5–6 hashtags from: #soulmate #zodiac #zodiacsigns #astrology #twinflame #lovesigns #birthmonth #zodiacmemes #crush.
5. Render: `python3 reelgen/<template>_reel.py reels/NNN/spec.json reels/NNN/reel` (split → split_reel.py, cards → cards_reel.py).
   Open reels/NNN/reel_cover.jpg and check nothing overlaps or is cut off; fix the spec once if needed.
6. Commit and push reels/NNN/ (Co-Authored-By trailer as usual). Wait until the raw URL of reel.mp4 returns 200 (check with a HEAD request, up to 2 min).
7. Publish ONCE: POST `/17841459940404036/media` media_type=REELS, share_to_feed=true, thumb_offset=(duration_ms − 300),
   video_url=<raw url>, caption=<spec caption>. Poll `/{creation_id}?fields=status_code,status` every 10 s up to 5 min.
   On FINISHED → POST `/17841459940404036/media_publish` creation_id=… → GET permalink.
   On ERROR → do not retry publishing; record the error in data/errors.log and stop.
8. Append to data/performance.csv: `date,media_id,hook,format,,,,,,`. Commit and push.
9. Sundays (evening run only): add a dated entry to the Learning log in playbook.md — best and worst format by views/reel,
   one decision for next week. Keep the mix rules updated.

## Safety limits
- Never more than 2 published reels per calendar day (US Eastern). Check data/performance.csv first.
- If the API returns an error about spam, action blocks or limits: stop, log it, and skip the next 24 h.
- Never change the bio, follow/like/comment, or DM anyone.
