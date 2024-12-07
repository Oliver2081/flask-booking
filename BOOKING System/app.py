from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# Define the correct file path
BOOKINGS_FILE = '/home/Oliver/Desktop/Python/BOOKING System/data/bookings.json'

# Ensure the directory and file exist
os.makedirs('/home/Oliver/Desktop/Python/BOOKING System/data/', exist_ok=True)
if not os.path.exists(BOOKINGS_FILE):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump([], f)

# Helper function to load bookings
def load_bookings():
    try:
        with open(BOOKINGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading bookings file: {e}")
        return []

# Helper function to save bookings
def save_bookings(bookings):
    try:
        with open(BOOKINGS_FILE, 'w') as f:
            json.dump(bookings, f, indent=4)
    except Exception as e:
        print(f"Error saving bookings file: {e}")

# Generate table data for the next two weeks
def generate_booking_table():
    bookings = load_bookings()

    # Generate the next two weeks of dates
    today = datetime.now()
    dates = [(today + timedelta(days=i)) for i in range(14) if (today + timedelta(days=i)).weekday() < 5]  # Exclude weekends
    rooms = ["Room 1", "Room 2", "Room 3", "Room 4", "Room 5", "Room 6", "Room 7", "Room 8", "Ensemble Room"]

    table_data = []
    for date_obj in dates:
        date_str = date_obj.strftime('%Y-%m-%d')
        row = {"date": date_obj.strftime('%a, %m/%d/%Y')}
        for room in rooms:
            row[room] = "Available"
        for booking in bookings:
            if booking["start"] == date_str and booking["title"] in rooms:
                row[booking["title"]] = "Booked"
        table_data.append(row)
    return table_data



# Endpoint to fetch booking table data
@app.route('/table-data', methods=['GET'])
def table_data():
    return jsonify(generate_booking_table())

# Route to serve the main index.html
@app.route('/')
def index():
    table_data = generate_booking_table()  # Pass table data to the template
    return render_template('index.html', table_data=table_data)

@app.route('/book-room', methods=['POST'])
def book_room():
    data = request.json
    full_name = data.get('fullName')
    room = data.get('title')
    date = data.get('start')

    if not full_name or not room or not date:
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

    try:
        # Convert the date to the desired format (YYYY-MM-DD)
        formatted_date = datetime.strptime(date, '%a, %m/%d/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format.'}), 400

    bookings = load_bookings()

    # Check if the room is already booked for the given date
    for booking in bookings:
        if booking['start'] == formatted_date and booking['title'] == room:
            return jsonify({'success': False, 'message': 'Room is already booked.'}), 400

    # Add the new booking
    bookings.append({'fullName': full_name, 'title': room, 'start': formatted_date})
    save_bookings(bookings)

    return jsonify({'success': True})


# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'Server is running'})
    
# Endpoint to fetch the next two weeks of dates without weekends
@app.route('/available-dates', methods=['GET'])
def available_dates():
    today = datetime.now()
    dates = [
        (today + timedelta(days=i)).strftime('%a, %m/%d/%Y')
        for i in range(14)
        if (today + timedelta(days=i)).weekday() < 5  # Exclude Saturday (5) and Sunday (6)
    ]
    return jsonify(dates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
