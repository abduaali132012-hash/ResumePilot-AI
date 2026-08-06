#!/usr/bin/env python3
"""
Decode the base64-encoded files back to binary (.pptx, .pdf, .zip).
Run this script to generate the actual files from the .b64 versions.

Usage:
    python3 decode_presentation_files.py
"""
import base64
import os

files = [
    ("ResumePilot_AI_Presentation.pptx.b64", "ResumePilot_AI_Presentation.pptx"),
    ("ResumePilot_AI_Presentation.pdf.b64", "ResumePilot_AI_Presentation.pdf"),
    ("ResumePilot_AI_Source_Code.zip.b64", "ResumePilot_AI_Source_Code.zip"),
    ("README.pdf.b64", "README.pdf"),
]

for b64_path, output_path in files:
    if not os.path.exists(b64_path):
        print(f"⚠️  Missing: {b64_path}")
        continue
    with open(b64_path, "r") as f:
        encoded = f.read().strip()
    decoded = base64.b64decode(encoded)
    with open(output_path, "wb") as f:
        f.write(decoded)
    print(f"✅ Decoded {b64_path} → {output_path} ({len(decoded)} bytes)")

print("\nDone! All files are ready.")