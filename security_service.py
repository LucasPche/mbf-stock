"""Serviços de segurança e validação independentes do servidor HTTP."""
import hashlib
import secrets

def validar_id(valor):
    try:
        numero = int(valor)
        if numero <= 0:
            return None
        return numero
    except (ValueError, TypeError, OverflowError):
        return None

def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000).hex()
    return f"{salt}${digest}"


def check_password(password, stored):
    if not isinstance(stored, str) or "$" not in stored:
        return False
    salt, digest = stored.split("$", 1)
    return secrets.compare_digest(password_hash(password, salt).split("$", 1)[1], digest)


