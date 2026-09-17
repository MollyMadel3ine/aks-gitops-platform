"""
FastAPI service — Phase 4: zero secrets.

The app authenticates to Key Vault and Blob Storage as its managed
identity via DefaultAzureCredential. There are no connection strings,
keys, or passwords anywhere: not in code, not in environment
variables, not in Terraform state for this app's access.

/health   - liveness + runtime metadata (unchanged contract)
/identity - the Phase 4 proof: reads a secret from Key Vault and
            increments a visit counter blob in Storage, reporting
            both — all as the managed identity.
"""

import os
import socket
from datetime import datetime, timezone

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="container-demo")

ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "local")
IMAGE_TAG = os.environ.get("IMAGE_TAG", "dev")
KEY_VAULT_URI = os.environ.get("KEY_VAULT_URI", "")
STORAGE_ACCOUNT_URL = os.environ.get("STORAGE_ACCOUNT_URL", "")

STARTED_AT = datetime.now(timezone.utc).isoformat()

# One credential for everything; picks up the user-assigned identity
# via AZURE_CLIENT_ID in Azure, and falls back to az-cli auth locally.
credential = DefaultAzureCredential()


@app.get("/")
def root():
    return {
        "app": "container-demo",
        "environment": ENVIRONMENT,
        "message": "Containerized IaC demo - /health for liveness, /identity for the zero-secrets proof",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "image_tag": IMAGE_TAG,
        "hostname": socket.gethostname(),
        "started_at": STARTED_AT,
    }


@app.get("/identity")
def identity():
    """Prove identity-based access: read a KV secret, bump a blob counter."""
    result = {"environment": ENVIRONMENT, "auth": "managed identity (no secrets configured)"}

    try:
        # ---- Key Vault: read the demo secret ----
        kv = SecretClient(vault_url=KEY_VAULT_URI, credential=credential)
        secret = kv.get_secret("demo-message")
        result["key_vault"] = {"status": "ok", "demo_message": secret.value}

        # ---- Storage: increment a visit counter blob ----
        blob_service = BlobServiceClient(account_url=STORAGE_ACCOUNT_URL, credential=credential)
        blob = blob_service.get_blob_client(container="visits", blob="counter.txt")
        try:
            count = int(blob.download_blob().readall().decode()) + 1
        except Exception:
            count = 1  # first visit: blob doesn't exist yet
        blob.upload_blob(str(count), overwrite=True)
        result["storage"] = {"status": "ok", "visit_count": count}

        return result
    except Exception as exc:
        result["error"] = str(exc)
        return JSONResponse(status_code=503, content=result)