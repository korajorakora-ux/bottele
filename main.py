import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Union

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import (
    ChatJoinRequest,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile,
    LinkPreviewOptions,
    ErrorEvent,
    Message,
    ChatMemberUpdated
)
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter

from config import BOT_TOKEN, BASE_DIR, ADMIN_ID
from database import upsert_user, get_all_users

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
FILE_CACHE = {
    "vip1": None,
    "register": None
}

# ----------------- MESSAGES -----------------
AR_MESSAGE = """👋 <b>أهلاً بك يا بطل، ونورت القناة!</b> ❤️

علشان تستلم القسايم التراكمية اليومية ونبدأ نحقق أرباح مستمرة مع بعض، لازم يكون عندك حساب على SpinBetter لأن كل أكوادنا وتوقعاتنا الـ VIP مخصصة للتطبيق ده فقط.

<b>خطوات بسيطة جداً تفصلك عن الانضمام:</b>

1️⃣ <b>لإنشاء حسابك الجديد:</b>
🌐 اضغط على زر (سجل الآن) بالأسفل.

2️⃣ <b>لتحميل تطبيق الأندرويد:</b>
📱 اضغط على زر (حمل التطبيق الآن) بالأسفل.

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
🌐 Cliquez sur le bouton (S'inscrire maintenant) ci-dessous.

2️⃣ <b>Pour télécharger l'application Android :</b>
📱 Cliquez sur le bouton (Télécharger l'application) ci-dessous.

3️⃣ 🎁 <b>Lors de l'inscription, utilisez le code promo :</b>
<code>KORAWIN</code>
<i>(Ce code garantit un puissant bonus de bienvenue sur votre compte !)</i>

💡 <b>Le service est totally gratuit.</b> Aucun frais ou abonnement ne sera demandé !

💬 <b>Pour toute question, contactez-moi personnellement :</b>
@generalFady

👇 <b>Une fois terminé, cliquez sur le bouton "Terminé" sous l'image pour être accepté.</b>"""

THANK_YOU_MSG = """✅ شكراً لك! / Merci !

تم استلام تأكيدك. سيتم قبول طلب انضمامك للقناة خلال دقائق.
Votre confirmation a été reçue. Votre demande sera acceptée dans quelques minutes.

بالتوفيق ❤️🍀"""

APPROVAL_MSG = """🎉 <b>مبروك! تم قبول انضمامك للقناة الـ VIP بنجاح.</b>

تذكير أخير ومهم جداً لضمان بقائك معنا واستفادتك من التوقعات:

1️⃣ إذا لم تقم بإنشاء حسابك بعد، قم بإنشائه الآن من خلال زر التسجيل بالأسفل.

2️⃣ حمل التطبيق من خلال زر التحميل بالأسفل.

🎁 <b>لا تنسَ استخدام كود البونص:</b> <code>KORAWIN</code> للحصول على المكافأة.

بالتوفيق، ونراك في أرباح اليوم! 💸❤️"""


# ----------------- INLINE KEYBOARDS -----------------
def get_ar_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇲🇦 Voir en Français", callback_data="switch_fr")],
            [InlineKeyboardButton(text="🟢 🌐 سجل الآن", url="https://redirspinner.com/30jg?p=%2Fregistration%2F")],
            [InlineKeyboardButton(text="🔵 📱 حمل التطبيق الآن", url="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K")]
        ]
    )

def get_fr_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇪🇬 عرض بالعربية", callback_data="switch_ar")],
            [InlineKeyboardButton(text="🟢 🌐 S'inscrire maintenant", url="https://redirspinner.com/30jg?p=%2Fregistration%2F")],
            [InlineKeyboardButton(text="🔵 📱 Télécharger l'application", url="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K")]
        ]
    )

def get_approval_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟢 🌐 سجل الآن", url="https://redirspinner.com/30jg?p=%2Fregistration%2F")],
            [InlineKeyboardButton(text="🔵 📱 حمل التطبيق الآن", url="https://spin-b.com/mwGY27?tag=d_220149m_716178c_cz_P9pguCUE7MR9srqvUvka4K")]
        ]
    )

