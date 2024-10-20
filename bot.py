from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import logging
import json

bot_token = "7716348784:AAHZ04rPQaIqn6GY9RKvkQodDuCLnFClwCM"

# INICIO DE SESION
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Almacenar roles en un archivo JSON
def load_roles():
    try:
        with open('roles.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_roles(roles):
    with open('roles.json', 'w') as file:
        json.dump(roles, file)

roles = load_roles()

# Almacenamiento de puntos de recogida o entrega
puntos_conductor = {}
estado_conductor = {}  # Para almacenar el estado de recogida o entrega

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🌟 ¡Bienvenido a nuestro sistema de transporte municipal! 🌟\n\nPor favor, indícanos: ¿Cuál es tu rol? (admin, cliente, empresa, conductor, propietario)")

async def set_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if context.args:
        role = context.args[0].lower()
        
        if role in ['admin', 'cliente', 'empresa', 'conductor', 'propietario']:
            roles[user_id] = role
            save_roles(roles)
            await context.bot.send_message(chat_id=user_id, text=f"✅ Tu rol ha sido establecido como: *{role}*. Usa /consultar para verificar el estado del servicio.")
        else:
            await context.bot.send_message(chat_id=user_id, text="❌ Rol no válido. Por favor, usa un rol correcto.")
    else:
        await context.bot.send_message(chat_id=user_id, text="⚠️ Por favor, proporciona un rol. Ejemplo: /setrole conductor")

async def consultar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_role = roles.get(user_id)

    if user_role:
        # Todos los roles pueden consultar el estado del servicio
        await context.bot.send_message(chat_id=user_id, text=f"🔍 Consulta de estado para {user_role}: [Detalles del servicio].")

        if user_role == 'conductor':
            await context.bot.send_message(chat_id=user_id, text="¿Estás recogiendo o llevando el pedido? (responde 'recoger' o 'llevar')")
        # Eliminar la parte que menciona que si eres conductor indiques algo.
    else:
        await context.bot.send_message(chat_id=user_id, text="⚠️ No has establecido un rol. Usa /setrole para definir tu rol.")

async def manejar_accion_conductor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if roles.get(user_id) == 'conductor':
        accion = update.message.text.lower()  # Obtiene la acción que el conductor ingresó
        
        if accion in ['recoger', 'llevar']:
            estado_conductor[user_id] = accion  # Almacena el estado de la acción
            await context.bot.send_message(chat_id=user_id, text=f"🚚 Estás preparado para {accion}. Por favor, indica el punto correspondiente.")
            return  # Espera a que el conductor proporcione el punto
        
        # Inicializa la variable `puntos` si no existe
        if user_id not in puntos_conductor:
            puntos_conductor[user_id] = {}

        # Guardar el punto según la acción
        if user_id in estado_conductor:
            puntos_conductor[user_id][estado_conductor[user_id]] = update.message.text  # Guardar el punto en la estructura
            await context.bot.send_message(chat_id=user_id, text=f"✅ Gracias. Has indicado que vas a {estado_conductor[user_id]} en: {puntos_conductor[user_id][estado_conductor[user_id]]}.")
            del estado_conductor[user_id]  # Eliminar estado después de usarlo
            
            # Mensaje de finalización
            await context.bot.send_message(chat_id=user_id, text="🎉 El proceso de consulta ha finalizado. ¡Buen viaje!")
        else:
            await context.bot.send_message(chat_id=user_id, text="⚠️ No se ha definido una acción. Responde 'recoger' o 'llevar' primero.")
    else:
        await context.bot.send_message(chat_id=user_id, text="🚫 Este comando solo es para conductores.")

# Crear la aplicación
app = ApplicationBuilder().token(bot_token).build()

# Añadir los manejadores de comandos
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('setrole', set_role))
app.add_handler(CommandHandler('consultar', consultar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_accion_conductor))  # Maneja cualquier texto enviado

# Iniciar el bot
app.run_polling()