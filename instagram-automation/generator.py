"""
NUBEAUX Collective Instagram Automation - Content Generator

Generates ready-to-post content based on analysis and briefs.
Outputs formatted content for Canva and scheduling.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from config import (
    BRAND,
    CONTENT_PILLARS,
    POSTING_SCHEDULE,
    HASHTAG_SETS,
    OUTPUT_DIR,
    GENERATION_SETTINGS,
)


class ContentGenerator:
    """Generates Instagram content ready for posting."""

    def __init__(self):
        self.output_dir = OUTPUT_DIR

    def load_latest_analysis(self) -> Optional[dict]:
        """Load the most recent analysis file."""
        analysis_files = sorted(OUTPUT_DIR.glob("analysis_*.json"), reverse=True)
        if not analysis_files:
            print("No analysis data found. Run analyzer.py first.")
            return None

        with open(analysis_files[0]) as f:
            return json.load(f)

    def generate_weekly_content(self, start_date: Optional[datetime] = None) -> List[dict]:
        """
        Generate a week's worth of content.

        Args:
            start_date: Starting date for the content calendar

        Returns:
            List of content items ready for posting
        """
        if start_date is None:
            # Start from next Monday
            today = datetime.now()
            days_ahead = 7 - today.weekday()  # Days until next Monday
            if days_ahead <= 0:
                days_ahead += 7
            start_date = today + timedelta(days=days_ahead)

        analysis = self.load_latest_analysis()
        content_briefs = analysis.get("content_briefs", {}) if analysis else {}

        weekly_content = []
        current_date = start_date

        for day_name, pillar in POSTING_SCHEDULE.items():
            # Find the next occurrence of this day
            while current_date.strftime("%A") != day_name:
                current_date += timedelta(days=1)

            # Get content for this pillar
            if pillar == "carousel":
                # Alternate between educational and listicle carousels
                pillar_key = "aspirational_travel"
            else:
                pillar_key = pillar

            brief = content_briefs.get(pillar_key, {}).get("brief", {})
            posts = brief.get("posts", [])

            if posts:
                post = posts[0]  # Take first post from brief
                content_item = self._format_post(post, current_date, pillar)
                weekly_content.append(content_item)

            current_date += timedelta(days=1)

        return weekly_content

    def _format_post(self, post: dict, post_date: datetime, pillar: str) -> dict:
        """Format a post for output."""
        # Build hashtag string
        post_hashtags = post.get("hashtags", [])
        if len(post_hashtags) < 15:
            # Add from hashtag sets
            post_hashtags.extend(HASHTAG_SETS["core"])
            if pillar == "market_intelligence":
                post_hashtags.extend(HASHTAG_SETS["market"][:3])
            elif pillar == "creator_campaign":
                post_hashtags.extend(HASHTAG_SETS["creator"][:3])
            else:
                post_hashtags.extend(HASHTAG_SETS["travel"][:3])

        # Deduplicate and limit
        seen = set()
        unique_hashtags = []
        for tag in post_hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_hashtags.append(tag if tag.startswith("#") else f"#{tag}")
        unique_hashtags = unique_hashtags[:GENERATION_SETTINGS["hashtags_per_post"]]

        return {
            "id": f"post_{post_date.strftime('%Y%m%d')}_{pillar[:3]}",
            "scheduled_date": post_date.strftime("%Y-%m-%d"),
            "scheduled_day": post_date.strftime("%A"),
            "pillar": pillar,
            "concept": post.get("concept", ""),
            "hook": post.get("hook", ""),
            "caption": post.get("caption", ""),
            "hashtags": unique_hashtags,
            "hashtag_string": " ".join(unique_hashtags),
            "full_caption": f"{post.get('caption', '')}\n\n.\n.\n.\n{' '.join(unique_hashtags)}",
            "visual_direction": post.get("visual_direction", ""),
            "template_type": post.get("template_type", ""),
            "cta": post.get("cta", ""),
            "status": "draft",
            "canva_link": "",  # To be filled after creating in Canva
        }

    def generate_content_calendar(self, weeks: int = 4) -> dict:
        """
        Generate a multi-week content calendar.

        Args:
            weeks: Number of weeks to generate

        Returns:
            Content calendar with all posts
        """
        all_content = []
        current_start = datetime.now()

        for week in range(weeks):
            weekly = self.generate_weekly_content(current_start)
            all_content.extend(weekly)
            current_start += timedelta(weeks=1)

        calendar = {
            "generated_at": datetime.now().isoformat(),
            "weeks": weeks,
            "total_posts": len(all_content),
            "posts": all_content,
        }

        return calendar

    def export_for_notion(self, calendar: dict) -> str:
        """
        Export calendar in a format suitable for Notion import.

        Args:
            calendar: Content calendar dict

        Returns:
            CSV string for Notion import
        """
        lines = [
            "Date,Day,Pillar,Concept,Hook,Caption,Hashtags,Template,Visual Direction,Status"
        ]

        for post in calendar.get("posts", []):
            line = [
                post.get("scheduled_date", ""),
                post.get("scheduled_day", ""),
                post.get("pillar", ""),
                f'"{post.get("concept", "")}"',
                f'"{post.get("hook", "")}"',
                f'"{post.get("caption", "").replace(chr(10), " ").replace(chr(34), chr(39))}"',
                f'"{post.get("hashtag_string", "")}"',
                post.get("template_type", ""),
                f'"{post.get("visual_direction", "")}"',
                post.get("status", "draft"),
            ]
            lines.append(",".join(line))

        return "\n".join(lines)

    def export_for_later(self, calendar: dict) -> List[dict]:
        """
        Export calendar in a format for Later bulk upload.

        Args:
            calendar: Content calendar dict

        Returns:
            List of posts formatted for Later
        """
        later_posts = []
        for post in calendar.get("posts", []):
            later_posts.append({
                "caption": post.get("full_caption", ""),
                "scheduled_time": f"{post.get('scheduled_date')}T10:00:00",  # 10 AM default
                "media_url": "",  # To be filled with Canva export
            })
        return later_posts

    def save_weekly_content(self, content: List[dict]) -> Path:
        """Save weekly content to output directory."""
        filename = OUTPUT_DIR / f"weekly_content_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, "w") as f:
            json.dump(content, f, indent=2)
        return filename

    def save_calendar(self, calendar: dict, include_csv: bool = True) -> dict:
        """
        Save content calendar to output directory.

        Args:
            calendar: Content calendar dict
            include_csv: Whether to also save CSV for Notion

        Returns:
            Dict with file paths
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        paths = {}

        # Save JSON
        json_path = OUTPUT_DIR / f"calendar_{timestamp}.json"
        with open(json_path, "w") as f:
            json.dump(calendar, f, indent=2)
        paths["json"] = str(json_path)

        # Save CSV for Notion
        if include_csv:
            csv_path = OUTPUT_DIR / f"calendar_{timestamp}.csv"
            csv_content = self.export_for_notion(calendar)
            with open(csv_path, "w") as f:
                f.write(csv_content)
            paths["csv"] = str(csv_path)

        return paths


