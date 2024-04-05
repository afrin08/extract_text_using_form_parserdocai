from typing import Optional, Sequence
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud import storage

# Function to download a blob from GCS bucket
def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f'Blob {source_blob_name} downloaded to {destination_file_name}.')

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f'File {source_file_name} uploaded to {destination_blob_name}.')

def process_document_form_sample(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    bucket_name: str,
    file_name: str,
    mime_type: str,
    output_bucket_name: str,
    output_file_name: str,
) -> None:
    # Online processing request to Document AI
    document = process_document(
        project_id, location, processor_id, processor_version, bucket_name, file_name, mime_type
    )

    # Extract table body content
    table_content = []
    for page in document.pages:
        for table in page.tables:
            for table_row in table.body_rows:
                row_text = ""
                for cell in table_row.cells:
                    cell_text = layout_to_text(cell.layout, document.text)
                    row_text += f"{cell_text.strip()} | "
                table_content.append(row_text.strip())

    # Write table content to a file
    output_file_path = "/tmp/table_content.txt"  # Temporary local file
    with open(output_file_path, "w") as f:
        f.write("\n".join(table_content))

    # Upload file to destination bucket
    upload_blob(output_bucket_name, output_file_path, output_file_name)

def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document's text. This function converts
    offsets to a string.
    """
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    return "".join(
        text[int(segment.start_index) : int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )

# Example usage
process_document_form_sample(
    project_id="project-id",
    location="us",  # Change if your processor is in a different region
    processor_id="Your-processor-id",
    processor_version="rc",
    bucket_name="input-bucket",
    file_name="91926392e1128a5bb7e506a40d85349c.jpg",  # Adjust the file path
    mime_type="image/jpeg",
    output_bucket_name="output-bucket",  # Provide the destination bucket name
    output_file_name="table_content.txt",  # Provide the output file path
)
