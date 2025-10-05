from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('dining.db')
    c = conn.cursor()
    
    # Create dining courts table with hours
    c.execute('''CREATE TABLE IF NOT EXISTS dining_courts
                 (id INTEGER PRIMARY KEY,
                  name TEXT UNIQUE,
                  breakfast_start TEXT,
                  breakfast_end TEXT,
                  lunch_start TEXT,
                  lunch_end TEXT,
                  dinner_start TEXT,
                  dinner_end TEXT)''')
    
    # Insert dining court hours (typical schedule)
    courts_hours = [
        ('Earhart', '07:00', '10:00', '11:00', '14:00', '17:00', '20:00'),
        ('Ford', '07:00', '10:00', '11:00', '14:00', '17:00', '20:00'),
        ('Hillenbrand', '07:00', '10:00', '11:00', '14:00', '17:00', '20:00'),
        ('Wiley', '07:00', '10:00', '11:00', '14:00', '17:00', '20:00'),
        ('Windsor', '07:00', '10:00', '11:00', '14:00', '17:00', '20:00')
    ]
    
    c.executemany('''INSERT OR IGNORE INTO dining_courts 
                     (name, breakfast_start, breakfast_end, lunch_start, lunch_end, dinner_start, dinner_end)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', courts_hours)
    
    conn.commit()
    conn.close()

# Get current meal period
def get_meal_period():
    now = datetime.now().time()
    hour = now.hour
    
    if 7 <= hour < 10:
        return 'Breakfast'
    elif 11 <= hour < 14:
        return 'Lunch'
    elif 17 <= hour < 20:
        return 'Dinner'
    else:
        return None

# Check if dining court is open
def is_court_open(court_name):
    conn = sqlite3.connect('dining.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM dining_courts WHERE name = ?', (court_name,))
    court = c.fetchone()
    conn.close()
    
    if not court:
        return False
    
    now = datetime.now().time()
    current_hour = now.hour
    current_minute = now.minute
    
    # Check breakfast
    if court[2] and court[3]:
        start = datetime.strptime(court[2], '%H:%M').time()
        end = datetime.strptime(court[3], '%H:%M').time()
        if start <= now <= end:
            return True
    
    # Check lunch
    if court[4] and court[5]:
        start = datetime.strptime(court[4], '%H:%M').time()
        end = datetime.strptime(court[5], '%H:%M').time()
        if start <= now <= end:
            return True
    
    # Check dinner
    if court[6] and court[7]:
        start = datetime.strptime(court[6], '%H:%M').time()
        end = datetime.strptime(court[7], '%H:%M').time()
        if start <= now <= end:
            return True
    
    return False

# Get open dining courts
def get_open_courts():
    conn = sqlite3.connect('dining.db')
    c = conn.cursor()
    c.execute('SELECT name FROM dining_courts')
    all_courts = [row[0] for row in c.fetchall()]
    conn.close()
    
    open_courts = [court for court in all_courts if is_court_open(court)]
    return open_courts

# Fetch menu from Purdue API
def fetch_menu(dining_court, date=None):
    if date is None:
        date = datetime.now().strftime('%m-%d-%Y')
    
    url = f'http://api.hfs.purdue.edu/menus/v1/locations/{dining_court}/{date}'
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return parse_menu_xml(response.content)
        return None
    except Exception as e:
        print(f"Error fetching menu: {e}")
        return None

# Parse XML menu
def parse_menu_xml(xml_content):
    try:
        root = ET.fromstring(xml_content)
        menu = {'Breakfast': [], 'Lunch': [], 'Dinner': []}
        
        for meal in root.findall('.//Meal'):
            meal_name = meal.get('Name')
            if meal_name in menu:
                for station in meal.findall('.//Station'):
                    for item in station.findall('.//Item'):
                        item_data = {
                            'name': item.find('Name').text if item.find('Name') is not None else 'Unknown',
                            'isVegetarian': item.get('IsVegetarian') == 'True',
                            'calories': item.find('.//Calories').text if item.find('.//Calories') is not None else 'N/A',
                            'protein': item.find('.//Protein').text if item.find('.//Protein') is not None else 'N/A',
                            'fat': item.find('.//TotalFat').text if item.find('.//TotalFat') is not None else 'N/A',
                            'carbs': item.find('.//Carbohydrates').text if item.find('.//Carbohydrates') is not None else 'N/A'
                        }
                        menu[meal_name].append(item_data)
        
        return menu
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None

# Categorize items
def categorize_items(items):
    mains = []
    sides = []
    desserts = []
    
    dessert_keywords = ['cookie', 'cake', 'brownie', 'ice cream', 'pie', 'pudding', 'dessert']
    side_keywords = ['fries', 'rice', 'beans', 'salad', 'vegetables', 'potato', 'corn', 'green beans']
    
    for item in items:
        name_lower = item['name'].lower()
        
        if any(keyword in name_lower for keyword in dessert_keywords):
            desserts.append(item)
        elif any(keyword in name_lower for keyword in side_keywords):
            sides.append(item)
        else:
            mains.append(item)
    
    return mains, sides, desserts

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/open-courts', methods=['GET'])
def open_courts():
    courts = get_open_courts()
    meal_period = get_meal_period()
    return jsonify({
        'open_courts': courts,
        'meal_period': meal_period,
        'current_time': datetime.now().strftime('%H:%M')
    })

@app.route('/api/random-meal', methods=['GET'])
def random_meal():
    open_courts = get_open_courts()
    meal_period = get_meal_period()
    
    if not open_courts:
        return jsonify({'error': 'No dining courts are currently open'}), 404
    
    if not meal_period:
        return jsonify({'error': 'No meal period is currently active'}), 404
    
    # Pick random court
    selected_court = random.choice(open_courts)
    
    # Fetch menu
    menu = fetch_menu(selected_court)
    
    if not menu or not menu.get(meal_period):
        return jsonify({'error': f'No menu available for {selected_court}'}), 404
    
    items = menu[meal_period]
    mains, sides, desserts = categorize_items(items)
    
    # Select random items
    result = {
        'dining_court': selected_court,
        'meal_period': meal_period,
        'main': random.choice(mains) if mains else {'name': 'No main available', 'calories': 'N/A'},
        'side': random.choice(sides) if sides else {'name': 'No side available', 'calories': 'N/A'},
        'dessert': random.choice(desserts) if desserts else {'name': 'No dessert available', 'calories': 'N/A'},
        'hours': get_court_hours(selected_court)
    }
    
    return jsonify(result)

def get_court_hours(court_name):
    conn = sqlite3.connect('dining.db')
    c = conn.cursor()
    c.execute('SELECT * FROM dining_courts WHERE name = ?', (court_name,))
    court = c.fetchone()
    conn.close()
    
    if court:
        return {
            'breakfast': f"{court[2]} - {court[3]}" if court[2] else 'Closed',
            'lunch': f"{court[4]} - {court[5]}" if court[4] else 'Closed',
            'dinner': f"{court[6]} - {court[7]}" if court[6] else 'Closed'
        }
    return {}

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)