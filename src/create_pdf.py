from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

# Get the desktop path
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# Create the full file path (underscore = safer for terminals)
file_path = os.path.join(desktop_path, "Kyoto_Report.pdf")

# Get today's date
today_date = datetime.now().strftime("%Y-%m-%d")

# Create a PDF file
c = canvas.Canvas(file_path, pagesizes=letter)

# Set the font and size for the text
c.setFont("Helvetica", 12)

# Write the text on the PDF
text = f"Hello from Hermes! Today is {today_date}"
c.drawString(72, 750, text)

# Save the PDF file
c.save()

# ✅ CONFIRMATION (this was missing!)
print(f"🎉 SUCCESS! PDF created: {file_path}")