# ----------------- SAFE SEND WRAPPERS -----------------
async def safe_send_message(chat_id: int, text: str, reply_markup: Optional[InlineKeyboardMarkup] = None) -> Optional[Message]:
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
    retries = 3
    for attempt in range(retries):
        try:
            photo_to_send: Union[str, FSInputFile] = FILE_CACHE[photo_key] if FILE_CACHE[photo_key] else FSInputFile(path=photo_path)
            
            msg = await bot.send_photo(
                chat_id=chat_id,
                photo=photo_to_send,
                reply_markup=reply_markup
            )
            
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


@dp.message(Command("broadcast"))
async def handle_broadcast(message: Message):
    if not ADMIN_ID or message.from_user.id != int(ADMIN_ID):
        return

    text = message.text.replace("/broadcast", "", 1).strip()
    if not text:
        await message.reply("⚠️ <b>خطأ:</b> برجاء كتابة الرسالة بعد الأمر.\n\n📝 مثال:\n`/broadcast عرض خاص جداً اليوم للمسجلين الجدد!`")
        return

    await message.reply("⏳ <b>جاري تجهيز الإرسال الجماعي...</b>")
    
    users = await get_all_users()
    if not users:
        await message.reply("⚠️ لم يتم العثور على أي مستخدمين في قاعدة البيانات.")
        return

    await message.reply(f"🚀 <b>بدأ الإرسال إلى {len(users)} عميل...</b>\nستصلك رسالة نهائية عند الانتهاء.")
    
    success = 0
    failed = 0
    
    for user_id in users:
        res = await safe_send_message(chat_id=user_id, text=text)
        if res:
            success += 1
        else:
            failed += 1
        
        await asyncio.sleep(0.05)

    report = f"""✅ <b>اكتمل الإرسال الجماعي!</b>

🟢 نجح الإرسال لـ: {success} مستخدم
🔴 فشل الإرسال لـ: {failed} مستخدم (قاموا بحظر البوت)"""
    
    await message.reply(report)


@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_approved(event: ChatMemberUpdated):
    try:
        user = event.new_chat_member.user
        
        await upsert_user(
            user_id=user.id,
            first_name=user.first_name,
            username=user.username
        )
        
        await safe_send_message(chat_id=user.id, text=APPROVAL_MSG, reply_markup=get_approval_keyboard())
        logger.info(f"Sent approval follow-up and saved user {user.id} to DB.")
        
    except Exception as e:
        logger.error(f"Error in on_user_approved: {e}", exc_info=True)


@dp.chat_join_request()
async def handle_chat_join_request(chat_join_request: ChatJoinRequest):
    try:
        user = chat_join_request.from_user
        user_id = user.id
        vip1_path = BASE_DIR / "images" / "vip1.png"
        register_img_path = BASE_DIR / "images" / "register.jpeg"
        
        await upsert_user(
            user_id=user_id,
            first_name=user.first_name,
            username=user.username
        )

        if vip1_path.exists() and vip1_path.is_file():
            await safe_send_photo(chat_id=user_id, photo_key="vip1", photo_path=vip1_path)
        else:
            logger.warning(f"Image '{vip1_path}' not found.")

        await safe_send_message(chat_id=user_id, text=AR_MESSAGE, reply_markup=get_ar_keyboard())
        
        # Delay increased to 8 seconds per user request
        await asyncio.sleep(8)
        
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
    await callback_query.answer(cache_time=2)
    try:
        if callback_query.message:
            await callback_query.message.edit_text(
                text=FR_MESSAGE,
                reply_markup=get_fr_keyboard(),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
    except TelegramAPIError as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Error switching to French: {e}")
    except Exception as e:
        logger.error(f"Unexpected error switching to French: {e}", exc_info=True)


@dp.callback_query(F.data == "switch_ar")
async def switch_to_arabic(callback_query: CallbackQuery):
    await callback_query.answer(cache_time=2)
    try:
        if callback_query.message:
            await callback_query.message.edit_text(
                text=AR_MESSAGE,
                reply_markup=get_ar_keyboard(),
                link_preview_options=LinkPreviewOptions(is_disabled=True)
            )
    except TelegramAPIError as e:
        if "message is not modified" not in str(e).lower():
            logger.error(f"Error switching to Arabic: {e}")
    except Exception as e:
        logger.error(f"Unexpected error switching to Arabic: {e}", exc_info=True)


@dp.callback_query(F.data == "confirm_registration")
async def handle_confirmation(callback_query: CallbackQuery):
    await callback_query.answer(cache_time=5)
    try:
        if callback_query.message:
            await callback_query.message.edit_reply_markup(reply_markup=None)
        
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
