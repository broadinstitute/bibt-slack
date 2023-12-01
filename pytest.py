def test(capsys):
    with capsys.disabled():
        cf.main(pubsub, mock_context)
    return
