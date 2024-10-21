import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Obtener las variables de entorno para SMTP
smtp_server = os.getenv("SMTP_SERVER")  # Por ejemplo: smtp.ucaldas.edu.co
smtp_port = int(os.getenv("SMTP_PORT"))  # Asegúrate de convertir a int
smtp_user = os.getenv("SMTP_USER")  # Tu correo electrónico
smtp_password = os.getenv("SMTP_PASSWORD")  # Contraseña o App password de tu correo

# Función para enviar correos usando SMTP
def send_email(subject, recipient_email, body_html):
    # Crear el mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = smtp_user
    message["To"] = recipient_email

    # Crear la parte HTML del mensaje
    part_html = MIMEText(body_html, "html")
    message.attach(part_html)

    try:
        # Conectar al servidor SMTP usando SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)  # Iniciar sesión con el servidor SMTP
            server.sendmail(smtp_user, recipient_email, message.as_string())  # Enviar correo
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

# Endpoint para enviar correos
@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    data = request.json
    subject = data.get('subject')
    recipient = data.get('recipient')
    body_html = data.get('body_html')

    success, result = send_email(subject, recipient, body_html)

    if success:
        print('Email sent successfully')
        return jsonify({'message': result})
    else:
        print('Failed to send email')
        return jsonify({'error': 'Failed to send email', 'details': result})

# Endpoint para obtener usuarios (ejemplo)
@app.route('/get-users', methods=['GET'])
def get_users():
    return jsonify([
        {'name': 'John Doe', 'email': 'johndoe@example.com'},
        {'name': 'Jane Doe', 'email': 'janedoe@example.com'}
    ])

# Endpoint para validar usuarios
@app.route("/validation", methods=['POST'])
def validation_user():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    subject = "Código de validación"
    body_html = f"<p>Tu código de validación es: <strong>{code}</strong></p>"

    success, result = send_email(subject, email, body_html)

    if success:
        print('Validation email sent successfully')
        return jsonify({'message': result})
    else:
        print('Failed to send validation email')
        return jsonify({'error': 'Failed to send validation email', 'details': result})

if __name__ == '__main__':
    app.run(debug=True)
