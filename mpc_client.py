from mpc_server import MPCServer

# ====================== MPC Client ======================
class MPCClient:
    def __init__(self):
        self.server = MPCServer()

    def run(self):
        # Step 1: Fetch weather data
        self.server.fetch_weather()

        # Step 2: Generate weather description using AI
        self.server.generate_description()

        # Step 3: Generate PDF
        self.server.generate_pdf()

        # Step 4: Send email with PDF attachment
        self.server.send_email(
            email_address='raomadhav653@gmail.com',
            email_password='fxux rpsu qlzz bxpl',
            recipient_email='labhinavvarma@gmail.com'
        )


# ====================== Main ======================
if __name__ == "__main__":
    client = MPCClient()
    client.run()