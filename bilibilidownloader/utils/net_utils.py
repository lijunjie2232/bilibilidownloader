import ctypes
import importlib
import inspect
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from email.utils import decode_rfc2231
from functools import wraps
from pathlib import Path
from time import localtime, sleep, time_ns
from urllib.parse import parse_qs, unquote, urlparse

import curl_cffi
from bilibilicore.config import Config
from loguru import logger
from PySide6.QtCore import QOperatingSystemVersion, Qt, QUrl
from PySide6.QtGui import QDesktopServices

plugins = []
cfg = Config()


def isGreaterEqualWin10():
    """determine if the Windows version ≥ Win10"""
    cv = QOperatingSystemVersion.current()
    return sys.platform == "win32" and cv.majorVersion() >= 10


def isLessThanWin10():
    """determine if the Windows version < Win10"""
    cv = QOperatingSystemVersion.current()
    return sys.platform == "win32" and cv.majorVersion() < 10


def isGreaterEqualWin11():
    """determine if the windows version ≥ Win11"""
    return isGreaterEqualWin10() and sys.getwindowsversion().build >= 22000


def isAbleToShowToast():
    return (sys.platform == "win32" and sys.getwindowsversion().build >= 10240) or True


def getSystemProxy():
    if sys.platform == "win32":
        try:
            import winreg

            # 打开 Windows 注册表项
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            )

            # 获取代理开关状态
            proxy_enable, _ = winreg.QueryValueEx(key, "ProxyEnable")

            if proxy_enable:
                # 获取代理地址和端口号
                proxy_server, _ = winreg.QueryValueEx(key, "ProxyServer")
                return "http://" + proxy_server
            else:
                return None

        except Exception as e:
            logger.error(f"Cannot get Windows proxy server：{e}")
            return None

    elif sys.platform == "linux":  # 读取 Linux 系统代理
        try:
            return os.environ.get("http_proxy")
        except Exception as e:
            logger.error(f"Cannot get Linux proxy server：{e}")
            return None

    elif sys.platform == "darwin":
        import SystemConfiguration

        _ = SystemConfiguration.SCDynamicStoreCopyProxies(None)

        if _.get("SOCKSEnable", 0):
            return f"socks5://{_.get('SOCKSProxy')}:{_.get('SOCKSPort')}"
        elif _.get("HTTPEnable", 0):
            return f"http://{_.get('HTTPProxy')}:{_.get('HTTPPort')}"
        else:
            return None
    return None


def getProxy():
    if not cfg.network.use_proxy:
        return None
    elif cfg.network.sys_proxy:
        return getSystemProxy()
    else:
        return f"{cfg.network.proxy_url}"


def getReadableSize(size):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    K = 1024.0
    while size >= K:
        size = size / K
        unit_index += 1
    return "%.2f %s" % (size, units[unit_index])


def retry(retries: int = 3, delay: float = 0.1, handleFunction: callable = None):
    """
    是装饰器。函数执行失败时，重试

    :param retries: 最大重试的次数
    :param delay: 每次重试的间隔时间，单位 秒
    :param handleFunction: 处理函数，用来处理异常
    :return:
    """

    # 校验重试的参数，参数值不正确时使用默认参数
    if retries < 1 or delay <= 0:
        retries = 3
        delay = 1

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries + 1):  # 第一次正常执行不算重试次数，所以 retries+1
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # 检查重试次数
                    if i == retries:
                        logger.error(
                            f'Error: {repr(e)}! "{func.__name__}()" 执行失败，已重试{retries}次.'
                        )
                        try:
                            handleFunction(e)
                        finally:
                            break
                    else:
                        logger.warning(
                            f'Error: {repr(e)}! "{func.__name__}()"执行失败，将在{delay}秒后第[{i+1}/{retries}]次重试...'
                        )
                        sleep(delay)

        return wrapper

    return decorator


def openFile(fileResolve):
    """
    打开文件

    :param fileResolve: 文件路径
    """
    QDesktopServices.openUrl(QUrl.fromLocalFile(fileResolve))


def getLocalTimeFromGithubApiTime(gmtTimeStr: str):
    # 解析 GMT 时间
    gmtTime = datetime.fromisoformat(gmtTimeStr.replace("Z", "+00:00"))

    # 获取本地时间的时区偏移量（秒）
    localTimeOffsetSec = localtime().tm_gmtoff

    # 创建带有本地时区偏移量的时区信息
    localTz = timezone(timedelta(seconds=localTimeOffsetSec))

    # 转换为系统本地时间
    localTime = gmtTime.astimezone(localTz)

    # 去掉时区信息
    localTimeNaive = localTime.replace(tzinfo=None)

    return localTimeNaive


def get_link(
    url: str,
    headers: dict,
    start: int = 0,
    cookies: dict = {},
    fileName: str = "download",
    verify: bool = cfg.network.ssl_verify,
    proxy: str = "",
    followRedirects: bool = True,
) -> tuple:
    if not proxy:
        proxy = getProxy()
    headers = headers.copy()
    headers["Range"] = f"bytes={start}-"  # 尝试发送范围请求
    # 使用 stream 请求获取响应, 反爬
    response = curl_cffi.get(
        url,
        stream=True,
        headers=headers,
        cookies=cookies,
        verify=verify,
        proxy=proxy,
        allow_redirects=followRedirects,
        impersonate="chrome",
    )
    response.raise_for_status()  # 如果状态码不是 2xx，抛出异常

    resp_head = response.headers

    url = str(response.url)

    continual_download = False

    total_size = 0

    content_size = 0

    # 获取文件大小, 判断是否可以分块下载
    # 状态码为206才是范围请求，200表示服务器拒绝了范围请求同时将发送整个文件
    if response.status_code == 206 and "content-range" in resp_head:
        # https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Reference/Headers/Content-Range
        _left, _char, right = resp_head["content-range"].rpartition("/")

        continual_download = True
        if (
            right
            and right != "*"
            and int(right) == int(resp_head["content-length"]) + start
        ):
            total_size = int(right)
            content_size = int(resp_head["content-length"])
            logger.info(
                f"content-range: {resp_head['content-range']}, fileSize: {total_size}, content-length: {resp_head['content-length']}"
            )
            logger.info("文件支持续传")

        elif "content-length" in resp_head:
            content_size = int(resp_head["content-length"])
            total_size = content_size + start
            logger.info("文件似乎支持续传，但无法获取文件大小, 尝试使用 content-length")

        else:
            total_size = 0
            logger.info("文件似乎支持续传，但无法获取文件大小")
    else:
        total_size = 0
        logger.info("文件不支持续传")

    response.close()
    return (
        url,
        fileName,
        total_size,
        content_size,
        continual_download,
        resp_head,
        headers,
    )


def bringWindowToTop(window):
    window.setWindowState(Qt.WindowActive)
    window.show()
    window.activateWindow()
    window.raise_()


if __name__ == "__main__":
    print(
        get_link(
            "https://download.gimp.org/gimp/v3.0/windows/gimp-3.0.4-setup.exe",
            {},
            start=357986,
        )
    )


def bytes_2_str(size: int, readable: bool = True, round: int = 2) -> str:
    """
    Convert bytes to human-readable string.

    Args:
        size: Size in bytes
        readable: If True, convert to KB, MB, GB, etc.
        round: Decimal places to round to

    Returns:
        Human-readable size string
    """
    if not readable:
        return f"{size} B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    K = 1024.0
    while size >= K and unit_index < len(units) - 1:
        size = size / K
        unit_index += 1
    return (f"%.{round}f %s") % (size, units[unit_index])
