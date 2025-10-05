# 🎲 Boilermaker Dining Roulette

A fun web app for indecisive Purdue students! Roll the dice and get a random full meal (main course, side, and dessert) from a currently open dining court.

## Features

✅ **Smart Time-Based Selection** - Only shows dining courts that are currently open  
✅ **Complete Meal Generation** - Random main, side, and dessert  
✅ **Nutritional Information** - Calories, protein, fat, and carbs for each item  
✅ **Dining Court Hours** - See when each court is open  
✅ **Purdue Styling** - Black and gold Boilermaker colors  
✅ **Dice Animation** - Fun rolling animation when generating meals  
✅ **Real-Time Data** - Fetches today's menus from Purdue's API  

## Project Structure

```
purdue-dining-roulette/
├── app.py              # Python Flask backend
├── index.html          # Frontend interface
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel deployment config
├── dining.db          # SQLite database (auto-generated)
└── README.md          # This file
```

## Local Development Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Clone/Create Project Directory
```bash
mkdir purdue-dining-roulette
cd purdue-dining-roulette
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Backend
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Step 4: Open the Frontend
Simply open `index.html` in your browser, or use a local server:

```bash
# Using Python's built-in server
python -m http.server 8000
```

Then visit `http://localhost:8000`

## How It Works

1. **User clicks the dice button** 🎲
2. **Backend checks current time** and identifies which dining courts are open
3. **Randomly selects an open dining court**
4. **Fetches today's menu** from Purdue's API
5. **Categorizes items** into mains, sides, and desserts
6. **Returns random meal** with nutritional info and dining court hours

## API Endpoints

### `GET /api/health`
Health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-10-05T14:30:00"
}
```

### `GET /api/open-courts`
Returns currently open dining courts
```json
{
  "open_courts": ["Earhart", "Wiley"],
  "meal_period": "Lunch",
  "current_time": "14:30"
}
```

### `GET /api/random-meal`
Generates a random meal from an open dining court
```json
{
  "dining_court": "Earhart",
  "meal_period": "Lunch",
  "main": {
    "name": "Grilled Chicken Breast",
    "calories": "250",
    "protein": "45",
    "fat": "5",
    "carbs": "2"
  },
  "side": {
    "name": "Steamed Broccoli",
    "calories": "55",
    "protein": "4",
    "fat": "1",
    "carbs": "10"
  },
  "dessert": {
    "name": "Chocolate Chip Cookie",
    "calories": "160",
    "protein": "2",
    "fat": "8",
    "carbs": "21"
  },
  "hours": {
    "breakfast": "07:00 - 10:00",
    "lunch": "11:00 - 14:00",
    "dinner": "17:00 - 20:00"
  }
}
```

## Deploying to Vercel

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login to Vercel
```bash
vercel login
```

### Step 3: Deploy
```bash
vercel
```

Follow the prompts to deploy your app!

### Step 4: Update API URL
After deployment, update the `API_URL` in `index.html`:
```javascript
const API_URL = 'https://your-app-name.vercel.app/api';
```

## Future Enhancements (v2)

- 🥗 **Dietary Filters** - Vegetarian, vegan, gluten-free options
- 👤 **User Accounts** - Save preferences and meal history
- 🔄 **Individual Re-rolls** - Re-roll just the main, side, or dessert
- 📱 **Mobile App** - Native iOS/Android app
- 📊 **Stats Dashboard** - Track most popular meals and courts
- 🗺️ **Campus Map** - Show dining court locations
- ⭐ **Ratings System** - Let users rate meals
- 🔔 **Notifications** - Alert when favorite foods are available

## Tech Stack

**Frontend:**
- HTML5
- CSS3 (with animations)
- Vanilla JavaScript

**Backend:**
- Python 3
- Flask (REST API)
- SQLite (database)
- Requests (HTTP library)

**External API:**
- Purdue Dining Court API (XML format)

## Dining Court Hours

| Dining Court | Breakfast | Lunch | Dinner |
|-------------|-----------|--------|---------|
| Earhart | 7:00-10:00 | 11:00-14:00 | 17:00-20:00 |
| Ford | 7:00-10:00 | 11:00-14:00 | 17:00-20:00 |
| Hillenbrand | 7:00-10:00 | 11:00-14:00 | 17:00-20:00 |
| Wiley | 7:00-10:00 | 11:00-14:00 | 17:00-20:00 |
| Windsor | 7:00-10:00 | 11:00-14:00 | 17:00-20:00 |

*Note: These are typical hours. Actual hours may vary by semester and holidays.*

## Troubleshooting

### Backend won't start
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is already in use
- Try running on a different port: `flask run --port=5001`

### Frontend shows "Backend not connected"
- Ensure the backend is running on `http://localhost:5000`
- Check browser console for CORS errors
- Verify the API_URL in index.html matches your backend URL

### No meals appearing
- Check if any dining courts are currently open (based on time)
- Verify Purdue's API is accessible: visit `http://api.hfs.purdue.edu/menus/v1/locations/Earhart/10-05-2025`
- Check backend logs for API fetch errors

### Database errors
- Delete `dining.db` and restart the app to recreate it
- Ensure write permissions in the project directory

## Database Schema

### dining_courts table
```sql
CREATE TABLE dining_courts (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    breakfast_start TEXT,
    breakfast_end TEXT,
    lunch_start TEXT,
    lunch_end TEXT,
    dinner_start TEXT,
    dinner_end TEXT
);
```

## Contributing

Want to add features? Here's how:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - Feel free to use this for your own projects!

## Credits

Created with ❤️ for Purdue students by a fellow Boilermaker

**Boiler Up! 🚂**

---

## Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
python app.py

# Open frontend (in another terminal)
python -m http.server 8000

# Deploy to Vercel
vercel
```

## Contact & Support

Having issues? Want to contribute? Reach out!

- 🐛 Report bugs
- 💡 Suggest features  
- ⭐ Star the project if you like it!

---

**Disclaimer:** This is an unofficial student project and is not affiliated with Purdue University or Purdue Dining Services.
