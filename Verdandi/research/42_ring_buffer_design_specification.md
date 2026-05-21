# Ring Buffer Design Specification
## 256-Event Circular Buffer for Fast Recent Event Access

---

## 1. Purpose

The ring buffer holds the last 256 nerve impulses in memory for O(1) access. This eliminates the need to read the feed file for recent events.

## 2. Design

```python
class RingBuffer:
    def __init__(self, capacity=256):
        self.capacity = capacity
        self.buffer = [None] * capacity
        self.head = 0
        self.size = 0
    
    def add(self, event):
        self.buffer[self.head] = event
        self.head = (self.head + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)
    
    def recent(self, n=10):
        events = []
        for i in range(min(n, self.size)):
            idx = (self.head - 1 - i) % self.capacity
            events.append(self.buffer[idx])
        return events
```

## 3. Thread Safety

The ring buffer is protected by the hub's file lock. All writes go through `_hub_write()` which acquires the lock before modifying the buffer.

---

*Created by the Mythic Engineering Forge for VERÐANDI — The Norn of Becoming*
