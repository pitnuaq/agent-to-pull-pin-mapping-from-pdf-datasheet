6. ANTI-HALLUCINATION ENFORCEMENT:
   - Transcribe characters EXACTLY as drawn in the target diagram. Do not standardize names.
   - Pay precise spatial attention to OCR details: do not confuse 'I' with '1', or 'O' with '0'.

OUTPUT FORMAT RULE:
Output the synthesized results EXCLUSIVELY as a raw, valid JSON object. Do not include markdown tags (like ```json), backticks, or conversational text.
If the image is completely empty of pin data, or if it explicitly labels a DIFFERENT, conflicting component package without the target, return an empty array for 'pinout'.

Expected Schema Structure:
{
  "reasoning": "string (Briefly explain which clue [Package, Fuzzy MPN, or Single Fallback] triggered the extraction and your spatial tracing logic)",
  "pinout": [
    {
      "pin_number": "string",
      "pin_name": "string",
      "pin_function": "string"
    }
  ]
}