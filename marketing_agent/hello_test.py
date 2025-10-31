import sys
print("✓ Python OK:", sys.version)
try:
    import pandas, streamlit, gspread
    print("✓ Imports OK (pandas / streamlit / gspread)")
except Exception as e:
    print("Import error:", e)
