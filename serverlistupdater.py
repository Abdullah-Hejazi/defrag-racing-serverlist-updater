import json
import server
from datetime import datetime
import time
import os

""" serverlist contains a variable called servers, that is an array of objects representing the servers """
""" each object has the following properties: ip, port, rconpassword """
import serverlist

def get_server_data(serverdata):
    try:
        connection = server.Server(serverdata['ip'], serverdata['port'])

        if 'rconpassword' in serverdata:
            result = connection.get_rcon_data(serverdata['rconpassword'])
        else:
            result = connection.get_data()

        if result == 'Bad rconpassword':
            result = connection.get_data()

        if result is None:
            return None

        result['address'] = serverdata['ip'] + ':' + str(serverdata['port'])

        result['timestamp'] = str(datetime.now())

        if 'rconpassword' not in serverdata:
            result['notice'] = 'The data provided for this server is not complete, because the script does not have the rcon password for this server. Contact [neyo#0382] on discord to attach the rcon password for your server.'

        return result

    except Exception as exception:
        print('Failed to connect to server: ' + serverdata['ip'] + ':' + str(serverdata['port']))
        print('Reason: ' + str(exception))
        return None

    return result

def get_server_list():
    allservers = {
        'active': {},
        'empty': {}
    }

    onlineservers = []
    with open('onlineservers.txt', 'r') as infile:
        for line in infile:
            onlineservers.append(line.strip())

    for serverdata in serverlist.servers:
        if serverdata['ip'] + ':' + str(serverdata['port']) not in onlineservers:
            continue

        data = get_server_data(serverdata)

        if data is None or 'scores' not in data or 'num_players' not in data['scores']:
            continue

        print(str(data))

        if data['scores']['num_players'] == 0:
            allservers['empty'][data['address']] = data

        else:
            allservers['active'][data['address']] = data

    with open('servers.json', 'w') as outfile:
        json.dump(allservers, outfile, indent=4)

def transfer_file_to_container():
    os.system("docker cp " + serverlist.servers_file_location + " " + serverlist.container_file_location)

while True:
    get_server_list()
    transfer_file_to_container()
    print("Updated server list.")
    time.sleep(10)
