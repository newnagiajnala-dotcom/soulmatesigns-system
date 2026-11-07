# Daily promo reels — TWO styles A/B (owner 7 Nov: "both reels promo, different hooks, scripts and editing, see what works")
# Daily promo reel (Soulmate Sketch sales reel) — owner request 7 Nov 2026, goal: break the ~150-view wall, 100K views in Nov
Template proven by promo 001 (148 views in 7 h = 2nd best ever). Morning slot, every day. Cost ≈ 2.5 credits (4 images + voice); hook clips are reused.

1. Script: first entry in promo/scripts.json with used=false. If none left, write 7 new ones in the same shape:
   hook_text ≤ 6 words CAPS (no emoji); voice 44–50 words, short sentences, NO "..." (pauses are added by the editor),
   beats = hook (≤ 9 words, first sentence ≤ 4 s) → relatable twist → "psychic artist Tina sketches your soulmate's face by hand, from your energy"
   → one curiosity line → "Curious what yours looks like? Link in bio."; never guarantees, never fake reviews/testimonials, never say the clip/images are Tina's work.
   Caption: hook line + emoji · a SHARE ask ("Send this to …" / "Tag the friend who …") · "Curious what yours looks like? Link in bio ✨ (just for fun)" · 5 hashtags.
   Rotate the 4 hook clips in promo/hooks.json (never the same clip 2 days running). Write promo/NNN/spec.json (NNN = next number).
2. Images: 4 × generate_image model gpt_image_2_5, aspect_ratio 9:16, prompt = the script's image line + ", vertical 9:16, natural skin, no text, no watermark".
   get_cost first; abort (post a template reel instead) if one image > 0.5 credits.
3. Voice: per ai/WORKFLOW.md §4 (elevenlabs_v4, voice Willow unless data/approvals.txt says otherwise); abort if > 2 credits.
4. Build in the Higgsfield sandbox: `curl -sfO <raw>/ai/promo_reel.py && python3 promo_reel.py spec.json out` with spec
   {hook_text, cta_text: "LINK IN BIO", highlight, scenes: [{url: <hook clip url>, video: true, dur: 4.3}, {url: img1}, …, {url: img4}],
    voice_url, music_url: dreamy or emotional track from music/library.json}. The editor cuts pauses to 0.85 s automatically.
   Result must be 18–24 s. Check out/cover.jpg + 2 frames (captions readable). Upload: media_upload → PUT in the same command → media_confirm.
5. Post with RUNBOOK steps 7 + 7b. Instagram caption = script caption. Facebook description = caption with "Link in bio" replaced by "Link on our Page" (NO URLs on Facebook). performance.csv format "promo-voice" / "promo-voice FB" (style B: "promo-text" / "promo-text FB"). Mark the script used=true, promo_id=NNN.
If Higgsfield is unavailable or balance < 30: post the best template reel instead and log it.

## Style B — SHORT interactive text reel (EVENING slot) — updated 7 Nov after niche research (research/sales-reels-2026-11-07.md):
## the top soulmate-sketch affiliate reels (6–18M views) are 5–13 s, interactive (affirm YES / save / pick 1-2-3 / screenshot / comment a word), and sell in the CAPTION + bio.
- Script: first style "B" entry in promo/scripts.json with used=false (new ones: hook_text ≤ 5 words, 2 lines ≤ 9 words each, line 2 = the interaction ask,
  *word* marks the orange word, last line = curiosity question; dur 1.9 s for short lines, 2.6 s for long; caption with a share/comment ask).
- Images: 2 × gpt_image_2_5 (same rules as style A). No voice. Hook clip dur 3.0 (scene 0 {url, video:true, dur:3.0}). Target 7–10 s total.
- Spec: {hook_text, cta_text: "LINK IN BIO", lines, scenes: [{url: hook clip, video: true, dur: 4.3}, img1, img2, img3], music_url}.
  promo_reel.py detects "lines" and builds a 11–14 s text reel with music only.
