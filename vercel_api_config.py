from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import random
import os

app = Flask(__name__)
CORS(app)

# In-memory storage for dining court hours (since SQLite doesn't work well on Vercel serverless)
DINING_COURTS = {
    'Earhart': {
        'breakfast': ('07:00', '10:00'),
        'lunch': ('11:00', '14:00'),
        'dinner': ('17:00', '20:00')
    },
    'Ford': {
        'breakfast': ('07:00', '10:00'),
        'lunch': ('11:00', '14:00'),
        'dinner': ('17:00', '20:00')
    },
    'Hillenbrand': {
        'breakfast': ('07:00', '10:00'),
        'lunch': ('11:00', '14:00'),
        'dinner': ('17:00', '20:00')
    },
    'Wiley': {
        'breakfast': ('07:00', '10:00'),
        'lunch': ('11:00', '14:00'),
        'dinner': ('17:00', '20:00')
    },
    'Windsor': {
        'breakfast': ('07:00', '10:00'),
        'lunch': ('11:00', '14:00'),
        'dinner': ('17:00', '20:00')
    }
}

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

def is_court_open(court_name):
    if court_name not in DINING_COURTS:
        return False
    
    now = datetime.now().time()
    court = DINING_COURTS[court_name]
    
    for meal_period, (start_str, end_str) in court.items():
        start = datetime.strptime(start_str, '%H:%M').time()
        end = datetime.strptime(end_str, '%H:%M').time()
        if start <= now <= end:
            return True
    
    return False

def get_open_courts():
    return [court for court in DINING_COURTS.keys() if is_court_open(court)]

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

def get_court_hours(court_name):
    if court_name in DINING_COURTS:
        court = DINING_COURTS[court_name]
        return {
            'breakfast': f"{court['breakfast'][0]} - {court['breakfast'][1]}",
            'lunch': f"{court['lunch'][0]} - {court['lunch'][1]}",
            'dinner': f"{court['dinner'][0]} - {court['dinner'][1]}"
        }
    return {}

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
    
    selected_court = random.choice(open_courts)
    menu = fetch_menu(selected_court)
    
    if not menu or not menu.get(meal_period):
        return jsonify({'error': f'No menu available for {selected_court}'}), 404
    
    items = menu[meal_period]
    mains, sides, desserts = categorize_items(items)
    
    result = {
        'dining_court': selected_court,
        'meal_period': meal_period,
        'main': random.choice(mains) if mains else {'name': 'No main available', 'calories': 'N/A'},
        'side': random.choice(sides) if sides else {'name': 'No side available', 'calories': 'N/A'},
        'dessert': random.choice(desserts) if desserts else {'name': 'No dessert available', 'calories': 'N/A'},
        'hours': get_court_hours(selected_court)
    }
    
    return jsonify(result)

# Vercel serverless function handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()