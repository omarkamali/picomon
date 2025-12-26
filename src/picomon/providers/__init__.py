"""GPU providers for different hardware vendors."""

from __future__ import annotations

import logging
from typing import List, Type

from .base import GPUProvider, GPUStaticInfo, GPUMetrics, GPUHistory
from .amd import AMDProvider
from .nvidia import NVIDIAProvider
from .apple import AppleSiliconProvider

__all__ = [
    "GPUProvider",
    "GPUStaticInfo",
    "GPUMetrics",
    "GPUHistory",
    "AMDProvider",
    "NVIDIAProvider",
    "AppleSiliconProvider",
    "detect_providers",
    "get_provider",
    "get_all_providers",
]

logger = logging.getLogger(__name__)

# Provider classes in detection order (most specific first)
PROVIDER_CLASSES: List[Type[GPUProvider]] = [
    AMDProvider,
    NVIDIAProvider,
    AppleSiliconProvider,
]


def detect_providers() -> List[GPUProvider]:
    """Detect and return all available GPU providers.

    Returns:
        List of available provider instances.
    """
    available = []
    for provider_cls in PROVIDER_CLASSES:
        try:
            if provider_cls.is_available():
                provider = provider_cls()
                gpu_count = provider.get_gpu_count()
                if gpu_count > 0:
                    logger.info(
                        "Detected %s provider with %d GPU(s)",
                        provider.name,
                        gpu_count,
                    )
                    available.append(provider)
        except Exception as exc:
            logger.debug("Failed to check %s provider: %s", provider_cls.__name__, exc)

    return available


def get_provider(vendor: str | None = None) -> GPUProvider | None:
    """Get a specific provider or the first available one.

    Args:
        vendor: Vendor name ('AMD', 'NVIDIA', 'Apple') or None for auto-detect.

    Returns:
        Provider instance or None if not available.
    """
    if vendor is not None:
        vendor_lower = vendor.lower()
        for provider_cls in PROVIDER_CLASSES:
            if provider_cls.__name__.lower().startswith(vendor_lower) or \
               vendor_lower in provider_cls.__name__.lower():
                try:
                    if provider_cls.is_available():
                        return provider_cls()
                except Exception:
                    pass
        return None

    # Auto-detect: return first available
    providers = detect_providers()
    return providers[0] if providers else None


def get_all_providers() -> List[GPUProvider]:
    """Get all available providers.

    This is useful for systems with multiple GPU vendors.

    Returns:
        List of all available provider instances.
    """
    return detect_providers()


class MultiProvider(GPUProvider):
    """A provider that aggregates multiple GPU providers.

    This is useful for systems with GPUs from different vendors.
    """

    def __init__(self, providers: List[GPUProvider] | None = None):
        """Initialize with a list of providers.

        Args:
            providers: List of providers to aggregate. If None, auto-detects.
        """
        self._providers = providers if providers is not None else detect_providers()
        self._gpu_offset: dict[GPUProvider, int] = {}

        # Calculate GPU index offsets for each provider
        offset = 0
        for provider in self._providers:
            self._gpu_offset[provider] = offset
            offset += provider.get_gpu_count()

    @property
    def name(self) -> str:
        if len(self._providers) == 0:
            return "None"
        elif len(self._providers) == 1:
            return self._providers[0].name
        else:
            names = [p.name for p in self._providers]
            return " + ".join(names)

    @property
    def vendor(self) -> str:
        return "Multi"

    @classmethod
    def is_available(cls) -> bool:
        """Check if any provider is available."""
        return len(detect_providers()) > 0

    def get_gpu_count(self) -> int:
        """Get total GPU count across all providers."""
        return sum(p.get_gpu_count() for p in self._providers)

    def get_static_info(self, timeout: float = 10.0) -> dict[int, GPUStaticInfo]:
        """Get static info from all providers with reindexed GPU IDs."""
        all_info: dict[int, GPUStaticInfo] = {}

        for provider in self._providers:
            offset = self._gpu_offset[provider]
            provider_info = provider.get_static_info(timeout=timeout)

            for gpu_idx, info in provider_info.items():
                new_idx = gpu_idx + offset
                # Create a copy with updated index
                new_info = GPUStaticInfo(
                    gpu_idx=new_idx,
                    name=info.name,
                    vendor=info.vendor,
                    architecture=info.architecture,
                    compute_units=info.compute_units,
                    pcie_bus=info.pcie_bus,
                    vram_total_mb=info.vram_total_mb,
                    power_limit_w=info.power_limit_w,
                    sort_index=info.sort_index if info.sort_index is not None else new_idx,
                )
                all_info[new_idx] = new_info

        return all_info

    def get_metrics(self, timeout: float = 5.0) -> List[GPUMetrics]:
        """Get metrics from all providers with reindexed GPU IDs."""
        all_metrics: List[GPUMetrics] = []

        for provider in self._providers:
            offset = self._gpu_offset[provider]
            provider_metrics = provider.get_metrics(timeout=timeout)

            for metrics in provider_metrics:
                # Create a copy with updated index
                new_metrics = GPUMetrics(
                    timestamp=metrics.timestamp,
                    gpu_idx=metrics.gpu_idx + offset,
                    gpu_utilization=metrics.gpu_utilization,
                    memory_controller_utilization=metrics.memory_controller_utilization,
                    power_draw_w=metrics.power_draw_w,
                    vram_used_mb=metrics.vram_used_mb,
                    temperature_c=metrics.temperature_c,
                    gpu_clock_mhz=metrics.gpu_clock_mhz,
                    memory_clock_mhz=metrics.memory_clock_mhz,
                    fan_speed_percent=metrics.fan_speed_percent,
                )
                all_metrics.append(new_metrics)

        return all_metrics
