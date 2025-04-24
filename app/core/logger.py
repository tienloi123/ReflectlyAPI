import base64
import binascii
import http
import logging
import os
import sys
import time
from copy import copy
from datetime import datetime

import click

TRACE_LOG_LEVEL = 5


class ColourizedFormatter(logging.Formatter):
    """
    A custom log formatter class that:
    * Outputs the LOG_LEVEL with an appropriate color.
    * If a log call includes an `extras={"color_message": ...}` it will be used
      for formatting the output, instead of the plain text message.
    """

    level_name_colors = {
        TRACE_LOG_LEVEL: lambda level_name: click.style(str(level_name), fg="blue"),
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(self, fmt=None, datefmt=None, style="%", use_colors=None):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = sys.stdout.isatty()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name, level_no):
        default = lambda level_name: str(level_name)
        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self):
        return True

    def formatMessage(self, record):
        recordcopy = copy(record)
        levelname = recordcopy.levelname
        seperator = " " * (8 - len(recordcopy.levelname))
        if self.use_colors:
            levelname = self.color_level_name(levelname, recordcopy.levelno)
            if "color_message" in recordcopy.__dict__:
                recordcopy.msg = recordcopy.__dict__["color_message"]
                recordcopy.__dict__["message"] = recordcopy.getMessage()
        recordcopy.__dict__["levelprefix"] = levelname + ":" + seperator
        return super().formatMessage(recordcopy)


class DefaultFormatter(ColourizedFormatter):
    def should_use_colors(self):
        return sys.stderr.isatty()


class AccessFormatter(ColourizedFormatter):
    status_code_colours = {
        1: lambda code: click.style(str(code), fg="bright_white"),
        2: lambda code: click.style(str(code), fg="green"),
        3: lambda code: click.style(str(code), fg="yellow"),
        4: lambda code: click.style(str(code), fg="red"),
        5: lambda code: click.style(str(code), fg="bright_red"),
    }

    def get_client_addr(self, scope):
        client = scope.get("client")
        if not client:
            return ""
        return "%s:%d" % (client[0], client[1])

    def get_path(self, scope):
        return scope.get("root_path", "") + scope["path"]

    def get_full_path(self, scope):
        path = scope.get("root_path", "") + scope["path"]
        query_string = scope.get("query_string", b"").decode("ascii")
        if query_string:
            return path + "?" + query_string
        return path

    def get_status_code(self, record):
        status_code = record.__dict__["status_code"]
        try:
            status_phrase = http.HTTPStatus(status_code).phrase
        except ValueError:
            status_phrase = ""
        status_and_phrase = "%s %s" % (status_code, status_phrase)

        if self.use_colors:
            default = lambda code: status_and_phrase
            func = self.status_code_colours.get(status_code // 100, default)
            return func(status_and_phrase)
        return status_and_phrase

    def formatMessage(self, record):
        recordcopy = copy(record)
        scope = recordcopy.__dict__["scope"]
        method = scope["method"]
        path = self.get_path(scope)
        full_path = self.get_full_path(scope)
        client_addr = self.get_client_addr(scope)
        status_code = self.get_status_code(recordcopy)
        http_version = scope["http_version"]
        request_line = "%s %s HTTP/%s" % (method, full_path, http_version)
        if self.use_colors:
            request_line = click.style(request_line, bold=True)
        recordcopy.__dict__.update(
            {
                "method": method,
                "path": path,
                "full_path": full_path,
                "client_addr": client_addr,
                "request_line": request_line,
                "status_code": status_code,
                "http_version": http_version,
            }
        )
        return super().formatMessage(recordcopy)


class SafeAtoms(dict):

    def __init__(self, atoms):
        dict.__init__(self)
        for key, value in atoms.items():
            if isinstance(value, str):
                self[key] = value.replace('"', '\\"')
            else:
                self[key] = value

    def __getitem__(self, k):
        if k.startswith("{"):
            kl = k.lower()
            if kl in self:
                return super().__getitem__(kl)
            else:
                return "-"
        if k in self:
            return super().__getitem__(k)
        else:
            return '-'


class CustomFormatter(AccessFormatter):
    atoms_wrapper_class = SafeAtoms

    def now(self):
        """ return date in Apache Common Log Format """
        return time.strftime('[%d/%b/%Y:%H:%M:%S %z]')

    def _get_user(self, environ):
        user = None
        http_auth = environ.get("HTTP_AUTHORIZATION")
        if http_auth and http_auth.lower().startswith('basic'):
            auth = http_auth.split(" ", 1)
            if len(auth) == 2:
                try:
                    # b64decode doesn't accept unicode in Python < 3.3
                    # so we need to convert it to a byte string
                    auth = base64.b64decode(auth[1].strip().encode('utf-8'))
                    # b64decode returns a byte string
                    auth = auth.decode('utf-8')
                    auth = auth.split(":", 1)
                except (TypeError, binascii.Error, UnicodeDecodeError) as exc:
                    self.debug("Couldn't get username: %s", exc)
                    return user
                if len(auth) == 2:
                    user = auth[0]
        return user

    def atoms(self, environ, request_time, scope, statuscode, created):
        headers = dict(scope.get('headers', [('-', '-')]))
        response_headers = dict(scope.get('response_headers', [('-', '-')]))
        atoms = {
            'h': scope.get("client", ('-', ''))[0],
            'l': '-',
            's': statuscode,
            'u': self._get_user(environ) or '-',
            't': created,
            'm': str(scope.get("method", "-")),
            'U': scope.get("path", "-"),
            'q': scope.get("query_string", "-").decode("utf-8"),
            'H': str(scope.get("type", "-")),
            'f': headers.get(b"referer", b"-").decode("utf-8"),
            'a': headers.get(b"user-agent", b"-").decode("utf-8"),
            'x-session-id': headers.get(b"x-session-id", b"-").decode("utf-8"),
            'x-google-id': headers.get(b"x-google-id", b"-").decode("utf-8"),
            'x-server-time': response_headers.get(b"x-server-time", b"").decode("utf-8"),
            'p': "<%s>" % os.getpid()
        }

        return atoms

    def formatMessage(self, record):
        recordcopy = copy(record)
        scope = recordcopy.__dict__["scope"]
        safe_atoms = self.atoms_wrapper_class(
            self.atoms(os.environ, datetime.now(), scope, recordcopy.status_code, recordcopy.created)
        )
        recordcopy.__dict__.update(safe_atoms)

        return super().formatMessage(recordcopy)