def generate_sample_week():
    """Generate sample content for the first week."""
    # This creates mock content without needing API calls
    sample_posts = [
        {
            "id": "post_20250106_mar",
            "scheduled_date": "2025-01-06",
            "scheduled_day": "Monday",
            "pillar": "market_intelligence",
            "concept": "The $4.2 trillion diaspora travel opportunity",
            "hook": "The travel industry is leaving $4.2 trillion on the table.",
            "caption": """The travel industry is leaving $4.2 trillion on the table.

The African diaspora represents over 200 million potential travellers, with disposable income and a deep desire to connect with the continent.

Yet most luxury African properties still market exclusively to European and American audiences, using imagery that doesn't reflect this massive market.

The solution isn't complicated:
- Authentic representation in brand assets
- Creator partnerships with cultural resonance
- Marketing that speaks TO the diaspora, not ABOUT Africa

Representation isn't just the right thing to do—it's the profitable thing to do.

We're here to bridge that gap.""",
            "hashtags": ["#nubeauxcollective", "#diasporatravel", "#luxuryafricantravel", "#representationmatters", "#blackluxurytravel", "#africanexcellence", "#heritagetourism", "#africansafari", "#luxurytravel", "#travelmarketing", "#diversityintravel", "#blacktravel", "#africantourism", "#travelindustry", "#marketopportunity"],
            "visual_direction": "Bold stat graphic with '$4.2 TRILLION' in large Playfair Display on charcoal background with terracotta accent line. Could be carousel with supporting stats.",
            "template_type": "stat_post",
            "cta": "Save this for your next strategy meeting.",
            "status": "draft",
        },
        {
            "id": "post_20250108_cre",
            "scheduled_date": "2025-01-08",
            "scheduled_day": "Wednesday",
            "pillar": "creator_campaign",
            "concept": "Meet Klein: Behind the lens of African luxury",
            "hook": "This is what happens when you give African creatives the platform they deserve.",
            "caption": """This is what happens when you give African creatives the platform they deserve.

Meet Klein (@kleinnettoh), cinematographer and photographer bringing luxury African properties to life through a lens that understands both excellence and authenticity.

From the golden light of Namibian sunsets to the intimate moments at boutique safari lodges, Klein captures what many brands miss: the soul of African luxury.

This January, Klein joins us on our Southern Africa campaign—19 days, 5 countries, world-class properties.

The talent has always been here. Now it's getting the spotlight.""",
            "hashtags": ["#nubeauxcollective", "#creatorsofcolour", "#africancreatives", "#travelcreator", "#cinematographer", "#luxuryphotography", "#safariphotography", "#africanexcellence", "#creatorspotlight", "#behindthelens", "#contentcreator", "#travelphotography", "#namibia", "#southernafrica", "#luxurytravel"],
            "visual_direction": "Portrait of Klein with camera gear, warm natural lighting. Carousel: 1) Portrait, 2-4) Best work samples showcasing luxury properties, 5) Campaign announcement slide with dates.",
            "template_type": "creator_spotlight",
            "cta": "Follow the journey this January.",
            "status": "draft",
        },
        {
            "id": "post_20250110_asp",
            "scheduled_date": "2025-01-10",
            "scheduled_day": "Friday",
            "pillar": "aspirational_travel",
            "concept": "Onguma Camp Kala: Where Namibian wilderness meets luxury",
            "hook": "Some places change you. This is one of them.",
            "caption": """Some places change you. This is one of them.

Onguma Camp Kala sits on the edge of Etosha—Namibia's crown jewel of wildlife. But it's not just about the Big Five.

It's the silence at sunrise.
It's the way the light paints the salt pan gold.
It's luxury that feels earned, not manufactured.

This January, we're bringing creators here to capture what brochures can't: the feeling of being somewhere that matters.

Properties like Onguma understand something crucial—authentic storytelling requires authentic storytellers.

That's where we come in.""",
            "hashtags": ["#nubeauxcollective", "#onguma", "#namibia", "#etosha", "#safarilodge", "#africanluxury", "#luxurysafari", "#wildlifelodge", "#africansafari", "#luxurytravel", "#boutiquehotel", "#sustainabletravel", "#africandestination", "#travelphotography", "#wanderlust"],
            "visual_direction": "Stunning hero shot of Onguma - either the lodge at golden hour or wildlife at the waterhole. Carousel could include: exterior, room interior, dining, wildlife, landscape.",
            "template_type": "destination",
            "cta": "Save for your Namibia wishlist.",
            "status": "draft",
        },
        {
            "id": "post_20250112_car",
            "scheduled_date": "2025-01-12",
            "scheduled_day": "Sunday",
            "pillar": "carousel",
            "concept": "5 Luxury Lodges Redefining African Safari",
            "hook": "Safari, but make it fashion.",
            "caption": """Safari, but make it fashion.

These 5 properties are redefining what luxury looks like on the African continent:

1. Singita Sabora - Where tented camp meets haute couture
2. &Beyond Sossusvlei - Desert minimalism at its finest
3. Royal Malewane - Big Five meets fine dining
4. One&Only Gorilla's Nest - Mountain luxury, conservation soul
5. Bisate Lodge - Volcanic views, volcanic prices (worth every penny)

The common thread? Properties that understand luxury isn't just thread count—it's experience, authenticity, and increasingly, representation.

Which one's going on your list?""",
            "hashtags": ["#nubeauxcollective", "#luxurysafari", "#africanlodges", "#safarilodge", "#luxurytravel", "#africanluxury", "#singita", "#andbeyond", "#oneandonly", "#boutiquehotels", "#travellist", "#bucketlist", "#safarilife", "#africantravel", "#luxuryexperiences"],
            "visual_direction": "Carousel with 6 slides: 1) Cover with title in brand fonts on charcoal, 2-6) One stunning image per property with name and one-line description overlay. Use terracotta accent color for numbering.",
            "template_type": "carousel_listicle",
            "cta": "Save this for your 2025 planning.",
            "status": "draft",
        },
    ]

    # Add full captions with hashtags
    for post in sample_posts:
        post["hashtag_string"] = " ".join(post["hashtags"])
        post["full_caption"] = f"{post['caption']}\n\n.\n.\n.\n{post['hashtag_string']}"

    return sample_posts


