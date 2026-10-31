"""Builds research/top-reels.csv — breakdown of 129 reels with 100K+ views (scanned 31 Oct 2026).
Notes are our own analysis/paraphrase; no scripts or media are copied."""
import csv

def fmt(v):
    return v

# Reels viewed and analysed individually: id -> (account, views, format, hook_pattern, thumbnail, cta, why, our_idea)
A = {
 # zodiacbear — label memes
 "CyjCitot320": ("zodiacbear", 40_900_000, "Label meme", "Two kids reacting; signs split 6 vs 6 over each kid", "Frozen reaction frame, white sign lists on both sides", "Send to friends", "Every viewer finds their sign instantly → shares to 'the other half'", "Text-chat meme: 'how 6 signs vs the other 6 reply to I miss you'"),
 "CxtDo1ItULG": ("zodiacbear", 25_400_000, "Label meme", "'There are two types of wives' + 6 signs on one person", "Bold black-on-white title box top, sign list mid-frame", "Send to friends", "Relationship identity + 'which type am I' → tags partner", "'Two types of girlfriends' illustrated scene, our art"),
 "Cxn7XCoNdLC": ("zodiacbear", 7_000_000, "Label meme", "Late-night relatable situation ('3am and she won't sleep') + 2 sign groups", "Situation text top, two sign stacks", "Send to bestie", "Hyper-specific relatable moment = friend tagging", "'3am texts: fire signs vs water signs' chat screenshot reel"),
 "Cy1GIHUtOVY": ("zodiacbear", 6_900_000, "Label meme", "'Two types of best friends' — two people, 6+6 signs", "Rounded title pill top, sign stacks over each person", "Send to friends", "Splits ALL 12 signs → nobody is left out", "'Two types of best friends at a party' original illustration"),
 "C1H8LnkCFsf": ("zodiacbear", 4_800_000, "Label meme", "Over-confident performer clip labelled with 5 signs", "Sign list in white box beside face", "Send to friends", "Roast humour — people tag friends of those signs", "'Signs when they think they can sing' cartoon"),
 "CwstqrzNhU_": ("zodiacbear", 3_200_000, "Label meme", "Group scene, each person a different sign pair", "Question text top, signs labelled per person", "Send to friends", "Multi-character = more signs represented", "'Group chat when someone says lets plan a trip' by sign"),
 "Cy8_xoNN0Qf": ("zodiacbear", 3_100_000, "Trend/news tribute", "Celebrity tribute tied to that week's news", "Tribute frame", "Follow", "Rode a trending moment", "Skip (needs news + footage)"),
 "CxyRcOKNI9s": ("zodiacbear", 2_600_000, "Label meme", "'What he thought he was getting' + 6 signs (expectation vs reality)", "Big white caption top, sign list on clip", "Send to friends", "Expectation/reality twist + relationship angle", "'What he expected vs what he got: dating a Scorpio' 2-panel"),
 "C1AI-mBC_ky": ("zodiacbear", 2_500_000, "Label meme", "'Every trio has…' + 4 signs", "Caption mid-lower in white + red sign names", "Send to friends", "Friend-group identity → sent to the group chat", "'Every friend group has these 4 signs' card reel"),
 "Cx3VxvMN0Ve": ("zodiacbear", 2_500_000, "Label meme", "Chaotic person: 'I need an ADULT!' + 6 signs", "Two-line caption top, sign stack left", "Send to friends", "Self-roast humour, relatable chaos", "'Signs trying to do adult tasks' chat meme"),
 "Cxvou2JtotM": ("zodiacbear", 2_400_000, "Label meme", "'Bestie I got…' vs '*Me' — two characters, 6+6 signs", "Two labels with arrows, sign stacks", "Send to bestie", "Duo dynamic = send to your duo", "'Bestie energy: 6 signs vs 6 signs' text reel"),
 "CxqiVcDtGA8": ("zodiacbear", 2_200_000, "Label meme", "'The zodiac signs as best friends…' 6 vs 6", "Title top, sign stacks left/right", "Send to friends", "Same 6-vs-6 split template", "Same template, original visuals"),
 "Cz4MB75C-p2": ("zodiacbear", 1_300_000, "Label meme", "'Kids as zodiac signs explaining love'", "Kid frame with sign label", "Send to friends", "Love + cuteness", "'Signs explaining love in 5 words' text cards"),
 # thekaurcards — tarot / interactive
 "DUn0IFID_Ho": ("thekaurcards", 763_000, "Pick-a-pile (birth month)", "'Who will you marry? Choose your bday month'", "Red box headline + white subheading over reader", "Comment / save", "Forces a personal choice; marriage curiosity", "Faceless: month list over dreamy b-roll → 'link in bio to see their face'"),
 "DPGzlPiEYDG": ("thekaurcards", 271_000, "Timely reading", "'New beginning or same story repeating? Your love life this month'", "Red question box + month banner", "Comment", "Timely (this month) + emotional question", "'Your love life in November' monthly series"),
 "DY4vml7Mjzv": ("thekaurcards", 258_000, "Pick-a-pile", "'Will you marry the person in your mind?'", "Navy + white two-line box", "Comment", "Everyone has 'a person' — direct curiosity", "Text: 'Will you end up with the person you're thinking of? Pick 1, 2, 3'"),
 "DVUYHeFE6tS": ("thekaurcards", 239_000, "Reassurance", "'Stop worrying, everything is working out'", "Text box over reader", "Save", "Comfort content gets saved", "Calm night-sky reel with reassurance text"),
 "DQ_w9TjkSuF": ("thekaurcards", 223_000, "Reassurance", "'This message didn't reach you by accident'", "Text box", "Save/share", "Personal destiny framing", "'If this found you at 11:11…' reel"),
 "DQecVxXEgeK": ("thekaurcards", 170_000, "Faceless b-roll + text", "'Your no-contact situation' over POV hand out car window", "Black text box on moving b-roll", "Comment", "Faceless, emotional situation", "Same style: our own b-roll/animated sky + situation text"),
 "DQJoTcbkW4E": ("thekaurcards", 118_000, "Pick-a-card (birth date)", "Cards by birth-date numbers: 'karmic person'", "Card numbers listed", "Comment", "Number groups = everyone included", "'Born on 1–10, 11–20, 21–31: your soulmate's first letter'"),
 "DUgMwk4ASC2": ("thekaurcards", 115_000, "List", "'3 signs someone is manifesting you'", "Text box", "Save", "Hopeful + listable", "'3 signs your soulmate is near' text reel"),
 # readswithtishh — sketch
 "DUnxepqCTMm": ("readswithtishh", 898_000, "Sketch offer + comment bait", "'I can sketch your future spouse!'", "Magenta box hook over artist at work", "Comment to get it (27K comments)", "Direct offer + curiosity + comment trigger", "'Want to see your soulmate's face? Comment SKETCH' (honest, link in bio)"),
 "Db8TaKkpU4h": ("readswithtishh", 253_000, "Sketch offer + comment bait", "Same hook re-posted", "Same magenta box", "Comment (8.7K)", "Re-posting a winner works", "Re-post our best hook weekly"),
 # fett.astrology — zodiac rankings
 "DZ06F9hMJMv": ("fett.astrology", 415_000, "Zodiac list (talking head)", "'Three zodiac signs it's impossible not to fall in love with'", "Big white caps caption in dark pill + emojis", "Follow", "Flattering identity list", "Same list as faceless text-on-art reel"),
 "DRnxxL5jFtW": ("fett.astrology", 363_000, "AI cinematic image + kinetic text", "'There is one zodiac…' (suspense)", "AI angel image, yellow/white bold word-by-word captions", "Follow", "Suspense: viewers wait to see if it's their sign", "Code-made cinematic art + 'There is ONE sign who…'"),
 "DZnvcU9sbZ3": ("fett.astrology", 340_000, "Zodiac list (talking head)", "'Three zodiac signs you should marry the second you meet them'", "White caps in dark pill + ring emojis", "Comment", "Marriage + flattering list", "Faceless version with soulmate CTA"),
 "DRVY-YkEamI": ("fett.astrology", 309_000, "Zodiac tribute", "Sign tribute ('they prepare you for war')", "Cinematic image + bold text", "Follow", "Identity pride", "'The sign that loves the hardest' tribute"),
 "DRlHKT0jBV5": ("fett.astrology", 306_000, "AI cinematic image + kinetic text", "'The most powerful aura in the zodiac'", "AI dark queen on throne, yellow/white caps", "Follow", "Power/identity + suspense reveal", "'The sign with the strongest soulmate energy'"),
 # tech.oak — comment-for-link tools
 "DeFLadUz8ha": ("tech.oak", 3_300_000, "Tool demo + comment for link", "AI hairstyle tool demo", "Before/after face", "Comment keyword (71K)", "Comment trigger + useful tool", "'Comment SOULMATE for the link' (only if auto-DM set up)"),
 "DemgeFiz36L": ("tech.oak", 743_000, "Tool demo + comment for link", "'Attractiveness score' tool", "Score on screen", "Comment (23K)", "Self-curiosity", "—"),
}