- performance.csv format "promo-text" (style A rows use "promo-voice"). Never the same hook clip as the morning reel of the same day.
## Comparing (every Sunday + 12 Nov review)
- Compare promo-voice vs promo-text vs old templates on views/reel, shares and link clicks (ClickBank tid igbio / fbpromo).
  Double down on the winner style; keep testing new hooks inside it.

## Style C — SOULMATE CHECK handwriting reel (AFTERNOON slot, 4:41 PM ET) — owner 7 Nov: "3 reels per day, soulmate check between both reels"
Promo 003 got 167 views + 2 comments in its first hour (best start ever). Cost 0 credits (fixed background image).
1. Pick the first check in promo/checks.json with used=false (formulas rotate: age · initial · love number).
2. In the Higgsfield sandbox (background:true, poll — rendering ~3 min):
   R=https://raw.githubusercontent.com/newnagiajnala-dotcom/soulmatesigns-system/<commit>
   curl -sfO $R/reelgen/check_reel.py; curl -sfO $R/reelgen/fonts/Caveat.ttf; curl -sfO $R/promo/checks.json
   curl -sfo page.png <checks.json base.bg_url>; curl -sfo music.mp3 <music/library.json "playful"[0]>
   python3 check_reel.py --check checks.json <id> page.png music.mp3 out   → out/reel.mp4 (15 s)
   Check 2 frames (t=7.5 and t=13.5): numbers and words on the page, nothing cut off. Upload (media_upload → PUT → media_confirm).
3. Post with RUNBOOK 7 + 7b: caption = the check's caption; thumb_offset 7500; FB description = caption with "Link in bio ✨" → "Link on our Page ✨" (NO URLs on Facebook). performance.csv format "promo-check". Mark used=true, promo_id.
If the sandbox fails, skip the afternoon reel (do not post a fallback) and log it.

## Style D — LOVE % name check — OWNER FILMS THESE BY HAND (7 Nov: AI version looked fake). The autopilot does NOT make Style D; AFTERNOON slot = Style C every day.
## (old automated Style D notes kept for reference) — from the @soulmatesketch02 teardown (research/soulmatesketch02-2026-11-07.md: 96.8M / 22.7M / 11.5M views)
- (inactive) Even US days = Style C, odd = Style D.
- Names: FIRST look for a REAL comment on our IG reels containing two first names (GET /{media_id}/comments?fields=text,username on the last 10 reels);
  if found, use it and pass "@<username>|<their comment text>" as the 7th argument (reply bubble). NEVER invent a commenter or a bubble.
  If none, use the next unused pair from promo/names.json (popular US names) with NO bubble.
- Build (REALISTIC HAND version, owner 7 Nov: "make it feel like a real person is writing"):
  curl -sfO $R/reelgen/hand_reel.py; curl -sfO $R/reelgen/fonts/Caveat.ttf
  curl -sfo hand.png https://d8j0ntlcm91z4.cloudfront.net/user_3EzwJnQsE5b12PUKFrt1rTGUePG/hf_20261107_122005_900b18b5-0df6-416b-b1de-4a8afb99b90a.png
  curl -sfo paper.png https://d8j0ntlcm91z4.cloudfront.net/user_3EzwJnQsE5b12PUKFrt1rTGUePG/hf_20261107_121951_48ed0cca-fe8a-4f83-a3f0-eaef735b170e.png
  python3 hand_reel.py --names <Name1> <Name2> paper.png hand.png music.mp3 out ["@user|comment"]   (prints pct; 25–35 s; render ~4 min, background:true, poll)
  Check frames at 1/3, 2/3 and the last frame. thumb_offset = (seconds - 2) * 1000.
- Caption: "<Name1> + <Name2> = <pct>% 💞 Want me to do yours?\n\nDrop your names 👇 (yours + your crush) and I'll write them in the next video ✍️\n\nCurious what your soulmate looks like? Link in bio ✨ (just for fun)\n\n#namecompatibility #lovecalculator #soulmate #couple #lovesigns"
- performance.csv format "promo-love". Same posting/FB rules as Style C (no URL on Facebook).
