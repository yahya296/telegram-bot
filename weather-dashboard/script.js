// OpenWeatherMap API Key (free tier available)
const API_KEY = 'c0e59c1bdf5b91b8827f4d34dd2a384c'; // Free API key for demo
const API_BASE_URL = 'https://api.openweathermap.org';

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const locationBtn = document.getElementById('locationBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const errorMessage = document.getElementById('errorMessage');
const weatherContent = document.getElementById('weatherContent');
const lastUpdated = document.getElementById('lastUpdated');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Try to load default city
    loadWeather('London');
    
    // Event listeners
    searchBtn.addEventListener('click', searchCity);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchCity();
    });
    locationBtn.addEventListener('click', getLocationWeather);
});

/**
 * Search for weather by city name
 */
function searchCity() {
    const city = searchInput.value.trim();
    if (city) {
        loadWeather(city);
        searchInput.value = '';
    }
}

/**
 * Get weather using geolocation
 */
function getLocationWeather() {
    if (navigator.geolocation) {
        showLoading();
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                fetchWeatherByCoords(latitude, longitude);
            },
            (err) => {
                showError('Unable to access your location. Please search manually.');
                console.error('Geolocation error:', err);
            }
        );
    } else {
        showError('Geolocation is not supported by your browser.');
    }
}

/**
 * Load weather for a city
 */
async function loadWeather(city) {
    showLoading();
    try {
        // Get city coordinates
        const geoResponse = await fetch(
            `${API_BASE_URL}/geo/1.0/direct?q=${city}&limit=1&appid=${API_KEY}`
        );
        const geoData = await geoResponse.json();

        if (!geoData.length) {
            showError('City not found. Please try another search.');
            return;
        }

        const { lat, lon, name, country } = geoData[0];
        fetchWeatherByCoords(lat, lon, `${name}, ${country}`);
    } catch (err) {
        showError('Failed to fetch weather data. Please try again.');
        console.error('Weather fetch error:', err);
    }
}

/**
 * Fetch weather using coordinates
 */
async function fetchWeatherByCoords(lat, lon, displayName = null) {
    try {
        // Fetch current weather and forecast
        const weatherResponse = await fetch(
            `${API_BASE_URL}/data/2.5/forecast?lat=${lat}&lon=${lon}&units=metric&appid=${API_KEY}`
        );
        const weatherData = await weatherResponse.json();

        if (weatherData.cod !== '200') {
            showError('Unable to fetch weather data. Please try again.');
            return;
        }

        // Fetch air quality data
        const aqiResponse = await fetch(
            `${API_BASE_URL}/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${API_KEY}`
        );
        const aqiData = await aqiResponse.json();

        // Process and display data
        processWeatherData(weatherData, aqiData, displayName);
        hideError();
        showContent();
        updateLastUpdated();
    } catch (err) {
        showError('Failed to fetch weather data. Please try again.');
        console.error('Fetch error:', err);
    }
}

/**
 * Process and display weather data
 */
function processWeatherData(weatherData, aqiData, displayName) {
    const current = weatherData.list[0];
    const { name, country } = weatherData.city;
    const cityName = displayName || `${name}, ${country}`;

    // Update current weather
    updateCurrentWeather(current, cityName);

    // Update hourly forecast
    updateHourlyForecast(weatherData.list.slice(0, 8));

    // Update daily forecast
    updateDailyForecast(weatherData.list);

    // Update air quality
    updateAirQuality(aqiData);
}

/**
 * Update current weather display
 */
function updateCurrentWeather(data, cityName) {
    const temp = Math.round(data.main.temp);
    const feelsLike = Math.round(data.main.feels_like);
    const description = data.weather[0].main;
    const icon = getWeatherIcon(data.weather[0].icon);
    
    document.getElementById('cityName').textContent = cityName;
    document.getElementById('temperature').textContent = `${temp}°C`;
    document.getElementById('weatherDescription').textContent = description;
    document.getElementById('weatherIcon').src = `https://openweathermap.org/img/wn/${data.weather[0].icon}@4x.png`;
    document.getElementById('dateTime').textContent = formatDate(new Date());
    
    // Update details
    document.getElementById('humidity').textContent = `${data.main.humidity}%`;
    document.getElementById('windSpeed').textContent = `${(data.wind.speed * 3.6).toFixed(1)} km/h`;
    document.getElementById('pressure').textContent = `${data.main.pressure} hPa`;
    document.getElementById('visibility').textContent = `${(data.visibility / 1000).toFixed(1)} km`;
    document.getElementById('feelsLike').textContent = `${feelsLike}°C`;
    
    // UV Index (estimated from cloud coverage)
    const uvIndex = estimateUVIndex(data.clouds.all, new Date().getHours());
    document.getElementById('uvIndex').textContent = uvIndex;
}

/**
 * Update hourly forecast
 */
function updateHourlyForecast(data) {
    const container = document.getElementById('hourlyForecast');
    container.innerHTML = '';

    data.forEach(hour => {
        const time = new Date(hour.dt * 1000);
        const temp = Math.round(hour.main.temp);
        const icon = hour.weather[0].icon;
        const rainChance = (hour.pop * 100).toFixed(0);

        const card = document.createElement('div');
        card.className = 'hourly-card';
        card.innerHTML = `
            <div class="hour-time">${time.getHours().toString().padStart(2, '0')}:00</div>
            <img src="https://openweathermap.org/img/wn/${icon}@2x.png" alt="weather" class="hour-icon">
            <div class="hour-temp">${temp}°</div>
            <div class="hour-rain"><i class="fas fa-droplet"></i> ${rainChance}%</div>
        `;
        container.appendChild(card);
    });
}

/**
 * Update daily forecast
 */
