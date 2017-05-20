
import tweepy
from cocktaildb import *


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
            i = 139
            while message[i] != ' ':
                i -= 1
            self.post_tweet(message[:i], reply_id)
            m = message[i + 1:]
            return self.post_long_tweet(m, reply_id)
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


if __name__ == '__main__':
    main()
