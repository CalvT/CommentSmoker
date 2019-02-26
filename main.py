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
botHeader = '[ [CommentSmoker](https://github.com/CalvT/CommentSmoker) ] '
rooms = [57773]
bot = bp.Bot('CharlieB', commands, rooms, [], site, email, password)


# Bot Message System
cbm_queue = {}


def cbmG(msg):
    cbm_queue[datetime.now()] = (botHeader + msg)


def cbm():
    while len(cbm_queue) > 0:
        t = list(cbm_queue)[0]
        bot.post_global_message(cbm_queue[t])
        del cbm_queue[t]
        time.sleep(5)


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
        result = 3
    elif regex.search(chqKR, scan):
        result = 4
    elif regex.search(wR, scan):
        result = 1
    elif regex.search(kR, scan):
        result = 2
    else:
        result = 0
    return result


messages = {
    1: 'Website Detected | [Comment: {}]({}): `{}`',
    2: 'Keyword Detected | [Comment: {}]({}): `{}`',
    3: 'Charcoal Website Detected | [Comment: {}]({}): `{}` @CalvT',
    4: 'Charcoal Keyword Detected | [Comment: {}]({}): `{}` @CalvT'
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
def smokedetector(site):
    items = puller(site)
    a = b = c = 0
    for data in items:
        a += 1
        if data['comment_id'] not in cIDs:
            x = scanner(data['body'])
            cIDs.add(data['comment_id'])
            if x > 0:
                cbmG(messages.get(x).format(site, data['link'], data['body']))
                b += 1
        else:
            c += 1
    cRT.append(c)
    print(
        '{} Site: {} | Scanned: {} | New Matched: {} | Previously seen: {}'
        .format(datetime.now(), site, a, b, c))


cIDs = set()
cRT = [30, 30, 30, 30, 30, 30, 30, 30, 30, 30]


def runtime():
    while True:
        s = datetime.now()
        smokedetector('stackoverflow')
        smokedetector('stackapps')
        cbm()
        s = datetime.now() - s
        s = s.total_seconds()
        d = sum(cRT[-10:]) / 10
        s = 40 - s + d
        print(str(s) + " | " + str(d))
        time.sleep(s)


# Run Bot
bot.start()
runtime()
