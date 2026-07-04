import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Union

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile,
    LinkPreviewOptions,
    ErrorEvent,
    Message
)
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter

from config import BOT_TOKEN, BASE_DIR

# Professional Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ----------------- CACHE FOR FILE IDs -----------------
# This cache prevents uploading the same image 100 times under heavy load.
FILE_CACHE = {
    "vip1": None,
    "register": None
}

# ----------------- MESSAGES -----------------
AR_MESSAGE = """👋 <b>أهلاً بك يا بطل، ونورت القناة!</b> ❤️

علشان تستلم القسايم التراكمية اليومية ونبدأ نحقق أرباح مستمرة مع بعض، لازم يكون عندك حساب على SpinBetter لأن كل أكوادنا وتوقعاتنا الـ VIP مخصصة للتطبيق ده فقط.

<b>خطوات بسيطة جداً تفصلك عن الانضمام:</b>

1️⃣ <b>لإنشاء حسابك الجديد:</b>
<a href="https://redirspinner.com/30jg?p=%2Fregistration%2F">🌐 اضغط هنا للتسجيل</a>

2️⃣ <b>لتحميل تطبيق الأندرويد:</b>
<a href="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K">📱 اضغط هنا للتحميل</a>

3️⃣ 🎁 <b>عند التسجيل، استخدم كود البونص:</b>
<code>KORAWIN</code>
<i>(استخدام الكود هيضمن لك بونص ترحيبي قوي جداً على حسابك!)</i>

💡 <b>الخدمة مجانية بالكامل.</b> لن يُطلب منك أي رسوم أو اشتراكات!

💬 <b>لأي مساعدة أو استفسار تواصل معي شخصياً:</b>
@generalFady

👇 <b>بعد الانتهاء، اضغط على زر "تم" أسفل الصورة التوضيحية ليتم قبولك.</b>"""

FR_MESSAGE = """👋 <b>Bienvenue champion !</b> ❤️

Pour recevoir les coupons cumulatifs quotidiens et générer des profits continus avec nous, vous devez avoir un compte SpinBetter. Tous nos codes et pronostics VIP sont exclusifs à cette application.

<b>Des étapes très simples vous séparent de l'accès :</b>

1️⃣ <b>Pour créer votre nouveau compte :</b>
<a href="https://redirspinner.com/30jg?p=%2Fregistration%2F">🌐 Cliquez ici pour vous inscrire</a>

2️⃣ <b>Pour télécharger l'application Android :</b>
<a href="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K">📱 Cliquez ici pour télécharger</a>

3️⃣ 🎁 <b>Lors de l'inscription, utilisez le code promo :</b>
<code>KORAWIN</code>
<i>(Ce code garantit un puissant bonus de bienvenue sur votre compte !)</i>

💡 <b>Le service est totalement gratuit.</b> Aucun frais ou abonnement ne sera demandé !

💬 <b>Pour toute question, contactez-moi personnellement :</b>
@generalFady

👇 <b>Une fois terminé, cliquez sur le bouton "Terminé" sous l'image pour être accepté.</b>"""

THANK_YOU_MSG = """✅ شكراً لك! / Merci !

تم استلام تأكيدك. سيتم قبول طلب انضمامك للقناة خلال دقائق.
Votre confirmation a été reçue. Votre demande sera acceptée dans quelques minutes.

بالتوفيق ❤️🍀"""


# ----------------- SAFE SEND WRAPPERS (Anti-Flood) -----------------
async def safe_send_message(chat_id: int, text: str, reply_markup: Optional[InlineKeyboardMarkup] = None) -> Optional[Message]:
    """Sends a message safely with RetryAfter handling."""
    retries = 3
    for attempt in range(retries):
        try:
            return await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
        except TelegramRetryAfter as e:
            logger.warning(f"Rate limited. Sleeping for {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
        except TelegramForbiddenError:
            logger.error(f"User {chat_id} blocked the bot.")
            break
        except TelegramAPIError as e:
            logger.error(f"Telegram API Error sending message to {chat_id}: {e}")
            break
    return None

async def safe_send_photo(chat_id: int, photo_key: str, photo_path: Path, reply_markup: Optional[InlineKeyboardMarkup] = None) -> Optional[Message]:
    """Sends a photo safely, caching the file_id to prevent redundant uploads."""
    retries = 3
    for attempt in range(retries):
        try:
            # Use cached file_id if available (zero upload time)
            photo_to_send: Union[str, FSInputFile] = FILE_CACHE[photo_key] if FILE_CACHE[photo_key] else FSInputFile(path=photo_path)
            
            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_to_send,
                reply_markup=reply_markup
            )
            
            # Cache the file_id for future use
            if not FILE_CACHE[photo_key] and msg.photo:
                FILE_CACHE[photo_key] = msg.photo[-1].file_id
                logger.info(f"Cached file_id for {photo_key}")
                
            return msg
        except TelegramRetryAfter as e:
            logger.warning(f"Rate limited. Sleeping for {e.retry_after} seconds.")
            await asyncio.sleep(e.retry_after)
        except TelegramForbiddenError:
            logger.error(f"User {chat_id} blocked the bot.")
            break
        except TelegramAPIError as e:
            logger.error(f"Telegram API Error sending photo to {chat_id}: {e}")
            break
    return None


