from __future__ import annotations

import trio
import time

def usable_decode(text: bytes) -> str:
    """Decode the text so it can be used.
        vars:
            :@param text: a string of bytes that needs decoding
            :@return: string of decoded bytes (text)

    """
    try:
        decoded_text: str
        decoded_text = text.decode("utf8")
    except (UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
        try:
            decoded_text = text.decode("latin1")
        except (UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
            try:
                det = detect(text)
                decoded_text = text.decode(det['encoding'], errors="replace")
            except (UnicodeDecodeError, UnicodeError, UnicodeTranslateError):
                return ''
    return decoded_text

async def bounce_server_listen(cs_before_login: trio.SSLStream) -> None:
        while True:
            try:
                with trio.fail_after(40):
                    line = await cs_before_login.readline()
                    print('read : ' + line)
            except trio.TooSlowError as exc:
                print('Login too Slow')

