import os
import requests
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def tarea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Extraer el comando del mensaje
        prompt = update.message.text.replace('/tarea', '').strip()
        
        # Enviar a DeepSeek para procesar
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={'Authorization': f'Bearer {os.getenv("DEEPSEEK_API_KEY")}'},
            json={
                "model": "deepseek-r1",
                "messages": [{"role": "user", "content": f'Procesar: "{prompt}". Extraer: nombre (texto), fecha (YYYY-MM-DD), hora (HH:MM), descripción (texto). Respuesta en JSON.'}]
            }
        )
        
        # Convertir respuesta de la IA a JSON
        json_data = json.loads(response.json()['choices'][0]['message']['content'])
        
        # Enviar datos a n8n
        requests.post(
            os.getenv("N8N_WEBHOOK_URL"),
            headers={'Content-Type': 'application/json'},
            json=json_data
        )
        
        await update.message.reply_text('✅ Tarea enviada a n8n.')
    except Exception as e:
        await update.message.reply_text(f'❌ Error: {str(e)}')

if __name__ == '__main__':
    # Configurar el bot
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler('tarea', tarea))
    app.run_polling()