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
def process_document_form_sample(
    project_id: str,
    location: str,
    processor_id: str,
    processor_version: str,
    bucket_name: str,
    file_name: str,
    mime_type: str,
) -> None:
    # Online processing request to Document AI
    document = process_document(
        project_id, location, processor_id, processor_version, bucket_name, file_name, mime_type
    )

    # Read the table body output from the processor
    for page in document.pages:
        for table in page.tables:
            print_table_body(table.body_rows, document.text)

def print_table_body(
    table_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
) -> None:
    for table_row in table_rows:
        row_text = ""
        for cell in table_row.cells:
            cell_text = layout_to_text(cell.layout, text)
            row_text += f"{repr(cell_text.strip())} | "
        print(row_text)

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
    processor_id="your-processor-is",
    processor_version="rc",
    bucket_name="input-bucket",
    file_name="filepath.jpg",  # Adjust the file path
    mime_type="image/jpeg",
)