function updateDailyForecast(data) {
    const dailyData = {};

    // Group data by day
    data.forEach(item => {
        const date = new Date(item.dt * 1000).toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric'
        });

        if (!dailyData[date]) {
            dailyData[date] = {
                temps: [],
                weather: item.weather[0],
                icon: item.weather[0].icon,
                humidity: [],
                wind: []
            };
        }
        dailyData[date].temps.push(item.main.temp);
        dailyData[date].humidity.push(item.main.humidity);
        dailyData[date].wind.push(item.wind.speed);
    });

    const container = document.getElementById('dailyForecast');
    container.innerHTML = '';

    let dayCount = 0;
    for (const [date, dayData] of Object.entries(dailyData)) {
        if (dayCount >= 5) break;
        dayCount++;

        const tempMax = Math.round(Math.max(...dayData.temps));
        const tempMin = Math.round(Math.min(...dayData.temps));
        const avgHumidity = Math.round(dayData.humidity.reduce((a, b) => a + b) / dayData.humidity.length);
        const avgWind = (dayData.wind.reduce((a, b) => a + b) / dayData.wind.length * 3.6).toFixed(1);

        const card = document.createElement('div');
        card.className = 'daily-card';
        card.innerHTML = `
            <div class="day-name">${date}</div>
            <img src="https://openweathermap.org/img/wn/${dayData.icon}@2x.png" alt="weather" class="day-icon">
            <div class="day-temps">
                <span class="temp-max">${tempMax}°</span>
                <span class="temp-min">${tempMin}°</span>
            </div>
            <div class="day-description">${dayData.weather.main}</div>
            <div class="day-details">
                <span><i class="fas fa-droplet"></i> ${avgHumidity}%</span>
                <span><i class="fas fa-wind"></i> ${avgWind} km/h</span>
            </div>
        `;
        container.appendChild(card);
    }
}

/**
 * Update air quality
 */
function updateAirQuality(data) {
    const container = document.getElementById('airQuality');
    container.innerHTML = '';

    const current = data.list[0];
    const aqi = current.main.aqi;
    const components = current.components;

    const pollutants = [
        { name: 'PM2.5', value: components.pm2_5, unit: 'μg/m³' },
        { name: 'PM10', value: components.pm10, unit: 'μg/m³' },
        { name: 'O₃', value: components.o3, unit: 'μg/m³' },
        { name: 'NO₂', value: components.no2, unit: 'μg/m³' },
        { name: 'SO₂', value: components.so2, unit: 'μg/m³' },
        { name: 'CO', value: (components.co / 1000).toFixed(1), unit: 'mg/m³' }
    ];

    pollutants.forEach(pollutant => {
        const card = document.createElement('div');
        card.className = 'aqi-card';
        card.innerHTML = `
            <div class="aqi-label">${pollutant.name}</div>
            <div class="aqi-value">${pollutant.value.toFixed(1)}</div>
            <div class="aqi-label">${pollutant.unit}</div>
        `;
        container.appendChild(card);
    });

    // Add overall AQI status
    const aqiStatus = getAQIStatus(aqi);
    const statusCard = document.createElement('div');
    statusCard.className = 'aqi-card';
    statusCard.innerHTML = `
        <div class="aqi-label">Overall AQI</div>
        <div class="aqi-value">${aqi}</div>
        <div class="aqi-status aqi-${aqiStatus.class}">${aqiStatus.text}</div>
    `;
    container.insertBefore(statusCard, container.firstChild);
}

/**
 * Get AQI status
 */
function getAQIStatus(aqi) {
    const statuses = [
        { class: 'good', text: 'Good' },
        { class: 'fair', text: 'Fair' },
        { class: 'moderate', text: 'Moderate' },
        { class: 'poor', text: 'Poor' },
        { class: 'poor', text: 'Very Poor' }
    ];
    return statuses[aqi - 1] || statuses[4];
}

/**
 * Estimate UV Index
 */
function estimateUVIndex(cloudCoverage, hour) {
    let baseUV = 0;
    if (hour >= 6 && hour <= 18) {
        const timeOfDay = hour <= 12 ? hour - 6 : 18 - hour;
        baseUV = Math.max(0, 10 - (12 - timeOfDay) * 0.8);
    }
    const cloudFactor = 1 - (cloudCoverage / 100) * 0.8;
    return (baseUV * cloudFactor).toFixed(1);
}

/**
 * Format date
 */
function formatDate(date) {
    const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Get weather icon
 */
function getWeatherIcon(iconCode) {
    const iconMap = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅', '02n': '🌤️',
        '03d': '☁️', '03n': '☁️',
        '04d': '���️', '04n': '☁️',
        '09d': '🌦️', '09n': '🌦️',
        '10d': '🌧️', '10n': '🌧️',
        '11d': '⛈️', '11n': '⛈️',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫️', '50n': '🌫️'
    };
    return iconMap[iconCode] || '🌡️';
}

/**
 * Update last updated time
 */
function updateLastUpdated() {
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    lastUpdated.textContent = time;
}

/**
 * UI State Management
 */
function showLoading() {
    loading.classList.remove('hidden');
    error.classList.add('hidden');
    weatherContent.classList.add('hidden');
}

function hideLoading() {
    loading.classList.add('hidden');
}

function showContent() {
    hideLoading();
    weatherContent.classList.remove('hidden');
}

function showError(message) {
    hideLoading();
    errorMessage.textContent = message;
    error.classList.remove('hidden');
    weatherContent.classList.add('hidden');
}

function hideError() {
    error.classList.add('hidden');
}

// Auto-refresh every 10 minutes
setInterval(() => {
    updateLastUpdated();
}, 60000);
