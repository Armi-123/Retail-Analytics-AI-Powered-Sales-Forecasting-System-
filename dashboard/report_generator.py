import os
import tempfile
from datetime import datetime
import pandas as pd
from fpdf import FPDF


# ================= PDF CLASS =================
class PDF(FPDF):

    def header(self):
        if self.page_no() == 1:
            self.set_font("Arial", "B", 16)
            self.cell(0, 12, "Retail Analytics & Sales Forecasting Report", ln=True, align="C")

            self.set_font("Arial", size=9)
            self.cell(
                0, 6,
                f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
                ln=True,
                align="C"
            )

            self.ln(5)
            self.set_draw_color(180, 180, 180)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=8)
        self.set_text_color(120)
        self.cell(
            0, 10,
            f"Retail Analytics & AI-Powered Sales Forecasting System  |  Page {self.page_no()}",
            align="C"
        )
        self.set_text_color(0)


# ================= HELPERS =================
def section_title(pdf, title):
    pdf.set_fill_color(230, 238, 249)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, f"  {title}", ln=True, fill=True)
    pdf.ln(6)


def generate_executive_summary(df):
    revenue = df["Revenue"].sum()
    units = df["Units_Sold"].sum()
    best_region = df.groupby("Region")["Revenue"].sum().idxmax()
    best_category = df.groupby("Product_Category")["Revenue"].sum().idxmax()

    return (
        f"This report presents a comprehensive analysis of retail performance based on the selected filters. "
        f"A total revenue of {revenue:,.0f} was generated with {units:,.0f} units sold. "
        f"The strongest contribution is observed from the {best_region} region and "
        f"the {best_category} category. Overall trends indicate consistent demand and "
        f"stable business performance."
    )


def kpi_table(pdf, df):
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(245, 245, 245)

    data = [
        ("Total Revenue", f"{df['Revenue'].sum():,.0f}"),
        ("Units Sold", f"{df['Units_Sold'].sum():,.0f}"),
        ("Average Discount", f"{df['Discount_Percentage'].mean():.2f}%"),
        ("Average Store Rating", f"{df['Store_Rating'].mean():.2f}")
    ]

    col_widths = [80, 60]
    row_height = 9

    for label, value in data:
        pdf.cell(col_widths[0], row_height, label, border=1, fill=True)
        pdf.cell(col_widths[1], row_height, value, border=1)
        pdf.ln()

    pdf.ln(8)


# ================= MAIN PDF =================
def generate_pdf_report(df, filters, prepared_by, charts=None, date_range=None):

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # -------- REPORT FILTERS --------
    section_title(pdf, "Report Filters")
    pdf.set_font("Arial", size=10)

    for k, v in filters.items():
        pdf.cell(0, 6, f"{k}: {v}", ln=True)

    if date_range:
        pdf.cell(0, 6, f"Date Range: {date_range[0]} to {date_range[1]}", ln=True)

    pdf.ln(8)

    # -------- EXECUTIVE SUMMARY --------
    section_title(pdf, "Executive Summary")
    pdf.set_font("Arial", size=10)
    pdf.set_fill_color(248, 249, 250)
    pdf.multi_cell(
        0, 8,
        generate_executive_summary(df),
        border=0,
        fill=True
    )

    pdf.ln(10)

    # -------- BUSINESS OVERVIEW --------
    section_title(pdf, "Business Overview")
    kpi_table(pdf, df)

    # -------- VISUAL INSIGHTS --------
    if charts:
        pdf.add_page()
        section_title(pdf, "Visual Insights")

        tmp = tempfile.mkdtemp()

        for title, fig in charts:
            if pdf.get_y() > 140:
                pdf.add_page()

            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, title, ln=True)

            img_path = os.path.join(tmp, f"{title}.png")
            fig.write_image(img_path, scale=2)

            pdf.image(img_path, x=15, w=180)
            pdf.ln(12)

    # -------- DATA PREVIEW (LANDSCAPE FIX) --------
    pdf.add_page(orientation="L")

    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_top_margin(15)

    section_title(pdf, "Data Preview (Top 15 Records)")

    preview = df.head(15).copy()
    preview["Date"] = pd.to_datetime(preview["Date"]).dt.strftime("%Y-%m-%d")
    preview["Revenue"] = preview["Revenue"].map(lambda x: f"{x:,.2f}")
    preview["Units_Sold"] = preview["Units_Sold"].astype(int)

    cols = [
        "Date", "Store_ID", "Store_Location",
        "Product_Category", "Brand",
        "Units_Sold", "Revenue", "Region"
    ]

    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_widths = [
        page_width * 0.10,
        page_width * 0.10,
        page_width * 0.16,
        page_width * 0.18,
        page_width * 0.12,
        page_width * 0.08,
        page_width * 0.14,
        page_width * 0.12
    ]

    row_height = 8

    # Header
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(230, 238, 249)

    for i, col in enumerate(cols):
        pdf.cell(col_widths[i], row_height, col.replace("_", " "), border=1, align="C", fill=True)
    pdf.ln()

    # Rows
    pdf.set_font("Arial", size=9)
    fill = False

    for _, row in preview.iterrows():
        pdf.set_fill_color(245, 245, 245) if fill else pdf.set_fill_color(255, 255, 255)

        for i, col in enumerate(cols):
            align = "R" if col in ["Units_Sold", "Revenue"] else "L"
            text = str(row[col])[:40]
            pdf.cell(col_widths[i], row_height, text, border=1, align=align, fill=True)
        pdf.ln()
        fill = not fill




    # -------- PREPARED BY --------
    pdf.ln(12)
    pdf.set_font("Arial", size=9)
    pdf.cell(0, 6, f"Prepared by: {prepared_by}", ln=True)

    # -------- SAVE --------
    filename = f"Retail_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(tempfile.gettempdir(), filename)
    pdf.output(path)

    return path
