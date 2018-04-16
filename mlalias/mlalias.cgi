#!/usr/bin/env python2.7
# This script updates the mailing list subscriptions of an individual
# Info is GET'd (lol) from the CSEsoc's website

import cgitb
cgitb.enable(0, format='text')

import os
import cgi
import json
from subprocess import Popen, PIPE

def pp(studentId):
    pipe = Popen(['pp', studentId], stdout=PIPE)
    pipe.wait()
    resp = pipe.stdout.read()
    ret = pipe.returncode
    return (resp, ret)

def user_exists(studentId):
    resp, ret = pp(studentId)
    return ret == 0

def mailing_list(team):
    return Popen(['mlalias', team], stdout=PIPE).stdout.read()

def team_members(team):
    team = Popen(['mlalias', '-r', team], stdout=PIPE).stdout.read()
    team = team.split(':')
    members = team[2].split(',')
    return members

def send_info(team, action, studentId):
    message = """\
Hey! {id} {action} your team.

Some info about {id}:
{info}

Your team now looks like this:
{list}
""".format(id=studentId, action=action, info=pp(studentId)[0], list=mailing_list(team))

    Popen([
        'mail', '-s' ,
        'mlalias update for {team}'.format(team=team),
        '{team}.head@cse.unsw.edu.au'.format(team=team)
    ], stdin=PIPE).stdin.write(message)


# FieldStorage is an annoying dictionary. No get method.
form = {key: cgi.FieldStorage()[key].value for key in cgi.FieldStorage().keys()}

cseid = form.get('cseid', '') # Who is the individual?
team = form.get('team', '') # Which team are we talking about?
action = form.get('action', '') # Joining or leaving the team?
callback = form.get('callback')

valid_aliases = [
    'publicity',
    'social',
    'beta',
    'dev',
    'devspace',
    'compclub',
    'talks',
    'workshops'
]

valid_actions = ['join', 'leave', 'status']
valid_aliases = list(map(lambda x: 'csesoc.' + x, valid_aliases))


# CORS Headers Are Cool!
print("""\
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET""")


if len(cseid) == 0 or len(team) == 0 or len(action) == 0 or \
    not user_exists(cseid) or  \
    team not in valid_aliases or \
    action not in valid_actions:
    print('Status: 400 Bad Request\nContent-type: application/json\n\n{"error": "Bad Request!"}')
    exit(1)


print("Status: 200 Success\r\nContent-type: application/json\r\n\r\n")
extra_resp = dict()

if action == 'join':
    p = Popen(['mlalias', team, '-a', cseid], stdout=PIPE, stderr=PIPE)
    p.communicate()

    if cseid not in team_members(team):
        send_info(team=team, action='joined', studentId=cseid)

elif action == 'leave':
    p = Popen(['mlalias', team, '-d', cseid], stdout=PIPE, stderr=PIPE)
    p.communicate()

    if cseid not in team_members(team):
        send_info(team=team, action='left', studentId=cseid)

elif action == 'status':
    extra_resp['on_list'] = cseid in team_members(team)

success = json.dumps(dict(success=True, list=team, action=action, **extra_resp))
if callback:
    print callback + '('  + success + ')'
else:
    print success
