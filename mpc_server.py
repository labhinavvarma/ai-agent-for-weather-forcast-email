import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from fpdf import FPDF
import ollama  # Import Ollama for AI integration

# ====================== Resources ======================
class WeatherAPI:
    @staticmethod
    def fetch_weather():
        # Open-Meteo API endpoint for current weather
        url = "https://api.open-meteo.com/v1/forecast?latitude=33.7490&longitude=-84.3880&current_weather=true"
        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_json = response.json()

            # Extract relevant weather data
            temperature = weather_json['current_weather']['temperature']
            wind_speed = weather_json['current_weather']['windspeed']
            weather_code = weather_json['current_weather']['weathercode']

            # Map weather code to a human-readable condition
            weather_conditions = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Fog",
                48: "Depositing rime fog",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                56: "Light freezing drizzle",
                57: "Dense freezing drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                66: "Light freezing rain",
                67: "Heavy freezing rain",
                71: "Slight snow fall",
                73: "Moderate snow fall",
                75: "Heavy snow fall",
                77: "Snow grains",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                85: "Slight snow showers",
                86: "Heavy snow showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail",
            }
            condition = weather_conditions.get(weather_code, "Unknown")

            # Format the weather data
            return f"{condition}, {temperature}°C, {wind_speed} km/h"
        except Exception as e:
            print(f"Failed to fetch weather data: {e}")
            return None


# ====================== Tools ======================
class PDFGenerator:
    @staticmethod
    def generate_pdf(weather_data, weather_description, filename="weather_report.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add a title
        pdf.cell(200, 10, txt="Daily Atlanta Weather Report", ln=True, align="C")

        # Add weather data
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"Weather Data:\n{weather_data}")

        # Add AI-generated weather description
        if weather_description:
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=f"Weather Description:\n{weather_description}")

        # Save the PDF
        pdf.output(filename)
        print(f"PDF created: {filename}")


