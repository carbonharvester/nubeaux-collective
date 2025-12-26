#!/usr/bin/env python3
"""Generate media kit PDFs for NUBEAUX Collective creators."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Brand colors matching the website
CHARCOAL = HexColor('#1a1a1a')
WARM_GREY = HexColor('#6b6b6b')
BONE = HexColor('#f5f3ef')
ECRU = HexColor('#e8e4dc')
WHITE = HexColor('#ffffff')
ACCENT = HexColor('#8b7355')  # Warm accent color

def draw_header(c, width, height, name, handle, tags):
    """Draw the header section with elegant styling."""
    # Full bleed dark header
    c.setFillColor(CHARCOAL)
    c.rect(0, height - 3.5*inch, width, 3.5*inch, fill=1, stroke=0)

    # "Creator" label
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(0.75*inch, height - 0.6*inch, "CREATOR")

    # NUBEAUX logo on right
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 9)
    c.drawRightString(width - 0.75*inch, height - 0.6*inch, "NUBEAUX")

    # Creator name - large serif-style
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 48)
    c.drawString(0.75*inch, height - 1.5*inch, name)

    # Handle
    c.setFillColor(HexColor('#888888'))
    c.setFont("Helvetica", 12)
    c.drawString(0.75*inch, height - 2*inch, handle)

    # Tags
    tag_x = 0.75*inch
    tag_y = height - 2.75*inch
    c.setFont("Helvetica", 7)
    for tag in tags:
        c.setStrokeColor(HexColor('#444444'))
        c.setLineWidth(0.5)
        tag_width = c.stringWidth(tag.upper(), "Helvetica", 7) + 16
        c.rect(tag_x, tag_y - 4, tag_width, 18, fill=0, stroke=1)
        c.setFillColor(HexColor('#cccccc'))
        c.drawString(tag_x + 8, tag_y, tag.upper())
        tag_x += tag_width + 8

def draw_stats_section(c, width, height, stats, y_pos):
    """Draw the stats section with elegant grid."""
    stat_width = width / len(stats)

    for i, (value, label) in enumerate(stats):
        x = i * stat_width + stat_width/2

        # Divider lines between stats
        if i > 0:
            c.setStrokeColor(ECRU)
            c.setLineWidth(0.5)
            c.line(i * stat_width, y_pos - 0.2*inch, i * stat_width, y_pos - 1.1*inch)

        # Value in serif
        c.setFillColor(CHARCOAL)
        c.setFont("Times-Roman", 28)
        c.drawCentredString(x, y_pos - 0.5*inch, value)

        # Label
        c.setFillColor(WARM_GREY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x, y_pos - 0.9*inch, label.upper())

def draw_section_title(c, title, y_pos, width):
    """Draw a section title with serif font."""
    c.setFillColor(CHARCOAL)
    c.setFont("Times-Roman", 18)
    c.drawString(0.75*inch, y_pos, title)

    # Subtle line underneath
    c.setStrokeColor(ECRU)
    c.setLineWidth(0.5)
    c.line(0.75*inch, y_pos - 0.15*inch, width - 0.75*inch, y_pos - 0.15*inch)

def draw_about_section(c, width, about_text, y_pos):
    """Draw the about section with elegant typography."""
    # Intro text in larger italic serif
    c.setFillColor(CHARCOAL)
    c.setFont("Times-Italic", 14)

    # Simple text wrapping
    words = about_text.split()
    lines = []
    current_line = []
    max_width = width - 1.5*inch

    for word in words:
        test_line = ' '.join(current_line + [word])
        if c.stringWidth(test_line, "Times-Italic", 14) < max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))

    text_y = y_pos
    for line in lines[:5]:  # Max 5 lines
        c.drawString(0.75*inch, text_y, line)
        text_y -= 0.3*inch

    return text_y - 0.2*inch

def draw_specializations(c, specs, y_pos, width):
    """Draw specializations in a clean grid."""
    draw_section_title(c, "Content Specialisation", y_pos, width)

    spec_y = y_pos - 0.6*inch
    for spec, desc in specs:
        c.setFillColor(CHARCOAL)
        c.setFont("Times-Roman", 14)
        c.drawString(0.75*inch, spec_y, spec)

        c.setFillColor(WARM_GREY)
        c.setFont("Helvetica", 9)
        c.drawString(0.75*inch, spec_y - 0.25*inch, desc)

        spec_y -= 0.7*inch

    return spec_y

def draw_brands(c, brands, y_pos, width, brand_logos=None):
    """Draw brand partners with elegant styling, using logos if available."""
    # Label
    c.setFillColor(WARM_GREY)
    c.setFont("Helvetica", 7)
    c.drawString(0.75*inch, y_pos, "TRUSTED BY")

    if brand_logos:
        # Draw brand logos
        logo_x = 0.75*inch
        logo_y = y_pos - 0.6*inch
        logo_height = 0.4*inch
        logo_spacing = 0.2*inch

        for logo_path in brand_logos:
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(logo_path)
                img_width, img_height = img.getSize()
                aspect = img_width / img_height
                scaled_width = logo_height * aspect

                c.drawImage(logo_path, logo_x, logo_y,
                           width=scaled_width, height=logo_height,
                           preserveAspectRatio=True, mask='auto')
                logo_x += scaled_width + logo_spacing
            except Exception as e:
                # Fallback to text if image fails
                pass
    else:
        # Fallback: Brands in serif (text only)
        c.setFillColor(CHARCOAL)
        c.setFont("Times-Roman", 11)
        brands_text = "   ·   ".join(brands)
        c.drawString(0.75*inch, y_pos - 0.35*inch, brands_text)

    return y_pos - 0.8*inch

def draw_contact(c, width, y_pos):
    """Draw contact section with elegant footer."""
    # Dark footer band
    c.setFillColor(CHARCOAL)
    c.rect(0, 0, width, 1.25*inch, fill=1, stroke=0)

    # Label
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 7)
    c.drawCentredString(width/2, 0.85*inch, "FOR PARTNERSHIP ENQUIRIES")

    # Email
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 16)
    c.drawCentredString(width/2, 0.5*inch, "hello@nubeauxcollective.com")

    # Website
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 0.2*inch, "nubeauxcollective.com")

def create_nia_media_kit():
    """Create Nia The Light's media kit."""
    filename = "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/media_kits/nia-the-light-media-kit.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Tags
    tags = ["Luxury Travel", "Cultural Heritage", "Lifestyle", "Wellness"]

    # Header
    draw_header(c, width, height, "Nia The Light", "@niathelight", tags)

    # Stats
    stats = [
        ("438K", "Followers"),
        ("25.9M+", "Video Views"),
        ("120+", "Brand Partners"),
        ("12+", "Years Experience")
    ]
    draw_stats_section(c, width, height, stats, height - 3.75*inch)

    # About
    about = "Luxury travel and lifestyle content creator specialising in authentic storytelling that captures transformative travel experiences. With over a decade of experience and partnerships with 120+ brands, Nia's work focuses on cultural connection, luxury hospitality, and the emotional resonance of travel."
    next_y = draw_about_section(c, width, about, height - 5.25*inch)

    # Specializations
    specs = [
        ("Luxury Hospitality", "Five-star resorts, boutique hotels, property tours, and guest experience storytelling"),
        ("Cultural Travel", "Heritage sites, local traditions, art experiences, and authentic community connections"),
        ("Wellness & Lifestyle", "Spa retreats, mindfulness experiences, holistic travel, and self-care narratives")
    ]
    next_y = draw_specializations(c, specs, next_y - 0.3*inch, width)

    # Brands with logos
    brands = ["Four Seasons", "Park Hyatt", "Onguma", "Intrepid"]
    brand_logos = [
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/four-seasons.png",
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/park-hyatt.png",
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/onguma.png",
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/intrepid.png"
    ]
    draw_brands(c, brands, next_y - 0.3*inch, width, brand_logos)

    # Contact
    draw_contact(c, width, 0)

    c.save()
    print(f"Created: {filename}")

