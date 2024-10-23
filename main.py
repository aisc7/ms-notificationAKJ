import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()
app = Flask(__name__)

# Obtener credenciales de Gmail del archivo .env
email_sender = os.environ.get("GoogleMail_EmailSender")
email_password = os.environ.get("GoogleMail_ApiKey")
smtp_host = os.environ.get("GoogleMail_Host")
smtp_port = int(os.environ.get("GoogleMail_Port"))

# Función para enviar correos
def send_email_smtp(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Conectar al servidor SMTP de Gmail y enviar el correo
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(email_sender, email_password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        return str(e)

# Endpoint para enviar correos genéricos
@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.get_json()

    # Validar los campos requeridos
    if 'email' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    result = send_email_smtp(data['email'], data['subject'], data['body'])
    if result is True:
        return jsonify({'success': 'Email sent successfully'}), 200
    else:
        return jsonify({'error': result}), 500

# Endpoint para enviar correos de 2FA
@app.route('/validation', methods=['POST'])
def validation():
    data = request.get_json()

    # Validar el campo de email y el código 2FA
    if 'email' not in data or 'code2FA' not in data:  # Cambia a code2FA
        return jsonify({'error': 'Missing required fields'}), 400

    subject = "Your 2FA Code"
    body = f"Your 2FA code is: {data['code2FA']}. Please use this to complete your login."

    result = send_email_smtp(data['email'], subject, body)
    if result is True:
        return jsonify({'success': '2FA email sent successfully'}), 200
    else:
        return jsonify({'error': result}), 500


# Endpoint para enviar correos de restablecimiento de contraseña
@app.route('/reset-password', methods=['PATCH'])
def reset_password():
    data = request.get_json()

    # Validar solo el campo de email (no se valida 'new_password' aquí)
    if 'email' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    subject = "Password Reset Request"
    body = f"Your new password is: {data.get('new_password', 'unknown')}."  # Aquí puedes dejar un valor por defecto si no viene la contraseña

    result = send_email_smtp(data['email'], subject, body)
    if result is True:
        return jsonify({'success': 'Password reset email sent successfully'}), 200
    else:
        return jsonify({'error': result}), 500

    

if __name__ == '__main__':
    app.run(debug=True)