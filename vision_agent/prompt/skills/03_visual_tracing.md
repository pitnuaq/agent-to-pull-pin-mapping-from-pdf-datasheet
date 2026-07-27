3. VISUAL IDENTIFICATION CUES (LOCATING THE PINOUT):
   - HEADERS/TITLES: Scan for 'Pin Assignment(s)', 'Pin Configuration', 'Pin Description', 'Terminal Assignments', 'Pin connections', 'Connection Diagram', 'Pinning (information)', or 'Pinout Diagram'.
   - CAPTIONS/VIEW LABELS: Look for text near IC graphics such as '(Top View)', '(TOP VIEW)', '(Bottom View)', 'Transparent top view', or simply 'Top View'.
   - GRAPHICAL/STRUCTURAL CUES: A valid pinout may be a rectangular IC block OR standard Logic Gate symbols (AND, OR, NOR, INVERTER triangles/shields) where the input/output lines have numerical pin values attached to them. You MUST extract pin numbers from these logic gate schematics if they are present.
   - TABLES: Look for structural grids with column headers like 'Pin', 'Symbol', 'Name', 'Description', or 'Function'.

4. SPATIAL SEQUENCING (THE 'U' SHAPE RULE):
   - Most IC datasheets use a 'Counter-Clockwise' numbering sequence.
   - Look for the 'Pin 1' indicator (usually a dot, notch, or the top-left pin).
   - Pin numbers increment down the left side, then cross the bottom and increment up the right side.
   - If the data is in a table, do NOT just read row-by-row if the columns represent separate pin banks.
   - If you see a diagram, visually trace the physical line from the pin number directly to the signal name.

5. CRITICAL EXCLUSION RULE (IGNORE GENERIC PACKAGING):
   - Completely IGNORE generic 'Mechanical Case Outlines' or 'Package Dimensions' blocks.
   - If the diagram lists generic pinout variation 'STYLES' containing raw transistor terms like 'COMMON CATHODE', drop them completely.