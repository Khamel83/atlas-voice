#!/usr/bin/env python3
"""
Telegram Bot for Atlas Voice System
Responds to messages using your personalized AI voice
"""

import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramVoiceBot:
    """Telegram bot that responds in your personalized voice"""

    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        # Initialize voice integration engine (will be lazy-loaded)
        self.voice_engine = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        await update.message.reply_text(
            "🎤 *AI Voice Bot Activated!*\n\n"
            "I'm your personal AI assistant that responds in your authentic voice style. "
            "Send me any message and I'll respond using your unique communication patterns!\n\n"
            "Type /help to see available commands.",
            parse_mode='Markdown'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await update.message.reply_text(
            "🎯 *Available Commands:*\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/voice - Create your personalized voice prompt\n"
            "/status - Check bot status\n\n"
            "Just send me any message and I'll respond in your voice!",
            parse_mode='Markdown'
        )

    async def voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /voice command - generate voice prompt"""
        try:
            await update.message.reply_text(
                "🔧 *Generating your voice prompt...*\n\n"
                "This would analyze your writing samples and create a personalized AI prompt. "
                "For now, I'll respond using your pre-configured voice style!",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in voice command: {e}")
            await update.message.reply_text("❌ Sorry, there was an error generating your voice prompt.")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        await update.message.reply_text(
            "✅ *Bot Status: Online*\n\n"
            f"🤖 Bot Token: {'✅ Configured' if self.bot_token else '❌ Missing'}\n"
            f"👤 Chat ID: {'✅ Configured' if self.chat_id else '❌ Missing'}\n"
            f"🎤 Voice Engine: {'✅ Ready' if self.voice_engine else '🔄 Standby'}",
            parse_mode='Markdown'
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular messages and respond in your voice"""
        try:
            user_message = update.message.text

            # Your voice characteristics (based on the sample analysis)
            voice_response = self._generate_voice_response(user_message)

            await update.message.reply_text(voice_response)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("❌ Sorry, I had trouble processing that message.")

    def _generate_voice_response(self, user_message: str) -> str:
        """Generate a response in your personalized voice style"""

        # Your voice characteristics from the sample analysis:
        # - Communication Style: technical + enthusiastic
        # - Enthusiasm: High (1.0)
        # - Directness: High (1.0)
        # - Key phrases: "Let's make this happen!", frequent exclamations

        responses = {
            "greeting": [
                "Hey! Awesome to hear from you! 👋 Let's make this happen!",
                "Hi there! Great to see your message! What can I help you with today?",
                "Hello! Super excited to chat with you! What's on your mind?"
            ],
            "question": [
                "Great question! Basically, what you want to think about is...",
                "Yeah, so like... here's how I'd approach this:",
                "Awesome question! Let me break this down for you:"
            ],
            "help": [
                "I'll totally help you with that! Basically, the way this works is...",
                "Awesome! Let me help you out with this. Here's what we need to do:",
                "Perfect! I can definitely assist you. Let's make this happen!"
            ],
            "technical": [
                "Basically, the way this works is... [technical explanation]",
                "So the key thing to understand is... [technical details]",
                "Yeah, so like... here's the technical approach:"
            ],
            "default": [
                "Awesome! Let me help you with that. I'm thinking we should...",
                "Great! I've got some ideas about this. Basically...",
                "Perfect! Here's what I'm thinking we can do:"
            ]
        }

        # Simple response selection based on message content
        message_lower = user_message.lower()

        if any(word in message_lower for word in ['hi', 'hello', 'hey']):
            return responses["greeting"][0]
        elif '?' in user_message:
            return responses["question"][0]
        elif any(word in message_lower for word in ['help', 'assist', 'support']):
            return responses["help"][0]
        elif any(word in message_lower for word in ['code', 'technical', 'system', 'api']):
            return responses["technical"][0]
        else:
            return responses["default"][0]

    def run(self):
        """Start the bot"""
        if not self.bot_token:
            logger.error("Bot token not configured!")
            return

        # Create the Application
        application = Application.builder().token(self.bot_token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("voice", self.voice_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Start the bot
        logger.info("🤖 Telegram Voice Bot started!")
        print("🤖 Bot is running! Press Ctrl+C to stop.")

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function to run the bot"""
    try:
        bot = TelegramVoiceBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"❌ Bot error: {e}")

if __name__ == "__main__":
    main()