import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from fpdf import FPDF
import ollama  # Import Ollama for AI integration

# ====================== Context ======================
class Context:
    def __init__(self):
        # Configuration
        self.SMTP_SERVER = 'smtp.gmail.com'  # Replace with your SMTP server
        self.SMTP_PORT = 587  # Replace with your SMTP port
        self.EMAIL_ADDRESS = 'raomadhav653@gmail.com'  # Replace with your email
        self.EMAIL_PASSWORD = 'fxux rpsu qlzz bxpl'  # Replace with your email password
        self.RECIPIENT_EMAIL = 'labhinavvarma@gmail.com'  # Replace with recipient's email

        # Data
        self.weather_data = None
        self.weather_description = None  # Store AI-generated weather description
        self.pdf_filename = "atlanta_weather_report.pdf"


# ====================== Modules ======================
class WeatherFetcher:
    def fetch_weather(self, context):
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
            context.weather_data = f"{condition}, {temperature}°C, {wind_speed} km/h"
            print("Weather data fetched successfully.")
        except Exception as e:
            print(f"Failed to fetch weather data: {e}")
            context.weather_data = None


class WeatherDescriber:
    def generate_description(self, context):
        if not context.weather_data:
            print("No weather data available to generate description.")
            return

        # Use Ollama to generate a brief weather description
        prompt = f"Write a brief and professional description of the weather in Atlanta based on this data: {context.weather_data}."
        try:
            # Specify the model name as "mistral"
            response = ollama.generate(model="mistral", prompt=prompt)
            context.weather_description = response['response']
            print("Weather description generated successfully.")
        except Exception as e:
            print(f"Failed to generate weather description: {e}")
            context.weather_description = None


class PDFGenerator:
    def generate_pdf(self, context):
        if not context.weather_data:
            print("No weather data available to generate PDF.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add a title
        pdf.cell(200, 10, txt="Daily Atlanta Weather Report", ln=True, align="C")

        # Add weather data
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=f"Weather Data:\n{context.weather_data}")

        # Add AI-generated weather description
        if context.weather_description:
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=f"Weather Description:\n{context.weather_description}")

        # Save the PDF
        pdf.output(context.pdf_filename)
        print(f"PDF created: {context.pdf_filename}")


class EmailSender:
    def send_email(self, context, subject, body):
        if not context.weather_data:
            print("No weather data available to send email.")
            return

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = context.EMAIL_ADDRESS
        msg['To'] = context.RECIPIENT_EMAIL
        msg['Subject'] = subject

        # Attach the body of the email
        msg.attach(MIMEText(body, 'plain'))

        # Attach the PDF file
        with open(context.pdf_filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {context.pdf_filename}",
            )
            msg.attach(part)

        # Connect to the SMTP server and send the email
        try:
            server = smtplib.SMTP(context.SMTP_SERVER, context.SMTP_PORT)
            server.starttls()  # Upgrade the connection to secure
            server.login(context.EMAIL_ADDRESS, context.EMAIL_PASSWORD)
            server.sendmail(context.EMAIL_ADDRESS, context.RECIPIENT_EMAIL, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
        finally:
            server.quit()


# ====================== Protocol ======================
class WeatherReportAgent:
    def __init__(self):
        self.context = Context()
        self.weather_fetcher = WeatherFetcher()
        self.weather_describer = WeatherDescriber()  # Add AI module
        self.pdf_generator = PDFGenerator()
        self.email_sender = EmailSender()

    def run(self):
        # Step 1: Fetch weather data
        self.weather_fetcher.fetch_weather(self.context)

        # Step 2: Generate weather description using AI
        self.weather_describer.generate_description(self.context)

        # Step 3: Generate PDF
        self.pdf_generator.generate_pdf(self.context)

        # Step 4: Send email with PDF attachment
        email_subject = "Daily Atlanta Weather Report"
        email_body = "Please find the daily Atlanta weather report attached as a PDF.\n\n"
        if self.context.weather_description:
            email_body += f"Weather Description:\n{self.context.weather_description}"
        self.email_sender.send_email(self.context, email_subject, email_body)


# ====================== Main ======================
if __name__ == "__main__":
    agent = WeatherReportAgent()
    agent.run()