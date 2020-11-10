import notify2
import librus
import datetime
import re
import time
import argparse

parser = argparse.ArgumentParser(description='Notifies about lessons.')
parser.add_argument('username', type=str, help='Librus Synergia username')
parser.add_argument('password', type=str, help='Librus Synergia password')
args = parser.parse_args()

def notify(header, text):
    notify2.Notification(header, text, 'notification-message-im').show()

notify2.init('Librus Schedule Notifier')

session = librus.LibrusSession()
try:
    session.login(args.username, args.password)
    print('Login successful.')
except RuntimeError:
    print('Login failed.')
    exit()

time_regex = re.compile(r'(\d*)\:(\d*) - (\d*)\:(\d*)')
weekday = datetime.date.today().weekday()
schedule = session.schedule()

lessons = []

print('Downloading schedule.')
for l in schedule:
    try:
        assert isinstance(l, librus.Lesson)
        if l.day == weekday:
            match = re.match(time_regex, l.time)
            lessons.append({
                'name': l.name,
                'time': datetime.time(hour=int(match.group(1)), minute=int(match.group(2))),
                'teacher': l.teacher
            })
    except IndexError as e:
        print(e)

last_notification = None

while True:
    dt = datetime.datetime.now()
    t = datetime.time(hour=dt.hour, minute=dt.minute)
    if t != last_notification:
        for l in lessons:
            lt = l['time']
            if lt == t:
                notify('{} rozpoczyna się'.format(l['name']), l['teacher'])
                print('Sending notification.')
                last_notification = t
                break
            elif lt.hour == t.hour and lt.minute == t.minute + 5:
                notify('{} za 5 minut'.format(l['name']), l['teacher'])
                print('Sending notification.')
                last_notification = t
                break
    print('Waiting.')
    time.sleep(60)


