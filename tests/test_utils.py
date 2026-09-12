"""
离线单元测试（不依赖网络 / 浏览器）。
GitHub Actions 也可单独加一步：pytest tests/ -m "not browser"
"""
import os
import sys
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import (  # noqa: E402
    parse_cookie,
    mask_cookie,
    cookie_to_dict,
    human_delay,
)

from douyin_web import _split_for_typing  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch):
    """每个测试隔离环境变量，避免互相污染。"""
    monkeypatch.delenv("DOUYIN_COOKIE", raising=False)
    monkeypatch.delenv("TARGET_USER", raising=False)
    monkeypatch.delenv("MESSAGE_TEXT", raising=False)
    yield


def test_parse_cookie_strips_whitespace():
    assert parse_cookie("  a=1;\n b=2 ") == "a=1; b=2"


def test_cookie_to_dict():
    d = cookie_to_dict("k1=v1; k2=v2")
    assert d == {"k1": "v1", "k2": "v2"}


def test_mask_cookie_short():
    assert mask_cookie("short") == "***"


def test_mask_cookie_long():
    out = mask_cookie("abcdefgh12345678xyz")
    assert out.startswith("abcdefgh")
    assert out.endswith("678xyz")  # 前8 + ... + 后6


def test_split_for_typing():
    chunks = _split_for_typing("你好世界", size=2)
    assert chunks == ["你好", "世界"]


@pytest.mark.parametrize("a,b", [(0.5, 1.0), (1.0, 2.0)])
def test_human_delay_runs(a, b):
    t = time.time()
    human_delay(a, b)
    assert time.time() - t >= a - 0.05


def test_config_validate_requires_cookie():
    """没有 DOUYIN_COOKIE 时 validate 应报错；导入本身不报错。"""
    from config import config
    with pytest.raises(RuntimeError):
        config.validate()


def test_config_validate_passes_with_env(monkeypatch):
    from config import config
    monkeypatch.setenv("DOUYIN_COOKIE", "x=1")
    monkeypatch.setenv("TARGET_USER", "http://example.com")
    monkeypatch.setenv("MESSAGE_TEXT", "hi")
    config.validate()  # 不应抛异常
