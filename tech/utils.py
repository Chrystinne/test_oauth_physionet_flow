import time, requests
from django.conf import settings

def get_valid_token(request):
    """
    Returns a valid access token, refreshing it if expired.
    Returns None if unable to refresh (user must log in again).
    """
    expires_at = request.session.get("physionet_token_expires_at", 0)
    access_token = request.session.get("physionet_access_token")

    # Refresh 60 seconds early to avoid edge cases
    if time.time() < expires_at - 60:
        return access_token

    # Token expired (or missing) — try to refresh
    refresh_token = request.session.get("physionet_refresh_token")
    if not refresh_token:
        return None

    response = requests.post(
        f"{settings.PHYSIONET_BASE_URL}/oauth/token/",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.PHYSIONET_CLIENT_ID,
            "client_secret": settings.PHYSIONET_CLIENT_SECRET,
        },
    )

    if response.status_code != 200:
        return None

    token_data = response.json()
    request.session["physionet_access_token"] = token_data["access_token"]
    request.session["physionet_refresh_token"] = token_data["refresh_token"]
    request.session["physionet_token_expires_at"] = time.time() + token_data["expires_in"]

    return token_data["access_token"]