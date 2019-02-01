import requests
import re
from datetime import datetime
import time
import BotpySE as bp
import cbenv

email = cbenv.email
password = cbenv.password

commands = bp.all_commands

bot = bp.Bot("CharlieB", commands, 57773, [], "stackexchange.com", email, password)

def cbm(msg):
    bot.post_global_message('[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] ' + msg)

l = []
def pullcomments():
    s = datetime.now()
    regex = r'.*<a href=\"http(|s):\/\/(?!(meta\.|(meta\.|)[a-z]*\.|)(stackoverflow|stackexchange))'
    comments = requests.get('http://api.stackexchange.com/2.2/comments?page=1&pagesize=75&key=IAkbitmze4B8KpacUfLqkw((&order=desc&sort=creation&site=stackoverflow&filter=!SWK9z*gpvuT.wQS8A.').json() 
    items = comments['items']
    a = b = c = 0
    for i in items:
        data = items[a]
        if data['owner']['reputation'] < 50:
            if data['comment_id'] in l:
                c = c + 1
            else:
                if re.match(regex, str(data['body'])):
                    cbm('URL Detected | [Comment]({}): `{}`'.format(data['link'], data['body'])))
                    b = b + 1
                    l.append(data['comment_id'])
        a = a + 1
    cbm('{} Scanned: {} | New Matched: {} | Previously seen: {} | Quota: {}'.format(datetime.now(), a, b, c, comments['quota_remaining']))
    s = datetime.now() - s
    s = s.total_seconds()
    s = 60 - s
    time.sleep(s)

bot.start()

while True:
    pullcomments()
