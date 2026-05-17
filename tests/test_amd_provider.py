from picomon.providers.amd import AMDProvider


def test_get_static_info_reads_nested_ppt_power_limit(monkeypatch):
    payloads = {
        "static": {
            "gpu_data": [
                {
                    "gpu": 0,
                    "vram": {"size": {"value": 32624, "unit": "MB"}},
                    "limit": {
                        "ppt0": {
                            "socket_power_limit": {"value": 300, "unit": "W"},
                            "max_power_limit": {"value": 300, "unit": "W"},
                        },
                        "ppt1": {
                            "socket_power_limit": "N/A",
                            "max_power_limit": "N/A",
                        },
                    },
                }
            ]
        },
        "list": [{"gpu": 0, "node_id": 7}],
    }

    def fake_run_json(args, timeout):
        return payloads[args[1]]

    monkeypatch.setattr("picomon.providers.amd._run_json", fake_run_json)

    static_info = AMDProvider().get_static_info()

    assert static_info[0].vram_total_mb == 32624
    assert static_info[0].power_limit_w == 300
    assert static_info[0].sort_index == 7


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
