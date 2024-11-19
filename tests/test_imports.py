def test_level1_import():
    try:
        import bibt  # noqa: F401
    except ImportError:
        assert False
    assert True


def test_level2_import():
    try:
        from bibt import slack  # noqa: F401
    except ImportError:
        assert False
    assert True


def test_level3_import():
    try:
        from bibt.slack import post_message  # noqa: F401
    except ImportError:
        assert False
    assert True