def create_klein_media_kit():
    """Create Klein Nettoh's media kit."""
    filename = "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/media_kits/klein-nettoh-media-kit.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Tags
    tags = ["Wildlife Film", "Conservation", "Safari", "Photography"]

    # Header
    draw_header(c, width, height, "Klein Nettoh", "@klein_nettoh", tags)

    # Stats
    stats = [
        ("870K+", "Travel Views"),
        ("192K", "Engagement"),
        ("59", "Lodge Features"),
        ("228", "Travel Posts")
    ]
    draw_stats_section(c, width, height, stats, height - 3.75*inch)

    # About
    about = "Award-winning wildlife filmmaker and conservation photographer based in Kenya. Klein captures Africa's wilderness through cinematic storytelling, specialising in luxury safari lodges and authentic travel experiences across East and Southern Africa."
    next_y = draw_about_section(c, width, about, height - 5.25*inch)

    # Specializations
    specs = [
        ("Cinematic Film", "Professional wildlife filmmaking with cinematic composition and storytelling techniques"),
        ("Conservation", "Powerful imagery communicating conservation stories and sustainable tourism narratives"),
        ("Safari Lodges", "Specialised experience creating compelling content for luxury safari properties")
    ]
    next_y = draw_specializations(c, specs, next_y - 0.3*inch, width)

    # Brands with logos
    brands = ["The Safari Collection", "Secret Safari", "Giraffe Manor", "Kenya Wildlife Service", "The Enasoit Collection"]
    brand_logos = [
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/The-Safari-Collection-Sketch-Logo.png",
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/logo_secret-safari-gold-updated.png",
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/Giraffe-Manor-Logo-46px.png",
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/kenya-wildlife-service-logo.png",
        "/Users/matthewbenjamin/Documents/nubeaux-collective/assets/brand_logos/the_enasoit_collection.png"
    ]
    draw_brands(c, brands, next_y - 0.3*inch, width, brand_logos)

    # Contact
    draw_contact(c, width, 0)

    c.save()
    print(f"Created: {filename}")

if __name__ == "__main__":
    create_nia_media_kit()
    create_klein_media_kit()
    print("Media kits generated successfully!")
