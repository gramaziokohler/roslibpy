import pytest

from roslibpy import Header, Time

REF_FLOAT_SECS_TIME = 1610122759.677662


def test_time_from_sec_based_on_time_module():
    t = Time.from_sec(REF_FLOAT_SECS_TIME)
    assert t.secs == 1610122759
    assert t.nsecs == 677661895


def test_to_nsec():
    t = Time.from_sec(REF_FLOAT_SECS_TIME)
    assert t.to_nsec() == 1610122759677661895


def test_to_sec():
    t = Time.from_sec(REF_FLOAT_SECS_TIME)
    assert t.to_sec() == REF_FLOAT_SECS_TIME


def test_is_zero():
    assert Time(0, 0).is_zero()
    assert Time(1, 0).is_zero() is False


def test_header_ctor_supports_time():
    header = Header(seq=1, stamp=Time.from_sec(REF_FLOAT_SECS_TIME))
    assert header["stamp"]["secs"] == 1610122759
    assert header["stamp"]["secs"] == header["stamp"].secs
    assert header["stamp"].to_sec() == REF_FLOAT_SECS_TIME


def test_header_ctor_supports_dict():
    header = Header(seq=1, stamp=dict(secs=1610122759, nsecs=677661895))
    assert header["stamp"]["secs"] == 1610122759
    assert header["stamp"]["secs"] == header["stamp"].secs
    assert header["stamp"].to_sec() == REF_FLOAT_SECS_TIME


def test_time_accepts_only_ints():
    with pytest.raises(ValueError):
        Time(1.3, 1.0)
    with pytest.raises(ValueError):
        Time(100.0, 3.1)

    t = Time(110.0, 0.0)
    assert t.secs == 110
    assert t.nsecs == 0


def test_time_properties_are_readonly():
    t = Time.now()
    with pytest.raises(AttributeError):
        t.secs = 10
    with pytest.raises(AttributeError):
        t.nsecs = 10
