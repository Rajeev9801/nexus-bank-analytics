import pandas as pd
from utils import COLORS, generate_pdf_report, export_to_csv, export_to_excel, logger, EXPORT_DIR
from services.database import get_connection
from services.ai_engine import predict_future_balance, get_spending_insights, analyze_fraud
import os
from datetime import datetime

def generate_enterprise_report(format='PDF'):
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM transactions ORDER BY date DESC", conn)
        conn.close()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Use absolute EXPORT_DIR
        filename = str(EXPORT_DIR / f"Nexus_Report_{timestamp}.{format.lower()}")
        
        if format == 'PDF':
            # Gather rich data
            balance = df['balance'].iloc[0] if not df.empty else 0
            prediction = predict_future_balance(df)
            insights = get_spending_insights(df)
            fraud_count = len(analyze_fraud(df))
            
            stats = {
                "Generation Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Current Liquid Balance": f"INR {balance:,.2f}",
                "AI Liquid Forecast (30d)": f"INR {prediction:,.2f}",
                "Active Fraud Alerts": str(fraud_count),
                "Total Record Count": str(len(df)),
                "Spending Insight": insights
            }
            
            success = generate_pdf_report(df, stats, filename)
        elif format == 'CSV':
            success = export_to_csv(df, filename)
        elif format == 'Excel':
            success = export_to_excel(df, filename)
        else:
            success = False
            
        if success:
            logger.info(f"Enterprise {format} report generated successfully: {filename}")
        return success, filename
    except Exception as e:
        logger.error(f"Report generation engine failure: {e}")
        return False, str(e)
