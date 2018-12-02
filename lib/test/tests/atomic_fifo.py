from atomic import FIFO

def test_fifo():
    sz = 5
    f = FIFO(sz)
    for i in range(sz):
        f.put(i)
    assert not f.put("abc"), "write to full fifo succeeds"
    for i in range(sz):
        assert f.get() == i, "fifo returns wrong data"
    try:
        f.get()
        assert True, "reading from empty fifo does not raise error"
    except IndexError:
        pass