# token_gen.py

from itsdangerous import URLSafeTimedSerializer


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer("secret-key-goes-here")
    return serializer.dumps(email, salt="my_precious_two")


def confirm_token(token, expiration=18000):
    serializer = URLSafeTimedSerializer("secret-key-goes-here")
    try:
        email = serializer.loads(token, salt="my_precious_two", max_age=expiration)
    except:
        return False
    return email


def generate_email_token(email):
    serializer = URLSafeTimedSerializer("secret-key-goes-here")
    return serializer.dumps(email, salt="my_precious_three")


def confirm_email_token(token, expiration=18000):
    serializer = URLSafeTimedSerializer("secret-key-goes-here")
    try:
        email = serializer.loads(token, salt="my_precious_three", max_age=expiration)
    except:
        return False
    return email
