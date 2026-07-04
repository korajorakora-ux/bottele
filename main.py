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

# Detailed convincing messages
AR_MESSAGE = """👋 <b>أهلاً بك يا بطل، ونورت القناة! ❤️</b>

علشان تستلم القسايم التراكمية اليومية ونبدأ نحقق أرباح مستمرة مع بعض، لازم يكون عندك حساب على SpinBetter لأن كل أكوادنا وتوقعاتنا الـ VIP مخصصة للتطبيق ده فقط.

<b>خطوات بسيطة جداً تفصلك عن الانضمام:</b>

1️⃣ <a href="https://redirspinner.com/30jg?p=%2Fregistration%2F">اضغط هنا لإنشاء حسابك الجديد</a> 🌐
2️⃣ <a href="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K">حمل تطبيق الأندرويد من هنا</a> 📱
3️⃣ 🎁 عند التسجيل، استخدم كود البونص: <code>KORAWIN</code> 
<i>(استخدام الكود هيضمن لك بونص ترحيبي قوي جداً على حسابك!)</i>

💡 <b>الخدمة مجانية بالكامل.</b> لن يُطلب منك أي رسوم أو اشتراكات!
💬 <a href="https://t.me/generalFady">تواصل معي شخصياً لأي استفسار</a>

👇 <b>بعد الانتهاء، اضغط على زر "تم" أسفل الصورة التوضيحية ليتم قبولك.</b>"""

FR_MESSAGE = """👋 <b>Bienvenue champion ! ❤️</b>

Pour recevoir les coupons cumulatifs quotidiens et générer des profits continus avec nous, vous devez avoir un compte SpinBetter. Tous nos codes et pronostics VIP sont exclusifs à cette application.

<b>Des étapes très simples vous séparent de l'accès :</b>

1️⃣ <a href="https://redirspinner.com/30jg?p=%2Fregistration%2F">Cliquez ici pour créer votre nouveau compte</a> 🌐
2️⃣ <a href="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K">Téléchargez l'application Android ici</a> 📱
3️⃣ 🎁 Lors de l'inscription, utilisez le code promo : <code>KORAWIN</code> 
<i>(Ce code garantit un puissant bonus de bienvenue sur votre compte !)</i>

💡 <b>Le service est totalement gratuit.</b> Aucun frais ou abonnement ne sera demandé !
💬 <a href="https://t.me/generalFady">Contactez-moi pour toute question</a>

👇 <b>Une fois terminé, cliquez sur le bouton "Terminé" sous l'image pour être accepté.</b>"""

THANK_YOU_MSG = """✅ شكراً لك! / Merci !

تم استلام تأكيدك. سيتم قبول طلب انضمامك للقناة خلال دقائق.
Votre confirmation a été reçue. Votre demande sera acceptée dans quelques minutes.

بالتوفيق ❤️🍀"""


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
        
        # 1. Send the VIP image (if exists) without text
        if vip1_path.exists() and vip1_path.is_file():
            await bot.send_photo(chat_id=user_id, photo=FSInputFile(path=vip1_path))
        else:
            logger.warning(f"Image '{vip1_path}' not found.")

        # 2. Send the convincing Arabic message with a French switch button
        lang_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🇲🇦 Voir en Français", callback_data="switch_fr")]]
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=AR_MESSAGE,
            reply_markup=lang_keyboard,
            link_preview_options=LinkPreviewOptions(is_disabled=True)
        )
        
        # 3. Send the registration illustration image with "Done" button
        done_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✅ تم / Terminé", callback_data="confirm_registration")]]
        )
        
        if register_img_path.exists() and register_img_path.is_file():
            await bot.send_photo(
                chat_id=user_id,
                photo=FSInputFile(path=register_img_path),
                reply_markup=done_keyboard
            )
        else:
            logger.warning(f"Image '{register_img_path}' not found.")
            await bot.send_message(
                chat_id=user_id,
                text="⚠️ لم يتم العثور على الصورة التوضيحية للتسجيل.",
                reply_markup=done_keyboard
            )
            
        logger.info(f"Sent complete onboarding to user {user_id}")
        
    except TelegramForbiddenError as e:
        logger.error(f"User {chat_join_request.from_user.id} has blocked the bot: {e}")
    except Exception as e:
        logger.error(f"Error in handle_chat_join_request: {e}", exc_info=True)


@dp.callback_query(F.data == "switch_fr")
async def switch_to_french(callback_query: CallbackQuery):
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
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Error switching to French: {e}", exc_info=True)


@dp.callback_query(F.data == "switch_ar")
async def switch_to_arabic(callback_query: CallbackQuery):
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
        await callback_query.answer()
    except Exception as e:
        logger.error(f"Error switching to Arabic: {e}", exc_info=True)


@dp.callback_query(F.data == "confirm_registration")
async def handle_confirmation(callback_query: CallbackQuery):
    try:
        if callback_query.message:
            # Remove the "Done" button from the photo
            await callback_query.message.edit_reply_markup(reply_markup=None)
        
        # Send Thank You message
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=THANK_YOU_MSG
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
