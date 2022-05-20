from urllib.parse import urljoin
import requests
import click
import json


class Redash:
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key

    def _request(self, method, path, *args, **kwargs):
        if self.host.endswith("/"):
            url = self.host[0:-1] + path
        else:
            url = self.host + path

        kwargs["headers"] = {"Authorization": "Key {}".format(self.api_key)}
        response = requests.request(method, url, *args, **kwargs)

        return response.json()

    def get_queries(self, tag, skip_scheduled):
        if tag:
            params = {"tags": tag}
        else:
            params = {}

        stop_loading = False
        page = 1
        page_size = 100

        items = []

        while not stop_loading:
            params["page"] = page
            params["page_size"] = page_size
            response = self._request("get", "/api/queries", params=params)

            items += response["results"]
            page += 1

            stop_loading = response["page"] * response["page_size"] >= response["count"]

        if skip_scheduled:
            items = [query for query in items if query['schedule'] is None]

        return items

    def trigger_refresh(self, query, parameters):
        print("Triggering refresh of {}...".format(query['id']))

        data = {'max_age': 0, 'parameters': parameters}
        response = self._request('post', '/api/queries/{}/results'.format(query['id']), json=data)

        if 'job' in response:
            if 'id' in response['job']:
                print("Job id: {}".format(response['job']['id']))
            else:
                print("Error: {}".format(response['job']['error']))
        else:
            print(response)

        return response


@click.command()
@click.argument("redash_host")
@click.option(
    "--api-key",
    "api_key",
    envvar="REDASH_API_KEY",
    show_envvar=True,
    prompt="API Key",
    help="User API Key",
)
@click.option('--parameters', help="Query Parameters in JSON form", default='{}')
@click.option('--skip-scheduled', 'skip_scheduled', is_flag=True, default=False, help="Skip scheduled queries")
@click.option("--tag", default=None, help="Tag to filter the queries list with.")
def trigger(redash_host, api_key, tag, skip_scheduled, parameters):
    """Trigger query refresh on REDASH_HOST using given api-key and optional list of tags."""

    message = "Refreshing queries from {}"
    if tag:
        message += " with tag: {}"

    if skip_scheduled:
        message += " (skipping scheduled ones)"

    message += "..."

    print(message.format(redash_host, tag))

    redash = Redash(redash_host, api_key)
    queries = redash.get_queries(tag, skip_scheduled=skip_scheduled)

    print("Found {} queries to refresh.".format(len(queries)))

    parameters = json.loads(parameters)
    for query in queries:
        job = redash.trigger_refresh(query, parameters)


if __name__ == "__main__":
    trigger()
