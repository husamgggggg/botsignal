"""Main entry point for OANDA Telegram Signals."""
import asyncio
import signal
import sys
import logging

from src.config import Config
from src.utils.logging import setup_logging, get_logger
from src.clients.oanda import OANDAClient
from src.strategies.ema_support_bounce import EMASupportBounceStrategy
from src.strategies.macd_crossover import MACDCrossoverStrategy
from src.strategies.price_action_sr import PriceActionSRStrategy
from src.strategies.advanced_multi_indicator import AdvancedMultiIndicatorStrategy
from src.engine.state import StateManager
from src.engine.runner import TradingEngine
from src.notifier.telegram import TelegramNotifier

logger = get_logger(__name__)


class Application:
    """Main application class."""
    
    def __init__(self, config: Config):
        """Initialize application.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.engine: TradingEngine | None = None
        self.oanda_client: OANDAClient | None = None
        self.notifier: TelegramNotifier | None = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self) -> None:
        """Initialize all components."""
        logger.info("Initializing application...")
        
        # Initialize OANDA client
        self.oanda_client = OANDAClient(
            base_url=self.config.oanda.base_url,
            access_token=self.config.oanda.access_token
        )
        await self.oanda_client.__aenter__()
        
        # Initialize strategy based on config
        if self.config.trading.strategy_type == "advanced":
            strategy = AdvancedMultiIndicatorStrategy(
                macd_fast=12,
                macd_slow=26,
                macd_signal=9,
                rsi_period=14,
                rsi_buy_min=45.0,
                rsi_buy_max=70.0,
                rsi_sell_min=30.0,
                rsi_sell_max=55.0,
                ema_short=10,
                ema_medium=20,
                ema_long=50,
                sr_lookback=50,
                sr_min_touches=2,
                sr_tolerance_pct=0.15,
                sr_proximity_pct=0.2,
                min_confirmations=4
            )
            logger.info("Using Advanced Multi-Indicator Strategy (أقوى استراتيجية)")
        elif self.config.trading.strategy_type == "macd":
            strategy = MACDCrossoverStrategy(
                fast_period=12,
                slow_period=26,
                signal_period=9,
                lookback_candles=6
            )
            logger.info("Using MACD Crossover Strategy")
        elif self.config.trading.strategy_type == "price_action":
            strategy = PriceActionSRStrategy(
                lookback=20,
                min_touches=2,
                tolerance_pct=0.1,
                proximity_pct=0.15
            )
            logger.info("Using Price Action + Support/Resistance Strategy")
        else:  # default: ema_bounce
            strategy = EMASupportBounceStrategy(
                ema_period=10,
                ema_long_period=50,  # EMA50 للترند العام
                support_tolerance_pct=0.1,  # 0.1% tolerance for support zone
                trend_lookback=5,  # Check last 5 candles for uptrend
                rsi_period=14,  # فترة RSI
                min_rsi_buy=45.0,  # الحد الأدنى لـ RSI للشراء
                max_rsi_sell=55.0  # الحد الأقصى لـ RSI للبيع
            )
            logger.info("Using EMA Support Bounce Strategy (with RSI and EMA50 filters)")
        
        # Initialize state manager
        state_manager = StateManager()
        
        # Initialize Telegram notifier
        self.notifier = TelegramNotifier(
            bot_token=self.config.telegram.bot_token,
            chat_id=self.config.telegram.chat_id
        )
        
        # Initialize engine
        self.engine = TradingEngine(
            oanda_client=self.oanda_client,
            strategy=strategy,
            state_manager=state_manager,
            notifier=self.notifier,
            instruments=self.config.trading.instruments,
            granularity=self.config.trading.granularity,
            candle_count=self.config.trading.candle_count,
            cooldown_seconds=self.config.engine.cooldown_seconds
        )
        
        logger.info("Application initialized successfully")
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("Cleaning up resources...")
        
        if self.engine:
            self.engine.stop()
        
        if self.notifier:
            await self.notifier.close()
        
        if self.oanda_client:
            await self.oanda_client.__aexit__(None, None, None)
        
        logger.info("Cleanup completed")
    
    async def run(self) -> None:
        """Run the application."""
        try:
            await self.initialize()
            
            # Send test message on startup (optional, but helpful for verification)
            logger.info("Sending startup test message to Telegram...")
            try:
                await self.notifier.send_message(
                    "🚀 بوت حسام الاحترافي\n\n"
                    f"✅ تم تشغيل البوت بنجاح\n"
                    f"📊 المراقبة: {', '.join(self.config.trading.instruments)}\n"
                    f"⏱ المدة: 1 دقيقة\n"
                    f"🔄 الفترة: {self.config.engine.interval_seconds} ثانية"
                )
                logger.info("Startup message sent successfully")
            except Exception as e:
                logger.warning(f"Failed to send startup message: {e}")
            
            # Run engine
            await self.engine.run(self.config.engine.interval_seconds)
        
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()
    
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            self._shutdown_event.set()
            if self.engine:
                self.engine.stop()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Windows doesn't support SIGTERM
        if sys.platform == "win32":
            logger.debug("Windows platform detected, using Ctrl+C for shutdown")


async def main():
    """Main entry point."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Setup logging
        setup_logging(config.log_level)
        
        logger.info("Starting OANDA Telegram Signals Bot")
        logger.info(f"OANDA Environment: {config.oanda.env}")
        logger.info(f"Instruments: {', '.join(config.trading.instruments)}")
        logger.info(f"Interval: {config.engine.interval_seconds}s")
        logger.info(f"Cooldown: {config.engine.cooldown_seconds}s")
        
        # Create and run application
        app = Application(config)
        app.setup_signal_handlers()
        
        await app.run()
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

