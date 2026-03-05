"""Configuration management for OANDA Telegram Signals."""
import os
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OANDAConfig:
    """OANDA API configuration."""
    env: str
    access_token: str
    base_url: str
    
    @classmethod
    def from_env(cls) -> "OANDAConfig":
        """Load OANDA configuration from environment variables."""
        env = os.getenv("OANDA_ENV", "practice").lower()
        access_token = os.getenv("OANDA_ACCESS_TOKEN", "")
        
        if not access_token:
            raise ValueError("OANDA_ACCESS_TOKEN environment variable is required")
        
        if env == "live":
            base_url = "https://api-fxtrade.oanda.com"
        else:
            base_url = "https://api-fxpractice.oanda.com"
        
        return cls(env=env, access_token=access_token, base_url=base_url)


@dataclass
class TradingConfig:
    """Trading strategy configuration."""
    instruments: List[str]
    granularity: str
    candle_count: int
    strategy_type: str  # "ema_bounce", "macd", "price_action", or "advanced"
    
    @classmethod
    def from_env(cls) -> "TradingConfig":
        """Load trading configuration from environment variables."""
        instruments_str = os.getenv("INSTRUMENTS", "EUR_USD")
        instruments = [i.strip() for i in instruments_str.split(",") if i.strip()]
        
        if not instruments:
            raise ValueError("INSTRUMENTS environment variable must contain at least one instrument")
        
        granularity = os.getenv("GRANULARITY", "M1")
        
        # Force M1 only - البوت يعمل فقط على إطار 1 دقيقة
        if granularity.upper() != "M1":
            raise ValueError(
                f"البوت يعمل فقط على إطار 1 دقيقة (M1). "
                f"GRANULARITY يجب أن يكون M1، لكن تم الحصول على: {granularity}"
            )
        
        granularity = "M1"  # Force to M1
        candle_count = int(os.getenv("CANDLE_COUNT", "200"))
        strategy_type = os.getenv("STRATEGY_TYPE", "advanced").lower()  # Default to advanced
        
        if strategy_type not in ["ema_bounce", "macd", "price_action", "advanced"]:
            raise ValueError(
                f"STRATEGY_TYPE must be 'ema_bounce', 'macd', 'price_action', or 'advanced', got: {strategy_type}"
            )
        
        return cls(
            instruments=instruments,
            granularity=granularity,
            candle_count=candle_count,
            strategy_type=strategy_type
        )


@dataclass
class EngineConfig:
    """Engine/scheduler configuration."""
    interval_seconds: int
    cooldown_seconds: int
    force_daily_summary: bool
    
    @classmethod
    def from_env(cls) -> "EngineConfig":
        """Load engine configuration from environment variables."""
        interval_seconds = int(os.getenv("INTERVAL_SECONDS", "60"))
        cooldown_seconds = int(os.getenv("COOLDOWN_SECONDS", "60"))  # دقيقة واحدة بين كل رسالة
        force_daily_summary = os.getenv("FORCE_DAILY_SUMMARY", "false").lower() == "true"
        
        return cls(
            interval_seconds=interval_seconds,
            cooldown_seconds=cooldown_seconds,
            force_daily_summary=force_daily_summary
        )


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    bot_token: str
    chat_id: str
    
    @classmethod
    def from_env(cls) -> "TelegramConfig":
        """Load Telegram configuration from environment variables."""
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        if not chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable is required")
        
        return cls(bot_token=bot_token, chat_id=chat_id)


@dataclass
class Config:
    """Main application configuration."""
    oanda: OANDAConfig
    trading: TradingConfig
    engine: EngineConfig
    telegram: TelegramConfig
    log_level: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load all configuration from environment variables."""
        log_level = os.getenv("LOG_LEVEL", "INFO")
        
        return cls(
            oanda=OANDAConfig.from_env(),
            trading=TradingConfig.from_env(),
            engine=EngineConfig.from_env(),
            telegram=TelegramConfig.from_env(),
            log_level=log_level
        )

