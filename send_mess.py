import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
import os

EMAIL_SERVER = "smtp.gmail.com"
PORT = 465
SENDER_EMAIL = "khushi2003p@gmail.com"
PASSWORD_EMAIL = "oora cvcr sjjd upgb"

def send_message(name, receiver_email, score_pdf, study_material_pdf):
    msg = MIMEMultipart()
    msg["Subject"] = "QUIZ Result"
    msg["From"] = formataddr(("AI Quizzer", SENDER_EMAIL))
    msg["To"] = receiver_email

    body = f"""
    Hey {name}!

    Thank you for participating in the quiz. Please find your quiz results and study material attached.

    Best regards,
    AI Quizzer Team
    """
    msg.attach(MIMEText(body, "plain"))

    # Attach Score PDF
    with open(score_pdf, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(score_pdf))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(score_pdf)}"'
        msg.attach(part)
    
    with open(study_material_pdf, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(study_material_pdf))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(study_material_pdf)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP_SSL(EMAIL_SERVER, PORT) as server:
            server.login(SENDER_EMAIL, PASSWORD_EMAIL)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
            print(f"Email sent to {receiver_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
