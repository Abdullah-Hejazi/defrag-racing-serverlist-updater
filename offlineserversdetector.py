import json
import server
import serverlist
import time

def server_online(serverdata):
    try:
        connection = server.Server(serverdata['ip'], serverdata['port'])

        if 'rconpassword' in serverdata:
            result = connection.get_rcon_data(serverdata['rconpassword'])
        else:
            result = connection.get_data()

        if result == 'Bad rconpassword':
            result = connection.get_data()

        if result is None:
            return False

        return True

    except Exception as exception:
        print(exception)
        return False

    return True

def validate_servers():
    onlineservers = []

    for serverdata in serverlist.servers:
        if server_online(serverdata):
            onlineservers.append(serverdata['ip'] + ':' + str(serverdata['port']))
        else:
            print('Server offline: ' + serverdata['ip'] + ':' + str(serverdata['port']))

    with open('onlineservers.txt', 'w') as outfile:
        for server in onlineservers:
            outfile.write(server + '\n')


while True:
    validate_servers()
    print("\n\n\n\n")
    time.sleep(120)