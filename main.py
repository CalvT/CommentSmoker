import requests
import regex
from datetime import datetime
import time
import BotpySE as bp
import cbenv

# Bot Variables
email = cbenv.email
password = cbenv.password
commands = bp.all_commands
site = 'stackexchange.com'
botHeader = '[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] '
bot = bp.Bot('CharlieB', commands, [57773], ['runtime()'], site, email, password)


# Bot Message Handler
def cbm(msg):
    bot.post_global_message(botHeader + msg)


# Regex Generation
chqGH = 'https://raw.githubusercontent.com/Charcoal-SE/SmokeDetector/master/'

chqW = requests.get(chqGH + 'blacklisted_websites.txt').text.splitlines()
chqWR = r'(?i)({})'.format('|'.join(chqW))

chqK = requests.get(chqGH + 'bad_keywords.txt').text.splitlines()
chqKR = r'(?is)(?:^|\b|(?w:\b))(?:{})'.format('|'.join(chqK))

wW = open('websiteWhitelist.txt').read().splitlines()
wR = r'.*<a href=\"http(s):\/\/(?!(www\.|)(' + '|'.join(wW) + '))'

kB = open('keywordBlacklist.txt').read().splitlines()
kR = r'(' + ')|('.join(kB) + ')'


# Comment Scanner
def scanner(scan):
    if regex.search(chqWR, scan):
        return 3
    elif regex.search(chqKR, scan):
        return 4
    elif regex.search(wR, scan):
        return 1
    elif regex.search(kR, scan):
        return 2
    else:
        return 0


messages = {
    1: 'Website Detected | [Comment]({}): `{}`',
    2: 'Keyword Detected | [Comment]({}): `{}`',
    3: 'Charcoal Website Detected | [Comment]({}): `{}`',
    4: 'Charcoal Keyword Detected | [Comment]({}): `{}`'
}


# Get Comments
def puller(site):
    comments = requests.get(
        'http://api.stackexchange.com/2.2/comments?'
        'page=1'
        '&pagesize=75'
        '&key=IAkbitmze4B8KpacUfLqkw(('
        '&order=desc'
        '&sort=creation'
        '&site=' + site +
        '&filter=!SWK9z*gpvuT.wQS8A.'
    ).json()
    return comments['items']


# Connect All Functions
def smokedetector():
    items = puller('stackoverflow')
    a = b = c = 0
    for data in items:
        a += 1
        if data['comment_id'] not in cIDs:
            x = scanner(data['body'])
            cIDs.add(data['comment_id'])
            if x > 0:
                cbm(messages.get(x).format(data['link'], data['body']))
                b += 1
        else:
            c += 1    
    cRT.append(c)
    print(
        '{} Scanned: {} | New Matched: {} | Previously seen: {}'
        .format(datetime.now(), a, b, c))


cIDs = set()
cRT = []


def runtime():
    while True:
        s = datetime.now()
        smokedetector()
        s = datetime.now() - s
        s = s.total_seconds()
        d = sum(cRT[-10:]) / 10
        s = 40 - s + d
        time.sleep(s)


# Run Bot
bot.start()
