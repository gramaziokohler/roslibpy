from roslibpy import Param, Ros


def test_param_manipulation():
    ros = Ros("127.0.0.1", 9090)
    ros.run()

    param = Param(ros, "test_param")
    assert param.get() is None

    param.set("test_value")
    assert param.get() == "test_value"

    param.delete()
    assert param.get() is None

    ros.close()
