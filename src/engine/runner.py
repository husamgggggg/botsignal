"""Engine runner for periodic analysis."""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from src.clients.oanda import OANDAClient
from src.strategies.ema_support_bounce import EMASupportBounceStrategy, Signal as EMASignal
from src.strategies.macd_crossover import MACDCrossoverStrategy, Signal as MACDSignal
from src.strategies.price_action_sr import PriceActionSRStrategy, Signal as PASignal
from src.strategies.advanced_multi_indicator import AdvancedMultiIndicatorStrategy, Signal as AdvancedSignal
from src.engine.state import StateManager
from src.notifier.telegram import TelegramNotifier

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading engine that orchestrates analysis and notifications."""
    
    def __init__(
        self,
        oanda_client: OANDAClient,
        strategy,  # EMASupportBounceStrategy or MACDCrossoverStrategy
        state_manager: StateManager,
        notifier: TelegramNotifier,
        instruments: List[str],
        granularity: str,
        candle_count: int,
        cooldown_seconds: int
    ):
        """Initialize trading engine.
        
        Args:
            oanda_client: OANDA API client
            strategy: Trading strategy instance (EMA or MACD)
            state_manager: State persistence manager
            notifier: Telegram notifier
            instruments: List of instruments to analyze
            granularity: Candle granularity (e.g., "M5")
            candle_count: Number of candles to fetch
            cooldown_seconds: Cooldown period between alerts
        """
        self.oanda_client = oanda_client
        self.strategy = strategy
        self.state_manager = state_manager
        self.notifier = notifier
        self.instruments = instruments
        self.granularity = granularity
        self.candle_count = candle_count
        self.cooldown_seconds = cooldown_seconds
        self._running = False
        self._is_macd_strategy = isinstance(strategy, MACDCrossoverStrategy)
        self._is_price_action_strategy = isinstance(strategy, PriceActionSRStrategy)
        self._is_advanced_strategy = isinstance(strategy, AdvancedMultiIndicatorStrategy)
    
    async def analyze_instrument(self, instrument: str) -> Optional[dict]:
        """Analyze a single instrument and return signal info if eligible.
        
        Args:
            instrument: Instrument to analyze
            
        Returns:
            Dict with signal info if eligible, None otherwise
        """
        # تجاهل EUR_USD و GBP_USD تماماً (لا تحليل ولا سحب بيانات)
        if instrument.upper() in ["EUR_USD", "EUR/USD", "GBP_USD", "GBP/USD"]:
            logger.debug(f"Skipping {instrument} - {instrument} is excluded from trading")
            return None
        
        try:
            logger.info(f"Analyzing {instrument}...")
            
            # Fetch candles - request extra to ensure we get enough completed candles
            # OANDA may return the last candle as incomplete, so request 5 extra
            requested_count = self.candle_count + 5
            candles = await self.oanda_client.get_candles(
                instrument=instrument,
                granularity=self.granularity,
                count=requested_count
            )
            
            # Take only the requested number of completed candles (most recent)
            if len(candles) > self.candle_count:
                candles = candles[-self.candle_count:]
            
            if len(candles) == 0:
                logger.warning(f"No candles retrieved for {instrument}")
                return None
            
            # Run strategy
            try:
                result = self.strategy.analyze(candles)
                # Log result summary
                logger.info(
                    f"{instrument}: Signal={result.signal.value}, "
                    f"Confidence={result.confidence}%, "
                    f"Candles={len(candles)}"
                )
            except ValueError as e:
                logger.error(f"Strategy analysis failed for {instrument}: {e}")
                return None
            
            # Log based on strategy type
            if self._is_advanced_strategy:
                macd_str = f"{result.macd_line:.5f}" if result.macd_line is not None else "None"
                signal_str = f"{result.macd_signal:.5f}" if result.macd_signal is not None else "None"
                hist_str = f"{result.macd_histogram:.5f}" if result.macd_histogram is not None else "None"
                rsi_str = f"{result.rsi:.2f}" if result.rsi is not None else "None"
                ema10_str = f"{result.ema_10:.5f}" if result.ema_10 is not None else "None"
                ema20_str = f"{result.ema_20:.5f}" if result.ema_20 is not None else "None"
                ema50_str = f"{result.ema_50:.5f}" if result.ema_50 is not None else "None"
                # إضافة سجل على مستوى INFO يوضح عدد التأكيدات
                logger.info(
                    f"{instrument}: Confirmations={result.confirmation_count}/5 (مطلوب 4 على الأقل), "
                    f"RSI={rsi_str}, MACD={macd_str}, EMA10={ema10_str}, EMA20={ema20_str}, EMA50={ema50_str}"
                )
                logger.debug(
                    f"{instrument}: Signal={result.signal.value}, "
                    f"Confidence={result.confidence}%, "
                    f"Confirmations={result.confirmation_count}/5, "
                    f"MACD={macd_str}, Signal={signal_str}, Hist={hist_str}, "
                    f"RSI={rsi_str}, EMA10={ema10_str}, EMA20={ema20_str}, EMA50={ema50_str}"
                )
            elif self._is_macd_strategy:
                macd_str = f"{result.macd_line:.5f}" if result.macd_line is not None else "None"
                signal_str = f"{result.signal_line:.5f}" if result.signal_line is not None else "None"
                hist_str = f"{result.histogram:.5f}" if result.histogram is not None else "None"
                logger.debug(
                    f"{instrument}: Signal={result.signal.value}, "
                    f"Confidence={result.confidence}, "
                    f"MACD={macd_str}, Signal={signal_str}, Hist={hist_str}"
                )
            elif self._is_price_action_strategy:
                support_str = f"{result.nearest_support:.5f}" if result.nearest_support is not None else "None"
                resistance_str = f"{result.nearest_resistance:.5f}" if result.nearest_resistance is not None else "None"
                logger.debug(
                    f"{instrument}: Signal={result.signal.value}, "
                    f"Confidence={result.confidence}, "
                    f"Support={support_str}, Resistance={resistance_str}, "
                    f"Pattern={result.candle_pattern.value}"
                )
            else:
                ema10_str = f"{result.ema_10:.5f}" if result.ema_10 is not None else "None"
                ema50_str = f"{result.ema_50:.5f}" if hasattr(result, 'ema_50') and result.ema_50 is not None else "None"
                rsi_str = f"{result.rsi:.2f}" if hasattr(result, 'rsi') and result.rsi is not None else "None"
                logger.debug(
                    f"{instrument}: Signal={result.signal.value}, "
                    f"Confidence={result.confidence}, "
                    f"EMA10={ema10_str}, EMA50={ema50_str}, RSI={rsi_str}, "
                    f"LastClose={result.last_close:.5f}"
                )
            
            # تحويل الإشارة إلى Signal موحد للـ state manager
            unified_signal = None
            if self._is_advanced_strategy:
                if result.signal == AdvancedSignal.BUY:
                    unified_signal = EMASignal.BUY
                elif result.signal == AdvancedSignal.SELL:
                    unified_signal = EMASignal.SELL
                elif result.signal == AdvancedSignal.NO_TRADE:
                    unified_signal = EMASignal.NO_TRADE
            elif self._is_macd_strategy:
                if result.signal == MACDSignal.BUY:
                    unified_signal = EMASignal.BUY
                elif result.signal == MACDSignal.SELL:
                    unified_signal = EMASignal.SELL
                elif result.signal == MACDSignal.NO_TRADE:
                    unified_signal = EMASignal.NO_TRADE
                elif result.signal in [MACDSignal.POTENTIAL_BUY, MACDSignal.POTENTIAL_SELL]:
                    unified_signal = EMASignal.NO_TRADE
            elif self._is_price_action_strategy:
                if result.signal == PASignal.BUY:
                    unified_signal = EMASignal.BUY
                elif result.signal == PASignal.SELL:
                    unified_signal = EMASignal.SELL
                elif result.signal == PASignal.NO_TRADE:
                    unified_signal = EMASignal.NO_TRADE
                elif result.signal in [PASignal.POTENTIAL_BUY, PASignal.POTENTIAL_SELL]:
                    unified_signal = EMASignal.NO_TRADE
            else:
                unified_signal = result.signal
            
            # لا ترسل رسالة إذا كانت الإشارة NO_TRADE أو POTENTIAL
            is_potential = result.signal.value in ["POTENTIAL_BUY", "POTENTIAL_SELL"]
            if is_potential:
                logger.info(
                    f"{instrument}: {result.signal.value} (Confidence: {result.confidence}%) - إشارة محتملة، لا يتم الإرسال"
                )
                return None
            
            if unified_signal == EMASignal.NO_TRADE:
                # إضافة السبب من rationale إذا كان متوفراً
                reason = ""
                if hasattr(result, 'rationale') and result.rationale:
                    # أخذ أول سطر من rationale كسبب مختصر
                    reason_lines = result.rationale.split('\n')
                    if reason_lines:
                        reason = f" - {reason_lines[0]}"
                logger.info(
                    f"{instrument}: NO_TRADE (Confidence: {result.confidence}%){reason}"
                )
                return None
            
            # التحقق من الحد الأقصى: إشارة واحدة فقط في الدقيقة (60 ثانية)
            if not self.state_manager.can_send_global(min_interval_seconds=60):
                logger.debug(
                    f"{instrument}: Skipping alert - أقل من 60 ثانية منذ آخر إشارة مرسلة"
                )
                return None
            
            # لا ترسل رسالة إذا كانت نسبة النجاح أقل من 70% (فقط للإشارات العادية، ليس POTENTIAL)
            # تم رفع الحد الأدنى من 50% إلى 70% لتقليل الصفقات الخاسرة
            if result.confidence < 70:
                logger.info(
                    f"{instrument}: {result.signal.value} (Confidence: {result.confidence}%) - أقل من 70%، لا يتم الإرسال"
                )
                return None
            
            # Check if we should send alert (only for BUY or SELL signals)
            if unified_signal and self.state_manager.should_send_alert(
                instrument=instrument,
                current_signal=unified_signal,
                cooldown_seconds=self.cooldown_seconds
            ):
                # إرجاع معلومات الإشارة بدلاً من إرسالها مباشرة
                last_close_price = self._get_last_close_price(result)
                return {
                    "instrument": instrument,
                    "result": result,
                    "unified_signal": unified_signal,
                    "last_close_price": last_close_price,
                    "strategy_type": (
                        "advanced" if self._is_advanced_strategy else
                        ("macd" if self._is_macd_strategy else
                         ("price_action" if self._is_price_action_strategy else "ema"))
                    )
                }
            else:
                logger.debug(
                    f"Skipping alert for {instrument}: signal unchanged and cooldown not expired"
                )
                return None
        
        except Exception as e:
            logger.error(f"Error analyzing {instrument}: {e}", exc_info=True)
            return None
    
    async def run_cycle(self) -> None:
        """Run one analysis cycle for all instruments."""
        logger.info(f"Starting analysis cycle for {len(self.instruments)} instruments")
        
        # Analyze all instruments concurrently
        tasks = [self.analyze_instrument(instrument) for instrument in self.instruments]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # جمع جميع الإشارات المؤهلة
        eligible_signals = []
        for result in results:
            if isinstance(result, dict) and result is not None:
                eligible_signals.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in analysis: {result}")

        # إذا كانت هناك إشارات مؤهلة، اختر الإشارة وفقاً لآخر زوج مُرسل
        if eligible_signals:
            # الحصول على آخر زوج تم إرسال إشارة له
            last_instrument = self.state_manager.get_last_global_instrument()

            # إذا كان هناك أكثر من إشارة، وحفظنا آخر زوج، نحاول تجنب تكرار نفس الزوج
            if last_instrument and len(eligible_signals) > 1:
                # استبعاد الإشارات لنفس الزوج الأخير قدر الإمكان
                non_repeated_signals = [
                    s for s in eligible_signals
                    if s["instrument"] != last_instrument
                ]

                if non_repeated_signals:
                    # اختر الأقوى من الأزواج المختلفة عن آخر زوج
                    strongest_signal = max(
                        non_repeated_signals, key=lambda x: x["result"].confidence
                    )
                else:
                    # إذا كانت كل الإشارات لنفس الزوج الأخير، اختر الأقوى كالمعتاد
                    strongest_signal = max(
                        eligible_signals, key=lambda x: x["result"].confidence
                    )
            else:
                # حالة إشارة واحدة فقط أو لا يوجد آخر زوج محفوظ -> اختر الأقوى مباشرة
                strongest_signal = max(
                    eligible_signals, key=lambda x: x["result"].confidence
                )
            
            # إرسال الإشارة الأقوى فقط
            try:
                await self.notifier.send_signal_alert(
                    instrument=strongest_signal["instrument"],
                    granularity=self.granularity,
                    signal=strongest_signal["result"].signal,
                    confidence=strongest_signal["result"].confidence,
                    last_close=strongest_signal["last_close_price"],
                    rationale=strongest_signal["result"].rationale,
                    strategy_type=strongest_signal["strategy_type"],
                    result=strongest_signal["result"]  # Pass full result for advanced strategy
                )
                
                # تحديث الوقت العام للإرسال
                self.state_manager.update_global_sent_at(
                    instrument=strongest_signal["instrument"]
                )
                
                # Update state
                if strongest_signal["unified_signal"]:
                    self.state_manager.update_signal(
                        strongest_signal["instrument"],
                        strongest_signal["unified_signal"]
                    )
                
                logger.info(
                    f"Sent {strongest_signal['result'].signal.value} alert for {strongest_signal['instrument']} "
                    f"(confidence: {strongest_signal['result'].confidence}%) - "
                    f"الأقوى من {len(eligible_signals)} إشارة مؤهلة"
                )
                
                # تسجيل الإشارات الأخرى التي تم تخطيها
                for signal in eligible_signals:
                    if signal != strongest_signal:
                        logger.info(
                            f"Skipped {signal['result'].signal.value} for {signal['instrument']} "
                            f"(confidence: {signal['result'].confidence}%) - "
                            f"إشارة أقوى موجودة"
                        )
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
        
        logger.info("Analysis cycle completed")
    
    async def run(self, interval_seconds: int) -> None:
        """Run the engine in a loop.
        
        Args:
            interval_seconds: Seconds between analysis cycles
        """
        self._running = True
        logger.info(f"Engine started. Analyzing every {interval_seconds} seconds.")
        
        try:
            while self._running:
                cycle_start = datetime.utcnow()
                
                await self.run_cycle()
                
                # Calculate sleep time (account for cycle duration)
                cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
                sleep_time = max(0, interval_seconds - cycle_duration)
                
                if sleep_time > 0:
                    logger.debug(f"Sleeping for {sleep_time:.2f} seconds until next cycle")
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(
                        f"Cycle took {cycle_duration:.2f}s, longer than interval {interval_seconds}s"
                    )
        
        except asyncio.CancelledError:
            logger.info("Engine stopped by cancellation")
            raise
        except Exception as e:
            logger.error(f"Engine error: {e}", exc_info=True)
            raise
    
    def _get_last_close_price(self, result) -> float:
        """Get last close price from strategy result.
        
        Args:
            result: StrategyResult object
            
        Returns:
            Last close price
        """
        # price_action strategy uses 'current_price' instead of 'last_close'
        if self._is_price_action_strategy:
            return getattr(result, 'current_price', 0.0)
        elif self._is_advanced_strategy:
            return getattr(result, 'last_close', 0.0)
        else:
            return getattr(result, 'last_close', 0.0)
    
    def stop(self) -> None:
        """Stop the engine."""
        logger.info("Stopping engine...")
        self._running = False

