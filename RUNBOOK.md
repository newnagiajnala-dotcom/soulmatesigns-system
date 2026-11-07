# Autopilot runbook — @soulmatesigns.daily

Every scheduled run follows these steps exactly. Owner: Malkiat. He approved automatic publishing of
reels made by this system to @soulmatesigns.daily (max 2 per day), following the rules below.

## Constants
- Instagram API: https://graph.facebook.com/v21.0  (the environment's network secret adds the token; never print or log tokens)
- IG user id: 17841459940404036
- Facebook Page: Soulmate Signs, https://www.facebook.com/profile.php?id=61596275964324 (created 2 Nov 2026; API page id 1402297082968632; app has pages_manage_posts/pages_read_engagement/pages_show_list; needs the regenerated token)
- Repo: newnagiajnala-dotcom/soulmatesigns-system (branch main). Public raw base:
  https://raw.githubusercontent.com/newnagiajnala-dotcom/soulmatesigns-system/main/
- Bio link (MAIN, since 7 Nov 2026 = sketch sales page): https://soulmatesigns.org/ (same page also at /sketch). Quiz moved to https://soulmatesigns.org/quiz/ (linked at the bottom of the sales page).  → hoplink affiliate=abhi10k
- Sales page for PROMO reels: https://soulmatesigns.org/sketch (headline matches promo reels; hoplink tid = ?src value + a/b, e.g. ?src=promo1 → tid promo1a).
  Promo reel captions say "Link in bio ✨"; FB promo descriptions use https://soulmatesigns.org/sketch?src=fbpromo<NNN>. All other reels/stories/posts: the main link.

## Steps each run
00. Tool check (every run, 10 s): note whether Higgsfield MCP tools are available (try the Higgsfield balance tool). Append one line to data/errors.log:
    "<ISO time> tools: higgsfield=<yes|no> balance=<n|-> run=<morning|midday|afternoon|evening>".
0. Check the current US Eastern time. 12:00–15:59 = MIDDAY STORY run: follow only the "Daily story" section, then stop.
   16:00–18:59 = AFTERNOON POST run: follow only the "Daily carousel post" section, then stop.
