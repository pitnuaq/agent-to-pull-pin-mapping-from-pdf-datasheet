## Tool: read_datasheet
- **Description**: Reads a PDF Datasheet, converts the specific page containing the Pin Assignment layout into an image, and leverages multimodal reasoning to output the exact pin mappings.
- **Inputs Required**: 
  - `pdf_path`: The file path to the target PDF.
  - `target_package`: The physical packaging profile of the IC.
  - `target_mpn`: The Manufacturer Part Number.
- **Execution Rules**: Always use this tool first to visually capture the layout before attempting any data extraction.