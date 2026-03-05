"""Retry utilities with exponential backoff and jitter."""
import asyncio
import random
import time
from typing import Callable, TypeVar, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_on: Optional[tuple] = None,
    *args,
    **kwargs
) -> T:
    """Retry a function with exponential backoff and jitter.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
        retry_on: Tuple of exception types to retry on (None = all)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result of func
        
    Raises:
        Last exception if all retries fail
    """
    if retry_on is None:
        retry_on = (Exception,)
    
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retry_on as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                raise
            
            # Calculate delay with exponential backoff
            delay = min(
                initial_delay * (exponential_base ** attempt),
                max_delay
            )
            
            # Add jitter (random value between 0 and 30% of delay)
            if jitter:
                jitter_amount = delay * 0.3 * random.random()
                delay = delay + jitter_amount
            
            logger.warning(
                f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            
            await asyncio.sleep(delay)
        except Exception as e:
            # Don't retry on unexpected exceptions
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry logic failed unexpectedly")

