import requests
import re
from datetime import datetime
import time
import BotpySE as bp
import cbenv

# Bot Variables
email = cbenv.email
password = cbenv.password
commands = bp.all_commands
bot = bp.Bot('CharlieB', commands, [57773], [], 'stackexchange.com', email, password)


# Bot Message Handler
def cbm(msg):
    bot.post_global_message('[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] ' + msg)


# Website Regex Generation
websiteWhitelist = open('websiteWhitelist.txt').read().splitlines()
websiteRegex = '.*<a href=\"http(s):\/\/(?!(www\.|)(' + '|'.join(websiteWhitelist) + '))'


# Keyword Regex Generation
keywordBlacklist = open('keywordBlacklist.txt').read().splitlines()
keywordRegex = '(' + ')|('.join(keywordBlacklist) + ')'


# Comment Scanner
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


# Get Comments
def puller(site):
    comments = requests.get('http://api.stackexchange.com/2.2/comments?page=1&pagesize=75&key=IAkbitmze4B8KpacUfLqkw((&order=desc&sort=creation&site=' + site + '&filter=!SWK9z*gpvuT.wQS8A.').json()
    return comments['items']


# Connect All Functions
def smokedetector():
    items = puller('stackoverflow')
    a = b = c = 0
    for data in items:
        a += 1
        if data['comment_id'] not in l:
            x = scanner(data['body'])
            l.add(data['comment_id'])
            if x > 0:
                cbm(messages.get(x).format(data['link'], data['body']))
                b += 1
        else:
            c += 1
    print('{} Scanned: {} | New Matched: {} | Previously seen: {}'.format(datetime.now(), a, b, c))


l = set()


def runtime():
    s = datetime.now()
    smokedetector()
    s = datetime.now() - s
    s = s.total_seconds()
    s = 60 - s
    time.sleep(s)

# Run Bot
bot.start()


while True:
    runtime()
