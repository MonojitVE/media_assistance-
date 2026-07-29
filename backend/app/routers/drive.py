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
    # Use credentials.json directly instead of hardcoding web/installed keys
    # This automatically supports the downloaded credentials.json structure.
    creds_path = os.path.join(os.path.dirname(__file__), '..', '..', 'credentials.json')
    if not os.path.exists(creds_path):
        raise HTTPException(status_code=500, detail="credentials.json not found in backend folder")
        
    return google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        creds_path,
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
