import requests

url = 'https://webapi.vvo-online.de/dm'
params = {
    'stopid' : 33000784,
    'limit' : 1,
}

try:
    request = requests.get(url=url, params=params)
    status = request.status_code
    if status == 200:
        response = request.json()
        print(f'Request succesful: Code {response['Status']['Code']}')
        print(response['Departures'])
    else:
        print(f'request failed with the error code {status}')
except Exception:
    print(f'an error occured: {Exception}')