class EmailSender:
    @staticmethod
    def send_email(email_address, email_password, recipient_email, subject, body, pdf_filename):
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the body of the email
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF file
        with open(pdf_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {pdf_filename}",
            )
            msg.attach(part)

        # Connect to the SMTP server and send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()  # Upgrade the connection to secure
            server.login(email_address, email_password)
            server.sendmail(email_address, recipient_email, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()


# ====================== Prompts ======================
class WeatherPrompt:
    @staticmethod
    def generate_description_prompt(weather_data):
        return f"Write a brief and professional description of the weather in Atlanta based on this data: {weather_data}."


# ====================== MPC Server ======================
class MPCServer:
    def __init__(self):
        self.weather_data = None
        self.weather_description = None
        self.pdf_filename = "atlanta_weather_report.pdf"

    def fetch_weather(self):
        self.weather_data = WeatherAPI.fetch_weather()

    def generate_description(self):
        if not self.weather_data:
            print("No weather data available to generate description.")
            return

        prompt = WeatherPrompt.generate_description_prompt(self.weather_data)
        try:
            # Specify the model name as "mistral"
            response = ollama.generate(model="mistral", prompt=prompt)
            self.weather_description = response['response']
            print("Weather description generated successfully.")
        except Exception as e:
            print(f"Failed to generate weather description: {e}")
            self.weather_description = None

    def generate_pdf(self):
        if not self.weather_data:
            print("No weather data available to generate PDF.")
            return

        PDFGenerator.generate_pdf(self.weather_data, self.weather_description, self.pdf_filename)

    def send_email(self, email_address, email_password, recipient_email):
        if not self.weather_data:
            print("No weather data available to send email.")
            return

        email_subject = "Daily Atlanta Weather Report"
        email_body = "Please find the daily Atlanta weather report attached as a PDF.\n\n"
        if self.weather_description:
            email_body += f"Weather Description:\n{self.weather_description}"

        EmailSender.send_email(email_address, email_password, recipient_email, email_subject, email_body, self.pdf_filename)








"""
Weather Forecast Application with Model Context Protocol Architecture

This implementation explicitly organizes code around the 5 key MCP components:
1. Client - Main application that orchestrates the workflow
2. Server - MCP-compatible API endpoints
3. Tools - Functional components for specific tasks (weather, email)
4. Prompts - Structured interactions with the AI model
5. Resources - Data objects with standard interfaces
"""

import os
import json
import smtplib
import uvicorn
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any, Union

# ------------------------------------------------------------------------
# 5. RESOURCES - Data objects with standard interfaces
# ------------------------------------------------------------------------

class Config(BaseModel):
    """Configuration resource for application settings"""
    email_address: str = "raomadhav653@gmail.com"
    email_password: str = "fxux rpsu qlzz bxpl"
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    anthropic_api_key: Optional[str] = ""
    
    class Config:
        validate_assignment = True


class WeatherCodes(BaseModel):
    """Weather code mapping resource"""
    codes: Dict[int, tuple] = {
        0: ("Clear sky", "☀️"),
        1: ("Mainly clear", "🌤️"),
        2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"),
        45: ("Fog", "🌫️"),
        48: ("Depositing rime fog", "🌫️"),
        51: ("Light drizzle", "🌦️"),
        53: ("Moderate drizzle", "🌦️"),
        55: ("Dense drizzle", "🌧️"),
        56: ("Light freezing drizzle", "🌨️"),
        57: ("Dense freezing drizzle", "🌨️"),
        61: ("Slight rain", "🌦️"),
        63: ("Moderate rain", "🌧️"),
        65: ("Heavy rain", "🌧️"),
        66: ("Light freezing rain", "🌨️"),
        67: ("Heavy freezing rain", "🌨️"),
        71: ("Slight snow fall", "🌨️"),
        73: ("Moderate snow fall", "🌨️"),
        75: ("Heavy snow fall", "❄️"),
        77: ("Snow grains", "❄️"),
        80: ("Slight rain showers", "🌦️"),
        81: ("Moderate rain showers", "🌧️"),
        82: ("Violent rain showers", "⛈️"),
        85: ("Slight snow showers", "🌨️"),
        86: ("Heavy snow showers", "❄️"),
        95: ("Thunderstorm", "⛈️"),
        96: ("Thunderstorm with slight hail", "⛈️"),
        99: ("Thunderstorm with heavy hail", "⛈️")
    }
    
    def get_description(self, code: int) -> tuple:
        """Get weather description and icon from code"""
        return self.codes.get(code, ("Unknown", "❓"))


class LocationCoordinates(BaseModel):
    """Location resource with geographical information"""
    latitude: float
    longitude: float
    name: str
    country: str = ""
    admin1: str = ""


class WeatherData(BaseModel):
    """Structured weather data resource"""
    location: Dict[str, Any]
    current: Dict[str, Any]
    hourly: List[Dict[str, Any]] = []
    forecast: List[Dict[str, Any]] = []
    ai_report: str = ""


class EmailRequest(BaseModel):
    """Email request resource"""
    recipient_email: EmailStr
    location_name: str
    location_admin1: str
    location_country: str
    ai_report: str


# ------------------------------------------------------------------------
# 3. TOOLS - Functional components for specific tasks
# ------------------------------------------------------------------------

class WeatherTools:
    """Tools for weather data retrieval and processing"""
    
    def __init__(self, weather_codes: WeatherCodes):
        """Initialize with required resources"""
        self.weather_codes = weather_codes
    
    def get_coordinates(self, location_name: str) -> Optional[dict]:
        """Get coordinates for a location using Open-Meteo Geocoding API"""
        try:
            geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location_name}&count=1&language=en&format=json"
            response = requests.get(geocoding_url)
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return {
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "name": result["name"],
                    "country": result.get("country", ""),
                    "admin1": result.get("admin1", "")
                }
            else:
                return None
        except Exception as e:
            print(f"Error fetching location data: {str(e)}")
            return None
    
    def fetch_weather_data(self, latitude: float, longitude: float) -> dict:
        """Fetch weather data from Open-Meteo API"""
        result = {
            "current": None,
            "forecast": None,
            "hourly": None
        }
        
        try:
            # Current weather data
            current_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,surface_pressure&temperature_unit=fahrenheit&wind_speed_unit=mph"
            current_response = requests.get(current_url)
            if current_response.status_code == 200:
                result["current"] = current_response.json()
        except Exception as e:
            print(f"Error fetching current weather data: {str(e)}")
        
        try:
            # 5-day forecast data
            forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,sunrise,sunset,uv_index_max&timezone=auto&temperature_unit=fahrenheit&forecast_days=5"
            forecast_response = requests.get(forecast_url)
            if forecast_response.status_code == 200:
                result["forecast"] = forecast_response.json()
        except Exception as e:
            print(f"Error fetching forecast data: {str(e)}")
        
        try:
            # Hourly forecast for today
            hourly_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation_probability,weather_code&timezone=auto&temperature_unit=fahrenheit&forecast_days=1"
            hourly_response = requests.get(hourly_url)
            if hourly_response.status_code == 200:
                result["hourly"] = hourly_response.json()
        except Exception as e:
            print(f"Error fetching hourly data: {str(e)}")
        
        return result
    
    def process_weather_data(self, weather_data: dict, location_info: dict) -> Optional[dict]:
        """Process and format weather data for template rendering"""
        # Check for valid data
        if not weather_data or not location_info:
            return None
        
        processed_data = {"location": location_info}
        
        # Process current weather - with error handling
        try:
            if weather_data.get("current") and "current" in weather_data["current"]:
                current = weather_data["current"]["current"]
                weather_code = current.get("weather_code", 0)
                weather_description, weather_icon = self.weather_codes.get_description(weather_code)
                
                processed_data["current"] = {
                    "temperature": round(current.get("temperature_2m", 0), 1),
                    "feels_like": round(current.get("apparent_temperature", 0), 1),
                    "humidity": round(current.get("relative_humidity_2m", 0)),
                    "wind_speed": round(current.get("wind_speed_10m", 0), 1),
                    "precipitation": round(current.get("precipitation", 0), 2),
                    "pressure": round(current.get("surface_pressure", 1000)),
                    "weather_code": weather_code,
                    "weather_description": weather_description,
                    "weather_icon": weather_icon,
                    "date": datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
                }
            else:
                # Default current weather if data is missing
                processed_data["current"] = {
                    "temperature": 0,
                    "feels_like": 0,
                    "humidity": 0,
                    "wind_speed": 0,
                    "precipitation": 0,
                    "pressure": 1000,
                    "weather_code": 0,
                    "weather_description": "Data unavailable",
                    "weather_icon": "❓",
                    "date": datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
                }
        except Exception as e:
            print(f"Error processing current weather: {str(e)}")
            # Default current weather on error
            processed_data["current"] = {
                "temperature": 0,
                "feels_like": 0,
                "humidity": 0, 
                "wind_speed": 0,
                "precipitation": 0,
                "pressure": 1000,
                "weather_code": 0,
                "weather_description": "Error processing data",
                "weather_icon": "❓",
                "date": datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
            }
        
        # Process hourly forecast - with error handling
        current_hour = datetime.now().hour
        hourly_data = []
        
        try:
            if weather_data.get("hourly") and "hourly" in weather_data["hourly"]:
                hourly = weather_data["hourly"]["hourly"]
                
                if "time" in hourly and "temperature_2m" in hourly:
                    hours_processed = 0
                    hourly_times = hourly["time"]
                    hourly_temps = hourly["temperature_2m"]
                    hourly_precip = hourly.get("precipitation_probability", [0] * len(hourly_times))
                    hourly_weather_codes = hourly.get("weather_code", [0] * len(hourly_times))
                    
                    for i in range(len(hourly_times)):
                        if i < len(hourly_times) and i < len(hourly_temps):
                            try:
                                hour_time = datetime.fromisoformat(hourly_times[i].replace("Z", "+00:00"))
                                if hour_time.hour >= current_hour and hours_processed < 12:
                                    weather_code = hourly_weather_codes[i] if i < len(hourly_weather_codes) else 0
                                    weather_description, weather_icon = self.weather_codes.get_description(weather_code)
                                    
                                    precipitation_prob = hourly_precip[i] if i < len(hourly_precip) else 0
                                    
                                    hourly_data.append({
                                        "time": hour_time.strftime("%I %p"),
                                        "temperature": round(hourly_temps[i], 1),
                                        "precipitation_prob": precipitation_prob,
                                        "weather_description": weather_description,
                                        "weather_icon": weather_icon
                                    })
                                    hours_processed += 1
                            except Exception as e:
                                print(f"Error processing hour {i}: {str(e)}")
        except Exception as e:
            print(f"Error processing hourly forecast: {str(e)}")
        
        # If no hourly data was processed, add default placeholders
        if not hourly_data:
            for i in range(12):
                hour = (current_hour + i) % 24
                hour_display = hour if hour != 0 else 12
                am_pm = "AM" if hour < 12 else "PM"
                if hour_display > 12:
                    hour_display -= 12
                    
                hourly_data.append({
                    "time": f"{hour_display} {am_pm}",
                    "temperature": processed_data["current"]["temperature"],
                    "precipitation_prob": 0,
                    "weather_description": "Forecast unavailable",
                    "weather_icon": "❓"
                })
        
        processed_data["hourly"] = hourly_data
        
        # Process 5-day forecast - with error handling
        forecast_data = []
        
        try:
            if weather_data.get("forecast") and "daily" in weather_data["forecast"]:
                forecast = weather_data["forecast"]["daily"]
                
                if "time" in forecast and "temperature_2m_max" in forecast and "temperature_2m_min" in forecast:
                    for i in range(min(5, len(forecast["time"]))):
                        try:
                            date_str = forecast["time"][i]
                            date_obj = datetime.fromisoformat(date_str)
                            
                            weather_code = forecast["weather_code"][i] if "weather_code" in forecast and i < len(forecast["weather_code"]) else 0
                            weather_description, weather_icon = self.weather_codes.get_description(weather_code)
                            
                            max_temp = forecast["temperature_2m_max"][i] if i < len(forecast["temperature_2m_max"]) else 0
                            min_temp = forecast["temperature_2m_min"][i] if i < len(forecast["temperature_2m_min"]) else 0
                            precipitation = forecast["precipitation_sum"][i] if "precipitation_sum" in forecast and i < len(forecast["precipitation_sum"]) else 0
                            uv_index = forecast["uv_index_max"][i] if "uv_index_max" in forecast and i < len(forecast["uv_index_max"]) else 0
                            
                            forecast_data.append({
                                "date": date_obj.strftime("%A, %b %d"),
                                "day": date_obj.strftime("%A"),
                                "date_short": date_obj.strftime("%b %d"),
                                "max_temp": round(max_temp, 1),
                                "min_temp": round(min_temp, 1),
                                "precipitation": round(precipitation, 2),
                                "uv_index": round(uv_index, 1),
                                "weather_code": weather_code,
                                "weather_description": weather_description,
                                "weather_icon": weather_icon
                            })
                        except Exception as e:
                            print(f"Error processing forecast day {i}: {str(e)}")
        except Exception as e:
            print(f"Error processing 5-day forecast: {str(e)}")
        
        # If no forecast data was processed, add default placeholders
        if not forecast_data:
            for i in range(5):
                date_obj = datetime.now()
                date_obj = date_obj.replace(day=date_obj.day + i)
                
                forecast_data.append({
                    "date": date_obj.strftime("%A, %b %d"),
                    "day": date_obj.strftime("%A"),
                    "date_short": date_obj.strftime("%b %d"),
                    "max_temp": processed_data["current"]["temperature"],
                    "min_temp": processed_data["current"]["temperature"] - 10,
                    "precipitation": 0,
                    "uv_index": 0,
                    "weather_code": 0,
                    "weather_description": "Forecast unavailable",
                    "weather_icon": "❓"
                })
        
        processed_data["forecast"] = forecast_data
        
        return processed_data


