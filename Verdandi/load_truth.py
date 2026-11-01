#!/usr/bin/env python3
"""E-075 — Load truth: the nerve hub's throughput, measured.

Part IV, slice E-075. Roadmap line: "Load truth: hub
throughput per profile, measured." Until this slice the
campaign had weighed the hub (E-041: 21.9 MiB RSS live on
the VM) and disciplined its traffic (E-062 budgets, E-070
backpressure), but no slice had ever measured how much
traffic the hub actually carries — E-074 said so plainly:
any throughput number quoted before E-075 is invented.
This module is the measuring instrument, and
``docs/architecture/E-075_LOAD_TRUTH.md`` is its first
reading. It states no new law: it measures the hub the
tree already has, exactly as E-073 leaves it.

What "per profile" means here — stated, not assumed:

* The profiles are the budget book's four (E-041,
  ``ember.budgets``): toaster, phone, pi, laptop, in that
  order. The names are duplicated as literals because
  every Verdandi contract module is stdlib-only and
  standalone (loaded file-by-file, E-061 discipline);
  the E-075 conformance tests pin this table's order
  equal to the book's.
* A profile is a *benchmark shape*, not a device claim:
  the hub process is pinned to the profile's CPU count
  (``taskset`` — the E-048 simulation method: toaster 1,
  phone 2, pi 4, laptop 4 — a Pi 5 and this VM both have
  four cores, so pi and laptop share a CPU envelope here
  and differ in publisher shape), driven by the profile's
  publisher count over persistent connections, with the
  profile's subscriber count listening. Every number the
  harness produces is a VM number under this envelope;
  no toaster, phone or Pi was touched, and the slice
  record says so.
* Two throughputs are reported per profile, because the
  hub has two real faces: the *persistent* face (a
  publisher holding one connection, one ack per event —
  the hub's ceiling shape) and the *producer* face (a
  fresh connection per event — exactly the shape of
  ``nervous_system.publish_event_sync``, the path every
  in-tree producer actually takes). The producer face is
  the honest everyday number; the persistent face is the
  headroom.

Correctness is measured with the speed, never assumed:
ack sequence numbers must be contiguous over everything
published (warmup + timed + producer), the feed's line
count must equal the number published, the ring must
answer ``recent`` with its full 256, and each subscriber
must have received every event published while it
listened. A run that fails any check reports the failure
in its ``errors`` — the harness never papers over a
dropped event with a fast time.

Stdlib only. Run it:

    python3 Verdandi/load_truth.py            # JSON report
    python3 Verdandi/load_truth.py toaster    # one profile
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

HUB = Path(__file__).resolve().with_name("nervous_system.py")

#: Payload padding per timed event, in bytes. One timed
#: event on the wire is then ~180 bytes of JSON — the size
#: of a real conversation/heartbeat event as stamped in
#: the feed (E-059/E-061 shapes run 120–260 bytes), not a
#: synthetic micro-packet chosen to flatter the hub.
PAYLOAD_PAD = 32

WARMUP_EVENTS = 32
RING_SIZE = 256  # nervous_system.RING_BUFFER_SIZE, pinned by test


@dataclass(frozen=True)
class ProfileShape:
    """One profile's benchmark shape (see module docstring)."""

    name: str
    cpus: int
    publishers: int
    subscribers: int
    events: int
    producer_events: int


#: The four benchmark shapes, in budget-book order.
PROFILES: tuple[ProfileShape, ...] = (
    ProfileShape("toaster", cpus=1, publishers=1, subscribers=0,
                 events=512, producer_events=60),
    ProfileShape("phone", cpus=2, publishers=2, subscribers=1,
                 events=512, producer_events=60),
    ProfileShape("pi", cpus=4, publishers=4, subscribers=1,
                 events=1024, producer_events=60),
    ProfileShape("laptop", cpus=4, publishers=8, subscribers=2,
                 events=1024, producer_events=60),
)


def profile_shapes() -> tuple[ProfileShape, ...]:
    return PROFILES


# ── Statistics (pure; pinned by the conformance tests) ──


def percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile of a non-empty sample."""
    if not values:
        raise ValueError("percentile of an empty sample")
    import math

    ordered = sorted(values)
    rank = max(1, math.ceil(len(ordered) * pct))
    return ordered[min(rank, len(ordered)) - 1]


def summarise(samples_ms: list[float], wall_s: float, count: int) -> dict:
    """The report shape for one timed run."""
    return {
        "events": count,
        "wall_s": round(wall_s, 4),
        "throughput_per_s": round(count / wall_s, 1) if wall_s > 0 else 0.0,
        "latency_ms_mean": round(sum(samples_ms) / len(samples_ms), 3)
        if samples_ms
        else 0.0,
        "latency_ms_p50": round(percentile(samples_ms, 0.50), 3)
        if samples_ms
        else 0.0,
        "latency_ms_p95": round(percentile(samples_ms, 0.95), 3)
        if samples_ms
        else 0.0,
        "latency_ms_max": round(max(samples_ms), 3) if samples_ms else 0.0,
    }


# ── The live measurement ────────────────────────────────


def _send_line(sock: socket.socket, obj: dict) -> None:
    sock.sendall((json.dumps(obj) + "\n").encode())


def _read_line(sock: socket.socket, buf: bytearray) -> dict:
    while b"\n" not in buf:
        chunk = sock.recv(65536)
        if not chunk:
            raise ConnectionError("hub closed the connection")
        buf.extend(chunk)
    line, _, rest = bytes(buf).partition(b"\n")
    buf[:] = rest
    return json.loads(line.decode())


def _ping(sock_path: Path) -> bool:
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.settimeout(2.0)
            s.connect(str(sock_path))
            _send_line(s, {"nerve_type": "ping"})
            resp = _read_line(s, bytearray())
            return resp.get("nerve_type") == "pong"
    except OSError:
        return False


def _event(i: int) -> dict:
    return {
        "v": 1,
        "type": "conv_event",
        "source": "load_truth_e075",
        "data": {"i": i, "pad": "x" * PAYLOAD_PAD},
    }


def measure_profile(shape: ProfileShape, workdir: Path) -> dict:
    """Boot the real hub under the profile's envelope and
    measure it. Returns the profile's report dict; every
    failure lands in ``errors``, never in a raised hand."""
    errors: list[str] = []
    state = workdir / f"state-{shape.name}"
    home = workdir / f"home-{shape.name}"
    state.mkdir(parents=True, exist_ok=True)
    home.mkdir(parents=True, exist_ok=True)
    sock_path = state / "runa.sock"
    feed_path = state / "nerve_feed.jsonl"

    env = dict(os.environ)
    env["VERDANDI_HOME"] = str(state)
    env["HOME"] = str(home)
    cmd = ["taskset", "-c", f"0-{shape.cpus - 1}",
           sys.executable, str(HUB), "serve"]
    proc = subprocess.Popen(
        cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.time() + 15.0
        while time.time() < deadline:
            if sock_path.exists() and _ping(sock_path):
                break
            if proc.poll() is not None:
                errors.append(f"hub exited early rc={proc.returncode}")
                return {"profile": shape.name, "errors": errors}
            time.sleep(0.05)
        else:
            errors.append("hub did not answer ping within 15 s")
            return {"profile": shape.name, "errors": errors}

        seqs: list[int] = []
        seq_lock = threading.Lock()

        # Subscribers first, so they hear everything after.
        sub_sockets: list[socket.socket] = []
        sub_received: list[int] = [0] * shape.subscribers
        sub_stop = threading.Event()

        def _listen(idx: int, sock: socket.socket) -> None:
            buf = bytearray()
            sock.settimeout(0.25)
            while not sub_stop.is_set():
                try:
                    line = _read_line(sock, buf)
                except socket.timeout:
                    continue
                except (ConnectionError, OSError):
                    return
                if "_seq" in line:
                    sub_received[idx] += 1

        sub_threads: list[threading.Thread] = []
        for idx in range(shape.subscribers):
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect(str(sock_path))
            _send_line(s, {"nerve_type": "subscribe"})
            hello = _read_line(s, bytearray())
            if hello.get("nerve_type") != "subscribed":
                errors.append(f"subscriber {idx}: no subscribed hello")
            sub_sockets.append(s)
            t = threading.Thread(target=_listen, args=(idx, s), daemon=True)
            t.start()
            sub_threads.append(t)

        def _publish_batch(count: int, collect: list[int],
                           latencies: list[float]) -> None:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(30.0)
            s.connect(str(sock_path))
            buf = bytearray()
            try:
                for i in range(count):
                    t0 = time.perf_counter()
                    _send_line(s, _event(i))
                    ack = _read_line(s, buf)
                    latencies.append((time.perf_counter() - t0) * 1000.0)
                    if ack.get("nerve_type") != "ack":
                        with seq_lock:
                            errors.append(f"non-ack reply: {ack!r}")
                        continue
                    collect.append(int(ack["seq"]))
            finally:
                s.close()

        # Warmup (untimed, but its seqs/feed lines count).
        warm_collect: list[int] = []
        _publish_batch(WARMUP_EVENTS, warm_collect, [])
        with seq_lock:
            seqs.extend(warm_collect)

        # Timed run: the profile's publishers, persistent.
        per_pub = shape.events // shape.publishers
        timed_collect: list[list[int]] = [[] for _ in range(shape.publishers)]
        timed_lat: list[list[float]] = [[] for _ in range(shape.publishers)]
        threads = [
            threading.Thread(
                target=_publish_batch,
                args=(per_pub, timed_collect[k], timed_lat[k]))
            for k in range(shape.publishers)
        ]
        t0 = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wall = time.perf_counter() - t0
        lat_all = [x for part in timed_lat for x in part]
        for part in timed_collect:
            seqs.extend(part)
        timed = summarise(lat_all, wall, shape.events)

        # Producer face: a fresh connection per event, the
        # publish_event_sync shape, sequential.
        prod_collect: list[int] = []
        prod_lat: list[float] = []
        t0 = time.perf_counter()
        for i in range(shape.producer_events):
            one: list[int] = []
            one_lat: list[float] = []
            _publish_batch(1, one, one_lat)
            prod_collect.extend(one)
            prod_lat.extend(one_lat)
        prod_wall = time.perf_counter() - t0
        seqs.extend(prod_collect)
        producer = summarise(prod_lat, prod_wall, shape.producer_events)

        # Give subscribers a breath to drain, then count.
        time.sleep(0.3)
        sub_stop.set()
        for t in sub_threads:
            t.join(timeout=2.0)
        for s in sub_sockets:
            try:
                s.close()
            except OSError:
                pass

        total = WARMUP_EVENTS + shape.events + shape.producer_events

        # Correctness: contiguous seqs, feed lines, ring.
        if sorted(seqs) != list(range(1, total + 1)):
            errors.append(
                f"seqs not contiguous: got {len(seqs)} acks, "
                f"expected 1..{total}")
        feed_lines = 0
        feed_bytes = 0
        if feed_path.exists():
            raw = feed_path.read_bytes()
            feed_bytes = len(raw)
            feed_lines = raw.count(b"\n")
        if feed_lines != total:
            errors.append(f"feed holds {feed_lines} lines, expected {total}")
        ring_n = None
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                s.connect(str(sock_path))
                _send_line(s, {"nerve_type": "recent", "count": 1000})
                resp = _read_line(s, bytearray())
                ring_n = resp.get("count")
        except OSError as exc:
            errors.append(f"recent probe failed: {exc}")
        expected_ring = min(total, RING_SIZE)
        if ring_n != expected_ring:
            errors.append(
                f"ring answers {ring_n} events, expected {expected_ring}")
        for idx, got in enumerate(sub_received):
            # A subscriber hears everything published after
            # it subscribed; the warmup raced its hello, so
            # the honest window is timed+producer (floor) to
            # everything (ceiling).
            if not (total - WARMUP_EVENTS <= got <= total):
                errors.append(
                    f"subscriber {idx} received {got}, expected "
                    f"{total - WARMUP_EVENTS}..{total}")

        # Hub peak RSS (VmHWM of the hub process itself).
        rss_mib = None
        try:
            for line in Path(f"/proc/{proc.pid}/status").read_text().splitlines():
                if line.startswith("VmHWM:"):
                    rss_mib = round(int(line.split()[1]) / 1024.0, 1)
        except OSError as exc:
            errors.append(f"hub RSS unread: {exc}")

        return {
            "profile": shape.name,
            "shape": {
                "cpus": shape.cpus,
                "publishers": shape.publishers,
                "subscribers": shape.subscribers,
                "events": shape.events,
                "producer_events": shape.producer_events,
                "warmup_events": WARMUP_EVENTS,
            },
            "persistent": timed,
            "producer": producer,
            "published_total": total,
            "feed_lines": feed_lines,
            "feed_bytes": feed_bytes,
            "feed_bytes_per_event": round(feed_bytes / feed_lines, 1)
            if feed_lines
            else None,
            "ring_recent_count": ring_n,
            "subscriber_received": sub_received,
            "hub_peak_rss_mib": rss_mib,
            "errors": errors,
        }
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5.0)


def run_all(workdir: Path, names: list[str] | None = None) -> dict:
    shapes = [s for s in PROFILES if names is None or s.name in names]
    return {
        "slice": "E-075",
        "hub": str(HUB),
        "python": sys.version.split()[0],
        "profiles": [measure_profile(s, workdir) for s in shapes],
    }


def main(argv: list[str]) -> int:
    import tempfile

    names = argv[1:] or None
    with tempfile.TemporaryDirectory(prefix="ember-e075-") as tmp:
        report = run_all(Path(tmp), names)
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if all(not p["errors"] for p in report["profiles"]) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
