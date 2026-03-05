"""Telegram notification module."""
import logging
from typing import Optional
from datetime import datetime, timezone, timedelta

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError

from src.strategies.ema_support_bounce import Signal as EMASignal
from src.strategies.macd_crossover import Signal as MACDSignal

logger = logging.getLogger(__name__)

# توقيت تركيا (UTC+3)
TURKEY_TIMEZONE = timezone(timedelta(hours=3))


class TelegramNotifier:
    """Telegram bot for sending trading alerts."""
    
    def __init__(self, bot_token: str, chat_id: str):
        """Initialize Telegram notifier.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
    
    async def send_message(self, text: str, use_html: bool = False) -> None:
        """Send a text message to Telegram.
        
        Args:
            text: Message text
            use_html: If True, use HTML parse mode. Otherwise, send as plain text.
            
        Raises:
            TelegramAPIError: If sending fails
        """
        try:
            parse_mode = ParseMode.HTML if use_html else None
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.debug("Message sent to Telegram successfully")
        except TelegramAPIError as e:
            logger.error(f"Telegram API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            raise
    
    async def send_signal_alert(
        self,
        instrument: str,
        granularity: str,
        signal,  # EMASignal, MACDSignal, or AdvancedSignal
        confidence: int,
        last_close: float,
        rationale: str,
        strategy_type: str = "ema",
        ema_10: Optional[float] = None,
        result=None  # Full strategy result for advanced strategy
    ) -> None:
        """Send a trading signal alert.
        
        Args:
            instrument: Instrument name (e.g., "EUR_USD")
            granularity: Timeframe (e.g., "M5")
            signal: Trading signal (EMA or MACD Signal)
            confidence: Confidence score (0-100)
            last_close: Last close price
            rationale: Strategy rationale
            strategy_type: Strategy type ("ema" or "macd")
            ema_10: EMA10 value (only for EMA strategy)
            
        Raises:
            TelegramAPIError: If sending fails
        """
        # التحقق من نوع الإشارة
        signal_value = signal.value if hasattr(signal, 'value') else str(signal)
        
        # لا ترسل رسالة إذا كانت الإشارة NO_TRADE أو POTENTIAL
        if signal_value == "NO_TRADE":
            logger.debug(f"Skipping Telegram message for {instrument}: NO_TRADE signal")
            return
        
        is_potential = signal_value in ["POTENTIAL_BUY", "POTENTIAL_SELL"]
        if is_potential:
            logger.info(f"Skipping Telegram message for {instrument}: POTENTIAL signal (not sending potential signals)")
            return
        
        # لا ترسل رسالة إذا كانت نسبة النجاح أقل من 50%
        if confidence < 50:
            logger.debug(f"Skipping Telegram message for {instrument}: Confidence ({confidence}%) below 50%")
            return
        
        # Convert instrument format from EUR_USD to EUR/USD
        instrument_display = instrument.replace("_", "/")
        
        # البوت يعمل فقط على إطار 1 دقيقة
        timeframe_display = "1 دقيقة"
        
        # Convert signal to direction text (فقط BUY و SELL - لا POTENTIAL)
        if signal_value == "BUY":
            direction = "شراء (CALL)"
        elif signal_value == "SELL":
            direction = "بيع (PUT)"
        else:
            direction = "لا تداول"
        
        # الحصول على الوقت بتوقيت تركيا وإضافة دقيقة واحدة (وقت الدخول في الدقيقة القادمة)
        turkey_time = datetime.now(TURKEY_TIMEZONE)
        entry_time = turkey_time + timedelta(minutes=1)
        time_display = entry_time.strftime("%H:%M")
        
        # تحديد قوة الإشارة بناءً على نسبة الثقة
        if confidence >= 75:
            strength_text = "قوية"
            strength_emoji = "🔥"
        elif confidence >= 60:
            strength_text = "متوسطة"
            strength_emoji = "⭐"
        else:
            strength_text = "ضعيفة"
            strength_emoji = "⚡"
        
        # Build message in the requested format
        message = f"""🟢 بوت حسام الاحترافي

🏆 الزوج: {instrument_display}
⏱ المدة: {timeframe_display}
🎯 الاتجاه: {direction}
{strength_emoji} القوة: {strength_text}
🕐 وقت الدخول: {time_display} (توقيت تركيا)"""
        
        # For advanced strategy, add confirmation count
        if strategy_type == "advanced" and result and hasattr(result, 'confirmation_count'):
            message += f"\n✅ تأكيدات: {result.confirmation_count}/5 مؤشرات"
        
        await self.send_message(message, use_html=False)
    
    async def close(self) -> None:
        """Close the bot session."""
        try:
            await self.bot.session.close()
        except Exception as e:
            logger.warning(f"Error closing Telegram bot session: {e}")

