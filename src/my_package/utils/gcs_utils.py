from google.cloud import storage

def list_pdfs_in_folder(folder_path):
    """Lists PDF files in a GCS folder."""
    client = storage.Client()
    bucket_name = folder_path.split('/')[2]
    prefix = "/".join(folder_path.split('/')[3:])
    blobs = client.list_blobs(bucket_name, prefix=prefix)
    return [f"{bucket_name}/{blob.name}" for blob in blobs if blob.name.endswith('.pdf')]


def download_blob(blob_name):
    """Downloads a blob as bytes."""
    client = storage.Client()
    bucket_name = blob_name.split('/')[0]
    blob_name = "/".join(blob_name.split('/')[1:])
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.download_as_bytes()


def upload_blob(blob_name, data):
    """Uploads data to a blob."""
    client = storage.Client()
    bucket_name = blob_name.split('/')[2]
    blob_name = "/".join(blob_name.split('/')[3:])
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(data)


def move_blob(source_blob_name, destination_blob_name):
    """Moves a blob from source to destination."""
    client = storage.Client()
    bucket_name = source_blob_name.split('/')[0]
    source_blob_name = "/".join(source_blob_name.split('/')[1:])
    destination_blob_name = "/".join(destination_blob_name.split('/')[3:])
    bucket = client.bucket(bucket_name)
    source_blob = bucket.blob(source_blob_name)
    bucket.rename_blob(source_blob, destination_blob_name)
