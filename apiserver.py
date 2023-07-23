# import necessary libraries 
from flask import Flask, jsonify, request 
from pymongo import MongoClient
from datetime import datetime, timedelta

# initialise a Flask application and create a MongoDB Client 
app = Flask(__name__)
client = MongoClient('mongodb+srv://userReadOnly:7ZT817O8ejDfhnBM@minichallenge.q4nve1r.mongodb.net/')
db = client['minichallenge']

# Define the API routes
########################## /flight API ##########################

@app.route('/flight', methods=['GET'])
def get_flight():
    # db name
    collection = db['flights']
    
    # get query parameters from URL
    departureDate = request.args.get('departureDate')
    returnDate = request.args.get('returnDate')
    destination = request.args.get('destination')

    # Error Exception: check if there is null parameters
    if departureDate == '' or returnDate == '' or destination == '':
        return jsonify({'message': 'Missing query parameters.'}), 400

    # Error Exception: check if date parameter is in the correct format
    try:
        departureDateValidate = datetime.fromisoformat(departureDate)
        returnDateValidate = datetime.fromisoformat(returnDate)
    except:
        return jsonify({'message': 'Invalid date format.'}), 400

    # Define the fields to include or exclude (1 to include, 0 to exclude)
    projection = {'srccity': 1, 'date': 1, 'destcity': 1, 'airlinename': 1, 'price': 1, '_id': 0}  # Include only these fields

    ############# DEPARTURE FLIGHT #############

    # query the db based on the parameters / projections
    result = collection.find({
        'srccountry': 'Singapore',
        'date': datetime.fromisoformat(departureDate),
        'destcity': destination
    }, projection).sort('price', 1)

    try:
        # check if item more than 1
        tempPrice = result[0]['price']
    
        departure_flight = []
        departure_flight.append(result[0])

        i = 0

        while(True):
            i = i + 1
            if result[i]['price'] > tempPrice:
                break
            else:
                departure_flight.append(result[i])
    # if result is null, return empty list
    except:
        return jsonify([])

    ############# RETURN FLIGHT #############

    # query the db based on the parameters / projections
    result = collection.find({
        'srccity': destination,
        'date': datetime.fromisoformat(returnDate),
        'destcountry': 'Singapore'
    }, projection).sort('price', 1)

    # check if item more than 1
    try:
        tempPrice = result[0]['price']
        
        return_flight = []
        return_flight.append(result[0])

        i = 0

        while(True):
            i = i + 1
            if result[i]['price'] > tempPrice:
                break
            else:
                return_flight.append(result[i])
    # if result is null, return empty list
    except:
        return jsonify([])

    ############# COMBINE RESULT #############

    # append the result 
    flight_answer = []
    # If result is one
    if len(departure_flight) == 1 and len(return_flight) == 1:

        flight_result = {
            "City": destination,
            "Departure Date": departureDate,
            "Departure Airline": departure_flight[0]['airlinename'],
            "Departure Price": departure_flight[0]['price'],
            "Return Date": returnDate,
            "Return Airline": return_flight[0]['airlinename'],
            "Return Price": return_flight[0]['price']}

        flight_answer.append(flight_result)
    else:
        # double for loop for different combinations
        for i in departure_flight:
            
            flight_result = {}

            flight_result = {
            "City": destination,
            "Departure Date": departureDate,
            "Departure Airline": departure_flight[i]['airlinename'],
            "Departure Price": departure_flight[i]['price']}
            
            for j in return_flight:

                flight_result = {
                "Return Date": returnDate,
                "Return Airline": return_flight[j]['airlinename'],
                "Return Price": return_flight[j]['price']}

                flight_answer.append(flight_result)
    
    
    # return result
    return jsonify(flight_answer)

########################## /hotel API ##########################
@app.route('/hotel', methods=['GET'])
def get_hotel():
    collection = db['hotels']
    
    # get query parameters
    checkInDate = request.args.get('checkInDate')
    checkOutDate = request.args.get('checkOutDate')
    destination = request.args.get('destination')

    # Error Exception for null parameters
    if checkInDate == '' or checkOutDate == '' or destination == '':
        return jsonify({'message': 'Missing query parameters.'}), 400

    # Error Exception for invalid date format
    try:
        departureDateValidate = datetime.fromisoformat(checkInDate)
        returnDateValidate = datetime.fromisoformat(checkOutDate)
    except:
        return jsonify({'message': 'Invalid date format.'}), 400

    # calculate the date differences between two dates
    dateDiff = (datetime.fromisoformat(checkOutDate) - datetime.fromisoformat(checkInDate)).days + 1

    # query the db based on the parameters
    
    hotel_result = {}

    # loop thru the db for different dates
    for i in range(dateDiff):
        cursor_result = collection.find({
            'date': datetime.fromisoformat(checkInDate) + timedelta(days=i),
            'city': destination
        })

        # loop thru the query result and add the price
        for j in cursor_result:
            # if is the first result, create dic key and add price
            if i == 0:
                hotel_result[j['hotelName']] = j['price']
            # if not first result, add curr price to existing price
            else:
                hotel_result[j['hotelName']] = hotel_result[j['hotelName']] + j['price']
    
    # Sort the dictionary based on values in ascending order
    sorted_result = dict(sorted(hotel_result.items(), key=lambda item: item[1]))

    # create variables
    cheapestPrice = 0
    hotel_answer = []

    # for loop
    for key, value in sorted_result.items():
        
        # if empty -> add to list and set price to curr 
        if cheapestPrice == 0:
            cheapestPrice = value
            hotel_answer.append(
                {
                    "City": destination,
                    "Check In Date": checkInDate,
                    "Check Out Date": checkOutDate,
                    "Hotel": key,
                    "Price": value
                }
            )
        
        # second result onwards, if same price as curr, add to list
        elif value == cheapestPrice:
            hotel_answer.append(
                {
                    "City": destination,
                    "Check In Date": checkInDate,
                    "Check Out Date": checkOutDate,
                    "Hotel": key,
                    "Price": value
                }
             )
        # if not first result and not same price as curr. break out of loop
        else:
            break
    
    return jsonify(hotel_answer)


# Define a default route to the root URL ("/")
@app.route('/')
def default_page():
    return "Welcome to the default page of the API server! Kindly use /flight or /hotel to access the endpoint."

# Start the flask application
if __name__ == '__main__':
    app.json.sort_keys = False
    app.run(host='0.0.0.0', port=8080)

