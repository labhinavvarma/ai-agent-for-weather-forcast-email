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