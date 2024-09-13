import logging
import base64
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace with the allowed user ID
ALLOWED_USER_ID = 6255431752

# Replace with your actual API key
API_KEY = "7318191310:AAGxbU6vLZJtGYeXtCSZE3qZ6rpUKJMIuPw"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID:
        update.message.reply_text("You don't have access. Contact @codexzord for assistance.")
        return
    
    update.message.reply_text('Hello! Send me a PHP file and I will decode it if it\'s base64 encoded or obfuscated with eval.')

def decode_base64(encoded_str):
    try:
        # Remove quotes if necessary
        encoded_str = encoded_str.strip("'\"")
        decoded_bytes = base64.b64decode(encoded_str)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f'Base64 decoding failed: {e}'

def handle_document(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID:
        update.message.reply_text("You don't have access. Contact @codexzord for assistance.")
        return

    document = update.message.document
    file_id = document.file_id
    file = context.bot.get_file(file_id)
    file.download('uploaded_php.php')

    with open('uploaded_php.php', 'r') as file:
        content = file.read()

    try:
        # Decode base64 if present
        base64_match = re.search(r'base64_decode\s*\(\s*\'([^\']*)\'\s*\)', content)
        if base64_match:
            base64_encoded = base64_match.group(1)
            decoded_php = decode_base64(base64_encoded)
        else:
            decoded_php = content
        
        # Try to extract and decode eval content
        eval_match = re.search(r'eval\s*\(\s*\'([^\']*)\'\s*\)', decoded_php)
        if eval_match:
            eval_encoded = eval_match.group(1)
            decoded_php = decode_base64(eval_encoded)

        # Save the final decoded PHP
        with open('decoded_php.php', 'w') as file:
            file.write(decoded_php)
        
        update.message.reply_text('File has been decoded and saved as decoded_php.php')
    except Exception as e:
        update.message.reply_text(f'Failed to decode file: {e}')

def main():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher

    # Register handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/x-httpd-php"), handle_document))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()