from unittest.mock import Mock, MagicMock
import pytest

@pytest.fixture
def wpilib_extensions():
    from yeti import wpilib_extensions
    return wpilib_extensions

def test_referee(yeti, wpilib_extensions):
    fake_mod = yeti.HookServer()
    referee = yeti.wpilib_extensions.Referee(fake_mod)
    freeable1 = Mock()
    freeable2 = Mock()
    freeable1.free = MagicMock()
    freeable2.free = MagicMock()
    referee.watch(freeable1)
    referee.watch(freeable2)
    fake_mod.call_hook("deinit")
    freeable1.free.assert_called_with()
