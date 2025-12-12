import json
from datetime import datetime

from picomon.config import PicomonConfig
from picomon.smi import load_static_info, update_dynamic_info


def _runner_with_payloads(payloads: dict[str, object]):
    responses = {key: json.dumps(value) for key, value in payloads.items()}

    def _runner(args, *, timeout):  # type: ignore[override]
        cmd = args[1] if len(args) > 1 else ""
        return responses.get(cmd, next(iter(responses.values())))

    return _runner


def test_load_static_info_populates_static_fields():
    config = PicomonConfig(update_interval=1.0, history_minutes=1)
    runner = _runner_with_payloads(
        {
            "static": {
                "gpu_data": [
                    {
                        "gpu": 0,
                        "vram": {"size": {"value": 16384, "unit": "MB"}},
                        "limit": {"socket_power": {"value": 250, "unit": "W"}},
                    }
                ]
            },
            "list": [
                {"gpu": 0, "node_id": 42},
            ],
        }
    )

    gpus = load_static_info(config, runner=runner)

    assert 0 in gpus
    hist = gpus[0]
    assert hist.vram_total_mb == 16384
    assert hist.power_limit_w == 250
    assert hist.hip_id == 42


def test_update_dynamic_info_appends_samples():
    config = PicomonConfig(update_interval=1.0, history_minutes=1)
    static_runner = _runner_with_payloads(
        {
            "static": {
                "gpu_data": [
                    {
                        "gpu": 0,
                        "vram": {"size": {"value": 16384, "unit": "MB"}},
                        "limit": {"socket_power": {"value": 250, "unit": "W"}},
                    }
                ]
            },
            "list": [
                {"gpu": 0, "node_id": 7},
            ],
            "metric": {
                "gpu_data": [
                    {
                        "gpu": 0,
                        "usage": {"gfx_activity": {"value": 40, "unit": "%"}},
                        "power": {"socket_power": {"value": 120, "unit": "W"}},
                        "mem_usage": {
                            "used_visible_vram": {"value": 8192, "unit": "MB"},
                            "total_visible_vram": {"value": 16384, "unit": "MB"},
                        },
                    }
                ]
            },
        }
    )
    gpus = load_static_info(config, runner=static_runner)

    now = datetime(2024, 1, 1, 12, 0, 0)
    update_dynamic_info(
        config,
        gpus,
        runner=static_runner,
        timestamp_provider=lambda: now,
    )

    hist = gpus[0]
    assert hist.timestamps[-1] == now
    assert hist.gfx[-1] == 40
    assert hist.power_w[-1] == 120
    assert hist.vram_used_mb[-1] == 8192
    assert hist.vram_total_mb == 16384
