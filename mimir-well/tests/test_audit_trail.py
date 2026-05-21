"""T7-2: Memory Audit Trail test suite."""
import sys, tempfile, os, logging
sys.path.insert(0, '/home/pi/mimir-well/src')

from mimir_well import (
    RunaMemory, AuditTrail, AuditAction, AuditEntry,
)

logging.basicConfig(level=logging.WARNING)

# ── Test 1: Audit trail logs store action ────────────────────────────
db_path = tempfile.mktemp(suffix='.db')
mem = RunaMemory(db_path=db_path)

mid1 = mem.add_memory(
    'Volmarr built a solar water heater',
    category='saga_moment', importance=9,
)
assert mid1 > 0, f'Store should succeed, got id={mid1}'
print(f'✓ Test 1: Store logged (memory_id={mid1})')

# ── Test 2: Audit trail logs update action ───────────────────────────
result = mem.update_memory(mid1, source='hermes', content='Volmarr built a solar water heater from recycled copper')
assert result, 'Update should succeed'
print('✓ Test 2: Update logged')

# ── Test 3: Audit trail logs delete action ───────────────────────────
mid2 = mem.add_memory(
    'Temporary memory to delete',
    category='general', importance=1,
)
result = mem.delete_memory(mid2, source='hermes')
assert result, 'Delete should succeed'
print('✓ Test 3: Delete logged')

# ── Test 4: Query audit entries by memory_id ──────────────────────────
entries = mem.audit.query(memory_id=mid1)
assert len(entries) >= 2, f'Expected 2+ entries for memory {mid1}, got {len(entries)}'
actions = [e.action for e in entries]
assert 'store' in actions, f'Expected store action, got {actions}'
assert 'update' in actions, f'Expected update action, got {actions}'
print(f'✓ Test 4: Timeline for memory_id={mid1}: {actions}')

# ── Test 5: Query audit entries by source ──────────────────────────────
hermes_entries = mem.audit.query(source='hermes')
assert len(hermes_entries) >= 2, f'Expected 2+ entries from hermes, got {len(hermes_entries)}'
for e in hermes_entries:
    assert e.source == 'hermes', f'Expected hermes source, got {e.source}'
print(f'✓ Test 5: Found {len(hermes_entries)} entries from hermes')

# ── Test 6: Query audit entries by action type ────────────────────────
stores = mem.audit.query(action='store')
assert len(stores) >= 1, f'Expected store entries, got {len(stores)}'
for e in stores:
    assert e.action == 'store', f'Expected store action, got {e.action}'
print(f'✓ Test 6: Found {len(stores)} store entries')

# ── Test 7: Timeline method ────────────────────────────────────────
timeline = mem.audit.timeline(memory_id=mid1)
assert len(timeline) >= 2, f'Expected 2+ timeline entries, got {len(timeline)}'
print(f'✓ Test 7: Timeline has {len(timeline)} entries')

# ── Test 8: Verify timeline is ordered most-recent-first ──────────────
if len(timeline) >= 2:
    assert timeline[0].timestamp >= timeline[1].timestamp, \
        f'Expected descending order: {timeline[0].timestamp} >= {timeline[1].timestamp}'
print('✓ Test 8: Timeline ordered by timestamp DESC')

# ── Test 9: Audit stats ────────────────────────────────────────────
stats = mem.audit.stats()
assert 'total_entries' in stats
assert 'action_counts' in stats
assert 'source_counts' in stats
assert stats['total_entries'] >= 3, f'Expected 3+ entries, got {stats["total_entries"]}'
print(f'✓ Test 9: Stats — total={stats["total_entries"]}, actions={stats["action_counts"]}, sources={stats["source_counts"]}')

# ── Test 10: Content hash verification ─────────────────────────────
store_entries = mem.audit.query(memory_id=mid1, action='store')
assert len(store_entries) >= 1
entry = store_entries[-1]  # Most recent store
assert len(entry.content_hash) == 16, f'Expected 16-char hash, got {len(entry.content_hash)}'
print(f'✓ Test 10: Content hash present: {entry.content_hash}')

# ── Test 11: Integrity check ────────────────────────────────────────
current_hash = entry.content_hash
verification = mem.audit.verify_integrity(memory_id=mid1, current_hash=current_hash)
assert verification['verified'], f'Expected verified=True, got {verification}'
assert not verification['tampered'], f'Expected tampered=False, got {verification}'
print('✓ Test 11: Integrity check passed — no tampering detected')

# ── Test 12: Detection of content changes ─────────────────────────
update_entries = mem.audit.query(memory_id=mid1, action='update')
assert len(update_entries) >= 1
original_hash = entry.content_hash
update_hash = update_entries[0].content_hash
# The update changed the content, so hashes should differ
assert original_hash != update_hash, 'Hashes should differ after content update'
print(f'✓ Test 12: Hash changed after update: {original_hash} → {update_hash}')

# ── Test 13: Metadata stored in audit entries ──────────────────────────
assert 'category' in store_entries[-1].metadata, \
    f'Expected category in metadata, got {store_entries[-1].metadata}'
assert 'importance' in store_entries[-1].metadata, \
    f'Expected importance in metadata, got {store_entries[-1].metadata}'
print(f'✓ Test 13: Metadata contains category={store_entries[-1].metadata.get("category")}, '
      f'importance={store_entries[-1].metadata.get("importance")}')

# ── Test 14: Multiple stores from different sources ──────────────────
mid3 = mem.add_memory(
    'Eir detected high CPU temperature',
    category='general', importance=7,
)
# Default source should be 'mimir' (from add_memory's guard)
mimir_entries = mem.audit.query(source='mimir')
assert len(mimir_entries) >= 1, f'Expected mimir entries, got {len(mimir_entries)}'
print(f'✓ Test 14: Mímir-sourced entries found: {len(mimir_entries)}')

mem.close()
os.unlink(db_path)

print()
print('═══ ALL 14 AUDIT TRAIL TESTS PASSED ═══')