1. `git pull`. Read playbook.md, data/performance.csv, research/top-reels.csv (skim), and the last 10 reels/*/spec.json.
2. Update stats: for every row in data/performance.csv posted in the last 30 days, GET
   `/{media_id}/insights?metric=views,reach,likes,comments,shares,saved` (fall back to `plays` if `views` errors)
   and write the numbers into that row. Also GET `/17841459940404036?fields=followers_count` and append
   `date,followers` to data/followers.csv.
3. QUEUED FIRST: if any reels/NNN/spec.json has "queued": true, a post_on date ≤ today (US Eastern), matching slot, and no row in
   data/performance.csv for it, publish that reel (its reel.mp4 + spec caption) at step 7 instead of making a new one; then set queued to false.
   Otherwise decide what to make, using the weekly mix in playbook.md (count what was posted in the last 7 days and fill the
   biggest gap). From day 7 on, lean toward the format with the best views per reel over the last 14 days.
4. Write reels/NNN/spec.json (next number). Hook must be NEW (not used in any earlier spec). Rules:
   - F0 meme → template "split" (reelgen/split_reel.py): title, incoming, left{head,reply,signs[6]}, right{head,seen,reply,signs[6]}, cta. All 12 signs used exactly once.
   - F1/F2/F3/F5/F6 → template "cards" (reelgen/cards_reel.py): hook (≤ 6 words), sub, items (3–6, each ≤ 30 characters), cta.
   - VISUAL VARIETY (never the same template 3 times in a row; aim for every template each week):
     * template "tarot" (reelgen/tarot_reel.py) for F1 pick-a-card: hook, cards[3]{title,emoji,message}, cta. CTA = "comment 1, 2 or 3".
     * template "reveal" (reelgen/reveal_reel.py) for F3/F5 cinematic: lines[2-4] (*word* = gold), sign, tagline, cta.
     * template "souls" (reelgen/souls_reel.py) for soulmate/twin-flame messages: title, lines[2-4], cta ("send this to your person").
     * "split" and "cards" as before.
   - NICHE WINNERS (from research/sketch-niche-2026-11-01.md, 173 reels ≥100K). Use these for at least 1 of the 2 daily reels:
     * template "names" (reelgen/names_reel.py): name1, name2 (common US first names), cta "comment your names 👇 I'll write them next".
       Once real comments exist, take names from a real comment on our reels and set "reply_to": "@handle"; never invent a reply_to.
     * template "code" (reelgen/code_reel.py): title, title2, sub, cta "comment your CODE 👇". Vary title2 ("Soulmate?", "Twin Flame?", "Future Husband?").
     * template "sign" (reelgen/sign_reel.py): start_date = posting date (US Eastern, YYYY-MM-DD), message[2] (short, warm, no guarantees),
       cta "type 222 to claim it 🙏" (vary number: 111/333/777/888 or AMEN).
   - Comment-trigger CTAs work best (top niche reel: 14K comments from "comment 222"): use number/sign/card comment asks often.
   - Selling reels (F1, F2, F4) put "link in bio" in the caption, not in the video.
   - Honest only: entertainment framing, no guarantees, no fake testimonials, no income/health claims, no copying other creators' text or footage.
   - Caption: 1–2 short lines + 5–6 hashtags from: #soulmate #zodiac #zodiacsigns #astrology #twinflame #lovesigns #birthmonth #zodiacmemes #crush #situationship #astrologymemes #datinglife.
   - AUDIENCE = Tier-1 (US, UK, Canada, Australia), mostly women 18–34. Write in natural US English (US spelling: favorite, color),
     US/Western situations (texting, dating apps, situationships, ghosting, coffee dates, roommates, college/work life).
     No India-specific references, currency, festivals or Hinglish. Dates as "Nov 3", times as "11:02 pm".
   - MUSIC: every spec gets "music": "playful" (F0 memes, F6 debates), "dreamy" (F1, F2, F4 soulmate/selling) or
     "emotional" (F3 tributes, F5 reassurance). Use a different "seed" from the last 5 reels so tracks vary.
     Music is generated by reelgen/music.py (original, copyright-free) and added automatically when rendering.
     Never add copyrighted songs.
5. Render: `python3 reelgen/<template>_reel.py reels/NNN/spec.json reels/NNN/reel` (template name = file prefix: split, cards, tarot, reveal, souls, names, code, sign).
   Open reels/NNN/reel_cover.jpg and check nothing overlaps or is cut off; fix the spec once if needed.
   Check the mp4 has an audio stream (ffprobe); if not, re-run the render once.
6. Commit and push reels/NNN/ (Co-Authored-By trailer as usual). Wait until the raw URL of reel.mp4 returns 200 (check with a HEAD request, up to 2 min).
6b. REAL MUSIC (audio v2, 5 Nov 2026 — the code-generated music sounds fake): in the Higgsfield sandbox run
   `curl -sfO <raw>/reelgen/remix_music.py && python3 remix_music.py <raw url of reel.mp4> <spec music> <spec seed> reel_music.mp4`
   (swaps in a real instrumental from music/library.json, -14 LUFS). media_upload (video/mp4) → in the SAME sandbox command
   `curl -X PUT -H "Content-Type: video/mp4" -H "If-None-Match: *" --data-binary @reel_music.mp4 '<upload_url>'` → media_confirm.
   Use that Higgsfield URL as the video_url for steps 7 and 7b, and save it as "video_url" in spec.json.
   If Higgsfield is unavailable, publish the raw GitHub URL as before and log "audio v2 skipped" to data/errors.log.
7. Publish ONCE: POST `/17841459940404036/media` media_type=REELS, share_to_feed=true, thumb_offset=(duration_ms − 300),
   video_url=<Higgsfield URL from 6b, else raw url>, caption=<spec caption>. Poll `/{creation_id}?fields=status_code,status` every 10 s up to 5 min.
   On FINISHED → POST `/17841459940404036/media_publish` creation_id=… → GET permalink.
   On ERROR → do not retry publishing; record the error in data/errors.log and stop.
7b. FACEBOOK (every reel, right after Instagram succeeds; owner wants every reel on both). Page id 1402297082968632 (Soulmate Signs).
   a) GET /1402297082968632?fields=access_token → keep the page token in a shell variable only (never print, log or commit it).
   b) POST /1402297082968632/video_reels upload_phase=start access_token=<page token> → video_id.
   c) POST https://rupload.facebook.com/video-upload/v21.0/<video_id> with headers "Authorization: OAuth <page token>" and
      "file_url: <same public raw/CDN video url used for Instagram>".
   d) POST /1402297082968632/video_reels upload_phase=finish video_id=<id> video_state=PUBLISHED access_token=<page token>
      description=<Instagram caption + "\n\nCurious what your soulmate looks like? 👉 https://soulmatesigns.org/?src=fb"> (face reels: keep "AI host ✨").
   e) If any Facebook step fails (e.g. missing permission or token conflict), log it to data/errors.log and continue — never block Instagram,
      never retry a publish twice. Log a separate performance.csv row with reel_id "FB-<video_id>" and format "<format> FB".
8. Append to data/performance.csv: `date,media_id,hook,format,,,,,,`. Commit and push.
9. Sundays (evening run only): add a dated entry to the Learning log in playbook.md — best and worst format by views/reel,
   one decision for next week. Keep the mix rules updated.

## QUEUED PROMO FIRST: before building any reel, if a promo/NNN/spec.json has queued=true and posted=false and its post_on matches this slot (or is in the past), post THAT video (video_url, caption, fb_description, thumb_offset_ms) with steps 7 + 7b instead of building, then set posted=true + ids. It counts toward the 2-reel cap.

## Reel slots (updated 7 Nov 2026 — owner: "improve everything, 100K views this month")
- MORNING slot (7:41 AM ET) = PROMO reel style A (voice), per ai/PROMO.md (replaces Luna AI reels; Luna paused — same views as free templates).
- EVENING slot (7:41 PM ET) = PROMO reel style B (text-only, no voice), per ai/PROMO.md "Style B". AI host is paused.
  If Higgsfield is unavailable or balance < 30, post a free template reel (code / names / sign) instead.
- First run of each US day: still run the trend step (ai/WORKFLOW.md §1) and save data/trends/<date>.json.
- EVERY reel caption (all formats) must include one SHARE ask, e.g. "Send this to your bestie 💌" / "Tag the friend who…". Shares are what pushes a reel past the first ~150 views.

## Daily story (owner request, 2 Nov 2026): exactly 1 story per US day, Instagram + Facebook
- MIDDAY run only (the run that starts between 12:00 and 16:00 US Eastern). That run does ONLY the story — no reel, no stats.
  The 7:41 AM / 7:41 PM runs never post stories. Skip if stories/<today US Eastern>/ already has a "posted" file.
- Write stories/<YYYY-MM-DD>/spec.json: {date, title ("today's love message" / "your sign for tonight" / "a message from the universe"),
  number (angel number, different from the last 7 stories), message (≤ 18 words, warm, no guarantees, not repeated from the last 14),
  cta ("reply 💜 if this is for you" or "reply with your sign ✨"), seed}. Render: python3 reelgen/story_card.py <spec> stories/<date>/story.jpg
- Commit + push; wait until the raw URL of story.jpg returns 200.
- Instagram: POST /17841459940404036/media media_type=STORIES image_url=<raw url> → poll status → POST media_publish.
- Facebook (page token as in 7b): POST /1402297082968632/photos url=<raw url> published=false → photo id;
  POST /1402297082968632/photo_stories photo_id=<id>. If Facebook fails, log and continue.
- Write stories/<date>/posted with the ids, commit + push. Never post more than 1 story per day.

## Daily carousel post — PAUSED 7 Nov 2026 (6 carousels got 0–1 views each at 0 followers). The AFTERNOON run only appends a "carousel paused" line to data/errors.log and stops.
## (old rules kept for when it is switched back on)
- AFTERNOON run only (16:00–18:59 US Eastern, scheduled 4:41 PM ET). No reel, no story in that run.
  Skip if posts/<today US Eastern>/ already has a "posted" file.
- Write posts/<YYYY-MM-DD>/spec.json: {title (listicle hook, e.g. "5 signs you've already met your soulmate",
  "your soulmate's vibe by zodiac element", "3 things your person will notice first"), kicker, items (3–5 × {head ≤ 4 words, body ≤ 12 words}),
  cta, caption (hook line + "which one is you? 👇" + "save this + send it to your person 💌" + "Curious what your soulmate looks like? Link in bio ✨"
  + 5 hashtags), seed}. Title must be new (not used in posts/*/spec.json). Same honesty rules as reels.
