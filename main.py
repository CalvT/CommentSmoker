from stackapi import StackAPI
import json
import re
from datetime import timedelta
from datetime import datetime
import time
import BotpySE as bp
import cbenv

email = cbenv.email
password = cbenv.password

commands = bp.all_commands

rooms = [57773]

bot = bp.Bot("CharlieB", commands, rooms, [], "stackexchange.com", email, password)

global t
t = datetime.now()

def cbm(cbm):
  bot.post_global_message('[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] ' + cbm)

l = []
def pullcomments():
  s = datetime.now()
  site = StackAPI('stackoverflow')
  site.key='IAkbitmze4B8KpacUfLqkw(('
  site.max_pages=1
  site.page_size=75
  regex = r'.*<a href=\"http(|s):\/\/(?!(meta\.|(meta\.|)[a-z]*\.|)(stackoverflow|stackexchange))'
  comments = site.fetch('comments', sort='creation', filter='!SWK9z*gpvuT.wQS8A.')
  items = comments['items']
  a = 0
  b = 0
  c = 0
  for i in items:
    data = items[a]
    if data['owner']['reputation'] < 50:
      if data['comment_id'] in l:
        c = c + 1
      else:
        if re.match(regex, str(data['body'])):
          msg = '[Link](' + data['link'] + ') | Rep: ' + str(data['owner']['reputation']) + ' | Comment: `' + data['body'] + '`'
          cbm(msg)
          b = b + 1
          l.append(data['comment_id'])
    a = a + 1
  cbm(str(datetime.now()) + ' Scanned: ' + str(a) + ' | New Matched: ' + str(b) + ' | Previously seen: ' + str(c) + ' | Quota: ' + str(comments['quota_remaining']))
  s = datetime.now() - s
  s = s.total_seconds()
  s = 60 - s
  time.sleep(s)

bot.start()

while True:
  pullcomments()
