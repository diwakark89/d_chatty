# PDF QA System Persistence

## Overview

The PDF QA system now supports persistence across server restarts. This means that if you upload a PDF and then restart the application, the system will attempt to restore the previously uploaded PDF's data.

## How It Works

1. When a PDF is uploaded and processed, the system saves the vector store state to disk
2. When the application starts, it checks for a saved state file
3. If found, it restores the vector store and QA chain

## Limitations

- The current implementation only saves the most recent PDF
- If you upload a new PDF, it will overwrite the previous state
- Some aspects of the QA chain may need to be recreated on startup

## Data Location

Persistence data is stored in the `data/` directory in the project root:
- `data/qa_state.pkl`: Contains the serialized vector store and metadata

## Troubleshooting

If you experience issues with persistence:

1. Check the application logs for error messages
2. Try deleting the `data/qa_state.pkl` file to start fresh
3. Ensure the application has write permissions to the `data/` directory

## Future Improvements

- Support for multiple saved PDFs
- More robust serialization/deserialization
- Database-backed persistence instead of file-based
