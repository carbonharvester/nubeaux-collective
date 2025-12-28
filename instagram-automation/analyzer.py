"""
NUBEAUX Collective Instagram Automation - Content Analyzer

Analyzes research data using Claude to identify winning patterns
and generate content insights.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic not installed. Run: pip install anthropic")

from config import (
    ANTHROPIC_API_KEY,
    BRAND,
    CONTENT_PILLARS,
    DATA_DIR,
    OUTPUT_DIR,
    GENERATION_SETTINGS,
)


class ContentAnalyzer:
    """Analyzes Instagram content patterns using Claude."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        if ANTHROPIC_AVAILABLE and self.api_key != "your-anthropic-api-key-here":
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: Anthropic client not initialized.")

    def load_latest_research(self) -> Optional[dict]:
        """Load the most recent research data file."""
        research_files = sorted(DATA_DIR.glob("research_*.json"), reverse=True)
        if not research_files:
            print("No research data found. Run research.py first.")
            return None

        with open(research_files[0]) as f:
            return json.load(f)

    def analyze_patterns(self, research_data: dict) -> dict:
        """
        Analyze content patterns from research data.

        Args:
            research_data: Output from research.py

        Returns:
            Pattern analysis results
        """
        if not self.client:
            return self._mock_analysis(research_data)

        # Prepare data summary for Claude
        insights = research_data.get("insights", {})
        top_posts = insights.get("top_performing_posts", [])[:15]

        # Format top posts for analysis
        posts_summary = []
        for i, post in enumerate(top_posts, 1):
            posts_summary.append({
                "rank": i,
                "type": post.get("type"),
                "caption": post.get("caption", "")[:500],
                "engagement": post.get("engagement_rate"),
                "likes": post.get("likes"),
                "comments": post.get("comments"),
            })

        prompt = f"""Analyze these top-performing Instagram posts in the luxury African travel niche.
Identify patterns that make them successful.

TOP PERFORMING POSTS:
{json.dumps(posts_summary, indent=2)}

CONTENT TYPE PERFORMANCE:
{json.dumps(insights.get('content_type_performance', {}), indent=2)}

Provide analysis in JSON format with these sections:
{{
    "hook_patterns": ["list of effective opening hooks/first lines"],
    "caption_structure": "description of ideal caption structure",
    "optimal_length": "recommended caption length range",
    "effective_ctas": ["list of call-to-action phrases that work"],
    "content_themes": ["themes that resonate most"],
    "visual_patterns": ["observations about content types and visuals"],
    "hashtag_insights": "observations about hashtag usage",
    "posting_recommendations": ["specific recommendations for NUBEAUX"],
    "content_gaps": ["opportunities not being addressed by competitors"]
}}

Focus on actionable insights for a brand connecting luxury African properties with creators of colour."""

        response = self.client.messages.create(
            model=GENERATION_SETTINGS["model"],
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        try:
            response_text = response.content[0].text
            # Try to extract JSON from response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            analysis = json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            analysis = {"raw_response": response_text}

        return {
            "timestamp": datetime.now().isoformat(),
            "posts_analyzed": len(top_posts),
            "analysis": analysis,
        }

    def generate_content_brief(self, analysis: dict, pillar: str) -> dict:
        """
        Generate a content brief based on analysis.

        Args:
            analysis: Pattern analysis results
            pillar: Content pillar (market_intelligence, creator_campaign, aspirational_travel)

        Returns:
            Content brief with post concepts
        """
        if not self.client:
            return self._mock_content_brief(pillar)

        pillar_info = CONTENT_PILLARS.get(pillar, CONTENT_PILLARS["market_intelligence"])

        prompt = f"""Generate 3 Instagram post concepts for NUBEAUX Collective.

BRAND CONTEXT:
- Name: {BRAND['name']}
- Tagline: {BRAND['tagline']}
- Voice: {BRAND['voice']}
- Mission: Connecting Africa's luxury properties with creators of colour

CONTENT PILLAR: {pillar}
- Description: {pillar_info['description']}
- Examples: {', '.join(pillar_info['examples'])}

WINNING PATTERNS FROM ANALYSIS:
{json.dumps(analysis.get('analysis', {}), indent=2)}

Generate 3 post concepts in JSON format:
{{
    "posts": [
        {{
            "concept": "Brief description of the post concept",
            "hook": "The opening line/hook for the caption",
            "caption": "Full caption (150-300 words)",
            "hashtags": ["list", "of", "15", "relevant", "hashtags"],
            "visual_direction": "Description of the ideal image/carousel",
            "template_type": "stat_post|quote_post|destination|creator_spotlight|carousel_educational|carousel_listicle|behind_scenes|announcement",
            "cta": "Call to action"
        }}
    ]
}}

Make captions compelling, on-brand, and optimized for engagement based on the patterns identified."""

        response = self.client.messages.create(
            model=GENERATION_SETTINGS["model"],
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            response_text = response.content[0].text
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            brief = json.loads(json_str)
        except (json.JSONDecodeError, IndexError):
            brief = {"raw_response": response_text}

        return {
            "timestamp": datetime.now().isoformat(),
            "pillar": pillar,
            "brief": brief,
        }

    def _mock_analysis(self, research_data: dict) -> dict:
        """Return mock analysis for testing without API."""
        return {
            "timestamp": datetime.now().isoformat(),
            "posts_analyzed": 15,
            "analysis": {
                "hook_patterns": [
                    "Start with a bold statistic",
                    "Ask a thought-provoking question",
                    "Use 'The truth about...' format",
                    "Lead with transformation/before-after",
                ],
                "caption_structure": "Hook (1 line) -> Story/Context (2-3 lines) -> Value/Insight (2-3 lines) -> CTA (1 line)",
                "optimal_length": "150-300 characters for single images, 500-1000 for carousels",
                "effective_ctas": [
                    "Save this for your next trip",
                    "Tag someone who needs to see this",
                    "Drop a [emoji] if you agree",
                    "Link in bio for more",
                ],
                "content_themes": [
                    "Underrepresented luxury experiences",
                    "Heritage/roots travel",
                    "Behind-the-scenes authenticity",
                    "Data-backed insights",
                ],
                "visual_patterns": [
                    "Carousels outperform single images by 2x",
                    "People in photos increase engagement",
                    "Warm, golden hour lighting performs best",
                    "Minimalist design with bold text overlays",
                ],
                "hashtag_insights": "Mix of broad (500K-1M posts) and niche (10K-100K posts) hashtags",
                "posting_recommendations": [
                    "Focus on carousels for educational content",
                    "Feature creators prominently",
                    "Lead with data/stats for market content",
                    "Use terracotta/gold brand colors in graphics",
                ],
                "content_gaps": [
                    "Lack of content about the business case for diversity",
                    "Few brands showing real creator partnerships",
                    "Opportunity to own 'luxury + representation' space",
                ],
            },
        }

    def _mock_content_brief(self, pillar: str) -> dict:
        """Return mock content brief for testing."""
        briefs = {
            "market_intelligence": {
                "posts": [
                    {
                        "concept": "The $4.2 trillion diaspora travel opportunity",
                        "hook": "The travel industry is leaving $4.2 trillion on the table.",
                        "caption": "The travel industry is leaving $4.2 trillion on the table.\n\nThe African diaspora represents over 200 million potential travellers, with disposable income and a deep desire to connect with the continent.\n\nYet most luxury African properties still market exclusively to European and American audiences, using imagery that doesn't reflect this massive market.\n\nThe solution isn't complicated:\n- Authentic representation in brand assets\n- Creator partnerships with cultural resonance\n- Marketing that speaks TO the diaspora, not ABOUT Africa\n\nRepresentation isn't just the right thing to do—it's the profitable thing to do.\n\nWe're here to bridge that gap.",
                        "hashtags": ["#nubeauxcollective", "#diasporatravel", "#luxuryafricantravel", "#representationmatters", "#blackluxurytravel", "#africanexcellence", "#heritagetourism", "#africansafari", "#luxurytravel", "#travelmarketing", "#diversityintravel", "#blacktravel", "#africantourism", "#travelindustry", "#marketopportunity"],
                        "visual_direction": "Bold stat graphic with '$4.2 TRILLION' in large Playfair Display on charcoal background with terracotta accent. Secondary slides showing diaspora statistics.",
                        "template_type": "stat_post",
                        "cta": "Save this for your next strategy meeting."
                    }
                ]
            },
            "creator_campaign": {
                "posts": [
                    {
                        "concept": "Meet our creator: Behind the lens with Klein",
                        "hook": "This is what happens when you give African creatives the platform they deserve.",
                        "caption": "This is what happens when you give African creatives the platform they deserve.\n\nMeet Klein (@kleinnettoh), cinematographer and photographer bringing luxury African properties to life through a lens that understands both excellence and authenticity.\n\nFrom the golden light of Namibian sunsets to the intimate moments at boutique safari lodges, Klein captures what many brands miss: the soul of African luxury.\n\nThis January, Klein joins us on our Southern Africa campaign—19 days, 5 countries, world-class properties.\n\nThe talent has always been here. Now it's getting the spotlight.",
                        "hashtags": ["#nubeauxcollective", "#creatorsofcolour", "#africancreatives", "#travelcreator", "#cinematographer", "#luxuryphotography", "#safariphotography", "#africanexcellence", "#creatorspotlight", "#behindthelens", "#contentcreator", "#travelphotography", "#namibia", "#southernafrica", "#luxurytravel"],
                        "visual_direction": "Portrait of Klein with camera, warm natural lighting. Could be a carousel with: 1) Portrait, 2-4) Best work samples, 5) Campaign announcement graphic.",
                        "template_type": "creator_spotlight",
                        "cta": "Follow the journey this January."
                    }
                ]
            },
            "aspirational_travel": {
                "posts": [
                    {
                        "concept": "5 Luxury Lodges Redefining African Safari",
                        "hook": "Safari, but make it fashion.",
                        "caption": "Safari, but make it fashion.\n\nThese 5 properties are redefining what luxury looks like on the African continent:\n\n1. Singita Sabora - Where tented camp meets haute couture\n2. &Beyond Sossusvlei - Desert minimalism at its finest\n3. Royal Malewane - Big Five meets fine dining\n4. One&Only Gorilla's Nest - Mountain luxury, conservation soul\n5. Bisate Lodge - Volcanic views, volcanic prices (worth every penny)\n\nThe common thread? Properties that understand luxury isn't just thread count—it's experience, authenticity, and increasingly, representation.\n\nWhich one's going on your list?",
                        "hashtags": ["#nubeauxcollective", "#luxurysafari", "#africanlodges", "#safarilodge", "#luxurytravel", "#africanluxury", "#singita", "#andbeyond", "#oneandonly", "#boutiquehotels", "#travellist", "#bucketlist", "#safarilife", "#africantravel", "#luxuryexperiences"],
                        "visual_direction": "Carousel with cover slide ('5 Lodges Redefining African Safari') followed by one stunning image per property with name overlay in brand fonts.",
                        "template_type": "carousel_listicle",
                        "cta": "Save this for your 2025 planning."
                    }
                ]
            },
        }
        return {
            "timestamp": datetime.now().isoformat(),
            "pillar": pillar,
            "brief": briefs.get(pillar, briefs["market_intelligence"]),
        }

    def run_full_analysis(self, save: bool = True) -> dict:
        """
        Run complete analysis and generate briefs for all pillars.

        Args:
            save: Whether to save results to disk

        Returns:
            Complete analysis with content briefs
        """
        research_data = self.load_latest_research()
        if not research_data:
            # Use empty data structure
            research_data = {"insights": {}}

        print("\n=== Analyzing Content Patterns ===")
        analysis = self.analyze_patterns(research_data)

        print("\n=== Generating Content Briefs ===")
        briefs = {}
        for pillar in CONTENT_PILLARS.keys():
            print(f"  Generating brief for: {pillar}")
            briefs[pillar] = self.generate_content_brief(analysis, pillar)

        results = {
            "timestamp": datetime.now().isoformat(),
            "pattern_analysis": analysis,
            "content_briefs": briefs,
        }

        if save:
            filename = OUTPUT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {filename}")

        return results


def main():
    """Run analysis and display results."""
    analyzer = ContentAnalyzer()
    results = analyzer.run_full_analysis()

    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)

    analysis = results.get("pattern_analysis", {}).get("analysis", {})

    print("\nWinning Hook Patterns:")
    for hook in analysis.get("hook_patterns", [])[:5]:
        print(f"  - {hook}")

    print("\nContent Themes That Resonate:")
    for theme in analysis.get("content_themes", []):
        print(f"  - {theme}")

    print("\nRecommendations for NUBEAUX:")
    for rec in analysis.get("posting_recommendations", []):
        print(f"  - {rec}")

    print("\n" + "=" * 60)
    print("GENERATED CONTENT BRIEFS")
    print("=" * 60)

    for pillar, brief_data in results.get("content_briefs", {}).items():
        print(f"\n[{pillar.upper()}]")
        posts = brief_data.get("brief", {}).get("posts", [])
        for i, post in enumerate(posts, 1):
            print(f"\n  Post {i}: {post.get('concept', 'N/A')}")
            print(f"  Hook: {post.get('hook', 'N/A')}")
            print(f"  Template: {post.get('template_type', 'N/A')}")


if __name__ == "__main__":
    main()
