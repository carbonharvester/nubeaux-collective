#!/usr/bin/env python3
"""
NUBEAUX Collective Instagram Automation - Main Orchestrator

Run this script to execute the full content pipeline:
1. Research competitor content
2. Analyze patterns
3. Generate content briefs
4. Output ready-to-post content

Usage:
    python main.py              # Run full pipeline
    python main.py --research   # Only run research
    python main.py --analyze    # Only run analysis
    python main.py --generate   # Only generate content
    python main.py --sample     # Generate sample content (no API needed)
"""
import argparse
import sys
from datetime import datetime

from config import APIFY_API_KEY, ANTHROPIC_API_KEY


def check_dependencies():
    """Check if required packages are installed."""
    missing = []

    try:
        import anthropic
    except ImportError:
        missing.append("anthropic")

    try:
        from apify_client import ApifyClient
    except ImportError:
        missing.append("apify-client")

    if missing:
        print("Missing dependencies. Install with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    return True


def check_api_keys():
    """Check if API keys are configured."""
    issues = []

    if APIFY_API_KEY == "your-apify-api-key-here":
        issues.append("APIFY_API_KEY not set")

    if ANTHROPIC_API_KEY == "your-anthropic-api-key-here":
        issues.append("ANTHROPIC_API_KEY not set")

    if issues:
        print("API key issues:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nSet keys in config.py or as environment variables.")
        print("You can still run with --sample for demo content.")
        return False
    return True


def run_research():
    """Run the research phase."""
    from research import InstagramResearcher

    print("\n" + "=" * 60)
    print("PHASE 1: RESEARCH")
    print("=" * 60)

    researcher = InstagramResearcher()
    results = researcher.run_full_research()

    print(f"\nResearch complete. Analyzed {results.get('insights', {}).get('total_posts_analyzed', 0)} posts.")
    return results


def run_analysis():
    """Run the analysis phase."""
    from analyzer import ContentAnalyzer

    print("\n" + "=" * 60)
    print("PHASE 2: ANALYSIS")
    print("=" * 60)

    analyzer = ContentAnalyzer()
    results = analyzer.run_full_analysis()

    print("\nAnalysis complete.")
    return results


def run_generation():
    """Run the content generation phase."""
    from generator import ContentGenerator

    print("\n" + "=" * 60)
    print("PHASE 3: CONTENT GENERATION")
    print("=" * 60)

    generator = ContentGenerator()
    weekly_content = generator.generate_weekly_content()

    if not weekly_content:
        print("No content generated. Using sample content...")
        from generator import generate_sample_week
        weekly_content = generate_sample_week()

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

    return weekly_content


def run_sample():
    """Generate sample content without API calls."""
    from generator import ContentGenerator, generate_sample_week

    print("\n" + "=" * 60)
    print("GENERATING SAMPLE CONTENT")
    print("=" * 60)

    weekly_content = generate_sample_week()

    generator = ContentGenerator()
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

    return weekly_content


def display_content(content):
    """Display generated content in a readable format."""
    print("\n" + "=" * 60)
    print("GENERATED CONTENT")
    print("=" * 60)

    for post in content:
        print(f"\n{'─' * 50}")
        print(f"📅 {post['scheduled_day']} ({post['scheduled_date']})")
        print(f"📂 Pillar: {post['pillar']}")
        print(f"💡 Concept: {post['concept']}")
        print(f"🎯 Template: {post['template_type']}")
        print(f"\n🪝 HOOK:")
        print(f"   {post['hook']}")
        print(f"\n📝 CAPTION:")
        for line in post['caption'].split('\n'):
            print(f"   {line}")
        print(f"\n🖼️  VISUAL DIRECTION:")
        print(f"   {post['visual_direction']}")
        print(f"\n#️⃣  HASHTAGS:")
        print(f"   {post['hashtag_string']}")


def main():
    parser = argparse.ArgumentParser(
        description="NUBEAUX Instagram Content Automation"
    )
    parser.add_argument(
        "--research", action="store_true",
        help="Run only the research phase"
    )
    parser.add_argument(
        "--analyze", action="store_true",
        help="Run only the analysis phase"
    )
    parser.add_argument(
        "--generate", action="store_true",
        help="Run only the generation phase"
    )
    parser.add_argument(
        "--sample", action="store_true",
        help="Generate sample content (no API keys needed)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress detailed output"
    )

    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     NUBEAUX COLLECTIVE - Instagram Content Automation     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Check dependencies
    if not check_dependencies():
        print("\nInstall missing dependencies and try again.")
        sys.exit(1)

    # Handle sample mode (no API keys needed)
    if args.sample:
        content = run_sample()
        if not args.quiet:
            display_content(content)
        print("\n✅ Sample content generated successfully!")
        print("\nNext steps:")
        print("  1. Review the generated content in instagram-automation/output/")
        print("  2. Create Canva designs based on visual directions")
        print("  3. Schedule in Later or post directly to Instagram")
        sys.exit(0)

    # Check API keys for non-sample modes
    if not check_api_keys():
        print("\nRun with --sample to generate demo content without API keys.")
        sys.exit(1)

    # Run specific phases or full pipeline
    if args.research:
        run_research()
    elif args.analyze:
        run_analysis()
    elif args.generate:
        content = run_generation()
        if not args.quiet:
            display_content(content)
    else:
        # Full pipeline
        print("Running full content pipeline...")
        run_research()
        run_analysis()
        content = run_generation()
        if not args.quiet:
            display_content(content)

    print("\n✅ Pipeline complete!")
    print("\nNext steps:")
    print("  1. Review generated content in instagram-automation/output/")
    print("  2. Create Canva designs based on visual directions")
    print("  3. Import CSV to Notion for content calendar")
    print("  4. Schedule approved content in Later")


if __name__ == "__main__":
    main()
