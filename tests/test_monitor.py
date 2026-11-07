import pytest
import io
from src.monitor import GetStatus, GetMemoryInfo, GetCPUInfo, GetCPUUsage


def test_NormalStatus():
    assert GetStatus(50) == "NORMAL"


def test_WarningStatus():
    assert GetStatus(80) == "WARNING"


def test_CriticalStatus():
    assert GetStatus(90) == "CRITICAL"


def test_BelowWarningThreshold():
    assert GetStatus(79) == "NORMAL"


def test_BelowCriticalThreshold():
    assert GetStatus(89) == "WARNING"


def test_InvalidText():
    with pytest.raises(TypeError):
        GetStatus("abc")


def test_InvalidNone():
    with pytest.raises(TypeError):
        GetStatus(None)


def test_NegativeValue():
    with pytest.raises(ValueError):
        GetStatus(-1)


def test_ValueAbove100():
    with pytest.raises(ValueError):
        GetStatus(101)


def test_ZeroPercent():
    assert GetStatus(0) == "NORMAL"


def test_OneHundredPercent():
    assert GetStatus(100) == "CRITICAL"


def test_MemoryInfoReadError(monkeypatch):
    def MockOpen(*args, **kwargs):
        raise OSError("Simulated file read error")

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetMemoryInfo() is None


def test_CPUInfoReadError(monkeypatch):
    def MockOpen(*args, **kwargs):
        raise OSError("Simulated file read error")

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetCPUInfo() is None


def test_CPUUsageFirstReadError(monkeypatch):
    def MockGetCPUInfo():
        return None

    monkeypatch.setattr("src.monitor.GetCPUInfo", MockGetCPUInfo)

    assert GetCPUUsage() is None


def test_CPUUsageSecondReadError(monkeypatch):
    Measurements = iter([
        [100, 20, 30, 40, 5, 0, 0, 0],
        None
    ])

    def MockGetCPUInfo():
        return next(Measurements)

    monkeypatch.setattr("src.monitor.GetCPUInfo", MockGetCPUInfo)
    monkeypatch.setattr("src.monitor.time.sleep", lambda _: None)

    assert GetCPUUsage() is None


def test_CPUUsageCalculation(monkeypatch):
    Measurements = iter([
        [100, 20, 30, 40, 10, 0, 0, 0],
        [200, 30, 40, 50, 20, 0, 0, 0]
    ])

    def MockGetCPUInfo():
        return next(Measurements)

    monkeypatch.setattr("src.monitor.GetCPUInfo", MockGetCPUInfo)
    monkeypatch.setattr("src.monitor.time.sleep", lambda _: None)

    assert GetCPUUsage() == pytest.approx(85.7142857)


def test_MemoryInfoSuccess(monkeypatch):
    MockMemoryInfo = "MemTotal: 8000000 kB\nMemAvailable: 2000000 kB\n"

    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: io.StringIO(MockMemoryInfo)
    )

    MemoryInfo = GetMemoryInfo()

    assert MemoryInfo["MemTotal"] == 8000000
    assert MemoryInfo["MemAvailable"] == 2000000


def test_CPUInfoSuccess(monkeypatch):
    MockCPUInfo = "cpu 100 20 30 40 5 6 7 8 0 0\n"

    monkeypatch.setattr(
        "builtins.open",
        lambda *args, **kwargs: io.StringIO(MockCPUInfo)
    )

    CPUInfo = GetCPUInfo()

    assert CPUInfo == [100, 20, 30, 40, 5, 6, 7, 8, 0, 0]


def test_CPUUsageZeroDifference(monkeypatch):
    Measurements = iter([
        [100, 20, 30, 40, 10, 0, 0, 0],
        [100, 20, 30, 40, 10, 0, 0, 0]
    ])

    def MockGetCPUInfo():
        return next(Measurements)

    monkeypatch.setattr("src.monitor.GetCPUInfo", MockGetCPUInfo)
    monkeypatch.setattr("src.monitor.time.sleep", lambda _: None)

    assert GetCPUUsage() == 0.0


def test_MemoryInfoInvalidValue(monkeypatch):
    def MockOpen(*args, **kwargs):
        return io.StringIO(
            "MemTotal: invalid kB\n"
            "MemAvailable: 2000000 kB\n"
        )

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetMemoryInfo() is None


def test_CPUInfoInvalidValue(monkeypatch):
    def MockOpen(*args, **kwargs):
        return io.StringIO("cpu invalid 20 30 40 5 6 7 8\n")

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetCPUInfo() is None


def test_CPUInfoIncompleteData(monkeypatch):
    def MockOpen(*args, **kwargs):
        return io.StringIO("cpu 100 20 30\n")

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetCPUInfo() is None


def test_MemoryInfoMissingValue(monkeypatch):
    def MockOpen(*args, **kwargs):
        return io.StringIO("MemAvailable: 2000000 kB\n")

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetMemoryInfo() is None


def test_MemoryInfoZeroTotal(monkeypatch):
    def MockOpen(*args, **kwargs):
        return io.StringIO(
            "MemTotal: 0 kB\n"
            "MemAvailable: 0 kB\n"
        )

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetMemoryInfo() is None


def test_MemoryInfoNegativeAvailable(monkeypatch):
    def MockOpen(*args, **kwargs):
        return io.StringIO(
            "MemTotal: 8000000 kB\n"
            "MemAvailable: -1 kB\n"
        )

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetMemoryInfo() is None


def test_MemoryInfoAvailableExceedsTotal(monkeypatch):
    def MockOpen(*args, **kwargs):
        return io.StringIO(
            "MemTotal: 8000000 kB\n"
            "MemAvailable: 9000000 kB\n"
        )

    monkeypatch.setattr("builtins.open", MockOpen)

    assert GetMemoryInfo() is None
