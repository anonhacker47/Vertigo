from api import ma

class TokenSchema(ma.Schema):
    class Meta:
        ordered = True

    access_token = ma.String(required=True)
    refresh_token = ma.String()
