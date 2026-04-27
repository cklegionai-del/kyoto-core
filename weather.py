python
import requests

def get_weather():
    api_key = 'YOUR_API_KEY'  # Replace with your actual API key from a free weather service like OpenWeatherMap
    city = "Tunis"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        
        print(f"Weather in {city}:")
        print(f"Description: {weather_description}")
        print(f"Temperature: {temperature}°C")
        print(f"Humidity: {humidity}%")
    else:
        print("Failed to retrieve weather data")

def github_push(repo='kyoto-core', file='weather.py', content=''):
    import requests
    token = 'YOUR_GITHUB_TOKEN'  # Replace with your actual GitHub token
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/repos/{repo}/contents/{file}"
    data = {
        "message": "Add weather.py",
        "content": content.encode('utf-8').decode('latin1'),
        "branch": "main"
    }
    
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        print("File pushed to GitHub successfully")
    else:
        print(f"Failed to push file to GitHub: {response.text}")

if __name__ == "__main__":
    import io
    import sys
    
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    get_weather()
    
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    
    github_push(file='weather.py', content=output)
