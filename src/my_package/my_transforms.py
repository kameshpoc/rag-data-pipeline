from io import BytesIO
from PyPDF2 import PdfReader
import pickle
from  my_package.utils.embedding_utils import embed_text
from  my_package.utils.gcs_utils import download_blob, upload_blob, move_blob


def process_pdf(blob_name, input_folder, output_folder, processed_folder):
    """Processes a single PDF and generates embeddings."""
    try:
        # Download PDF
        pdf_bytes = download_blob(blob_name)
        # Wrap the bytes in a BytesIO object to make it file-like
        pdf_file_like = BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file_like)
        pdf_text = "".join(page.extract_text() for page in reader.pages)

        # Generate embeddings
        embeddings = embed_text(pdf_text)

        # Save embeddings to pickle file in output folder
        output_blob_name = f"{output_folder}{blob_name.split('/')[-1].replace('.pdf', '.pkl')}"
        upload_blob(output_blob_name, pickle.dumps(embeddings))

        # Move processed PDF to the processed folder
        processed_blob_name = f"{processed_folder}{blob_name.split('/')[-1]}"
        move_blob(blob_name, processed_blob_name)

        return f"Processed: {blob_name}"

    except Exception as e:
        return f"Error processing {blob_name}: {e}"