- Render: python3 reelgen/carousel.py <spec> posts/<date>  → slide1..N.jpg. Check slide1 and the last slide for overlaps. Commit + push; wait for raw URLs (200).
- Instagram: for each slide POST /17841459940404036/media image_url=<raw> is_carousel_item=true → child ids;
  POST /17841459940404036/media media_type=CAROUSEL children=<ids comma-separated> caption=<caption> → poll → media_publish.
- Facebook (page token as in 7b): for each slide POST /1402297082968632/photos url=<raw> published=false → photo ids;
  POST /1402297082968632/feed message=<caption> attached_media=[{"media_fbid":id},...]. If Facebook fails, log and continue.
- Write posts/<date>/posted with ids; add a performance.csv row (format "carousel"). Never more than 1 post per day.

## AI host face reels — PAUSED 7 Nov 2026 by owner ("stop AI host reels until we get 100K views"). Do NOT make or post face reels; face-reel days use the normal evening template reel. Resume only if data/approvals.txt contains "host resume".
## (old rules kept below for when it is resumed; budget was 10 reels in 30 days)
- Face-reel days (evening slot only): Nov 2, 5, 8, 11, 14, 17, 20, 23, 26, 29 (2026). All other slots stay faceless (0 credits).
- Nov 2 posts the finished test reel using tests/host001/post.json (caption, video_url, duration). video_url = https://d2ol7oe51mr4n9.cloudfront.net/user_3EzwJnQsE5b12PUKFrt1rTGUePG/bcd3d116-436b-4c02-871d-1715cd8d1c48.mp4
  (only after the owner has said "post" — check data/approvals.txt contains "host001 post").
