# 🧪 Testing Guide

## Running Tests

```bash
# Run all 489 tests
python3 -m pytest tests/ -v

# Run specific test modules
python3 -m pytest tests/test_heartbeat.py -v           # Core daemon tests
python3 -m pytest tests/test_heartbeat_checks.py -v     # Check module tests
python3 -m pytest tests/test_heartbeat_actions.py -v    # Action module tests
python3 -m pytest tests/test_heartbeat_integration.py -v # Integration tests

# Run with coverage
python3 -m pytest tests/ --cov=heartbeat --cov-report=html

# Run specific test by name
python3 -m pytest tests/test_heartbeat.py::test_pulse_advances_count -v
```

## Test Architecture

```
tests/
├── test_heartbeat.py              # 264 core tests
├── test_heartbeat_checks.py       # 149 check tests
├── test_heartbeat_actions.py      # 75 action tests (includes reactor)
├── test_heartbeat_integration.py  # 49 integration tests
├── test_nervous_system.py         # Nerve hub tests
├── test_reactor.py                # Reactor-specific tests
├── test_conversation_logger.py     # Conversation log tests
└── test_context_injector.py        # Context injection tests
```

## Writing New Tests

### Test Structure

Follow the existing pattern:

```python
import pytest
from unittest.mock import patch, MagicMock
from heartbeat.core import HeartbeatDaemon, CircuitBreaker, HealthScore
from heartbeat.checks.base import CheckResult, CheckSeverity

class TestMyNewFeature:
    """Test my new feature."""
    
    def test_basic_functionality(self):
        """It should do the basic thing."""
        # Arrange
        breaker = CircuitBreaker(failure_threshold=3, name="test")
        
        # Act
        result = breaker.allow()
        
        # Assert
        assert result is True
        assert breaker.stats["state"] == "closed"
    
    def test_failure_threshold(self):
        """It should open after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3, name="test")
        
        for _ in range(3):
            breaker.record_failure()
        
        assert breaker.state == "open"
        assert breaker.allow() is False  # Circuit is open
```

### Testing Checks

```python
class TestMyCheck:
    @pytest.fixture
    def config(self):
        return HeartbeatConfig()
    
    def test_check_returns_ok_when_healthy(self, config, tmp_path):
        """Check should return OK when system is healthy."""
        check = MyCheck(config)
        result = check.check()
        assert result.severity == CheckSeverity.OK
```

### Testing Actions

```python
class TestMyAction:
    def test_dry_run_does_nothing(self):
        """Dry run should not execute any real changes."""
        action = MyAction()
        ctx = ActionContext(trigger_severity=CheckSeverity.CRITICAL)
        result = action.dry_run(ctx)
        assert result.severity == ActionSeverity.DRY_RUN
```

### Test Configuration

Tests use temporary directories and mock configs:

```python
@pytest.fixture
def temp_config(self, tmp_path):
    """Create a config with temporary paths."""
    config = HeartbeatConfig()
    config._data["heartbeat"]["interval_seconds"] = 1
    config._data["paths"]["state_dir"] = str(tmp_path / "state")
    return config
```

## Continuous Integration

```bash
# Quick check (core tests only, ~3 seconds)
python3 -m pytest tests/test_heartbeat.py -q

# Full suite (all 489 tests, ~30 seconds)
python3 -m pytest tests/ -q

# Integration only (end-to-end, ~5 seconds)
python3 -m pytest tests/test_heartbeat_integration.py -v
```