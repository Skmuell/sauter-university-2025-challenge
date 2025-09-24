from google.cloud import storage  # type: ignore
from datetime import datetime
from typing import Optional
import shutil
import os

from google.cloud import storage  # type: ignore
from datetime import datetime
import os

def upload_folder_to_gcs(bucket_name: str, source_folder: str,package_name: str):
    """
    Upload all files from a local folder to a GCS bucket.
    Always uploads to 'ons/ear_diario_por_reservatorio/dt=<hoje>'.
    After uploading, clears the local folder.

    :param bucket_name: GCS bucket name
    :param source_folder: Path to the local folder
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Pasta destino com dt=hoje
    today_str = datetime.today().strftime("%Y-%m-%d")  # YYYY-MM-DD
    destination_folder = f"ons/{package_name}/dt={today_str}/"

    # Upload arquivos
    for root, _, files in os.walk(source_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, source_folder)
            blob_path = os.path.join(destination_folder, relative_path).replace("\\", "/")

            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)
            print(f"✅ Upload completed: {local_path} → gs://{bucket_name}/{blob_path}")

            # Remove arquivo local
            os.remove(local_path)

    # Clear local folder
    shutil.rmtree(source_folder)
    os.makedirs(source_folder, exist_ok=True)
    print("Local folder cleared after upload.")