- Nov 5 evening: post the pre-made tests/host002/post.json (same way as host001; check data/approvals.txt for "host002 post").
- Later face reels: follow tests/host001/NOTES.md (seed_audio hook ~6 s → intone 720p with [character sheet, selfie] → stitch in the
  Higgsfield sandbox with a sign/code/names body + host outro). Hard cap 52 credits per reel; get_cost first; never use 1080p;
  never retry a paid generation automatically. If Higgsfield tools are not available in the run, or balance < 60, post a faceless reel instead and log it.
- Every face-reel caption starts with "AI host ✨". Never claim she is a real psychic or a real person.
- Owner chose option B (1 Nov): label face reels only, not the profile. After a face reel publishes, the run's final message must
  say: "Face reel posted: <permalink> — open it in Instagram → ⋯ → Edit → turn on 'AI info' (AI label)". Faceless reels need no label.
  (Instagram's own post composer has an 'Add AI label' switch; manual posts of face reels must switch it on.)

## Safety limits
- Never more than 2 published reels per calendar day (US Eastern). Check data/performance.csv first.
  ONE-DAY OWNER EXCEPTION: 2026-11-07 (ET) allows 3 reels = promo 001 (posted), promo 003 (check, posted on owner request) and promo 002 (queued for the 7:41 AM ET slot).
- If the API returns an error about spam, action blocks or limits: stop, log it, and skip the next 24 h.
- Never change the bio, follow/like/comment, or DM anyone.
