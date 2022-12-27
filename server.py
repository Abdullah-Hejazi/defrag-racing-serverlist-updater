import socket

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connected = False

        self.connect()

    def connect(self):
        if self.connected:
            return

        self.socket.settimeout(10)
        self.socket.connect((self.ip, self.port))
        self.connected = True

    def get_rcon_data(self, rconpass):
        self.socket.sendall(b'\xff\xff\xff\xffrcon ' + bytes(rconpass, encoding='utf8') + b' score\x00')
        data = self.socket.recv(4096)

        data = data[10:].decode('utf8').split('\n')

        scores = []
        players = {}

        for line in data:
            if line.startswith('<player>'):
                player = self.parse_score_player(line)

                players[player['clientId']] = player
            
            elif line.startswith('scores'):
                scores = self.parse_scores(line)

        for player in players:
            playerinfo = self.get_player_info(players[player], rconpass)


            players[player]['country'] = playerinfo['tld']
            players[player]['nospec'] = playerinfo['color1'] == 'nospec'
            players[player]['model'] = playerinfo['model']
            players[player]['headmodel'] = playerinfo['team_headmodel']


        result = {
            'players': players,
            'map': data[0].split(':')[1].strip(),
            'hostname': data[1].split(':')[1].strip(),
            'defrag': data[2].split(':')[1].strip(),
            'scores': scores
        }

        return result

    def get_data(self):
        self.socket.sendall(b'\xff\xff\xff\xffgetstatus\x00')
        data = self.socket.recv(4096)

        serverdata, players = self.parse_response_body(data[19:])

        serverdata['players'] = self.parse_players(players)

        playerlist = {}

        i = 0
        for player in serverdata['players']:
            playerlist[i] = player

            i += 1

        result = {
            'players': playerlist,
            'map': serverdata['mapname'],
            'hostname': serverdata['sv_hostname'],
            'defrag': self.get_game_mode(serverdata),
            'scores': {
                'num_players': len(serverdata['players']),
                'speed': 0,
                'speed_player_num': 0,
                'speed_player_name': "",
                'players': serverdata['players']
            }
        }

        return result

    def get_game_mode(self, serverdata):
        physics = 'cpm' if serverdata['df_promode'] == '1' else 'vq3'
        mode = '.2' if serverdata['defrag_mode'] == '2' else ''

        return physics + mode

    def get_player_info(self, player, rconpass):
        self.socket.sendall(b'\xff\xff\xff\xffrcon ' + bytes(rconpass, encoding='utf8') + b' dumpuser ' + bytes(player['clientId'], encoding='utf8') + b'\x00')
        data = self.socket.recv(16384)

        data = data[28:].decode('utf8').split('\n')

        result = {}

        for line in data:
            key, value = self.extract_key_value_pair(line)
            result[key] = value

        return result

    def extract_key_value_pair(self, line):
        if line == '':
            return None, None

        for i in range(len(line)):
            if line[i] == ' ':
                return line[:i], line[i+1:].strip()

    def parse_score_player(self, data):
        # <player><ip>196.128.17.91</ip><num>23</num><uid>12705</uid><nick>^8HEJAZI</nick></player>
        player = {
            'clientId': data.split('<num>')[1].split('</num>')[0],
            'name': data.split('<nick>')[1].split('</nick>')[0],
            'mddId': data.split('<uid>')[1].split('</uid>')[0]
        }

        player['logged'] = player['mddId'] != '0'

        return player

    def parse_scores(self, data):
        scores = {}
        data = data.replace('scores ', '').split(' ')

        scores['num_players'] = data.pop(0)
        scores['speed'] = data.pop(0)
        scores['speed_player_num'] = data.pop(0)
        scores['speed_player_name'] = data.pop(0)[1:-1]

        scores['players'] = []

        # parse player scores, 4 values per player
        while len(data) > 0:
            player = {}
            player['player_num'] = data.pop(0)
            player['time'] = data.pop(0)
            player['ping'] = data.pop(0)
            player['follow_num'] = data.pop(0)

            scores['players'].append(player)

        return scores

    def parse_players(self, data):
        players = []
        for line in data:
            if line == b'':
                continue

            # convert line to string
            line = line.decode('utf8')

            player = dict(zip(('score', 'ping', 'name'), line.split(' ')))
            players.append({
                'name': player['name'],
            })

        return players

    def parse_response_body(self, body):
        i = 0
        keys = []
        values = []
        while body.startswith(b'\\'):
            if b'\\' in body[1:]:
                element_end = body.index(b'\\', 1)
            elif b'\n' in body[1:]:
                element_end = body.index(b'\n', 1)
            else:
                pass

            element = body[1:element_end]
            if i % 2 == 0:
                keys.append(element.decode('latin1'))
            else:
                values.append(element.decode('latin1'))

            # Cut used data from body
            body = body[element_end:]
            i += 1

        # Split remaining body into player lines
        lines = body.split(b'\n')

        return dict(zip(keys, values)), lines