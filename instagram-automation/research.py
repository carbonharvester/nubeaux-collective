"""
NUBEAUX Collective Instagram Automation - Research Engine

Scrapes competitor accounts and hashtags to identify top-performing content.
Uses Apify for Instagram data collection.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    APIFY_AVAILABLE = False
    print("Warning: apify-client not installed. Run: pip install apify-client")

from config import (
    APIFY_API_KEY,
    APIFY_SETTINGS,
    COMPETITOR_ACCOUNTS,
    TARGET_HASHTAGS,
    DATA_DIR,
)


class InstagramResearcher:
    """Researches Instagram content for competitive analysis."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or APIFY_API_KEY
        if APIFY_AVAILABLE and self.api_key != "your-apify-api-key-here":
            self.client = ApifyClient(self.api_key)
        else:
            self.client = None
            print("Warning: Apify client not initialized. Using mock data.")

    def scrape_profile(self, username: str, limit: int = 50) -> dict:
        """
        Scrape recent posts from an Instagram profile.

        Args:
            username: Instagram username (without @)
            limit: Maximum number of posts to retrieve

        Returns:
            dict with profile info and posts
        """
        if not self.client:
            return self._mock_profile_data(username)

        run_input = {
            "usernames": [username],
            "resultsLimit": limit,
        }

        print(f"Scraping @{username}...")
        run = self.client.actor(APIFY_SETTINGS["profile_scraper_id"]).call(
            run_input=run_input
        )

        # Fetch results
        items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
        return self._process_profile_data(username, items)

    def scrape_hashtag(self, hashtag: str, limit: int = 50) -> dict:
        """
        Scrape top posts from a hashtag.

        Args:
            hashtag: Hashtag to scrape (without #)
            limit: Maximum number of posts to retrieve

        Returns:
            dict with hashtag info and posts
        """
        if not self.client:
            return self._mock_hashtag_data(hashtag)

        run_input = {
            "hashtags": [hashtag],
            "resultsLimit": limit,
        }

        print(f"Scraping #{hashtag}...")
        run = self.client.actor(APIFY_SETTINGS["hashtag_scraper_id"]).call(
            run_input=run_input
        )

        items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
        return self._process_hashtag_data(hashtag, items)

    def _process_profile_data(self, username: str, items: list) -> dict:
        """Process raw Apify data into structured format."""
        posts = []
        for item in items:
            post = {
                "id": item.get("id"),
                "type": item.get("type", "image"),  # image, video, carousel
                "caption": item.get("caption", ""),
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
                "timestamp": item.get("timestamp"),
                "url": item.get("url"),
                "hashtags": self._extract_hashtags(item.get("caption", "")),
                "engagement_rate": self._calculate_engagement(item),
            }
            posts.append(post)

        # Sort by engagement
        posts.sort(key=lambda x: x["engagement_rate"], reverse=True)

        return {
            "username": username,
            "scraped_at": datetime.now().isoformat(),
            "post_count": len(posts),
            "posts": posts,
            "top_hashtags": self._get_top_hashtags(posts),
            "avg_engagement": sum(p["engagement_rate"] for p in posts) / len(posts) if posts else 0,
        }

    def _process_hashtag_data(self, hashtag: str, items: list) -> dict:
        """Process raw hashtag data into structured format."""
        posts = []
        for item in items:
            post = {
                "id": item.get("id"),
                "type": item.get("type", "image"),
                "caption": item.get("caption", ""),
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
                "timestamp": item.get("timestamp"),
                "url": item.get("url"),
                "owner": item.get("ownerUsername"),
                "engagement_rate": self._calculate_engagement(item),
            }
            posts.append(post)

        posts.sort(key=lambda x: x["engagement_rate"], reverse=True)

        return {
            "hashtag": hashtag,
            "scraped_at": datetime.now().isoformat(),
            "post_count": len(posts),
            "posts": posts,
            "avg_engagement": sum(p["engagement_rate"] for p in posts) / len(posts) if posts else 0,
        }

    def _calculate_engagement(self, item: dict) -> float:
        """Calculate engagement rate for a post."""
        likes = item.get("likesCount", 0)
        comments = item.get("commentsCount", 0)
        # Simple engagement score (can be refined with follower count)
        return likes + (comments * 2)  # Comments weighted higher

    def _extract_hashtags(self, caption: str) -> list:
        """Extract hashtags from caption."""
        if not caption:
            return []
        words = caption.split()
        return [w.lower() for w in words if w.startswith("#")]

    def _get_top_hashtags(self, posts: list, limit: int = 20) -> list:
        """Get most frequently used hashtags across posts."""
        hashtag_counts = {}
        for post in posts:
            for tag in post.get("hashtags", []):
                hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1

        sorted_tags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"tag": tag, "count": count} for tag, count in sorted_tags[:limit]]

    def _mock_profile_data(self, username: str) -> dict:
        """Return mock data for testing without API."""
        return {
            "username": username,
            "scraped_at": datetime.now().isoformat(),
            "post_count": 10,
            "posts": [
                {
                    "id": f"mock_{i}",
                    "type": "carousel" if i % 3 == 0 else "image",
                    "caption": f"Sample caption about luxury African travel #{username} #luxurytravel #africa",
                    "likes": 5000 - (i * 200),
                    "comments": 150 - (i * 10),
                    "timestamp": datetime.now().isoformat(),
                    "url": f"https://instagram.com/p/mock{i}",
                    "hashtags": ["#luxurytravel", "#africa", "#safari"],
                    "engagement_rate": 5000 - (i * 200) + (150 - (i * 10)) * 2,
                }
                for i in range(10)
            ],
            "top_hashtags": [
                {"tag": "#luxurytravel", "count": 10},
                {"tag": "#africa", "count": 8},
                {"tag": "#safari", "count": 7},
            ],
            "avg_engagement": 4500,
        }

    def _mock_hashtag_data(self, hashtag: str) -> dict:
        """Return mock data for testing without API."""
        return {
            "hashtag": hashtag,
            "scraped_at": datetime.now().isoformat(),
            "post_count": 10,
            "posts": [
                {
                    "id": f"mock_{hashtag}_{i}",
                    "type": "carousel" if i % 2 == 0 else "image",
                    "caption": f"Amazing experience in Africa! #{hashtag} #travel",
                    "likes": 8000 - (i * 500),
                    "comments": 200 - (i * 15),
                    "timestamp": datetime.now().isoformat(),
                    "url": f"https://instagram.com/p/mock{hashtag}{i}",
                    "owner": f"user_{i}",
                    "engagement_rate": 8000 - (i * 500) + (200 - (i * 15)) * 2,
                }
                for i in range(10)
            ],
            "avg_engagement": 7000,
        }

    def run_full_research(self, save: bool = True) -> dict:
        """
        Run full research across all competitors and hashtags.

        Args:
            save: Whether to save results to disk

        Returns:
            Complete research data
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "competitors": {},
            "hashtags": {},
            "insights": {},
        }

        # Scrape competitor profiles
        print("\n=== Scraping Competitor Profiles ===")
        for username in COMPETITOR_ACCOUNTS:
            try:
                data = self.scrape_profile(username)
                results["competitors"][username] = data
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"Error scraping {username}: {e}")

        # Scrape hashtags
        print("\n=== Scraping Hashtags ===")
        for hashtag in TARGET_HASHTAGS:
            try:
                data = self.scrape_hashtag(hashtag)
                results["hashtags"][hashtag] = data
                time.sleep(2)
            except Exception as e:
                print(f"Error scraping #{hashtag}: {e}")

        # Generate insights
        results["insights"] = self._generate_insights(results)

        if save:
            filename = DATA_DIR / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {filename}")

        return results

    def _generate_insights(self, results: dict) -> dict:
        """Generate insights from research data."""
        all_posts = []

        # Collect all posts
        for data in results["competitors"].values():
            all_posts.extend(data.get("posts", []))
        for data in results["hashtags"].values():
            all_posts.extend(data.get("posts", []))

        if not all_posts:
            return {}

        # Analyze content types
        type_performance = {}
        for post in all_posts:
            post_type = post.get("type", "image")
            if post_type not in type_performance:
                type_performance[post_type] = {"count": 0, "total_engagement": 0}
            type_performance[post_type]["count"] += 1
            type_performance[post_type]["total_engagement"] += post.get("engagement_rate", 0)

        for t in type_performance:
            type_performance[t]["avg_engagement"] = (
                type_performance[t]["total_engagement"] / type_performance[t]["count"]
            )

        # Get top performing posts
        all_posts.sort(key=lambda x: x.get("engagement_rate", 0), reverse=True)
        top_posts = all_posts[:20]

        # Analyze caption lengths
        caption_lengths = [len(p.get("caption", "")) for p in all_posts if p.get("caption")]
        avg_caption_length = sum(caption_lengths) / len(caption_lengths) if caption_lengths else 0

        return {
            "total_posts_analyzed": len(all_posts),
            "content_type_performance": type_performance,
            "top_performing_posts": top_posts,
            "avg_caption_length": avg_caption_length,
            "best_performing_type": max(
                type_performance.items(),
                key=lambda x: x[1]["avg_engagement"]
            )[0] if type_performance else "image",
        }


def main():
    """Run research and display results."""
    researcher = InstagramResearcher()
    results = researcher.run_full_research()

    print("\n" + "=" * 60)
    print("RESEARCH SUMMARY")
    print("=" * 60)

    insights = results.get("insights", {})
    print(f"\nTotal posts analyzed: {insights.get('total_posts_analyzed', 0)}")
    print(f"Average caption length: {insights.get('avg_caption_length', 0):.0f} characters")
    print(f"Best performing content type: {insights.get('best_performing_type', 'N/A')}")

    print("\nContent Type Performance:")
    for content_type, data in insights.get("content_type_performance", {}).items():
        print(f"  {content_type}: {data['avg_engagement']:.0f} avg engagement ({data['count']} posts)")

    print("\nTop 5 Performing Posts:")
    for i, post in enumerate(insights.get("top_performing_posts", [])[:5], 1):
        caption_preview = post.get("caption", "")[:50] + "..." if len(post.get("caption", "")) > 50 else post.get("caption", "")
        print(f"  {i}. {post.get('engagement_rate', 0):.0f} engagement - {caption_preview}")


if __name__ == "__main__":
    main()
