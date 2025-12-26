#!/usr/bin/env python3
"""Generate media kit PDFs for NUBEAUX Collective creators."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Brand colors
CHARCOAL = HexColor('#1a1a1a')
WARM_GREY = HexColor('#6b6b6b')
BONE = HexColor('#f5f3ef')
WHITE = HexColor('#ffffff')

def draw_header(c, width, height, name, handle):
    """Draw the header section."""
    # Background
    c.setFillColor(CHARCOAL)
    c.rect(0, height - 3*inch, width, 3*inch, fill=1, stroke=0)

    # Logo
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 10)
    c.drawString(0.75*inch, height - 0.75*inch, "NUBEAUX COLLECTIVE")

    # Creator name
    c.setFont("Helvetica-Bold", 36)
    c.drawString(0.75*inch, height - 1.75*inch, name)

    # Handle
    c.setFillColor(HexColor('#999999'))
    c.setFont("Helvetica", 14)
    c.drawString(0.75*inch, height - 2.25*inch, handle)

def draw_stats_section(c, width, height, stats, y_pos):
    """Draw the stats section."""
    c.setFillColor(BONE)
    c.rect(0.5*inch, y_pos - 1.25*inch, width - 1*inch, 1.25*inch, fill=1, stroke=0)

    stat_width = (width - 1*inch) / len(stats)
    for i, (value, label) in enumerate(stats):
        x = 0.5*inch + i * stat_width + stat_width/2

        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(x, y_pos - 0.5*inch, value)

        c.setFillColor(WARM_GREY)
        c.setFont("Helvetica", 8)
        c.drawCentredString(x, y_pos - 0.85*inch, label.upper())

def draw_section_title(c, title, y_pos):
    """Draw a section title."""
    c.setFillColor(CHARCOAL)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75*inch, y_pos, title)

    c.setStrokeColor(HexColor('#e0e0e0'))
    c.setLineWidth(0.5)
    c.line(0.75*inch, y_pos - 0.1*inch, 7.75*inch, y_pos - 0.1*inch)

def draw_about_section(c, width, about_text, y_pos):
    """Draw the about section."""
    draw_section_title(c, "ABOUT", y_pos)

    c.setFillColor(WARM_GREY)
    c.setFont("Helvetica", 10)

    # Simple text wrapping
    words = about_text.split()
    lines = []
    current_line = []
    max_width = width - 1.5*inch

    for word in words:
        test_line = ' '.join(current_line + [word])
        if c.stringWidth(test_line, "Helvetica", 10) < max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    text_y = y_pos - 0.4*inch
    for line in lines[:6]:  # Max 6 lines
        c.drawString(0.75*inch, text_y, line)
        text_y -= 0.2*inch

    return text_y - 0.2*inch

def draw_specializations(c, specs, y_pos):
    """Draw specializations."""
    draw_section_title(c, "CONTENT SPECIALISATION", y_pos)

    spec_y = y_pos - 0.5*inch
    for spec, desc in specs:
        c.setFillColor(CHARCOAL)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.75*inch, spec_y, spec)

        c.setFillColor(WARM_GREY)
        c.setFont("Helvetica", 9)
        c.drawString(0.75*inch, spec_y - 0.2*inch, desc)

        spec_y -= 0.55*inch

    return spec_y

def draw_brands(c, brands, y_pos):
    """Draw brand partners."""
    draw_section_title(c, "BRAND PARTNERS", y_pos)

    c.setFillColor(WARM_GREY)
    c.setFont("Helvetica", 10)
    brands_text = "  •  ".join(brands)
    c.drawString(0.75*inch, y_pos - 0.4*inch, brands_text)

    return y_pos - 0.8*inch

def draw_contact(c, width, y_pos):
    """Draw contact section."""
    c.setFillColor(CHARCOAL)
    c.rect(0, 0, width, 1*inch, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 0.6*inch, "FOR PARTNERSHIP ENQUIRIES")

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, 0.35*inch, "hello@nubeaux.co")

def create_nia_media_kit():
    """Create Nia The Light's media kit."""
    filename = "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/media_kits/nia-the-light-media-kit.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Header
    draw_header(c, width, height, "Nia The Light", "@niathelight")

    # Stats
    stats = [
        ("438K", "Followers"),
        ("25.9M+", "Video Views"),
        ("120+", "Brand Partners"),
        ("12+", "Years Experience")
    ]
    draw_stats_section(c, width, height, stats, height - 3.25*inch)

    # About
    about = "Luxury travel and lifestyle content creator specialising in authentic storytelling that captures transformative travel experiences. With over a decade of experience and partnerships with 120+ brands, Nia's work focuses on cultural connection, luxury hospitality, and the emotional resonance of travel — creating content that inspires wanderlust while delivering measurable results for brand partners."
    next_y = draw_about_section(c, width, about, height - 5*inch)

    # Specializations
    specs = [
        ("Luxury Hospitality", "Five-star resorts, boutique hotels, property tours, and guest experience storytelling"),
        ("Cultural Travel", "Heritage sites, local traditions, art experiences, and authentic community connections"),
        ("Wellness & Lifestyle", "Spa retreats, mindfulness experiences, holistic travel, and self-care narratives")
    ]
    next_y = draw_specializations(c, specs, next_y - 0.3*inch)

    # Brands
    brands = ["Four Seasons", "Park Hyatt", "Onguma Safari", "Dhow House", "Intrepid"]
    draw_brands(c, brands, next_y - 0.3*inch)

    # Contact
    draw_contact(c, width, 0)

    c.save()
    print(f"Created: {filename}")

def create_klein_media_kit():
    """Create Klein Nettoh's media kit."""
    filename = "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/media_kits/klein-nettoh-media-kit.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Header
    draw_header(c, width, height, "Klein Nettoh", "@klein_nettoh")

    # Stats
    stats = [
        ("870K+", "Travel Views"),
        ("192K", "Engagement"),
        ("59", "Lodge Features"),
        ("228", "Travel Posts")
    ]
    draw_stats_section(c, width, height, stats, height - 3.25*inch)

    # About
    about = "Award-winning wildlife filmmaker and conservation photographer based in Kenya. Klein captures Africa's wilderness through cinematic storytelling, specialising in luxury safari lodges and authentic travel experiences across East and Southern Africa. His work brings viewers closer to the continent's natural beauty while delivering premium visual content for hospitality partners."
    next_y = draw_about_section(c, width, about, height - 5*inch)

    # Specializations
    specs = [
        ("Cinematic Film", "Professional wildlife filmmaking with cinematic composition and storytelling techniques"),
        ("Conservation", "Powerful imagery communicating conservation stories and sustainable tourism narratives"),
        ("Safari Lodges", "Specialised experience creating compelling content for luxury safari properties")
    ]
    next_y = draw_specializations(c, specs, next_y - 0.3*inch)

    # Brands
    brands = ["Canon", "Instagram", "National Geographic", "Sony"]
    draw_brands(c, brands, next_y - 0.3*inch)

    # Contact
    draw_contact(c, width, 0)

    c.save()
    print(f"Created: {filename}")

if __name__ == "__main__":
    create_nia_media_kit()
    create_klein_media_kit()
    print("Media kits generated successfully!")
