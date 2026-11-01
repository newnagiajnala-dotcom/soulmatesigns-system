# AI host test 001 (1 Nov 2026) — not posted yet

Host: Look 1 (auburn hair, freckles). Character sheet job ae128733-e0ed-49b0-a579-4d835f9bb023;
candlelit selfie image job aee6eba7-d8be-4d94-bda4-2dd9fbc3cd90. Voice: seed_audio preset "Willow"
(f878bf3f-115b-5842-8934-c789c7947733).

Pipeline (works):
1. seed_audio hook line (~6 s): 1.5 credits
2. intone 720p, 9:16, image_references = [character sheet, location/selfie image] + audio_references = [hook]: 49 credits for ~6 s
   (grok_video_v15 fails on this face, no charge; 1080p intone ≈ 2.3x price)
3. Higgsfield sandbox: stitch hook (caption burned at top) + sign_reel body (skip_intro) → upload to Higgsfield storage.
   Our cloud workspace can't reach Higgsfield's CDN, so stitching happens in the Higgsfield sandbox.
Final: https://d2ol7oe51mr4n9.cloudfront.net/user_3EzwJnQsE5b12PUKFrt1rTGUePG/772dd25c-a160-466d-94f2-0e3c880903e2.mp4 (15.2 s)
Cost of this test incl. failed tries: ~50.5 credits. Ongoing per hybrid reel: ~51 credits → ~10 more from 545.
Rules: caption must say the host is AI (e.g. "AI host ✨"); turn on Instagram's AI label; no claims she is a real psychic.

## Full version (22.1 s, 0 extra credits)
https://d2ol7oe51mr4n9.cloudfront.net/user_3EzwJnQsE5b12PUKFrt1rTGUePG/e091f110-ff78-4b60-8e64-06084c685b3b.mp4
0–7 s host hook (caption + "AI host" tag) → 7–17.5 s sign body (3 messages, CTA) → 17.5–22 s slow zoom on host selfie,
"Type 222 below / Curious what your soulmate looks like? Link in bio". One music bed (emotional, seed 21), ducked under voice, −16 LUFS.
Built with Higgsfield sandbox h1/build.sh (cap output with -t; apad makes audio infinite).
