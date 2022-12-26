import json
import server
from datetime import datetime
import time

""" serverlist contains a variable called servers, that is an array of objects representing the servers """
""" each object has the following properties: ip, port, rconpassword """
import serverlist

def parse_server_data(data):
    players = []

    for player in data['players']:
        players.append({
            'name': str(player['name'].decode('utf-8').replace('\"', '')),
        })

    return {
        #'address': data['ip'] + ':' + str(data['port']),
        'map': data['mapname'],
        'hostname': data['sv_hostname'],
        'players': players
    }

def get_server_data(serverdata):
    connection = server.Server(serverdata['ip'], serverdata['port'])

    result = connection.get_rcon_data(serverdata['rconpassword'])

    result['address'] = serverdata['ip'] + ':' + str(serverdata['port'])

    result['timestamp'] = str(datetime.now())

    return result

def get_server_list():
    allservers = {
        'active': {},
        'empty': {}
    }

    for serverdata in serverlist.servers:
        data = get_server_data(serverdata)

        if data['scores']['num_players'] == 0:
            allservers['empty'][data['address']] = data

        else:
            allservers['active'][data['address']] = data

    with open('servers.json', 'w') as outfile:
        json.dump(allservers, outfile, indent=4)

# run get_server_list() every 10 seconds

while True:
    get_server_list()
    print("Updated server list.")
    time.sleep(10)