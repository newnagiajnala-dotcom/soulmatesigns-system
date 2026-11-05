# Luna AI reel workflow — fully automatic, repeatable, multi-post per day

One reel = TREND → SCRIPT → 4 IMAGES → VOICE → VIDEO → CAPTION → POST (IG + FB). Cost ≈ 3–3.5 Higgsfield credits (test 2 Nov: 4 images + voice).

## 1. Find today's trend (once per US day, first run of the day)
- `python3 ai/trends.py <YYYY-MM-DD>` → data/trends/<date>.json (Instagram hashtag API, 6 rotating hashtags/day, ≤30/week).
- Also do 2–3 web searches (e.g. "<topic> TikTok trend this week", "soulmate trend <month year>") and add notes to the same file under "web".
- Pick up to 3 TOPICS for the day: a topic must (a) appear in the top 40 posts or web results, (b) fit one of the 5 angles
  (research/content-angles-2026-11-02.md): soulmate reveal by sign · "there's a name for this" love psychology · invisible string / twin flame ·
  "if you're seeing this" sign · birthday / moon-phase match, and (c) not be used in the last 10 ai_reels.
  Record the choice in data/trends/<date>.json → "chosen".

## 2. Script (20–28 s finished reel → 45–55 spoken words; the voice reads ~2 words/s) — save as ai_reels/NNN/spec.json
Beats: HOOK (0–2 s) → TENSION/EMOTION (2–12 s) → PAYOFF / name it (12–20 s) → REPLAY LINE (20–24 s) → CTA (on screen).
- Hook: use or remix a hook from playbook.md "Stop-scroll hooks" (surprise / ego / fear / desire / controversy). Max 9 words. Second person.
- Plain US English, short sentences, "…" for pauses. No guarantees, no medical/clinical claims, no "you WILL meet", entertainment framing.
- hook_text (on-screen, ≤ 6 words, CAPS ok, NO emoji) — e.g. "YOU'RE NOT IN LOVE."
- cta_text (on-screen, ≤ 7 words, NO emoji) — e.g. "COMMENT 'LIMERENCE' IF YOU FELT THAT".
- highlight: 1–3 key words to color.

## 3. Images — 4 scenes, consistent mascot (ai/STYLE.md)
- For each scene: generate_image model gpt_image_2_5, aspect_ratio 9:16, medias [{role: image_references, value: <mascot ref job id>}],
  prompt = PREFIX + SCENE + SUFFIX from STYLE.md. Scene 1 must be the most striking (it is the scroll-stopper and cover).
- get_cost first; abort the AI reel (fall back to a code template) if a single image costs > 0.5 credits.

## 4. Voice (audio v2, 5 Nov 2026 — owner said the old voice sounded broken/unreal)
- generate_audio model elevenlabs_v4, dialogue [{text: script, voice_type: preset, voice_id: <VOICE>}] (≈1.15 credits).
  VOICE = f878bf3f-115b-5842-8934-c789c7947733 (Willow) until the owner picks one in data/approvals.txt ("voice: <name>"):
  Willow f878bf3f-115b-5842-8934-c789c7947733 · Emily 6b3e3642-f7b7-4cb8-9688-51e233c4b92f · Naomi caeba733-3c17-43db-863e-69c7025512cd.
- ElevenLabs reads faster (~2.6 words/s): 45–55 words ≈ 18–21 s. That is fine; do not pad.
- Do NOT use seed_audio any more (24 kHz, sounds robotic). Abort if cost > 2 credits.

## 5. Video (Higgsfield sandbox — the only place that can read Higgsfield files)
- Write spec (hook_text, cta_text, highlight, scenes = 4 image result URLs, voice_url, music_url =
  a track from music/library.json — "dreamy" or "emotional" (real instrumentals; never the old ai/music_*.wav synth files)) into the sandbox, then:
  `curl -sO <raw>/ai/build_reel.py && python3 build_reel.py spec.json out` (use background:true and poll; ~2–4 min).
- Inspect out/cover.jpg and 2 frames with image_paths: captions readable, nothing cut off. Fix spec once if needed.
- Upload: media_upload (video/mp4) → append the curl PUT to the same sandbox command → media_confirm → public URL.

## 6. Caption + hashtags (IG and FB)
- Line 1: the hook as a question or statement (≤ 12 words) + 1 emoji.
- Line 2: the engagement ask (comment X / send to someone).
- Line 3: "Curious what your soulmate looks like? Link in bio ✨" (FB: "… 👉 https://soulmatesigns.org").
- 5–8 hashtags: 2 broad (#soulmate #relationships) + 3 topic (#limerence #attachmentstyle …) + 1–2 from today's trend list.
- Never claim the images are psychic drawings or from Tina.

## 7. Post
- Use the normal reel publishing steps in RUNBOOK.md (Instagram 7, Facebook 7b) with video_url = the Higgsfield public URL.
- Log to data/performance.csv with format "ai-luna" and the topic; spec + URLs in ai_reels/NNN/.

## Budget guard
- Max 2 AI reels per day; stop making AI reels when the Higgsfield balance < 120 (keeps the AI-host budget).
- If Higgsfield tools are unavailable in a run, post a code-template reel instead and log it.