class EmailTools:
    """Tools for email operations"""
    
    def __init__(self, config: Config):
        """Initialize with email configuration"""
        self.config = config
    
    def send_email(self, recipient_email: str, subject: str, report: str) -> bool:
        """Send an email with the given report to the specified recipient"""
        try:
            if not self.config.email_address or not self.config.email_password or not recipient_email:
                print("Email configuration missing. Cannot send email.")
                return False
            
            # Create email message with 'alternative' subtype to indicate content alternatives
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.email_address
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add plain text version of the report
            plain_text = report.replace('<br>', '\n')
            msg.attach(MIMEText(plain_text, 'plain'))
            
            # Add HTML version of the report
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #4b6cb7; color: white; padding: 10px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; white-space: pre-line; }}
                    .footer {{ text-align: center; font-size: 0.8em; color: #666; padding: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Weather Report</h1>
                        <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                    </div>
                    <div class="content">
                        {report.replace('\n', '<br>')}
                    </div>
                    <div class="footer">
                        <p>This report was generated by Weather Forecast Application.</p>
                        <p>To unsubscribe, reply with "UNSUBSCRIBE" in the subject line.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server and send email
            try:
                # Choose connection method based on configuration
                if self.config.smtp_use_ssl:
                    print("Establishing SMTP_SSL connection")
                    smtp = smtplib.SMTP_SSL(self.config.smtp_server, self.config.smtp_port)
                else:
                    print("Establishing standard SMTP connection")
                    smtp = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
                    
                    # Use TLS if configured
                    if self.config.smtp_use_tls:
                        print("Starting TLS encryption")
                        smtp.starttls()
                
                # Debug mode for troubleshooting
                smtp.set_debuglevel(1)
                
                # Authentication and sending
                print(f"Logging in as {self.config.email_address}")
                smtp.login(self.config.email_address, self.config.email_password)
                
                print(f"Sending email to {recipient_email}")
                smtp.send_message(msg)
                
                print(f"Email sent successfully to {recipient_email}")
                return True
                
            finally:
                # Always close the connection
                smtp.quit()
                print("SMTP connection closed")
        
        except Exception as e:
            print(f"Error sending email: {e}")
            return False


# ------------------------------------------------------------------------
# 4. PROMPTS - Structured interactions with the AI model
# ------------------------------------------------------------------------

class WeatherReportPrompts:
    """Prompts for generating weather reports"""
    
    def __init__(self):
        """Initialize prompt templates"""
        # Try to import the Anthropic module, but continue if not available
        try:
            from anthropic import Anthropic
            self.anthropic_available = True
            self.anthropic_client = None
        except ImportError:
            self.anthropic_available = False
            print("Anthropic module not available. Using fallback report generator.")
    
    def initialize_anthropic(self, api_key: str):
        """Initialize Anthropic client if available"""
        if self.anthropic_available and api_key:
            try:
                from anthropic import Anthropic
                self.anthropic_client = Anthropic(api_key=api_key)
                return True
            except Exception as e:
                print(f"Failed to initialize Anthropic client: {e}")
                return False
        return False
    
    def generate_weather_report(self, processed_data: dict) -> str:
        """Generate a weather report using Anthropic API or fallback to a locally generated report"""
        # Use fallback if Anthropic is not available
        if not self.anthropic_available or not self.anthropic_client:
            return self.create_enhanced_report(processed_data)
        
        try:
            location_name = processed_data["location"]["name"]
            country = processed_data["location"]["country"]
            admin = processed_data["location"]["admin1"]
            full_location = f"{location_name}, {admin} {country}".strip()
            
            current = processed_data["current"]
            forecast = processed_data["forecast"]
            
            # Create prompt for Anthropic
            prompt = f"""Create a friendly, informative weather report for {full_location}. Here's the data:

Current conditions:
- Temperature: {current['temperature']}°F (feels like {current['feels_like']}°F)
- Condition: {current['weather_description']}
- Humidity: {current['humidity']}%
- Wind: {current['wind_speed']} mph
- Precipitation: {current['precipitation']} inches

5-Day Forecast:
"""
            
            for day in forecast:
                prompt += f"- {day['date']}: High {day['max_temp']}°F, Low {day['min_temp']}°F, {day['weather_description']}, Precipitation: {day['precipitation']} inches\n"
            
            prompt += "\nPlease include a friendly greeting, a summary of current conditions, key points about the forecast, and any weather-related advice or recommendations. Make it engaging and conversational."
            
            # Call Anthropic API
            message = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=800,
                temperature=0.7,
                system="You are a helpful weather reporter specialized in creating engaging and informative weather reports.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract content from response
            if hasattr(message, 'content') and message.content:
                if isinstance(message.content, list):
                    content = ""
                    for item in message.content:
                        if hasattr(item, 'text'):
                            content += item.text
                        elif isinstance(item, dict) and 'text' in item:
                            content += item['text']
                    return content
                else:
                    return str(message.content)
            else:
                return self.create_enhanced_report(processed_data)
        except Exception as e:
            print(f"Error generating report with Anthropic API: {str(e)}")
            return self.create_enhanced_report(processed_data)
    
    def create_enhanced_report(self, data: dict) -> str:
        """Create a comprehensive weather report without using external AI services"""
        try:
            location = data["location"]
            current = data["current"]
            forecast = data["forecast"]
            
            location_name = f"{location['name']}, {location['admin1']} {location['country']}".strip()
            current_date = current["date"]
            
            # Get time of day greeting
            current_hour = datetime.now().hour
            if 5 <= current_hour < 12:
                greeting = "Good morning!"
            elif 12 <= current_hour < 18:
                greeting = "Good afternoon!"
            else:
                greeting = "Good evening!"
            
            # Create weather summary
            temp_description = ""
            if current['temperature'] > 85:
                temp_description = "very warm"
            elif current['temperature'] > 75:
                temp_description = "warm"
            elif current['temperature'] > 60:
                temp_description = "mild"
            elif current['temperature'] > 40:
                temp_description = "cool"
            elif current['temperature'] > 30:
                temp_description = "cold"
            else:
                temp_description = "very cold"
            
            # Weather warnings and recommendations
            recommendations = []
            
            if current['temperature'] > 85:
                recommendations.append("Stay hydrated and seek shade during peak sun hours.")
            elif current['temperature'] < 32:
                recommendations.append("Bundle up and be cautious of ice when outdoors.")
                
            if current['humidity'] > 80:
                recommendations.append("High humidity may make it feel more uncomfortable outside.")
                
            if current['wind_speed'] > 15:
                recommendations.append("Be mindful of strong winds today.")
                
            if current['precipitation'] > 0.1:
                recommendations.append("Don't forget an umbrella or raincoat.")
                
            if any(day['precipitation'] > 0.1 for day in forecast[:2]):
                recommendations.append("Prepare for wet conditions in the coming days.")
                
            if any("snow" in day['weather_description'].lower() for day in forecast[:2]):
                recommendations.append("Snow is in the forecast - plan travel accordingly.")
                
            # Forecast trend analysis
            temp_trend = []
            for i in range(len(forecast) - 1):
                if forecast[i+1]['max_temp'] - forecast[i]['max_temp'] > 5:
                    temp_trend.append(f"warming trend on {forecast[i+1]['day']}")
                elif forecast[i]['max_temp'] - forecast[i+1]['max_temp'] > 5:
                    temp_trend.append(f"cooling trend on {forecast[i+1]['day']}")
            
            # Assemble the report
            report = f"""
🌤️ Weather Report for {location_name} - {current_date} 🌤️

{greeting}

Currently in {location['name']}, it's a {temp_description} {current['temperature']}°F with {current['weather_description']}.
It feels like {current['feels_like']}°F with humidity at {current['humidity']}% and winds at {current['wind_speed']} mph.

5-Day Forecast:
"""
            
            for day in forecast:
                report += f"\n• {day['date']}: High {day['max_temp']}°F, Low {day['min_temp']}°F"
                report += f"\n  {day['weather_description']} with {day['precipitation']} inches of precipitation"
            
            if temp_trend:
                report += "\n\nLooking ahead: " + ", ".join(temp_trend) + "."
                
            if recommendations:
                report += "\n\nRecommendations:\n"
                report += "\n".join(f"- {recommendation}" for recommendation in recommendations)
            
            report += "\n\nStay prepared and have a great day!"
            
            return report
        except Exception as e:
            print(f"Error generating enhanced report: {str(e)}")
            
            # Create minimal fallback report in case of error in the enhanced report
            try:
                location_name = f"{data['location']['name']}, {data['location']['admin1']} {data['location']['country']}".strip()
                current_date = data["current"]["date"]
                
                simple_report = f"""
Weather Report for {location_name} - {current_date}

Currently: {data['current']['temperature']}°F, {data['current']['weather_description']}
Wind: {data['current']['wind_speed']} mph
Humidity: {data['current']['humidity']}%

5-Day Forecast:
"""
                for day in data["forecast"]:
                    simple_report += f"\n• {day['date']}: High {day['max_temp']}°F, Low {day['min_temp']}°F"
                    
                return simple_report
                    
            except Exception:
                return "Unable to generate weather report. Please check the system logs for more information."


# ------------------------------------------------------------------------
# 2. SERVER - MCP-compatible API endpoints
# ------------------------------------------------------------------------

class WeatherServer:
    """Server component with API endpoints"""
    
    def __init__(self, app: FastAPI, templates: Jinja2Templates, config: Config,
                 weather_tools: WeatherTools, email_tools: EmailTools, prompt_handler: WeatherReportPrompts):
        """Initialize server with necessary components"""
        self.app = app
        self.templates = templates
        self.config = config
        self.weather_tools = weather_tools
        self.email_tools = email_tools
        self.prompt_handler = prompt_handler
        
        # Initialize Anthropic if available
        if self.config.anthropic_api_key:
            self.prompt_handler.initialize_anthropic(self.config.anthropic_api_key)
        
        # Register routes
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            """Render the main page with search form"""
            return self.templates.TemplateResponse("index.html", {"request": request, "error": None})
        
        @self.app.post("/search", response_class=HTMLResponse)
        async def search_location(request: Request, location: str = Form(...)):
            """Process location search and display weather data"""
            if not location or location.strip() == "":
                return self.templates.TemplateResponse("index.html", {
                    "request": request, 
                    "error": "Please enter a valid location"
                })
            
            # Get location coordinates
            location_info = self.weather_tools.get_coordinates(location)
            
            if not location_info:
                return self.templates.TemplateResponse("index.html", {
                    "request": request, 
                    "error": f"Location '{location}' not found. Please try another search term."
                })
            
            # Fetch weather data
            weather_data = self.weather_tools.fetch_weather_data(location_info["latitude"], location_info["longitude"])
            
            # Process weather data
            processed_data = self.weather_tools.process_weather_data(weather_data, location_info)
            
            if not processed_data:
                return self.templates.TemplateResponse("index.html", {
                    "request": request, 
                    "error": "Error processing weather data."
                })
            
            # Generate AI weather report
            ai_report = self.prompt_handler.generate_weather_report(processed_data)
            processed_data["ai_report"] = ai_report
            
            return self.templates.TemplateResponse("weather.html", {
                "request": request,
                "data": processed_data,
                "email_sent": False,
                "email_error": None
            })
        
        @self.app.post("/send-email", response_class=HTMLResponse)
        async def send_email_route(
            request: Request, 
            recipient_email: str = Form(...), 
            location_name: str = Form(...),
            location_admin1: str = Form(...),
            location_country: str = Form(...),
            ai_report: str = Form(...)
        ):
            """Send weather report to the specified email"""
            try:
                # Generate a subject line
                full_location = f"{location_name}, {location_admin1} {location_country}".strip()
                subject = f"Weather Report for {full_location} - {datetime.now().strftime('%A, %B %d, %Y')}"
                
                # Send the email
                email_success = self.email_tools.send_email(recipient_email, subject, ai_report)
                
                # Recreate minimal data structure for template rendering
                data = {
                    "location": {
                        "name": location_name,
                        "admin1": location_admin1,
                        "country": location_country
                    },
                    "ai_report": ai_report
                }
                
                # Get weather data to re-render the page
                coordinates = self.weather_tools.get_coordinates(location_name)
                if coordinates:
                    weather_data = self.weather_tools.fetch_weather_data(coordinates["latitude"], coordinates["longitude"])
                    processed_data = self.weather_tools.process_weather_data(weather_data, coordinates)
                    if processed_data:
                        processed_data["ai_report"] = ai_report
                        data = processed_data
                
                if email_success:
                    # Re-render the page with success message
                    return self.templates.TemplateResponse("weather.html", {
                        "request": request,
                        "data": data,
                        "email_sent": True,
                        "email_error": None
                    })
                else:
                    # Re-render the page with error message
                    return self.templates.TemplateResponse("weather.html", {
                        "request": request,
                        "data": data,
                        "email_sent": False,
                        "email_error": "Failed to send email. Please try again."
                    })
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                return self.templates.TemplateResponse("index.html", {
                    "request": request,
                    "error": f"Error sending email: {str(e)}"
                })
        
        @self.app.get("/api/weather/{location}")
        async def get_weather_api(location: str):
            """API endpoint to get weather data in JSON format"""
            if not location or location.strip() == "":
                raise HTTPException(status_code=400, detail="Location is required")
            
            # Get location coordinates
            location_info = self.weather_tools.get_coordinates(location)
            
            if not location_info:
                raise HTTPException(status_code=404, detail=f"Location '{location}' not found")
            
            # Fetch weather data
            weather_data = self.weather_tools.fetch_weather_data(location_info["latitude"], location_info["longitude"])
            
            # Process weather data
            processed_data = self.weather_tools.process_weather_data(weather_data, location_info)
            
            if not processed_data:
                raise HTTPException(status_code=500, detail="Error processing weather data")
            
            # Generate AI weather report
            ai_report = self.prompt_handler.generate_weather_report(processed_data)
            processed_data["ai_report"] = ai_report
            
            return processed_data


# ------------------------------------------------------------------------
# 1. CLIENT - Main application that orchestrates the workflow
# ------------------------------------------------------------------------

class WeatherClient:
    """Client application that orchestrates the workflow"""
    
    def __init__(self):
        """Initialize the client application"""
        # Create resources
        self.config = Config()
        self.weather_codes = WeatherCodes()
        
        # Create FastAPI application
        self.app = FastAPI(title="Weather Forecast Application")
        
        # Setup templates
        self.templates_dir = "templates"
        os.makedirs(self.templates_dir, exist_ok=True)
        self.templates = Jinja2Templates(directory=self.templates_dir)
        
        # Create tools
        self.weather_tools = WeatherTools(self.weather_codes)
        self.email_tools = EmailTools(self.config)
        self.prompt_handler = WeatherReportPrompts()
        
        # Create server
        self.server = WeatherServer(
            self.app, 
            self.templates, 
            self.config,
            self.weather_tools, 
            self.email_tools, 
            self.prompt_handler
        )
        
        # Create template files
        self.create_templates()
    
    def create_templates(self):
        """Create HTML templates for the application"""
        # Create index.html template
        with open(f"{self.templates_dir}/index.html", "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather Forecast App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f8ff;
            padding-top: 2rem;
        }
        .app-container {
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            padding: 2rem;
        }
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .header h1 {
            color: #0d6efd;
            font-weight: 700;
        }
        .search-form {
            max-width: 500px;
            margin: 0 auto;
        }
        .error-alert {
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container app-container">
        <div class="header">
            <h1>Weather Forecast App</h1>
            <p class="lead">Get accurate 5-day weather forecasts for any location worldwide</p>
        </div>
        
        <div class="search-form">
            <form action="/search" method="post">
                <div class="input-group mb-3">
                    <input type="text" name="location" class="form-control form-control-lg" placeholder="Enter a city or location..." required>
                    <button class="btn btn-primary btn-lg" type="submit">Search</button>
                </div>
            </form>
            
            {% if error %}
            <div class="alert alert-danger error-alert" role="alert">
                {{ error }}
            </div>
            {% endif %}
        </div>
        
        <div class="mt-5 text-center">
            <p>Try searching for cities like "New York", "London", "Tokyo", or "Sydney"</p>
        </div>
        
        <div class="mt-5 text-center">
            <!-- Footer content area -->
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")

        # Create weather.html template
        with open(f"{self.templates_dir}/weather.html", "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather for {{ data.location.name }} - Weather Forecast App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f8ff;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .app-container {
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            padding: 2rem;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        .location-info h1 {
            color: #0d6efd;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .current-weather {
            background: linear-gradient(to right, #4b6cb7, #182848);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        .weather-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .temp-large {
            font-size: 3.5rem;
            font-weight: 700;
        }
        .forecast-day {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            transition: transform 0.2s;
        }
        .forecast-day:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        .hourly-scroll {
            display: flex;
            overflow-x: auto;
            padding-bottom: 1rem;
            gap: 1rem;
        }
        .hourly-item {
            min-width: 100px;
            text-align: center;
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1rem 0.5rem;
        }
        .section-title {
            margin: 2rem 0 1rem 0;
            color: #0d6efd;
            font-weight: 600;
        }
        .ai-report {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 2rem 0;
            white-space: pre-line;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }
        .email-form {
            margin-top: 2rem;
            padding: 1.5rem;
            background-color: #f8f9fa;
            border-radius: 10px;
        }
        .temp-chart-container {
            height: 300px;
            margin: 2rem 0;
        }
        .back-link {
            margin-top: 2rem;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container app-container">
        <div class="header">
            <div class="location-info">
                <h1>{{ data.location.name }}, {{ data.location.admin1 }}</h1>
                <h5 class="text-muted">{{ data.location.country }}</h5>
                <p class="mb-0">{{ data.current.date }}</p>
            </div>
            <a href="/" class="btn btn-outline-primary">Search New Location</a>
        </div>
        
        <!-- Current Weather -->
        <div class="row current-weather">
            <div class="col-md-6">
                <div class="d-flex align-items-center">
                    <div class="weather-icon">{{ data.current.weather_icon }}</div>
                    <div class="ms-3">
                        <span class="temp-large">{{ data.current.temperature }}°F</span>
                        <p class="mb-0">Feels like {{ data.current.feels_like }}°F</p>
                    </div>
                </div>
                <h4 class="mt-3">{{ data.current.weather_description }}</h4>
            </div>
            <div class="col-md-6">
                <div class="row mt-3">
                    <div class="col-6">
                        <p>Humidity: {{ data.current.humidity }}%</p>
                        <p>Wind: {{ data.current.wind_speed }} mph</p>
                    </div>
                    <div class="col-6">
                        <p>Precipitation: {{ data.current.precipitation }} in</p>
                        <p>Pressure: {{ data.current.pressure }} hPa</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Today's Hourly Forecast -->
        <h3 class="section-title">Today's Hourly Forecast</h3>
        <div class="hourly-scroll">
            {% for hour in data.hourly %}
            <div class="hourly-item">
                <p class="mb-1"><strong>{{ hour.time }}</strong></p>
                <div class="my-2">{{ hour.weather_icon }}</div>
                <h5>{{ hour.temperature }}°F</h5>
                <small>{{ hour.precipitation_prob }}% <i class="bi bi-droplet"></i></small>
            </div>
            {% endfor %}
        </div>
        
        <!-- 5-Day Forecast -->
        <h3 class="section-title">5-Day Forecast</h3>
        <div class="row">
            {% for day in data.forecast %}
            <div class="col-md-4 mb-3">
                <div class="forecast-day">
                    <h5>{{ day.day }}</h5>
                    <p class="text-muted">{{ day.date_short }}</p>
                    <div class="mb-2">{{ day.weather_icon }}</div>
                    <p>{{ day.weather_description }}</p>
                    <div class="d-flex justify-content-between">
                        <span>High: <strong>{{ day.max_temp }}°F</strong></span>
                        <span>Low: <strong>{{ day.min_temp }}°F</strong></span>
                    </div>
                    <p class="mb-0 mt-2">Precipitation: {{ day.precipitation }} in</p>
                    <p class="mb-0">UV Index: {{ day.uv_index }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Temperature Chart -->
        <div class="temp-chart-container">
            <canvas id="temperatureChart"></canvas>
        </div>
        
        <!-- AI Weather Report -->
        <h3 class="section-title">Weather Report</h3>
        <div class="ai-report">
            {{ data.ai_report }}
        </div>
        
        <!-- Email Form -->
        <div class="email-form">
            <h4>Get this report in your email</h4>
            {% if email_sent %}
                <div class="alert alert-success" role="alert">
                    Weather report has been sent to your email successfully!
                </div>
            {% endif %}
            
            {% if email_error %}
                <div class="alert alert-danger" role="alert">
                    {{ email_error }}
                </div>
            {% endif %}
            
            <form action="/send-email" method="post">
                <div class="mb-3">
                    <label for="recipient_email" class="form-label">Email address</label>
                    <input type="email" class="form-control" id="recipient_email" name="recipient_email" placeholder="name@example.com" required>
                    <input type="hidden" name="location_name" value="{{ data.location.name }}">
                    <input type="hidden" name="location_admin1" value="{{ data.location.admin1 }}">
                    <input type="hidden" name="location_country" value="{{ data.location.country }}">
                    <input type="hidden" name="ai_report" value="{{ data.ai_report }}">
                </div>
                <button type="submit" class="btn btn-primary">Send Report</button>
            </form>
        </div>
        
        <div class="text-center mt-5">
            <!-- Footer content area -->
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Temperature Chart Script -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('temperatureChart').getContext('2d');
            
            // Extract forecast data
            const labels = [{% for day in data.forecast %}'{{ day.day }}'{% if not loop.last %}, {% endif %}{% endfor %}];
            const maxTemps = [{% for day in data.forecast %}{{ day.max_temp }}{% if not loop.last %}, {% endif %}{% endfor %}];
            const minTemps = [{% for day in data.forecast %}{{ day.min_temp }}{% if not loop.last %}, {% endif %}{% endfor %}];
            
            const temperatureChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'High °F',
                            data: maxTemps,
                            borderColor: '#dc3545',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            tension: 0.3,
                            fill: false
                        },
                        {
                            label: 'Low °F',
                            data: minTemps,
                            borderColor: '#0d6efd',
                            backgroundColor: 'rgba(13, 110, 253, 0.1)',
                            tension: 0.3,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: {
                                drawBorder: false
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>""")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the application"""
        uvicorn.run(self.app, host=host, port=port)


# Application entry point
if __name__ == "__main__":
    # Create and run the client application
    client = WeatherClient()
    client.run()
