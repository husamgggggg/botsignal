"""State persistence for engine."""
import json
import os
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import tempfile

from src.strategies.ema_support_bounce import Signal

logger = logging.getLogger(__name__)


class StateManager:
    """Manages persistent state for trading signals."""
    
    def __init__(self, state_file: str = "state.json"):
        """Initialize state manager.
        
        Args:
            state_file: Path to JSON state file
        """
        self.state_file = Path(state_file)
        self._state: Dict[str, Dict] = {}
        self._load()
    
    def get_last_global_sent_at(self) -> Optional[float]:
        """Get timestamp of last alert sent globally (any instrument).
        
        Returns:
            Unix timestamp or None if never sent
        """
        return self._state.get("_global", {}).get("last_sent_at")
    
    def update_global_sent_at(
        self,
        sent_at: Optional[float] = None,
        instrument: Optional[str] = None
    ) -> None:
        """Update global last sent timestamp and last instrument.
        
        Args:
            sent_at: Timestamp when alert was sent (defaults to now)
            instrument: Instrument for which the alert was sent
        """
        if "_global" not in self._state:
            self._state["_global"] = {}
        
        if sent_at is None:
            sent_at = datetime.utcnow().timestamp()
        self._state["_global"]["last_sent_at"] = sent_at
        
        if instrument is not None:
            self._state["_global"]["last_instrument"] = instrument
        
        self._save()
    
    def get_last_global_instrument(self) -> Optional[str]:
        """Get instrument of last alert sent globally.
        
        Returns:
            Instrument name or None if never sent
        """
        return self._state.get("_global", {}).get("last_instrument")
    
    def can_send_global(self, min_interval_seconds: int = 60) -> bool:
        """Check if we can send an alert globally (not more than one per minute).
        
        Args:
            min_interval_seconds: Minimum seconds between any alerts (default 60)
            
        Returns:
            True if we can send an alert
        """
        last_sent_at = self.get_last_global_sent_at()
        
        if last_sent_at is None:
            return True  # Never sent before
        
        elapsed = datetime.utcnow().timestamp() - last_sent_at
        return elapsed >= min_interval_seconds
    
    def _load(self) -> None:
        """Load state from file."""
        if not self.state_file.exists():
            logger.debug(f"State file {self.state_file} does not exist, starting with empty state")
            self._state = {}
            return
        
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                self._state = json.load(f)
            logger.debug(f"Loaded state from {self.state_file}")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load state from {self.state_file}: {e}. Starting with empty state.")
            self._state = {}
    
    def _save(self) -> None:
        """Save state to file atomically."""
        try:
            # Write to temporary file first (atomic operation)
            temp_file = self.state_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)
            
            # Atomically replace the original file
            if os.name == 'nt':  # Windows
                if self.state_file.exists():
                    os.replace(temp_file, self.state_file)
                else:
                    temp_file.rename(self.state_file)
            else:  # Unix-like
                temp_file.replace(self.state_file)
            
            logger.debug(f"Saved state to {self.state_file}")
        except IOError as e:
            logger.error(f"Failed to save state to {self.state_file}: {e}")
            # Try to clean up temp file
            temp_file = self.state_file.with_suffix(".tmp")
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except IOError:
                    pass
    
    def get_last_signal(self, instrument: str) -> Optional[Signal]:
        """Get last signal for an instrument.
        
        Args:
            instrument: Instrument name (e.g., "EUR_USD")
            
        Returns:
            Last signal or None if no previous signal
        """
        instrument_state = self._state.get(instrument, {})
        signal_str = instrument_state.get("last_signal")
        if signal_str:
            try:
                return Signal(signal_str)
            except ValueError:
                logger.warning(f"Invalid signal value '{signal_str}' for {instrument}")
                return None
        return None
    
    def get_last_sent_at(self, instrument: str) -> Optional[float]:
        """Get timestamp of last alert sent for an instrument.
        
        Args:
            instrument: Instrument name
            
        Returns:
            Unix timestamp or None if never sent
        """
        instrument_state = self._state.get(instrument, {})
        return instrument_state.get("last_sent_at")
    
    def update_signal(
        self,
        instrument: str,
        signal: Signal,
        sent_at: Optional[float] = None
    ) -> None:
        """Update signal for an instrument.
        
        Args:
            instrument: Instrument name
            signal: Current signal
            sent_at: Timestamp when alert was sent (defaults to now)
        """
        if instrument not in self._state:
            self._state[instrument] = {}
        
        self._state[instrument]["last_signal"] = signal.value
        if sent_at is None:
            sent_at = datetime.utcnow().timestamp()
        self._state[instrument]["last_sent_at"] = sent_at
        
        self._save()
    
    def should_send_alert(
        self,
        instrument: str,
        current_signal: Signal,
        cooldown_seconds: int
    ) -> bool:
        """Determine if an alert should be sent.
        
        Args:
            instrument: Instrument name
            current_signal: Current signal
            cooldown_seconds: Cooldown period in seconds
            
        Returns:
            True if alert should be sent
        """
        # لا ترسل إذا كانت الإشارة NO_TRADE
        if current_signal == Signal.NO_TRADE:
            return False
        
        last_signal = self.get_last_signal(instrument)
        last_sent_at = self.get_last_sent_at(instrument)
        
        # Send if signal changed (but not to NO_TRADE as checked above)
        if last_signal != current_signal:
            return True
        
        # Send if cooldown expired
        if last_sent_at:
            elapsed = datetime.utcnow().timestamp() - last_sent_at
            if elapsed >= cooldown_seconds:
                return True
        else:
            # Never sent before, send it (but not NO_TRADE as checked above)
            return True
        
        return False