@dp.errors()
async def global_error_handler(event: ErrorEvent):
    logger.critical(f"Update {event.update.update_id} caused error: {event.exception}", exc_info=True)
    return True


@dp.chat_join_request()
async def handle_chat_join_request(chat_join_request: ChatJoinRequest):
    try:
        user_id = chat_join_request.from_user.id
        vip1_path = BASE_DIR / "images" / "vip1.png"
        register_img_path = BASE_DIR / "images" / "register.jpeg"
        
        # 1. Send the VIP image using safe sender
        if vip1_path.exists() and vip1_path.is_file():
            await safe_send_photo(chat_id=user_id, photo_key="vip1", photo_path=vip1_path)
        else:
            logger.warning(f"Image '{vip1_path}' not found.")

        # 2. Send the convincing Arabic message with a French switch button
        lang_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🇲🇦 Voir en Français", callback_data="switch_fr")]]
        )
        await safe_send_message(chat_id=user_id, text=AR_MESSAGE, reply_markup=lang_keyboard)
        
        # 3. Send the registration illustration image with "Done" button
        done_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ تم / Terminé", callback_data="confirm_registration")]]
        )
        
        if register_img_path.exists() and register_img_path.is_file():
            await safe_send_photo(chat_id=user_id, photo_key="register", photo_path=register_img_path, reply_markup=done_keyboard)
        else:
            logger.warning(f"Image '{register_img_path}' not found.")
            await safe_send_message(chat_id=user_id, text="⚠️ لم يتم العثور على الصورة التوضيحية للتسجيل.", reply_markup=done_keyboard)
            
        logger.info(f"Sent complete onboarding to user {user_id}")
        
    except Exception as e:
        logger.error(f"Unexpected error in handle_chat_join_request: {e}", exc_info=True)


@dp.callback_query(F.data == "switch_fr")
async def switch_to_french(callback_query: CallbackQuery):
    # FIRST LINE: Answer callback immediately to prevent Telegram UI glitch ("kicking out")
    await callback_query.answer(cache_time=2)
    try:
        if callback_query.message:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="🇪🇬 عرض بالعربية", callback_data="switch_ar")]]
            )
            await callback_query.message.edit_text(
                text=FR_MESSAGE,
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
    except TelegramAPIError as e:
        # Ignore "message is not modified" error if user spams the button
        if "message is not modified" not in str(e).lower():
            logger.error(f"Error switching to French: {e}")
    except Exception as e:
        logger.error(f"Unexpected error switching to French: {e}", exc_info=True)


@dp.callback_query(F.data == "switch_ar")
async def switch_to_arabic(callback_query: CallbackQuery):
    # FIRST LINE: Answer callback immediately
    await callback_query.answer(cache_time=2)
    try:
        if callback_query.message:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="🇲🇦 Voir en Français", callback_data="switch_fr")]]
            )
            await callback_query.message.edit_text(
                text=AR_MESSAGE,
                reply_markup=keyboard,
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
    except TelegramAPIError as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Error switching to Arabic: {e}")
    except Exception as e:
        logger.error(f"Unexpected error switching to Arabic: {e}", exc_info=True)


@dp.callback_query(F.data == "confirm_registration")
async def handle_confirmation(callback_query: CallbackQuery):
    # FIRST LINE: Answer callback immediately
    await callback_query.answer(cache_time=5)
    try:
        if callback_query.message:
            # Safely remove the "Done" button from the photo
            await callback_query.message.edit_reply_markup(reply_markup=None)
        
        # Send Thank You message
        await safe_send_message(chat_id=callback_query.from_user.id, text=THANK_YOU_MSG)
        logger.info(f"User {callback_query.from_user.id} confirmed registration.")
        
    except TelegramAPIError as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Error in confirmation callback: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in confirmation callback: {e}", exc_info=True)


async def main():
    logger.info("Starting Enterprise Bot polling...")
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
