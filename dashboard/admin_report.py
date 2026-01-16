import os
import tempfile
from datetime import datetime

import pandas as pd
from fpdf import FPDF


class AdminPDF(FPDF):

    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Retail Analytics Admin Report", ln=True, align="C")

        self.set_font("Arial", size=9)
        self.cell(0, 6, f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", ln=True, align="C")

        self.ln(4)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_admin_report(df, filters, prepared_by, charts, date_range):
    pdf = AdminPDF()
    pdf.add_page()

    # ---------- Report Info ----------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Report Overview", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, f"""
Prepared By: {prepared_by}
Date Range: {date_range[0]} to {date_range[1]}
Total Records: {len(df)}

Applied Filters:
""" + "\n".join([f"- {k}: {v}" for k, v in filters.items()]))

    pdf.ln(5)

    # ---------- KPIs ----------
    total_revenue = df["Revenue"].sum()
    avg_order = df["Revenue"].mean()
    top_region = df.groupby("Region")["Revenue"].sum().idxmax()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Key Performance Indicators", ln=True)

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"Total Revenue: {total_revenue:,.2f}", ln=True)
    pdf.cell(0, 8, f"Average Order Value: {avg_order:,.2f}", ln=True)
    pdf.cell(0, 8, f"Top Performing Region: {top_region}", ln=True)

    pdf.ln(5)

    # ---------- Charts ----------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Visual Analytics", ln=True)

    for title, fig in charts:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, title, ln=True)

        # Save chart temporarily
        img_path = os.path.join(tempfile.gettempdir(), f"{title}.png")
        fig.write_image(img_path, width=900, height=500)

        pdf.image(img_path, x=15, w=180)
        pdf.ln(6)

    # ---------- Save ----------
    output_path = os.path.join(tempfile.gettempdir(), f"Admin_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(output_path)

    return output_path
