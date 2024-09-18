from hexon.core.logger import Logger


def test_logger():
    assert Logger.debug("Debug message") is None
    assert Logger.info("Info message") is None
    assert Logger.warning("Warning message") is None
    assert Logger.error("Error message") is None
    assert Logger.critical("Critical message") is None
