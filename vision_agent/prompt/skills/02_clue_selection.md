CRITICAL EXTRACTION LAWS & CONSTRAINTS (MANDATORY):

1. DATASHEET MULTI-PART FILTERING & CLUE SELECTION:
   - Datasheets often contain multiple pinouts on the same page. You MUST determine the correct one using the following priority clues:
   - CLUE 1 (PACKAGE MATCH): Scan labels, captions, or subheadings near the diagrams for a string that intersects or matches '{target_package}' (e.g., accept 'SO-14' if the target includes 'SOIC-14').
   - CLUE 2 (FUZZY MPN MATCH): Scan for strings that are a subset of '{target_mpn}'. Manufacturers often label diagrams using a base part number (e.g., 'CD4075B' is a valid prefix match for target 'CD4075BM96'). The valid substring match can occur at the prefix, middle, or suffix of the target MPN.
   - CLUE 3 (GENERIC APPLICABILITY): If a diagram has no specific package listed, but is the only structural logic or connection diagram on the page, assume it applies to the target package.
   - If multiple diagrams exist, ONLY extract the block that satisfies Clue 1 or Clue 2. IGNORE all other diagrams.

2. UNIVERSAL FALLBACK (SINGLE CONFIGURATION RULE):
   - If the image contains ONLY ONE valid pinout mapping, or if the datasheet is clearly dedicated to a single specific component, you MUST extract that pin mapping.
   - Do this EVEN IF the explicit package ('{target_package}') or MPN ('{target_mpn}') text clues are completely missing from the frame. Assume it is the primary configuration.