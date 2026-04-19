#!/usr/bin/env python3
"""
Test Telegram bot connection
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_telegram_connection():
    """Test if Telegram bot token is working"""

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    print(f"🤖 Testing Telegram Bot Connection...")
    print(f"Bot Token: {'✅ Configured' if bot_token else '❌ Missing'}")
    print(f"Chat ID: {'✅ Configured' if chat_id else '❌ Missing'}")

    if not bot_token:
        print("❌ Bot token not found in .env file")
        return False

    # Test bot info
    try:
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe")
        data = response.json()

        if data.get('ok'):
            bot_info = data['result']
            print(f"✅ Bot Connection Successful!")
            print(f"   Bot Name: {bot_info.get('first_name', 'Unknown')}")
            print(f"   Bot Username: @{bot_info.get('username', 'No username')}")
            print(f"   Bot ID: {bot_info.get('id', 'Unknown')}")

            # Send test message if chat_id is available
            if chat_id:
                try:
                    send_response = requests.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": "🎉 *Telegram Bot Test Successful!* \n\nYour AI Voice Bot is online and ready to respond in your personalized voice! 🤖✨",
                            "parse_mode": "Markdown"
                        }
                    )

                    if send_response.json().get('ok'):
                        print(f"✅ Test message sent to your chat!")
                        print(f"   Check your Telegram app for the message!")
                    else:
                        print(f"❌ Failed to send test message")
                        print(f"   Error: {send_response.json().get('description', 'Unknown error')}")

                except Exception as e:
                    print(f"❌ Error sending test message: {e}")
            else:
                print("ℹ️  Chat ID not configured - skipping test message")

            return True
        else:
            print(f"❌ Bot connection failed")
            print(f"   Error: {data.get('description', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_telegram_connection()