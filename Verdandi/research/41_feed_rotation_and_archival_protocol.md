# Feed Rotation and Archival Protocol
## Preserving the Chronicle of Becoming

---

## 1. Rotation Criteria

The nerve feed (`nerve_feed.jsonl`) rotates when it reaches 10MB. Rotated feeds are gzip-compressed and stored in `~/.hermes/state/archive/`.

## 2. Archival Format

```json
{
  "rotation_number": 42,
  "rotated_at": "2026-05-10T16:30:00Z",
  "original_size_bytes": 10485760,
  "compressed_size_bytes": 1048576,
  "event_count": 15000,
  "oldest_event": "2026-05-10T00:00:00Z",
  "newest_event": "2026-05-10T16:30:00Z"
}
```

## 3. Retention Policy

- Live feed: current, up to 10MB
- Recent archives: last 7 days, kept on disk
- Deep archives: older than 7 days, compressed and indexed in Mímir's Well

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
