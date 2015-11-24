import requests
import textwrap

from omnivore import api_base, api_version, error


def build_url(endpoint):
    url = api_base + api_version + '/'

    if endpoint:
        url += endpoint

    return url


def get_headers():
    from omnivore import api_key

    if api_key is None:
        raise error.AuthenticationError(
            'No API key provided. (HINT: set your API key using '
            '"omnivore.api_key = <API-KEY>"). You can generate API keys '
            'from the Omnivore web interface.'
        )

    return {
        'Api-Key': api_key,
        'Content-Type': 'application/json'
    }


def get(url):
    headers = get_headers()

    try:
        res = requests.get(url, headers=headers)
    except Exception, e:
        handle_request_error(e)

    try:
        json = res.json()
    except ValueError, e:
        handle_parse_error(e)

    if res.status_code != 200:
        handle_error_code(json, res.status_code, res.headers)

    return json


def post(url, json):
    headers = get_headers()

    try:
        res = requests.post(url, headers=get_headers(), json=json)
    except Exception, e:
        handle_request_error(e)

    try:
        json = res.json()
    except ValueError, e:
        handle_parse_error(e)

    if res.status_code != 200:
        handle_error_code(json, res.status_code, res.headers)

    return json


def handle_request_error(e):
    if isinstance(e, requests.exceptions.RequestException):
        msg = 'Unexpected error communicating with Omnivore.'
        err = '{}: {}'.format(type(e).__name__, str(e))
    else:
        msg = ('Unexpected error communicating with Omnivore. '
               'It looks like there\'s probably a configuration '
               'issue locally.')
        err = 'A {} was raised'.format(type(e).__name__)
        if str(e):
            err += ' with error message {}'.format(str(e))
        else:
            err += ' with no error message'

    msg = textwrap.fill(msg) + '\n\n(Network error: {})'.format(err)
    raise error.APIConnectionError(msg)


def handle_error_code(json, status_code, headers):
    if res.status_code == 400:
        error = json.get('error', 'Bad request')
        raise error.InvalidRequestError(error, status_code, headers)
    elif res.status_code == 401:
        error = json.get('error', 'Not authorized')
        raise error.AuthenticationError(error, status_code, headers)
    elif res.status_code == 404:
        error = json.get('error', 'Not found')
        raise error.InvalidRequestError(error, status_code, headers)
    elif res.status_code == 500:
        error = json.get('error', 'Internal server error')
        raise error.APIError(error, status_code, headers)
    else:
        error = json.get('error', 'Unknown status code')
        raise error.APIError(error, status_code, headers)


def handle_parse_error(e, status_code=None, headers=None):
    err = '{}: {}'.format(type(e).__name__, str(e))
    msg = 'Error parsing Omnivore JSON response. \n\n{}'.format(err)
    raise error.APIError(msg, status_code, headers)