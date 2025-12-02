import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_server = "smtp.gmail.com"
smtp_port = 587

sender_email = "tkflightsense@gmail.com"
receiver_email = "cyuksel21@ku.edu.tr"
app_password = "*****"  # NOT your actual Gmail password

# Create message
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = "Test Email from Python"

body = "Hello, this is a test email sent via Gmail SMTP!"
msg.attach(MIMEText(body, "plain"))

# Send email
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()                     # Secure the connection
    server.login(sender_email, app_password)
    server.send_message(msg)

print("Email sent!")
