from datetime import datetime
import BotpySE as bp
import cbenv
import multiprocessing
import regex
import requests
import subprocess
import tabulate
import time


# Bot Variables
email = cbenv.email
password = cbenv.password
site = 'stackexchange.com'
botHeader = '[ [CommentSmoker](https://github.com/CalvT/CommentSmoker) ] '
rooms = [57773]
stopscan = 0
cIDs = set()
cRT = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
manager = multiprocessing.Manager()
a = manager.dict()
b = manager.dict()
c = manager.dict()
cbmQueue = manager.dict()


# Bot Commands
class CommandAlive(bp.Command):
    @staticmethod
    def usage():
        return ['alive', 'status']

    def run(self):
        self.reply('Yes')


class CommandAmiprivileged(bp.Command):
    def usage():
        return ['amiprivileged', 'privs', 'privileges']

    def run(self):
        user_privs = self.message.user.get_privilege_type()
        if user_privs is None:
            self.reply('You do not have any privileges.')
        else:
            self.reply('You have the privilege: ' + user_privs.name)


class CommandListPrivilegedUsers(bp.Command):
    def usage():
        return ['membership', 'privileged', 'listprivileged']

    def run(self):
        privilege_list = list()

        for each_user in self.message.room.get_users():
            if each_user.get_privilege_type() is not None:
                privilege_list.append([each_user.id,
                                      each_user.get_privilege_type().name])

        table = tabulate.tabulate(privilege_list,
                                  headers=['User ID', 'Privilege level'],
                                  tablefmt='orgtbl')

        self.post("    " + table.replace('\n', '\n    '))


class CommandReboot(bp.Command):
    @staticmethod
    def usage():
        return ['reboot', 'restart']

    def privileges(self):
        return 2

    def run(self):
        self.reply('Rebooting, see you in a while.')
        bp.Utilities.StopReason.reboot = True


class CommandStop(bp.Command):
    @staticmethod
    def usage():
        return ['stop', 'shutdown']

    def run(self):
        self.reply('Goodbye, may we meet again.')
        bp.Utilities.StopReason.shutdown = True


class CommandPull(bp.Command):
    @staticmethod
    def usage():
        return ['pull']

    def privileges(self):
        return 2

    def run(self):
        output = subprocess.check_output(['git', 'pull'])
        self.reply(output.decode('UTF-8'))


class CommandHalt(bp.Command):
    @staticmethod
    def usage():
        return ['halt']

    def privileges(self):
        return 2

    def run(self):
        self.reply('Halting scanning')
        global stopscan
        stopscan = 1


class CommandScan(bp.Command):
    @staticmethod
    def usage():
        return ['scan *']

    def privileges(self):
        return 2

    def run(self):
        print('Scanning command received for ' + self.arguments[0])
        runtime(self.arguments[0])


commands = [CommandAlive,
            CommandStop,
            CommandAmiprivileged,
            CommandListPrivilegedUsers,
            CommandReboot,
            CommandPull,
            CommandHalt,
            CommandScan]


# Bot Starup
bot = bp.Bot('CharlieB', commands, rooms, [], site, email, password)
bot.start()
bot.add_privilege_type(1, "regular_user")
bot.add_privilege_type(2, "owner")


# Bot Message System
def cbmGenerator(msg):
    cbmQueue[datetime.now()] = (botHeader + msg)[:499]


def cbm():
    while len(cbmQueue) > 0:
        t = list(cbmQueue)[0]
        bot.post_global_message(cbmQueue[t])
        del cbmQueue[t]
        time.sleep(2)


# Regex Generation
chqGH = 'https://raw.githubusercontent.com/Charcoal-SE/SmokeDetector/master/'

city_list = [
    "Agra", "Amritsar", "Bangalore", "Bhopal", "Chandigarh",
    "Chennai", "Coimbatore", "Delhi", "Dubai", "Durgapur",
    "Ghaziabad", "Hyderabad", "Jaipur", "Jalandhar", "Kolkata",
    "Ludhiana", "Mumbai", "Madurai", "Patna", "Portland",
    "Rajkot", "Surat", "Telangana", "Udaipur", "Uttarakhand",
    "Noida", "Pune", "Rohini", "Trivandrum", "Thiruvananthapuram",
    "Nashik", "Gurgaon", "Kochi", "Ernakulam", "Nagpur",
    # yes, these aren't cities but...
    "India", "Pakistan",
    # buyabans.com spammer uses creative variations
    "Sri Lanka", "Srilanka", "Srilankan",
]

