import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
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

# Professional Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Using HTML parse mode for bold text and inline links
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Bilingual Welcome Message
WELCOME_MSG = """👋 <b>أهلاً بك! / Bienvenue !</b>

يرجى اختيار لغتك المفضلة للمتابعة:
Veuillez choisir votre langue préférée pour continuer :"""

# Arabic Instructions
AR_INSTRUCTIONS = """👋 أهلاً بك! للحصول على القسائم التراكمية، يرجى التسجيل في SpinBetter:

1️⃣ <a href="https://redirspinner.com/30jg?p=%2Fregistration%2F">إنشاء حساب جديد من هنا</a>
🎁 كود البونص: <code>KORAWIN</code>
2️⃣ <a href="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K">تحميل تطبيق الأندرويد</a>

💬 <a href="https://t.me/generalFady">تواصل معي لأي استفسار</a>

👇 بعد الانتهاء، اضغط على زر 'تم' أسفل الصورة."""

# French Instructions
FR_INSTRUCTIONS = """👋 Bienvenue ! Pour recevoir les coupons, veuillez vous inscrire sur SpinBetter :

1️⃣ <a href="https://redirspinner.com/30jg?p=%2Fregistration%2F">Créer un nouveau compte ici</a>
🎁 Code promo : <code>KORAWIN</code>
2️⃣ <a href="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K">Télécharger l'application Android</a>

💬 <a href="https://t.me/generalFady">Contactez-moi pour toute question</a>

👇 Une fois terminé, cliquez sur le bouton ci-dessous."""

# Arabic Thank You
AR_THANK_YOU = """✅ شكراً لك. 
سيتم قبول طلبك قريباً. بالتوفيق ❤️🍀"""

# French Thank You
FR_THANK_YOU = """✅ Merci.
Votre demande sera acceptée bientôt. Bonne chance ❤️🍀"""


@dp.errors()
async def global_error_handler(event: ErrorEvent):
    logger.critical(f"Update {event.update.update_id} caused error: {event.exception}", exc_info=True)
    return True


@dp.chat_join_request()
async def handle_chat_join_request(chat_join_request: ChatJoinRequest):
    try:
        vip1_path = BASE_DIR / "images" / "vip1.png"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🇲🇦 Français", callback_data="lang_fr"),
                    InlineKeyboardButton(text="🇪🇬 العربية", callback_data="lang_ar")
                ]
            ]
        )
        
        if vip1_path.exists() and vip1_path.is_file():
            photo = FSInputFile(path=vip1_path)
            await bot.send_photo(
                chat_id=chat_join_request.from_user.id,
                photo=photo,
                caption=WELCOME_MSG,
                reply_markup=keyboard
            )
        else:
            logger.warning(f"Image file '{vip1_path}' not found. Sending message without photo.")
            await bot.send_message(
                chat_id=chat_join_request.from_user.id,
                text=WELCOME_MSG,
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
            
        logger.info(f"Sent language selection to user {chat_join_request.from_user.id}")
        
    except TelegramForbiddenError as e:
        logger.error(f"User {chat_join_request.from_user.id} has blocked the bot: {e}")
    except Exception as e:
        logger.error(f"Error in handle_chat_join_request: {e}", exc_info=True)


async def send_language_instructions(user_id: int, message_id: int, lang: str):
    try:
        # Delete the language selection message cleanly
        await bot.delete_message(chat_id=user_id, message_id=message_id)
        
        instructions = AR_INSTRUCTIONS if lang == "ar" else FR_INSTRUCTIONS
        confirm_callback = "confirm_ar" if lang == "ar" else "confirm_fr"
        done_text = "✅ تم" if lang == "ar" else "✅ Terminé"
        
        # 1. Send the instruction text with hidden links
        await bot.send_message(
            chat_id=user_id,
            text=instructions,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        
        # 2. Send the registration illustration image with the "Done" button
        register_img_path = BASE_DIR / "images" / "register.jpeg"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=done_text, callback_data=confirm_callback)]
            ]
        )
        
        if register_img_path.exists() and register_img_path.is_file():
            photo = FSInputFile(path=register_img_path)
            await bot.send_photo(
                chat_id=user_id,
                photo=photo,
                reply_markup=keyboard
            )
        else:
            logger.warning(f"Image file '{register_img_path}' not found.")
            await bot.send_message(
                chat_id=user_id,
                text="⚠️ الصورة التوضيحية غير متوفرة حالياً." if lang == "ar" else "⚠️ L'image d'illustration n'est pas disponible.",
                reply_markup=keyboard
            )
            
    except TelegramAPIError as e:
        logger.error(f"Telegram API Error sending instructions to {user_id}: {e}")
    except Exception as e:
        logger.error(f"Error sending instructions: {e}", exc_info=True)


@dp.callback_query(F.data.in_({"lang_ar", "lang_fr"}))
async def handle_language_selection(callback_query: CallbackQuery):
    try:
        lang = "ar" if callback_query.data == "lang_ar" else "fr"
        if callback_query.message:
            await send_language_instructions(callback_query.from_user.id, callback_query.message.message_id, lang)
        
        await callback_query.answer()
        logger.info(f"User {callback_query.from_user.id} selected language: {lang}")
    except Exception as e:
        logger.error(f"Error in language callback: {e}", exc_info=True)


@dp.callback_query(F.data.in_({"confirm_ar", "confirm_fr"}))
async def handle_confirmation(callback_query: CallbackQuery):
    try:
        if callback_query.message:
            await callback_query.message.edit_reply_markup(reply_markup=None)
        
        thank_you_msg = AR_THANK_YOU if callback_query.data == "confirm_ar" else FR_THANK_YOU
        
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=thank_you_msg
        )
        
        await callback_query.answer()
        logger.info(f"User {callback_query.from_user.id} confirmed registration.")
        
    except TelegramForbiddenError as e:
        logger.error(f"User {callback_query.from_user.id} has blocked the bot: {e}")
    except Exception as e:
        logger.error(f"Error in confirmation callback: {e}", exc_info=True)


async def main():
    logger.info("Starting bot polling...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Critical error starting the bot: {e}", exc_info=True)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped gracefully.")