def main():
    """Generate and display weekly content."""
    generator = ContentGenerator()

    # Try to generate from analysis, fall back to samples
    print("\n=== Generating Weekly Content ===")

    try:
        weekly_content = generator.generate_weekly_content()
        if not weekly_content:
            print("No analysis found. Using sample content...")
            weekly_content = generate_sample_week()
    except Exception as e:
        print(f"Error generating from analysis: {e}")
        print("Using sample content...")
        weekly_content = generate_sample_week()

    # Save content
    calendar = {
        "generated_at": datetime.now().isoformat(),
        "weeks": 1,
        "total_posts": len(weekly_content),
        "posts": weekly_content,
    }

    paths = generator.save_calendar(calendar)
    print(f"\nContent saved to:")
    for format_type, path in paths.items():
        print(f"  {format_type.upper()}: {path}")

    # Display summary
    print("\n" + "=" * 60)
    print("WEEKLY CONTENT PLAN")
    print("=" * 60)

    for post in weekly_content:
        print(f"\n{post['scheduled_day']} ({post['scheduled_date']})")
        print(f"  Pillar: {post['pillar']}")
        print(f"  Concept: {post['concept']}")
        print(f"  Hook: {post['hook']}")
        print(f"  Template: {post['template_type']}")
        print(f"  CTA: {post['cta']}")

    print("\n" + "=" * 60)
    print("FULL CAPTIONS (Copy for Later/Instagram)")
    print("=" * 60)

    for post in weekly_content:
        print(f"\n{'='*40}")
        print(f"{post['scheduled_day'].upper()} - {post['concept']}")
        print(f"{'='*40}")
        print(post['full_caption'])


if __name__ == "__main__":
    main()
