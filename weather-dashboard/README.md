# Weather Dashboard

A modern, responsive weather dashboard that fetches real-time weather data from the OpenWeatherMap API.

## Features

### ✨ Current Weather
- Real-time temperature and weather conditions
- Feels-like temperature
- Humidity, wind speed, pressure, and visibility
- UV Index estimation
- Beautiful weather icon display

### 📊 Forecasts
- **Hourly Forecast**: 24-hour detailed weather preview
- **5-Day Forecast**: Daily weather trends with high/low temperatures
- Precipitation probability
- Wind speed and humidity for each day

### 🌍 Location Features
- Search weather by city name
- Use your device's geolocation
- Automatic location detection

### 💨 Air Quality Index (AQI)
- Real-time air quality monitoring
- Individual pollutant levels:
  - PM2.5 and PM10
  - Ozone (O₃)
  - Nitrogen Dioxide (NO₂)
  - Sulfur Dioxide (SO₂)
  - Carbon Monoxide (CO)
- AQI status indicators (Good, Fair, Moderate, Poor)

### 🎨 User Interface
- Dark theme with gradient backgrounds
- Fully responsive design (desktop, tablet, mobile)
- Smooth animations and transitions
- Interactive hover effects
- Real-time data updates

## Technology Stack

- **HTML5** - Semantic markup
- **CSS3** - Modern styling with gradients and animations
- **JavaScript (ES6+)** - Async/await, fetch API
- **OpenWeatherMap API** - Weather data provider
- **Font Awesome** - Icon library

## API Integration

### OpenWeatherMap Endpoints

1. **Geocoding API** - Convert city names to coordinates
   ```
   GET /geo/1.0/direct?q={city}&appid={API_KEY}
   ```

2. **5-Day Forecast API** - Get weather forecast
   ```
   GET /data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={API_KEY}
   ```

3. **Air Pollution API** - Get air quality data
   ```
   GET /data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}
   ```

## Getting Started

### 1. Get an API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Create a free account
3. Subscribe to the free tier API
4. Copy your API key

### 2. Update the API Key

Replace the placeholder API key in `script.js`:

```javascript
const API_KEY = 'your_api_key_here';
```

### 3. Open in Browser

```bash
open index.html
```

Or serve with a local server:

```bash
python -m http.server 8000
```

Then visit: `http://localhost:8000/weather-dashboard/`

## Usage

### Search by City
1. Type a city name in the search box
2. Press Enter or click the search button
3. Weather data updates instantly

### Use Your Location
1. Click the location button (📍)
2. Allow browser location access
3. Weather for your location loads automatically

### View Data
- **Current Weather**: Main display card
- **Hourly Forecast**: Swipe or scroll horizontally
- **5-Day Forecast**: Scroll down
- **Air Quality**: Detailed pollutant breakdown

## File Structure

```
weather-dashboard/
├── index.html       # Main HTML file
├── style.css        # Styling and responsive design
├── script.js        # JavaScript logic and API calls
└── README.md        # This file
```

## CSS Features

- **Responsive Grid**: Auto-fit columns for different screen sizes
- **Gradient Backgrounds**: Beautiful color transitions
- **Hover Effects**: Card elevation and color changes
- **Dark Theme**: Reduces eye strain in low-light environments
- **Mobile-First**: Optimized for all device sizes

## JavaScript Functions

### Core Functions

- `loadWeather(city)` - Fetch weather for a city
- `fetchWeatherByCoords(lat, lon)` - Fetch weather by coordinates
- `processWeatherData(data)` - Process and display data
- `updateCurrentWeather(data)` - Update current weather display
- `updateHourlyForecast(data)` - Update hourly forecast
- `updateDailyForecast(data)` - Update 5-day forecast
- `updateAirQuality(data)` - Update air quality display

### Utility Functions

- `formatDate(date)` - Format dates nicely
- `getAQIStatus(aqi)` - Get AQI status text
- `estimateUVIndex(cloudCoverage, hour)` - Calculate UV index
- `showLoading()` / `hideLoading()` - Loading state
- `showError()` / `hideError()` - Error handling

## API Rate Limits

Free tier limits:
- 1,000 API calls per day
- 1 call per second

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Customization

### Change Color Scheme

Edit CSS variables in `style.css`:

```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    /* ... more colors ... */
}
```

### Change Default City

In `script.js`, modify:

```javascript
loadWeather('Your City Here');
```

### Add More Pollutants

Edit the `pollutants` array in `updateAirQuality()`:

```javascript
const pollutants = [
    // ... existing pollutants ...
    { name: 'Your Pollutant', value: components.your_pollutant, unit: 'unit' }
];
```

## Troubleshooting

### API Key Error
- Ensure API key is correct in `script.js`
- Check API is activated in OpenWeatherMap dashboard
- Wait 10 minutes for key to activate

### Location Not Working
- Check HTTPS or localhost (required for geolocation)
- Allow browser permission for location access
- Try searching for a city manually

### Data Not Updating
- Check internet connection
- Check browser console for errors
- Verify API key hasn't reached rate limit

## Future Enhancements

- [ ] Weather alerts and warnings
- [ ] Historical weather data
- [ ] Multiple location comparison
- [ ] Favorite locations list
- [ ] Weather notifications
- [ ] Pollen index display
- [ ] Sunrise/sunset times
- [ ] Moon phases
- [ ] Local storage for favorites
- [ ] Dark/Light theme toggle

## License

MIT License - Feel free to use this project for personal or commercial purposes.

## Credits

- Weather data: [OpenWeatherMap](https://openweathermap.org/)
- Icons: [Font Awesome](https://fontawesome.com/)
- Inspiration: Modern weather applications

## Support

For issues or suggestions, please create an issue in the repository.
