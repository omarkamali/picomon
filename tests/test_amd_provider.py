from picomon.providers.amd import AMDProvider


def test_get_metrics_handles_na_usage_blocks(monkeypatch):
    payload = {
        "gpu_data": [
            {
                "gpu": 2,
                "usage": "N/A",
                "power": {"socket_power": "N/A"},
                "mem_usage": {
                    "total_visible_vram": {"value": 512, "unit": "MB"},
                    "used_visible_vram": {"value": 19, "unit": "MB"},
                },
            }
        ]
    }

    def fake_run_json(args, timeout):
        return payload

    monkeypatch.setattr("picomon.providers.amd._run_json", fake_run_json)

    metrics = AMDProvider().get_metrics()

    assert len(metrics) == 1
    gpu_metrics = metrics[0]
    assert gpu_metrics.gpu_idx == 2
    assert gpu_metrics.gpu_utilization == 0.0
    assert gpu_metrics.memory_controller_utilization == 0.0
    assert gpu_metrics.power_draw_w == 0.0
    assert gpu_metrics.vram_used_mb == 19.0
