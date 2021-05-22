import re

import requests
import yaml
from bs4 import BeautifulSoup

base_url = 'https://developer.riotgames.com'
response = requests.get(base_url + '/apis')
soup = BeautifulSoup(response.text, features='html.parser')


class API:

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.zones = {}
        self.compiled = re.compile('^(/[^/]*/[^/]*/[v\d]*/[^/]+)')

        print("\nCreated API %s" % name)
        self.server = list()
        self.get_endpoints()
        print("\tAllowed servers: %s" % self.server)

    def get_endpoints(self):
        if 'tournament' in self.name:
            self.server = ['AMERICAS']
            return

        response = requests.get(base_url + '/api-details/' + self.name)
        soup = BeautifulSoup(response.json()['html'], features='html.parser')
        operations = soup.find('ul', class_='operations')
        for operation in operations.find_all('li', class_='operation'):
            paths = operation.find_all('span', class_='path')
            for path in paths:
                endpoint = str(path.a.string)
                zone = self.compiled.findall(endpoint)[0]
                if zone not in self.zones:
                    self.zones[zone] = []
                self.zones[zone].append(endpoint.split(zone)[1])
                print("\tEndpoint %s added." % endpoint)
        self.server = [str(option.get('value')) for option in
                       operations.find('form', class_='sandbox') \
                           .find('select', attrs={'name': 'execute_against'}).find_all('option')]

    def dump(self):
        return str(self.name), {
            'zones': self.zones,
            'allowed_server': self.server
        }


data = {'apis': {}}
allowed_server = set()

for link in soup.find_all('a', class_='api_option'):
    api = API(
        name=link.get('api-name'),
        url=link.get('href')
    )
    name, content = api.dump()
    data['apis'][name] = content
    for server in content['allowed_server']:
        allowed_server.add(server)
    data['server'] = sorted(list(allowed_server))

with open('endpoints.yaml', 'w+') as output_file:
    yaml.dump(data, output_file)
