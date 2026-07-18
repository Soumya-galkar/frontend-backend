import os
import requests

from utils.superbase_client import supabase

BUCKET_NAME = "industrial-documents"


def download_file(storage_path: str):
    # Remove bucket name if someone accidentally sends it
    storage_path = storage_path.replace(f"{BUCKET_NAME}/", "")

    print("Bucket:", BUCKET_NAME)
    print("Storage path:", repr(storage_path))

    signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(
        storage_path,
        60
    )

    print(signed)

    signed_url = signed["signedURL"]

    response = requests.get(signed_url)

    os.makedirs("temp", exist_ok=True)

    local_path = os.path.join("temp", os.path.basename(storage_path))

    with open(local_path, "wb") as f:
        f.write(response.content)

    return local_path