import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from pathlib import Path
import logging
from datetime import datetime
import shutil

# --- Version & Metadata ---
VERSION = "2.1.2-Enterprise-Stable"
APP_NAME = "Nexus Bank Analytics"

# --- Absolute Path Resolution ---
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
BACKUP_DIR = BASE_DIR / "database_files" / "backups"
EXPORT_DIR = BASE_DIR / "exports"

# Ensure essential directories exist
for d in [LOG_DIR, BACKUP_DIR, EXPORT_DIR]:
    if not d.exists():
        d.mkdir(parents=True, exist_ok=True)

# --- Theme Constants (Premium Neon Fintech) ---
COLORS = {
    'bg': '#020617',         # Darker Slate 950
    'sidebar': '#0F172A',    # Slate 900
    'card': '#1E293B',       # Slate 800
    'text': '#F8FAFC',       # Slate 50
    'text_muted': '#64748B', # Slate 500
    'accent': '#0EA5E9',     # Sky 500 (Neon Blue)
    'success': '#22C55E',    # Green 500 (Neon Green)
    'danger': '#EF4444',     # Red 500 (Neon Red)
    'warning': '#F59E0B',    # Amber 500
    'info': '#6366F1',       # Indigo 500
    'border': '#1E293B',     # Slate 800
    'neon_blue': '#0EA5E9',
    'neon_purple': '#8B5CF6',
    'neon_cyan': '#06B6D4'
}

# --- Logging Configuration ---
# Runtime Logger
runtime_handler = logging.FileHandler(str(LOG_DIR / "runtime.log"))
runtime_handler.setLevel(logging.INFO)

# Error Logger
error_handler = logging.FileHandler(str(LOG_DIR / "errors.log"))
error_handler.setLevel(logging.ERROR)

# Stream Logger
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
runtime_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger = logging.getLogger("NexusEngine")
logger.setLevel(logging.INFO)
logger.addHandler(runtime_handler)
logger.addHandler(error_handler)
logger.addHandler(stream_handler)

logger.info(f"System Root Resolved: {BASE_DIR}")

def export_to_csv(df, filename):
    try:
        df.to_csv(filename, index=False)
        logger.info(f"Exported CSV: {filename}")
        return True
    except Exception as e:
        logger.error(f"CSV Export Failed: {e}")
        return False

def export_to_excel(df, filename):
    try:
        df.to_excel(filename, index=False)
        logger.info(f"Exported Excel: {filename}")
        return True
    except Exception as e:
        logger.error(f"Excel Export Failed: {e}")
        return False

def generate_pdf_report(df, stats, filename):
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = styles['Title']
        title_style.textColor = colors.HexColor(COLORS['accent'])
        elements.append(Paragraph(f"{APP_NAME} - Enterprise Report", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 24))
        
        # Summary Stats
        elements.append(Paragraph("Executive Summary", styles['Heading2']))
        stat_data = [["Key Metric", "Current Value"]]
        for key, val in stats.items():
            stat_data.append([key, str(val)])
        
        t = Table(stat_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['sidebar'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 30))
        
        # Recent Transactions
        elements.append(Paragraph("Activity Log (Latest 25)", styles['Heading2']))
        top_df = df.head(25).copy()
        # Clean data for PDF
        table_data = [["Date", "Account", "Type", "Bank", "Amount", "Status"]]
        for _, row in top_df.iterrows():
            table_data.append([
                str(row['date'])[:16],
                row['acc_no'],
                row['type'],
                row['bank'],
                f"{row['amount']:,.2f}",
                row['status']
            ])
        
        tt = Table(table_data, colWidths=[100, 70, 70, 80, 80, 70])
        tt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS['info'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        elements.append(tt)
        
        doc.build(elements)
        logger.info(f"Generated PDF: {filename}")
        return True
    except Exception as e:
        logger.error(f"PDF Generation Failed: {e}")
        return False

def backup_database(db_path):
    try:
        # Ensure backup directory exists
        if not BACKUP_DIR.exists():
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"nexus_backup_{timestamp}.db"
        shutil.copy2(db_path, str(backup_path))
        logger.info(f"Database backed up to {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        return False
