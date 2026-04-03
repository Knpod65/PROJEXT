"""
cmu_sso.py — CMU SSO OAuth2 stub
รอ client_id + client_secret จาก OIT

เมื่อมี CMU_SSO_CLIENT_ID env var:
  GET /api/auth/sso/login  → redirect ไป CMU OAuth
  GET /api/auth/sso/callback → รับ code → get user info → login

ตอนนี้: endpoints มีแต่ return 503 "SSO not configured"
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

router = APIRouter()

SSO_CLIENT_ID     = os.getenv("CMU_SSO_CLIENT_ID", "")
SSO_CLIENT_SECRET = os.getenv("CMU_SSO_CLIENT_SECRET", "")
SSO_REDIRECT_URI  = os.getenv("CMU_SSO_REDIRECT_URI", "")
SSO_ENABLED       = bool(SSO_CLIENT_ID and SSO_CLIENT_SECRET)

CMU_AUTH_URL  = "https://oauth.cmu.ac.th/v1/Authorize.aspx"
CMU_TOKEN_URL = "https://oauth.cmu.ac.th/v1/GetToken.aspx"
CMU_USER_URL  = "https://misapi.cmu.ac.th/cmuitaccount/v1/api/cmuitaccount/basicinfo"


@router.get("/login")
def sso_login():
    """Redirect ไป CMU OAuth login page"""
    if not SSO_ENABLED:
        raise HTTPException(503, "CMU SSO ยังไม่ได้ตั้งค่า — ติดต่อ admin")
    params = (
        f"?response_type=code"
        f"&client_id={SSO_CLIENT_ID}"
        f"&redirect_uri={SSO_REDIRECT_URI}"
        f"&scope=cmuitaccount.basicinfo"
        f"&state=ems_login"
    )
    return RedirectResponse(CMU_AUTH_URL + params)


@router.get("/callback")
async def sso_callback(code: str = "", state: str = ""):
    """รับ OAuth code → exchange token → get user → login"""
    if not SSO_ENABLED:
        raise HTTPException(503, "CMU SSO ยังไม่ได้ตั้งค่า")
    # TODO: implement when credentials available
    # 1. POST CMU_TOKEN_URL with code + client credentials
    # 2. GET CMU_USER_URL with access_token
    # 3. map CMU itaccount email → User in DB
    # 4. create JWT token → redirect frontend
    raise HTTPException(501, "SSO callback — pending credentials from OIT")
