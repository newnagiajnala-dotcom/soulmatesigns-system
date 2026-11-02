"""Daily trend finder (runs in the soulmate-ig environment).
Uses the Instagram Graph API hashtag endpoints (the env secret adds the token). Max 30 unique hashtags per 7 days:
we rotate 6 per day from a pool of 30 (5-day cycle).
Output: data/trends/<date>.json with top posts (likes, comments, caption hook) and topic scores.
usage: python3 ai/trends.py YYYY-MM-DD
"""
import json, re, sys, datetime as dt, urllib.request, urllib.parse
API = "https://graph.facebook.com/v21.0"; IG = "17841459940404036"
POOL = ["soulmate","soulmatesigns","twinflame","twinflames","redstring","invisiblestring","limerence","attachmentstyle",
        "anxiousattachment","avoidantattachment","angelnumbers","1111","222","manifestlove","lawofattraction","zodiaclove",
        "zodiaccompatibility","astrologymemes","tarotreading","pickacard","situationship","datingadvice","relationshipadvice",
        "lovepsychology","psychologyfacts","healingjourney","yourperson","futurehusband","soulmatesketch","spiritualawakening"]
def get(path, **q):
    url = f"{API}/{path}?" + urllib.parse.urlencode(q)
    with urllib.request.urlopen(url, timeout=30) as r: return json.load(r)
def main(day):
    d = dt.date.fromisoformat(day); k = d.toordinal() % 5
    tags = POOL[k*6:(k+1)*6]; posts = []
    for t in tags:
        try:
            hid = get("ig_hashtag_search", user_id=IG, q=t)["data"][0]["id"]
            for edge in ("top_media", "recent_media"):
                for m in get(f"{hid}/{edge}", user_id=IG, limit=50,
                             fields="caption,like_count,comments_count,media_type,permalink,timestamp").get("data", []):
                    cap = (m.get("caption") or "").strip()
                    posts.append({"tag": t, "src": edge, "type": m.get("media_type"), "likes": m.get("like_count", 0) or 0,
                                  "comments": m.get("comments_count", 0) or 0, "ts": m.get("timestamp", ""),
                                  "hook": re.split(r"[\n#]", cap)[0][:140], "url": m.get("permalink")})
        except Exception as e:
            posts.append({"tag": t, "error": str(e)[:200]})
    ok = [p for p in posts if "error" not in p]
    for p in ok: p["score"] = p["likes"] + 4 * p["comments"]
    ok.sort(key=lambda p: -p["score"])
    seen, top = set(), []
    for p in ok:
        if p["url"] in seen: continue
        seen.add(p["url"]); top.append(p)
    out = {"date": day, "hashtags": tags, "errors": [p for p in posts if "error" in p], "top": top[:40]}
    json.dump(out, open(f"data/trends/{day}.json", "w"), ensure_ascii=False, indent=1)
    print(f"ok {len(top)} posts from {tags}; errors {len(out['errors'])}")
if __name__ == "__main__": main(sys.argv[1])
