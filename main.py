import requests
import re
from datetime import datetime
import time
import BotpySE as bp
import cbenv

email = cbenv.email
password = cbenv.password

commands = bp.all_commands

websiteWhitelist = [
    '(meta\.|(meta\.|)[a-z]*\.|)(stackoverflow|stackexchange)',
    'i\.stack\.imgur\.com',
    'developer\.mozilla\.org',
    'docs\.microsoft\.com',
    'docs\.python\.org',
    'issues\.apache\.org',
    'jsfiddle\.net',
    'php\.net'
]

keywordBlacklist = [
    'fu(c|)k',
    'shit',
    'downvote'
]

websiteRegex = '.*<a href=\"http(|s):\/\/(?!' + '|'.join(websiteWhitelist) + ')'

keywordRegex = '(' + ')|('.join(keywordBlacklist) + ')'

bot = bp.Bot('CharlieB', commands, [57773], [], 'stackexchange.com', email, password)

def cbm(msg):
    bot.post_global_message('[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] ' + msg)

l = set()
def pullcomments():
    s = datetime.now()
    comments = requests.get('http://api.stackexchange.com/2.2/comments?page=1&pagesize=75&key=IAkbitmze4B8KpacUfLqkw((&order=desc&sort=creation&site=stackoverflow&filter=!SWK9z*gpvuT.wQS8A.').json() 
    items = comments['items']
    a = b = c = 0
    for i in items:
        data = items[a]
        if data['owner']['reputation'] < 50:
            if data['comment_id'] in l:
                c = c + 1
            else:
                if re.match(websiteRegex, data['body']):
                    cbm('Website Detected | [Comment]({}): `{}`'.format(data['link'], data['body']))
                    b = b + 1
                    l.add(data['comment_id'])
                elif re.match(keywordRegex, data['body']):
                    cbm('Keyword Detected | [Comment]({}): `{}`'.format(data['link'], data['body']))
                    b = b + 1
                    l.add(data['comment_id'])
        a = a + 1
    print('{} Scanned: {} | New Matched: {} | Previously seen: {} | Quota: {}'.format(datetime.now(), a, b, c, comments['quota_remaining']))
    s = datetime.now() - s
    s = s.total_seconds()
    s = 60 - s
    time.sleep(s)

bot.start()

while True:
    pullcomments()
