from flask import Flask, jsonify, request
from skyscanner_cred import *
import requests
import time
app = Flask(__name__)

api = 'http://partners.api.skyscanner.net/apiservices/'

data = {
"cabinclass":"Economy",
"country":"UK",
"currency":"EUR",
"locale":"en-GB",
"locationSchema":"iata",
"originplace":"MAD",
"destinationplace":"LON",
"outbounddate":"2018-05-30",
"inbounddate":"2018-06-02",
"adults":"1",
"children":"0",
"infants":"0",
"apikey": flights_and_car
}



session_url = "http://partners.api.skyscanner.net/apiservices/pricing/v1.0"

@app.route('/test', methods=['POST'])
def test():

    event = request.form['event_type']

    if event == 'ping':
        return jsonify({'content': 'pong'})
    elif event == 'uninstall':
        return ('ok', 200)
    else:
        argument = request.form['command_argument']
        arguments = argument.split()
        print(arguments)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        command = request.form['command']
        origin = get_airport(arguments[1])
        data['originplace'] = origin['PlaceId'][:3]
        data['country'] = origin['CountryId'][:2]
        destination = get_airport(arguments[0])
        data['destinationplace'] = destination['PlaceId'][:3]
        create_session_response = requests.request('POST', session_url, data=data, headers=headers)

        
        headers = {
            "Accept": "application/json"
        }
        polling_url = create_session_response.headers['Location'] + '?apikey=' + flights_and_car

        polling_response = requests.request('GET', polling_url, headers=headers)
        while polling_response.status_code == 304 or polling_response.json()['Status'] == 'UpdatesPending':
            time.sleep(1)
            polling_response = requests.request('GET', polling_url, headers=headers)
            print(polling_response.status_code)
        try:
            itins = polling_response.json()['Itineraries'][:3]
        except:
            return jsonify({'content' : 'There was an error with the wording of your request, please try again with a different input'})
        legs = polling_response.json()['Legs']
        deepurls = []
        price = []
        outboundlegs = []
        inboundlegs = []
        out_times = []
        in_times = []
        for itin in itins:
            price.append(itin['PricingOptions'][0]['Price'])
            outboundlegs.append(itin['OutboundLegId'])
            inboundlegs.append(itin['InboundLegId'])
            deepurls.append(itin['PricingOptions'][0]['DeeplinkUrl'])
        for leg in legs:
            for oleg in range(len(outboundlegs)):
                if leg['Id'] == outboundlegs[oleg]:
                    out_times.append((leg['Departure'][-8:], leg['Arrival'][-8:]))
            for ileg in range(len(inboundlegs)):
                if leg['Id'] == inboundlegs[ileg]:
                    in_times.append((leg['Departure'][-8:], leg['Arrival'][-8:]))
            
        print(price)
        print(out_times)
        print(in_times)
        print(deepurls)
        response = ('From ' + origin['PlaceName'] + ' to ' + destination ['PlaceName'])
        
        for itin in range(len(itins)):
            response += '\n* This journey will cost you about '
            response += ('**'+str(price[itin])+'**')
            response += ' euros.\n_Outbound_\nDeparture: '
            response += out_times[itin][0]
            response += '\nArrival: '
            response += out_times[itin][1]
            response += '\n_Inbound_:\nDeparture: '
            response += in_times[itin][0]
            response += '\nArrival: '
            response += in_times[itin][1]
            response += ('\n [Purchase](' + deepurls[itin] +')')

        return jsonify({'content': response})


def get_airport(location):
    endpoint = api + 'autosuggest/v1.0/UK/GBP/en-GB/?query=' + location + '&apiKey=' + hotels_and_autosuggest
    r = requests.get(endpoint)
    return r.json()['Places'][0]
    

if __name__ == '__main__':
    app.run()
