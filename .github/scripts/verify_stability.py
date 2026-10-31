"""Collect a short stability sample; this is not a load test or benchmark."""

import csv
import json
from pathlib import Path
import statistics
import subprocess
import time
import urllib.request


EVIDENCE = Path("evidence")
ROUNDS = 6
INTERVAL_SECONDS = 5


def docker(*arguments):
    return subprocess.check_output(
        ["docker", *arguments], text=True, timeout=20
    ).strip()


def main():
    started = time.monotonic()
    requests = []
    report = {
        "scope": "Short sequential sample, not a load test or availability guarantee",
        "configured_rounds": ROUNDS,
        "interval_seconds": INTERVAL_SECONDS,
        "cpu_note": "CPUPerc is the raw Docker CLI value, not percent of the CPU quota",
        "memory_note": "Docker CLI Linux MemUsage excludes cache; it is not RSS",
        "sampling_note": "Samples do not measure a continuous peak or prove optimal limits",
        "success": False,
        "samples": [],
    }

    try:
        baseline = json.loads((EVIDENCE / "replicas.json").read_text(encoding="utf-8"))
        expected_ids = set(baseline["container_ids"])
        replicas = baseline["replicas"]
        if len(expected_ids) != 2 or len(replicas) != 2:
            raise RuntimeError("The smoke-test baseline must contain two replicas")

        for round_number in range(1, ROUNDS + 1):
            deadline = started + (round_number - 1) * INTERVAL_SECONDS
            time.sleep(max(0, deadline - time.monotonic()))
            running_ids = set(
                docker("compose", "ps", "--status", "running", "-q", "microservicio").splitlines()
            )
            if running_ids != expected_ids:
                raise RuntimeError("Running replicas changed from the verified smoke-test baseline")

            for replica in replicas:
                for expected in replica["results"]:
                    request_started = time.perf_counter()
                    with urllib.request.urlopen(
                        f"http://{replica['address']}{expected['path']}", timeout=5
                    ) as response:
                        status = response.status
                        content_type = response.headers.get_content_type()
                        body = json.load(response)
                    latency_ms = (time.perf_counter() - request_started) * 1000
                    requests.append({
                        "round": round_number,
                        "replica": replica["index"],
                        "path": expected["path"],
                        "status": status,
                        "latency_ms": round(latency_ms, 3),
                    })
                    if status != 200 or content_type != "application/json" or body != expected["body"]:
                        raise RuntimeError(
                            f"Replica {replica['index']} {expected['path']}: unexpected response"
                        )


            containers = json.loads(docker("inspect", *sorted(expected_ids)))
            states = []
            for container in containers:
                state = container["State"]
                snapshot = {
                    "id": container["Id"],
                    "running": state["Running"],
                    "oom_killed": state["OOMKilled"],
                    "restart_count": container["RestartCount"],
                    "cpu_limit_cores": container["HostConfig"]["NanoCpus"] / 1_000_000_000,
                    "memory_limit_bytes": container["HostConfig"]["Memory"],
                }
                states.append(snapshot)
                if not snapshot["running"] or snapshot["oom_killed"] or snapshot["restart_count"]:
                    raise RuntimeError(f"Replica is not stable: {snapshot}")

            stats = [
                json.loads(line)
                for line in docker(
                    "stats", "--no-stream", "--no-trunc", "--format", "{{json .}}",
                    *sorted(expected_ids),
                ).splitlines()
            ]
            if len(stats) != len(expected_ids):
                raise RuntimeError("Expected one resource sample per running replica")
            report["samples"].append({
                "round": round_number,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "states": states,
                "docker_stats": stats,
            })
            print(f"PASS round {round_number}/{ROUNDS}: two unchanged replicas, six correct responses")

        report["success"] = True
    except Exception as error:
        report["error"] = str(error)
        raise
    finally:
        report["duration_seconds"] = round(time.monotonic() - started, 3)
        report["request_count"] = len(requests)
        if requests:
            latencies = [request["latency_ms"] for request in requests]
            report["observed_latency_ms"] = {
                "minimum": min(latencies),
                "median": round(statistics.median(latencies), 3),
                "maximum": max(latencies),
            }
        EVIDENCE.mkdir(exist_ok=True)
        (EVIDENCE / "stability.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        with (EVIDENCE / "stability-requests.csv").open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=["round", "replica", "path", "status", "latency_ms"])
            writer.writeheader()
            writer.writerows(requests)

    print(f"PASS: {len(requests)} repeated requests in {report['duration_seconds']} seconds")
    print(json.dumps(report.get("observed_latency_ms", {})))


if __name__ == "__main__":
    main()
