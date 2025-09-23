from google.cloud import storage # type: ignore
import os

def upload_folder_to_gcs(bucket_name: str, source_folder: str, destination_folder: str = ""):
    """
    Upload all files from a local folder to a Google Cloud Storage bucket.

    :param bucket_name: GCS bucket name
    :param source_folder: Path to the local folder
    :param destination_folder: Path inside the bucket (destination folder)
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for root, _, files in os.walk(source_folder):
        for file in files:
            local_path = os.path.join(root, file)

            relative_path = os.path.relpath(local_path, source_folder)
            blob_path = os.path.join(destination_folder, relative_path).replace("\\", "/")

            blob = bucket.blob(blob_path)
            blob.upload_from_filename(local_path)

            print(f"✅ Upload completed: {local_path} → gs://{bucket_name}/{blob_path}")
