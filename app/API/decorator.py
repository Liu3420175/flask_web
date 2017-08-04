from functools import wraps
from flask import request, Response


def check_http_auth(username, password):
    """
    检查HTTP_AUTHORIZATION的用户名机密码
    """
    return username == 'abcdefg' and password == '!@#123456'  # 该用户名及密码可以随便设置


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Bodaboda"'})


def http_basic_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_http_auth(auth.username, auth.password):
            return authenticate()
        return func(*args, **kwargs)

    return decorated
