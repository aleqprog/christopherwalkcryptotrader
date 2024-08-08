from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors


def create_pdf(data, references, datetime_str, formatted_date):
    doc = SimpleDocTemplate(f"report_{datetime_str}.pdf", pagesize=letter, leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)
    elements = []
    part_size = 5

    total_gain_percent = sum(record[6] for record in data)
    total_loss_percent = sum(abs(record[7]) for record in data)
    total_records = len(data)

    for i in range(0, len(data), part_size):
        part_data = data[i:i + part_size]

        table_part = []

        for record in part_data:
            formatted_data = []

            for j, ref in enumerate(references):
                formatted_data.append([ref, str(record[j])])

            style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
                                ('FONTSIZE', (0, 0), (-1, -1), 7),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  
                                ('LINEBELOW', (0, 0), (-1, -1), 0.1, colors.black),  
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 0.1), 
    
                                ])
            

            table = Table(formatted_data, colWidths=[40, 60])  
            table.setStyle(style)

            table_part.append(table)

        elements.append(Table([table_part], colWidths='*'))

    footer = Table([
        ['Trades', total_records],
        ['Gains', str(round(total_gain_percent,2)) + '%'],
        ['Losses', str(round(total_loss_percent,2))+ '%'],
        ['Date', formatted_date],
    ])
    footer.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('TEXTCOLOR', (1, 1), (1, 1), colors.green),
                                ('TEXTCOLOR', (1, 2), (1, 2), colors.red),
                                ('TEXTCOLOR', (1, 3), (1, 3), colors.blue)]))
    elements.append(footer)

    doc.build(elements)
    print(f"Report successfully generated. report_{datetime_str}.pdf")
