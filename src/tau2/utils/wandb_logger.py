"""Wandb logging utilities for tau2-bench.

Assumes wandb is configured via environment variables
(WANDB_API_KEY, WANDB_PROJECT, WANDB_ENTITY, etc.).
"""

from __future__ import annotations
from typing import Any
from loguru import logger
import time

_wandb_run: Any = None


def init_wandb_run(config: dict[str, Any]) -> None:
    """Initialize a wandb run. Project/entity/key come from env vars."""
    global _wandb_run
    try:
        import wandb
    except ImportError:
        logger.warning("wandb is not installed. Install with: pip install wandb")
        return

    try:
        _wandb_run = wandb.init(config=config,name=f"tau2bench_run_{int(time.time())}")
        logger.info(f"Wandb run initialized: {_wandb_run.url}")
    except Exception as e:
        logger.warning(f"Failed to initialize wandb: {e}")


def log_metrics(metrics_dict: dict[str, Any], prefix: str = "") -> None:
    """Log final metrics to wandb, optionally prefixed (e.g. 'airline/')."""
    if _wandb_run is None:
        return

    try:
        if prefix:
            metrics_dict = {f"{prefix}/{k}": v for k, v in metrics_dict.items()}
        _wandb_run.log(metrics_dict)
        logger.info(f"Logged metrics to wandb: {metrics_dict}")
    except Exception as e:
        logger.warning(f"Failed to log metrics to wandb: {e}")


def finish_wandb_run() -> None:
    """Finish the wandb run."""
    global _wandb_run
    if _wandb_run is None:
        return

    try:
        _wandb_run.finish()
    except Exception as e:
        logger.warning(f"Failed to finish wandb run: {e}")
    finally:
        _wandb_run = None

