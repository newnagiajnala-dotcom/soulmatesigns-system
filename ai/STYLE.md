# Style bible — "Luna" AI reels (keep EVERY image consistent)

Mascot reference (Higgsfield image job, pass as image_references on every scene):
  819ef1ca-8aec-4450-a5aa-01a0362d05ca   (backup sheet: 6d2890c1-05e7-4666-bb04-9810c7f43450)

Characters (original — do not imitate other creators' mascots):
- LUNA: small soft rose-pink 3D clay figure, rounded bean body, round head, no mouth, two tiny dark oval eyes,
  small glowing golden crescent moon floating above her head, short stubby arms/legs. She is "you" (the viewer).
- BLUE: same clay style, soft sky-blue, slightly taller, no moon. He/she is "them" (crush / ex / soulmate).
- Extra people only as faint grey clay silhouettes.

Fixed prompt blocks (copy exactly; only SCENE changes):
  PREFIX = "Vertical 9:16 frame. Same characters as the reference image: Luna (rose-pink clay figure with a glowing golden crescent moon above her head) "
           "and Blue (sky-blue clay figure). "
  SCENE  = "<one concrete action, props, mood — e.g. 'Luna sits on her bed at night staring at a glowing phone that says typing…, Blue appears as a soft reflection in the window'>"
  SUFFIX = " Setting: deep navy-to-violet starry night with soft pink nebula glow and a glossy reflective floor. Soft pastel 3D clay render, "
           "gentle rim light, cinematic soft lighting, centered subject in the middle third (top and bottom thirds calm for captions). No text, no letters, no logos."

Rules: 4 scenes per reel (hook / tension / payoff / CTA). Characters always centered in the middle third.
Never put words in the image (captions are added in editing). Model: gpt_image_2_5, aspect_ratio 9:16, count 1 per scene.
