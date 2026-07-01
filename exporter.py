# exporter.py
import pandas as pd
import io

def export_to_web_excel(results):
    df = pd.DataFrame(results)
    
    # Columns order alignment
    columns_order = [
        "Website URL", "Website Title", "Meta Description", "Canonical URL",
        "H1 Count", "Word Count", "Image Count", "Alt Text Coverage",
        "Has Open Graph", "Has Schema Markup", "Internal Links", "External Links",
        "CMS", "Contact Page", "Write for Us Page", "Guest Post Page",
        "Social Media Links", "Accepts Guest Posts"
    ]
    
    # Ensure all columns exist
    for col in columns_order:
        if col not in df.columns:
            df[col] = "N/A"
            
    df = df[columns_order]
    
    # Save Excel into a byte memory buffer instead of hard drive
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Publisher Database')
    
    output.seek(0)
    return output