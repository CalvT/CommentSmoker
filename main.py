import requests
import re
from datetime import datetime
import time
import BotpySE as bp
import cbenv

email = cbenv.email
password = cbenv.password

commands = bp.all_commands

websiteWhitelist = open('websiteWhitelist.txt').read().splitlines()

keywordBlacklist = open('keywordBlacklist.txt').read().splitlines()

websiteRegex = '.*<a href=\"http(s):\/\/(?!(www\.|)(' + '|'.join(websiteWhitelist) + '))'

keywordRegex = '(' + ')|('.join(keywordBlacklist) + ')'

bot = bp.Bot('CharlieB', commands, [57773], [], 'stackexchange.com', email, password)

def cbm(msg):
    bot.post_global_message('[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] ' + msg)

def scanner(scan):
    if re.match(websiteRegex, scan):
        return 1
    elif re.match(keywordRegex, scan):
        return 2
    else:
        return 0
    
messages = {
    1:'Website Detected | [Comment]({}): `{}`',
    2:'Keyword Detected | [Comment]({}): `{}`'
}

def smokedetector():
    comments = requests.get('http://api.stackexchange.com/2.2/comments?page=1&pagesize=75&key=IAkbitmze4B8KpacUfLqkw((&order=desc&sort=creation&site=stackoverflow&filter=!SWK9z*gpvuT.wQS8A.').json() 
    items = comments['items']
    a = b = c = 0
    for i in items:
        data = items[a]
        if data['owner']['reputation'] < 50:
            if data['comment_id'] in l:
                c = c + 1
            else:
                x = scanner(data['body'])
                l.add(data['comment_id'])
                if x > 0:
                    cbm(messages.get(x).format(data['link'], data['body']))
                    b = b + 1
        a = a + 1
    print('{} Scanned: {} | New Matched: {} | Previously seen: {} | Quota: {}'.format(datetime.now(), a, b, c, comments['quota_remaining']))

l = set()
def pullcomments():
    s = datetime.now()
    smokedetector()
    s = datetime.now() - s
    s = s.total_seconds()
    s = 60 - s
    time.sleep(s)

bot.start()

while True:
    pullcomments()
