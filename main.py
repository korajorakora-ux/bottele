import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile,
    LinkPreviewOptions,
    ErrorEvent
)
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError

from config import BOT_TOKEN, BASE_DIR

# 4. Professional Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

WELCOME_MESSAGE = """👋 أهلاً بيك، ونورت ❤️

علشان تستلم القسايم التراكمية والتوقعات اليومية بشكل مستمر، لازم يكون عندك حساب على SpinBetter لأن الأكواد اللي بننزلها خاصة بالتطبيق ده.

كل المطلوب منك:

1️⃣ سجل حساب جديد من الرابط ده:

https://redirspinner.com/30jg?p=%2Fregistration%2F

2️⃣ لو معاك أندرويد، حمل التطبيق من هنا:

https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K

3️⃣ أثناء التسجيل تقدر تستخدم البروموكود:

KORAWIN

استخدام البروموكود اختياري، لكن لو استخدمته هتحصل على البونص.

بعد ما تخلص التسجيل اضغط الزر الموجود بالأسفل.

الخدمة مجانية بالكامل.
لن يطلب منك أي شخص أي رسوم أو اشتراك.

شكراً لانضمامك ❤️"""

THANK_YOU_MESSAGE = """✅ شكراً ليك.

تم استلام تأكيدك.
سيتم قبول طلب انضمامك للقناة خلال دقائق بواسطة الأدمن.
بعد قبول الطلب ستتمكن من متابعة جميع القسايم التراكمية والتوقعات اليومية داخل القناة.

بالتوفيق ❤️🍀"""


# 6. Global error handling in Dispatcher
@dp.errors()
async def global_error_handler(event: ErrorEvent):
    """Global error handler for catching any unhandled exceptions during updates."""
    logger.critical(f"Update {event.update.update_id} caused error: {event.exception}", exc_info=True)
    # Returning True means we have handled the error, preventing it from stopping the polling
    return True


@dp.chat_join_request()
async def handle_chat_join_request(chat_join_request: ChatJoinRequest):
    try:
        # 3. Dynamic cross-platform image path using pathlib
        image_path = BASE_DIR / "images" / "register.jpeg"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ تم", callback_data="confirm_registration")]
            ]
        )
        
        if image_path.exists() and image_path.is_file():
            photo = FSInputFile(path=image_path)
            await bot.send_photo(
                chat_id=chat_join_request.from_user.id,
                photo=photo,
                caption=WELCOME_MESSAGE,
                reply_markup=keyboard
            )
        else:
            logger.warning(f"Image file '{image_path}' not found. Sending message without photo.")
            await bot.send_message(
                chat_id=chat_join_request.from_user.id,
                text=WELCOME_MESSAGE,
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
            
        logger.info(f"Sent welcome message to user {chat_join_request.from_user.id}")
        
    # 5. Handle user blocking the bot
    except TelegramForbiddenError as e:
        logger.error(f"User {chat_join_request.from_user.id} has blocked the bot or forbidden messages: {e}")
    except TelegramAPIError as e:
        logger.error(f"Telegram API Error sending message to {chat_join_request.from_user.id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in handle_chat_join_request: {e}", exc_info=True)


@dp.callback_query(F.data == "confirm_registration")
async def handle_confirmation(callback_query: CallbackQuery):
    try:
        if callback_query.message:
            # 1. Clean aiogram 3.x way to edit reply markup using the message object
            await callback_query.message.edit_reply_markup(reply_markup=None)
        
        # Send the thank you message
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=THANK_YOU_MESSAGE
        )
        
        # Answer the callback query to remove the loading state on the button
        await callback_query.answer()
        
        logger.info(f"User {callback_query.from_user.id} confirmed registration")
        
    # 5. Handle user blocking the bot
    except TelegramForbiddenError as e:
        logger.error(f"User {callback_query.from_user.id} has blocked the bot: {e}")
    except TelegramAPIError as e:
        logger.error(f"Telegram API Error in callback for user {callback_query.from_user.id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in callback handling: {e}", exc_info=True)


async def main():
    logger.info("Starting bot polling...")
    try:
        # Drop pending updates to avoid processing old requests on startup
        await bot.delete_webhook(drop_pending_updates=True)
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Critical error starting the bot: {e}", exc_info=True)
    finally:
        # Safe shutdown
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped gracefully.")