chqWatched = requests.get(chqGH + 'watched_keywords.txt').text
chqWd = {}
for line in chqWatched.splitlines():
    when, who, what = line.split('\t', 3)
    chqWd[what] = "when: {0} who: {1}".format(when, who)
chqWR = regex.compile(r'(?is)(?:^|\b|(?w:\b))(?:{})'
                      .format('|'.join(chqWd.keys())), city=city_list)

chqDomains = requests.get(chqGH +
                          'blacklisted_websites.txt').text.splitlines()
chqDR = regex.compile(r'(?i)({})'.format('|'.join(chqDomains)))

chqKeywords = requests.get(chqGH + 'bad_keywords.txt').text.splitlines()
chqKR = regex.compile(r'(?is)(?:^|\b|(?w:\b))(?:{})'
                      .format('|'.join(chqKeywords)))

wWebsites = open('websiteWhitelist.txt').read().splitlines()
wWR = regex.compile(r'.*<a href=\"http(s):\/\/(?!(www\.|)(' + '|'
                    .join(wWebsites) + '))')

bKeywords = open('keywordBlacklist.txt').read().splitlines()
bKR = regex.compile(r'(?is)(?:^|\b|(?w:\b))(?:{})'.format('|'.join(bKeywords)))

twR = regex.compile(r'(?is)(?:^|\b|(?w:\b))(?:downvote)')

cbmGenerator('Lists loaded')
cbm()


# Get Comments
def fetcher(site):
    comments = requests.get(
        'http://api.stackexchange.com/2.2/comments?'
        'page=1'
        '&pagesize=40'
        '&key=IAkbitmze4B8KpacUfLqkw(('
        '&order=desc'
        '&sort=creation'
        '&site=' + site +
        '&filter=!SWK9z*gpvuT.wQS8A.'
    ).json()
    return comments['items']


# Comment Scanner
def scanner(scan):
    if chqDR.search(scan):
        result = 3
    elif chqKR.search(scan):
        result = 4
    elif chqWR.search(scan):
        result = 5
#    elif wWR.search(scan):
#        result = 1
#    elif twR.search(scan):
#        result = 6
    elif bKR.search(scan):
        result = 2
    else:
        result = 0
    return result


messages = {
    1: 'Website Detected | [Comment: {}]({}): `{}`',
    2: 'Keyword Detected | [Comment: {}]({}): `{}`',
    3: 'Charcoal Website Detected | [Comment: {}]({}): `{}`',
    4: 'Charcoal Keyword Detected | [Comment: {}]({}): `{}`',
    5: 'Charcoal Watched Keyword Detected | [Comment: {}]({}): `{}`',
    6: 'Trigger Word Detected | [Comment: {}]({}): `{}`'
}


# Composer
def composer(data):
    a[data['comment_id']] = data['comment_id']
    if data['comment_id'] not in cIDs:
        x = scanner(data['body'])
        cIDs.add(data['comment_id'])
        if x > 0:
            cbmGenerator(messages.get(x)
                         .format(site, data['link'], data['body'][:250]))
            b[data['comment_id']] = data['comment_id']
        else:
            c[data['comment_id']] = data['comment_id']


# Connect All Functions
def smokedetector(site):
    items = fetcher(site)
    p = multiprocessing.Pool(3)
    p.map(composer, items)


def runtime(site):
    global stopscan
    stopscan = 0
    cbmGenerator('Comment scanning starting on ' + site)
    cbm()
    while True:
        s = datetime.now()
        a.clear()
        b.clear()
        c.clear()
        smokedetector(site)
        cbm()
        print('{} {} | S: {} | N: {} | O: {}'
              .format(datetime.now(), site, len(a), len(b), len(c)))
        cRT.append(len(c))
        s = datetime.now() - s
        s = s.total_seconds()
        d = sum(cRT[-10:]) / 10
        s = 20 - s + d
        if s < 0:
            s = 5
        print(str(s) + " | " + str(d))
        if stopscan == 1:
            cbmGenerator('Scanning halted on ' + site)
            cbm()
            break
        time.sleep(s)


# Run Scanner
runtime('stackoverflow')
