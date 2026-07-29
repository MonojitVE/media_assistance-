from fastapi import APIRouter, Depends, HTTPException, Request, Body
from pydantic import BaseModel
import google_auth_oauthlib.flow
import os
from app.config import settings
from app.gdrive_scanner import GDriveScanner

router = APIRouter(prefix="/drive", tags=["drive"])

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Simple in-memory store for PKCE state (safe for local single-user apps)
_oauth_state = {}

def get_flow():
    if not settings.client_id or not settings.client_secret:
        raise HTTPException(status_code=500, detail="Google client credentials not configured in environment")
        
    client_config = {
        "installed": {
            "client_id": settings.client_id,
            "project_id": "smart-media-assistant",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": settings.client_secret,
            "redirect_uris": [settings.google_redirect_uri]
        }
    }
    
    return google_auth_oauthlib.flow.Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=settings.google_redirect_uri
    )

@router.get("/auth/url")
def get_auth_url():
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    # Store the PKCE code_verifier generated during auth URL creation
    _oauth_state['code_verifier'] = flow.code_verifier
    return {"auth_url": authorization_url}

class TokenRequest(BaseModel):
    code: str

@router.post("/auth/token")
def exchange_token(req: TokenRequest):
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    flow = get_flow()
    
    # Restore the PKCE code_verifier from memory
    if 'code_verifier' in _oauth_state:
        flow.code_verifier = _oauth_state['code_verifier']
        
    try:
        flow.fetch_token(code=req.code)
        credentials = flow.credentials
        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

class ScanRequest(BaseModel):
    access_token: str
    refresh_token: str = None
    client_id: str = None
    client_secret: str = None
    token_uri: str = None

@router.post("/scan")
def scan_drive(req: ScanRequest):
    credentials_dict = {
        'token': req.access_token,
        'refresh_token': req.refresh_token,
        'client_id': req.client_id,
        'client_secret': req.client_secret,
        'token_uri': req.token_uri
    }
    
    scanner = GDriveScanner(credentials_dict)
    try:
        stats = scanner.scan_drive()
        return {"status": "success", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
