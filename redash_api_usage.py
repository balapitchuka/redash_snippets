import requests


class Redash(object):
    def __init__(self, redash_url, api_key):
        self.redash_url = redash_url
        if not self.redash_url.endswith('/'):
            self.redash_url = '{}/'.format(self.redash_url)

        self.auth_headers = {'Authorization': 'Key {}'.format(api_key)}

    def create_user(self, name, email):
        data = {
            'name': name,
            'email': email
        }
        user = self._post_request('users', data)
        return user

    def add_user_to_group(self, user_id, group_id):
        return self._post_request('groups/{}/members'.format(group_id), {'user_id': user_id})

    def get_alerts(self):
        return self._get_request('alerts')

    def _post_request(self, resource, data):
        url = '{}api/{}'.format(self.redash_url, resource)
        response = requests.post(url, json=data, headers=self.auth_headers)
        response.raise_for_status()
        return response.json()

    def _get_request(self, resource):
        url = '{}api/{}'.format(self.redash_url, resource)
        response = requests.get(url, headers=self.auth_headers)
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    redash = Redash('https://app.redash.io/your-account-slug/', 'your-user-api-key')
    group_id = 155

    user = redash.create_user('API Test User', 'api-test@example.com')

    user = redash.add_user_to_group(user['id'], group_id)

    assert group_id in user['groups']

    for alert in redash.get_alerts():
        print "Name: {}".format(alert['name'])
