from flask import Flask, jsonify, request
from skyscanner_cred import *
import requests
app = Flask(__name__)

api = 'http://partners.api.skyscanner.net/apiservices/'

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
        command = request.form['command']
        origin = get_airport(arguments[1])
        destination = get_airport(arguments[0])
        (journey, carriers) = get_journey(origin, destination)
        try:
            price = journey['MinPrice']
        except IndexError:
            return jsonify({'content' : 'There was an error with the wording of zour request, please try again'})
        departure = journey['OutboundLeg']['DepartureDate']
        arrival = journey['InboundLeg']['DepartureDate']

        carrier_out_names = []
        carrier_in_names = []

        for cid in journey['OutboundLeg']['CarrierIds']:
            for carrier in carriers:
                if cid == carrier['CarrierId']:
                    carrier_out_names.append(carrier['Name'])
        print(carrier_out_names)
        

        for cid in journey['InboundLeg']['CarrierIds']:
            for carrier in carriers:
                if cid == carrier['CarrierId']:
                    carrier_in_names.append(carrier['Name'])
        print(carrier_in_names)

        response = ('From ' + origin['PlaceName'] + ' to ' + destination ['PlaceName'])
        response += '\nThe journey will cost you about '
        response += str(price)
        response += ' euros.\nDeparture: '
        response += departure[:10]
        response += ' and will be with '
        for carrier in carrier_out_names:
            response += carrier
        response += '\nArrival: '
        response += arrival[:10]
        response += ' and will be with '
        for carrier in carrier_in_names:
            response += carrier

        return jsonify({'content': response})       
        



def get_airport(location):
    endpoint = api + 'autosuggest/v1.0/UK/GBP/en-GB/?query=' + location + '&apiKey=' + hotels_and_autosuggest
    r = requests.get(endpoint)
    return r.json()['Places'][0]


def get_journey(origin, destination):
    markets = api + 'reference/v1.0/countries/en-US?apikey=' + flights_and_car  
    r = requests.get(markets)
    markets = r.json()
    market = ''    
    for country in markets['Countries']:
        if country['Name'] == origin['CountryName']:
            market = country['Code']

    endpoint = api + 'browsequotes/v1.0/' + market + '/eur/en-US/' + origin['PlaceId'] + '/' + destination['PlaceId'] + '/anytime/anytime?apikey=' + flights_and_car
    r = requests.get(endpoint)
    return (r.json()['Quotes'], r.json()['Carriers'])
    

if __name__ == '__main__':
    app.run()
