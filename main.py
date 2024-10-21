import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Función para enviar correos
def send_email(subject, recipient_email, body_html):
    email_sender = os.getenv('GoogleMail_EmailSender')
    email_password = os.getenv('GoogleMail_ApiKey')
    smtp_server = os.getenv('GoogleMail_Host')
    smtp_port = os.getenv('GoogleMail_Port')
    
    print(f'Email sender: {email_sender}')
    print(f'Email password: {email_password}')
    print(f'SMTP server: {smtp_server}')
    print(f'SMTP port: {smtp_port}')

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Agregar el cuerpo del mensaje en formato HTML
    msg.attach(MIMEText(body_html, 'html'))

    try:
        # Conectar al servidor SMTP de Gmail
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()  # Asegura la conexión
            server.login(email_sender, email_password)
            server.sendmail(email_sender, recipient_email, msg.as_string())

        return True
    except Exception as e:
        return False, str(e)

# Endopoint para enviar correos
@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    data = request.json
    subject = data.get('subject')
    recipient = data.get('recipient')
    
    body_html = data.get('body_html')
    
    success = send_email(subject, recipient, body_html)
    print(f'Success: {success}')
    
    if success:
        print('Email sent successfully')
        return jsonify({'message': 'Email sent successfully'})
    else:
        print('Failed to send email')
        return jsonify({'error': 'Failed to send email'})
    
# Endpoint para obtener usuarios
@app.route('/get-users', methods=['GET'])
def get_users():
    return jsonify([
        {'name': 'John Doe', 'email': 'name@example.com'},
        {'name': 'John Doe', 'email': 'name@example.com'}
    ])
    
# Enpoint para validar usuarios
@app.route("/validation", methods=['POST'])
def ValidationUser():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    subject = "Código de validación"
    
    success = send_email(subject, email, code)
    
    if success:
        print('Email sent successfully')
        return jsonify({'message': 'Email sent successfully'})
    else:
        print('Failed to send email')
        return jsonify({'error': 'Failed to send email'})

if __name__ == '__main__':
    app.run(debug=True)