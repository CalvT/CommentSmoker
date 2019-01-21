from stackapi import StackAPI
import json
import re
from datetime import timedelta
from datetime import datetime
import time
import getpass
import chatexchange
import cbenv

email = cbenv.email
password = cbenv.password
client = chatexchange.Client('stackexchange.com', email, password)

me = client.get_me()
sandbox = client.get_room(57773)
my_message = None

global t
t = datetime.now()

def cbm(cbm):
  with sandbox.new_messages() as messages:
    global t
    if datetime.now() - t > timedelta(seconds=5):
      sandbox.send_message(cbm)
      t = datetime.now()
    else:
      time.sleep(5)
      sandbox.send_message(cbm)
      t = datetime.now()

cbm('[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] Started')

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
          msg = '[ [CharlieB](https://github.com/CalvT/CommentSmoker) ] [Link](' + data['link'] + ') | Rep: ' + str(data['owner']['reputation']) + ' | Comment: `' + data['body'] + '`'
          cbm(msg)
          b = b + 1
          l.append(data['comment_id'])
    a = a + 1
  print('Found ' + str(b) + ' new comments & ' + str(c) + ' already caught out of a total of ' + str(a) + ' | Quota left: ' + str(comments['quota_remaining']))
  s = datetime.now() - s
  s = s.total_seconds()
  s = 60 - s
  time.sleep(s)

while True:
  pullcomments()