REST = {
 "zodiacbear": [("C-x8bCKCSuF",13.3e6),("C_JTAlZikyA",7.2e6),("C-8nJOZCTpm",5.9e6),("C1C7lsGCz-M",2.0e6),("C2F0yeLC2g4",1.8e6),("C6W5OtICD4o",1.6e6),("C1FpUzliBNt",1.6e6),("DCPt_n_CSTz",1.5e6),("DAGw6qjCq7i",1.5e6),("CxLyHfitSaS",1.5e6),("CzeU1LetIJZ",1.3e6),("Cz5_pBYN8qA",1.1e6),("CyGsmBLtWwn",1.1e6),("DBRvrt9CqA3",1.0e6),("DAwYAaXiISq",1.0e6),("Cw8GFkPtbGF",1.0e6),("CwqFS3OteU5",927e3),("CyBq_L4t0qo",906e3),("Cx0z7wPtZzN",855e3),("C0aGz8_CNgP",841e3),("C1z10zYixOE",833e3),("Cx_CFQ3NNR7",827e3),("CwnY3mgtdUy",786e3),("CzEmEBJNVin",750e3),("C0XiBeMCF_e",741e3),("CyOYSkyNd85",720e3),("CyL5Wt-ruiR",692e3),("CzWppCbNNF_",691e3),("C1pcEwICKFA",680e3),("DEVitP9ifJP",677e3),("C6hEz3pi_0Z",676e3),("C1kS5o0iVm8",662e3),("C-ia-IxiqSi",660e3),("Cwk1stztBj9",638e3),("C17eLg2CYH4",608e3),("C0U39H5CmpL",597e3),("C1Kpd4gCYay",592e3),("C1X1sqhiBsB",568e3),("C4qq3o6CkTa",528e3),("CxduvVrtBl2",469e3),("C0C-bzACjTX",440e3),("C1SW285CkM-",433e3),("C1NX1uuiEY6",427e3),("C_G3lvCiSGV",426e3),("C4Yvq2OiqU6",408e3),("Cygf2X-Nb0N",398e3),("Cx8Z350ti0t",374e3),("CxQusuqNR2M",361e3),("C0pEq0niBKO",352e3),("C4EFogDiyA4",331e3),("C-c7z_PirNu",318e3),("C1xNd6Fiw9p",307e3),("DFgTNUUikfQ",299e3),("C07GT1CioJj",296e3),("CwiiGtbtJDq",292e3),("C1m93z4ijuN",291e3),("CyTp0Rdtmt_",289e3),("CxGicuvNOrC",283e3),("Cyqva5xtWlK",275e3),("C_ETWsyChsz",266e3),("C0KbsMKLqCY",266e3),("CyWcKmyNUYF",263e3),("CzzCJTvCskE",262e3),("C1Pqpm7CUdz",261e3),("C2DM_LiCBuh",251e3),("C3dX0utts8Z",224e3),("CxizMa-NK2N",224e3),("DKIQHViimQY",202e3),("DAtkLOkCGq2",198e3),("C2Aw_dEi9qM",198e3),("C3Dx8giidsr",196e3),("C7uILoCC6o5",195e3),("C04dhpFC-6E",190e3),("DUlyJU5CpLr",183e3),("C35spC-CEre",183e3),("DLk-lscCN6N",182e3),("C1ckgrBiM3W",163e3),("C92unwZirXz",162e3),("C1fR6KhiuyS",130e3),("DCC3Um3iJ4L",126e3),("DG9DohHC1Bt",119e3)],
 "fett.astrology": [("DSTcVBqjKSx",198e3),("DRidPWbDWDj",146e3),("DaEXA6ls56D",114e3),("DRxrhk_knaw",113e3),("DR0grvlDJ3n",109e3)],
 "tech.oak": [("DepCg3uztkp",610e3),("Debngi7TS5G",472e3),("Ddteu9hTQya",307e3),("DeekImqTWtr",294e3),("Demg_U-T6jZ",159e3),("De1tf_EydsG",152e3),("DbVj43bz1_m",138e3),("DezAA4fThFp",104e3)],
 "glossy_zodiac": [("DRkNs5LinyE",156e3),("DRnyLdJitzT",114e3),("DRsvvLBikHG",113e3),("DRveyWtCvX6",100e3)],
}
TEMPLATE = {
 "zodiacbear": ("Label meme (account template)", "6-vs-6 sign split over a relatable scene", "Title box + sign stacks", "Send to friends / tag", "Same proven template", "Original text/illustration version"),
 "fett.astrology": ("Zodiac list/tribute (account template)", "Zodiac ranking or tribute", "Bold caps captions", "Follow / comment", "Identity + suspense", "Faceless text-on-art version"),
 "tech.oak": ("Tool demo + comment for link (account template)", "Curiosity tool demo", "Result on screen", "Comment keyword", "Comment trigger", "—"),
 "glossy_zodiac": ("Sponsored collab", "Brand promo", "Lifestyle frame", "—", "Big account reach, not format", "—"),
}

rows = []
for rid, (acc, views, fmt_, hook, thumb, cta, why, idea) in A.items():
    rows.append([acc, rid, f"https://www.instagram.com/reel/{rid}/", int(views), fmt_, hook, thumb, cta, why, idea, "yes"])
for acc, items in REST.items():
    f, h, t, c, w, i = TEMPLATE[acc]
    for rid, v in items:
        if rid in A:
            continue
        rows.append([acc, rid, f"https://www.instagram.com/reel/{rid}/", int(v), f, h, t, c, w, i, "no (account template)"])
rows.sort(key=lambda r: -r[3])
with open("research/top-reels.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["account","reel_id","url","views","format","hook_pattern","thumbnail_style","cta","why_it_worked","our_original_idea","viewed_individually"])
    w.writerows(rows)
print(len(rows), "rows;", sum(1 for r in rows if r[3] >= 1_000_000), "over 1M;", sum(1 for r in rows if r[10]=="yes"), "analysed individually")
