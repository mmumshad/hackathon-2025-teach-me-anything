#!/usr/bin/env python3
"""
Create a simple test PDF for audiobook testing
"""

def create_simple_pdf():
    """Create a simple PDF using basic approach"""
    try:
        # Try using reportlab if available
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = "test_physics_book.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Add physics content
        y_position = 750
        content = [
            "Introduction to Physics",
            "",
            "Chapter 1: Motion and Forces",
            "",
            "Physics is the study of matter, energy, and their interactions.",
            "Newton's first law states that an object at rest stays at rest,",
            "and an object in motion stays in motion, unless acted upon by an external force.",
            "This is also known as the law of inertia.",
            "",
            "Force is a vector quantity that has both magnitude and direction.",
            "The SI unit of force is the Newton (N).",
            "",
            "Chapter 2: Energy and Work",
            "",
            "Energy is the capacity to do work. Work is done when a force causes displacement.",
            "The work-energy theorem states that the work done on an object equals",
            "the change in its kinetic energy.",
            "",
            "Power is the rate at which work is done.",
            "The SI unit of power is the Watt (W)."
        ]
        
        for line in content:
            c.drawString(100, y_position, line)
            y_position -= 20
        
        c.save()
        print(f"✅ Created PDF using reportlab: {pdf_path}")
        return pdf_path
        
    except ImportError:
        print("⚠️  reportlab not available, creating a minimal PDF manually")
        
        # Create a minimal PDF structure manually
        pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
100 700 Td
(Introduction to Physics) Tj
0 -20 Td
(Chapter 1: Motion and Forces) Tj
0 -20 Td
(Physics is the study of matter, energy, and their interactions.) Tj
0 -20 Td
(Newton's first law states that an object at rest stays at rest,) Tj
0 -20 Td
(and an object in motion stays in motion, unless acted upon by an external force.) Tj
0 -20 Td
(This is also known as the law of inertia.) Tj
0 -20 Td
(Force is a vector quantity that has both magnitude and direction.) Tj
0 -20 Td
(The SI unit of force is the Newton (N).) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000525 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
610
%%EOF"""
        
        pdf_path = "test_physics_book.pdf"
        with open(pdf_path, "w") as f:
            f.write(pdf_content)
        
        print(f"✅ Created minimal PDF: {pdf_path}")
        return pdf_path

if __name__ == "__main__":
    create_simple_pdf()
