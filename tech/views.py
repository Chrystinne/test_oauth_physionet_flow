from django.shortcuts import render, redirect
import secrets
import requests
from django.conf import settings
from django.http import JsonResponse
import base64
import hashlib
from urllib.parse import urlencode
import time

def index(request):
    return render(request, 'index.html')

# PhysioNet OAuth2 flow
def physionet_login(request):
    """Redireciona para o PhysioNet para autorizar o app."""
    state = secrets.token_urlsafe(16)
    code_verifier, code_challenge = generate_pkce_pair()

    request.session["physionet_oauth_state"] = state
    request.session["physionet_code_verifier"] = code_verifier

    params = {
        "response_type": "code",
        "client_id": settings.PHYSIONET_CLIENT_ID,
        "redirect_uri": settings.PHYSIONET_REDIRECT_URI,
        "scope": "credentialing:read",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = f"{settings.PHYSIONET_BASE_URL}/oauth/authorize/?{urlencode(params)}"
    return redirect(auth_url)


def physionet_callback(request):
    if request.GET.get("error"):
        return JsonResponse(
            {"error": request.GET.get("error"), "description": request.GET.get("error_description")},
            status=400,
        )

    returned_state = request.GET.get("state", "")
    saved_state = request.session.pop("physionet_oauth_state", "")
    if returned_state != saved_state:
        return JsonResponse({"error": "Invalid state"}, status=400)

    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "Missing authorization code"}, status=400)

    code_verifier = request.session.pop("physionet_code_verifier", None)
    if not code_verifier:
        return JsonResponse({"error": "Missing PKCE code verifier"}, status=400)

    token_response = requests.post(
        f"{settings.PHYSIONET_BASE_URL}/oauth/token/",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.PHYSIONET_REDIRECT_URI,
            "client_id": settings.PHYSIONET_CLIENT_ID,
            "client_secret": settings.PHYSIONET_CLIENT_SECRET,
            "code_verifier": code_verifier,
        },
    )

    if token_response.status_code != 200:
        return JsonResponse({"error": "Token exchange failed", "detail": token_response.text}, status=400)

    token_data = token_response.json()

    # Save access_token, refresh_token, and access token expiration time
    request.session["physionet_access_token"] = token_data["access_token"]
    request.session["physionet_refresh_token"] = token_data["refresh_token"]
    request.session["physionet_token_expires_at"] = time.time() + token_data["expires_in"]

    return redirect("/physionet/dataset/")


def physionet_dataset_check(request):
    """Chama o endpoint dataset-access do PhysioNet com o token."""
    token = request.session.get('physionet_access_token')
    if not token:
        return redirect('/physionet/login/')

    # slug    = request.GET.get('slug', 'mimic-iv')
    # version = request.GET.get('version', '3.1')

    slug    = request.GET.get('slug', 'demoeicu')
    version = request.GET.get('version', '2.0.0')

    # slug    = request.GET.get('slug', 'demoselfmanaged')
    # version = request.GET.get('version', '1.0.0')

    response = requests.get(
        f"{settings.PHYSIONET_BASE_URL}/oauth/dataset-access/",
        params={'slug': slug, 'version': version},
        headers={'Authorization': f'Bearer {token}'},
    )

    return JsonResponse({
        'status_code': response.status_code,
        'body':        response.json() if response.status_code == 200 else response.text,
    })


def generate_pkce_pair():
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        )
        .decode()
        .rstrip("=")
    )
    return code_verifier, code_challenge
