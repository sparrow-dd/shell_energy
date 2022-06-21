import gcp_auth
from google.cloud import storage


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


bucket_name = "australia-southeast1-sy-com-475ed864-bucket"
destination_blob_name = 'dags/dag.py'
source_file_name = 'd:/GitHub/shell_energy/dag.py'

print(destination_blob_name)
upload_blob(bucket_name,source_file_name,destination_blob_name)
