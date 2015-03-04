#!/usr/bin/python

import json
import logging
import PyGithub
import argparse
from requests import ConnectionError
from logging.handlers import RotatingFileHandler

Org = "orgname"
# When we use GitHub API need use team_id instead team_name 
Team_id = team_id # team id
Token = "Security token"

# Build connection
b = PyGithub.BlockingBuilder()
b.OAuth(Token)
g = b.Build()

logger = logging.getLogger(__name__)

file_handler = RotatingFileHandler('/tmp/updater.log', 'a', 10 * 1024 * 1024, 5)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(file_handler)

# Check script parameters 
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="set debug level for logs",
                    action="store_true")
args = parser.parse_args()

if args.debug:
	logger.setLevel(logging.DEBUG)
	file_handler.setLevel(logging.DEBUG)
else:
	logger.setLevel(logging.INFO)
	file_handler.setLevel(logging.INFO)

logger.info('Starting Updater')

#Connect to our org.
try:
	my_org = g.get_org(Org)
except ConnectionError, e:
	logger.error('Failed to connect org %s', e)
	raise SystemExit(1)
except Exception, e:
	logger.error('Failed to open %s - %s', Org, e[2].get('message',''))
	logger.debug('Failed to open org', exc_info=True)
	raise SystemExit(1)

#Get all members in our org.
try:
	all = my_org.get_members()
except Exception, e:
	logger.error('Failed get all members in %s - %s', Org, e[2].get('message',''))
	logger.debug('Failed get all members in %s', Org, exc_info=True)
	raise SystemExit(1)

#Get all members in our team
try:
	team = g.get_team(Team_id).get_members()
except Exception, e:
	logger.error('Failed get members in %s - %s', Team_id, e[2].get('message',''))
	logger.debug('Failed get members in %s', Team_id, exc_info=True)
	raise SystemExit(1)

# Add team logins to the lists
team_login = [t.login for t in team]

# Set Difference between two lists, if not included - add member to the group.
try:
	for i in all:
		if i.login not in team_login:
			g.get_team(Team_id).add_to_members(i.login)
			logger.info('Member %s has been added to the team %s', i.login, Team_id)
except Exception, e:
	logger.error('Failed add member %s to the %s - %s', i.login, Team_id, e[2].get('message',''))
	logger.debug('Failed add member %s to the %s', i.login, Team_id, exc_info=True)
	raise SystemExit(1)

logger.info('Updater finished running')
