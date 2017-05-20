
import requests
import json
import tweepy


class MentionReader(tweepy.StreamListener):
    def __init__(self, api):
        tweepy.StreamListener.__init__(self, api)

    def on_status(self, status):
        if status:
            mentions = status.entities[u'user_mentions']
            if mentions:
                for mention in mentions:
                    if mention[u'screen_name'] == u'pbzweihander':
                        self.handle_stream_mention(status)
                        break

    def on_error(self, status_id):
        print("stream error : %s" % status_id)
        return True

    def on_timeout(self):
        print("stream timeout")

    def handle_stream_mention(self, mention):
        if mention:
            print("mention read : %s - %s" % (mention.id, mention.text))
            if u'c!' in mention.text:
                name = mention.text.split(u'c!')[1].strip()
                print("finding cocktail : %s" % name)
                if name:
                    if name == 'random':
                        s = random_cocktails()
                        if s:
                            self.post_long_tweet(s, mention.id)
                    else:
                        s = find_cocktails(name)
                        if s:
                            self.post_long_tweet(s, mention.id)
            elif u'i!' in mention.text:
                name = mention.text.split(u'i!')[1].strip()
                print("finding ingredient : %s" % name)
                if name:
                    s = find_ingredient(name)
                    if s:
                        self.post_long_tweet(s, mention.id)

    def post_long_tweet(self, message, reply_id=None):
        if len(message) > 140:
            s = self.post_tweet(message[:140], reply_id)
            m = message[140:]
            return self.post_long_tweet(m, s.id)
        else:
            return self.post_tweet(message, reply_id)

    def post_tweet(self, message, reply_id=None):
        msg = message
        print("post tweet : %s" % message)
        try:
            s = self.api.update_status(status=msg, in_reply_to_status_id=reply_id)
        except Exception as e:  # twitter.TwitterError as e:
            print(e)
            return None
        return s

    def post_media(self, message, media, reply_id=None):
        msg = message
        try:
            s = self.api.update_with_media(media, status=msg, in_reply_to_status_id=reply_id)
        except Exception as e:
            print(e)
            return None
        return s


def main():
    ck = ""
    cs = ""
    atk = ""
    ats = ""
    try:
        with open("token.key", 'r') as f:
            ck = f.readline()[:-1]
            cs = f.readline()[:-1]
            atk = f.readline()[:-1]
            ats = f.readline()[:-1]
            ck.strip()
            cs.strip()
            atk.strip()
            ats.strip()
    except Exception as e:
        print(e)
        print("token load failed")
        return
    print("token loaded")
    auth = tweepy.OAuthHandler(ck, cs)
    auth.set_access_token(atk, ats)
    api = tweepy.API(auth)
    mr = tweepy.Stream(auth, MentionReader(api), timeout=None)
    print("bot starting")
    mr.userstream()
    print("bot closed")


def find_cocktails(name: str) -> str:
    dlist = get_drinklist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?s=" + name)
    if dlist[0].get('strDrink').strip().lower() == name.lower():
        return parse_cocktail(dlist[0])
    else:
        nlist = [d.get('strDrink') for d in dlist]
        if len(nlist) < 8:
            return ', '.join(nlist)
        else:
            return ', '.join(nlist[:8])


def random_cocktails() -> str:
    dlist = get_drinklist(r"http://www.thecocktaildb.com/api/json/v1/1/random.php")
    d = dlist[0]
    return parse_cocktail(d)


def parse_cocktail(d: dict) -> str:
    name = d.get('strDrink').strip()
    if not name:
        return ""
    glass = (d.get('strGlass') or "").strip()
    ingredients = []
    measures = []
    for i in range(1, 16):
        ii = d.get("strIngredient%s" % i).strip()
        mm = d.get("strMeasure%s" % i).strip()
        if len(ii) > 0 and len(mm) > 0:
            ingredients.append(ii)
            measures.append(mm)
    instruction = (d.get("strInstructions") or "").strip()
    s = name + '\n'
    if glass:
        s += glass + '\n'
    for i, m in zip(ingredients, measures):
        s += i + ' - ' + m + '\n'
    s += instruction
    return s


def get_drinklist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        dl = json.loads(r.text).get('drinks')
        if dl:
            return list(dl)
    return []


def find_ingredient(name: str) -> str:
    dlist = get_ingredientlist(r"http://www.thecocktaildb.com/api/json/v1/1/search.php?i=" + name)
    if not dlist:
        return ""
    if dlist[0].get('strIngredient').strip().lower() == name.lower():
        return parse_ingredient(dlist[0])
    else:
        nlist = [d.get('strIngredient') for d in dlist]
        if len(nlist) < 8:
            return ', '.join(nlist)
        else:
            return ', '.join(nlist[:8])


def parse_ingredient(d: dict) -> str:
    print(d)
    name = d.get('strIngredient').strip()
    if not name:
        return ""
    stype = (d.get('strType') or "").strip()
    description = (d.get("strDescription") or "").strip()
    s = name + '\n'
    if stype:
        s += 'Type : ' + stype + '\n'
    s += description
    return s


def get_ingredientlist(url: str) -> list:
    r = requests.get(url)
    if len(r.text) > 0:
        il = json.loads(r.text).get('ingredients')
        if il:
            return list(il)
    return []


if __name__ == '__main__':
    main()
