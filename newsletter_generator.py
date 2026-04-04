import feedparser
import requests
import os
from datetime import datetime, timedelta
import json
import re
from urllib.parse import quote

# Configuration
TOPICS = ["artificial intelligence", "product management", "business strategy"]
RECIPIENT_EMAIL = "mohinachadha.mac@gmail.com"
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

# High-quality RSS feeds for trending content
RSS_FEEDS = {
    "HackerNews": "https://news.ycombinator.com/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Reuters": "https://feeds.reuters.com/technology",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "MIT Technology Review": "https://www.technologyreview.com/feed.rss",
    "Wired": "https://www.wired.com/feed/rss",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "CNBC": "https://feeds.cnbc.com/id/100003114/",
    "FastCompany": "https://www.fastcompany.com/rss/",
}

# Google News RSS feeds (highly relevant, trending)
GOOGLE_NEWS_TOPICS = [
    "artificial intelligence",
    "product management", 
    "business strategy",
    "AI news",
    "startups",
    "technology trends"
]

def get_google_news_feeds():
    """Generate Google News RSS feeds for each topic"""
    feeds = {}
    for topic in GOOGLE_NEWS_TOPICS:
        encoded_topic = quote(topic)
        feeds[f"Google News - {topic}"] = f"https://news.google.com/rss/search?q={encoded_topic}"
    return feeds

def fetch_rss_articles():
    """Fetch articles from all RSS feeds"""
    articles = []
    all_feeds = {**RSS_FEEDS, **get_google_news_feeds()}
    
    for source_name, feed_url in all_feeds.items():
        try:
            print(f"  ✓ Fetching from {source_name}...")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:5]:  # Top 5 from each feed
                article = {
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": clean_html(entry.get("summary", ""))[:200],
                    "source": source_name,
                    "published": entry.get("published", ""),
                    "image": extract_image(entry),
                    "type": "rss",
                }
                
                # Only add if title exists
                if article["title"]:
                    articles.append(article)
        except Exception as e:
            print(f"  ✗ Error fetching from {source_name}: {str(e)[:50]}")
    
    return articles

def fetch_newsapi_articles():
    """Fetch from NewsAPI for better trending data (optional)"""
    news_api_key = os.environ.get("NEWS_API_KEY")
    if not news_api_key:
        print("  ⓘ NewsAPI disabled (no API key). Set NEWS_API_KEY env variable for better results.")
        return []
    
    articles = []
    
    # Search for each topic with trending/latest sort
    for topic in TOPICS:
        try:
            url = f"https://newsapi.org/v2/everything?q={quote(topic)}&sortBy=popularity&language=en&pageSize=5"
            headers = {"Authorization": f"Bearer {news_api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ NewsAPI found {len(data.get('articles', []))} articles on '{topic}'")
                
                for item in data.get("articles", []):
                    article = {
                        "title": item.get("title", ""),
                        "link": item.get("url", ""),
                        "summary": item.get("description", "")[:200],
                        "source": item.get("source", {}).get("name", "News Source"),
                        "published": item.get("publishedAt", ""),
                        "image": item.get("urlToImage", "https://via.placeholder.com/300x200?text=Article"),
                        "type": "newsapi",
                    }
                    
                    if article["title"]:
                        articles.append(article)
        except Exception as e:
            print(f"  ✗ Error fetching from NewsAPI for '{topic}': {str(e)[:50]}")
    
    return articles

def fetch_hackernews_top():
    """Fetch top/trending stories from HackerNews API (real-time trending)"""
    articles = []
    try:
        print("  ✓ Fetching HackerNews top stories...")
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            top_story_ids = response.json()[:30]  # Top 30
            
            for story_id in top_story_ids[:10]:  # Process top 10
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=5)
                
                if story_response.status_code == 200:
                    story = story_response.json()
                    
                    # Filter for AI, PM, Business keywords
                    title = story.get("title", "").lower()
                    if any(topic in title for topic in TOPICS):
                        article = {
                            "title": story.get("title", ""),
                            "link": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                            "summary": f"By {story.get('by', 'unknown')} • {story.get('score', 0)} points • {story.get('descendants', 0)} comments",
                            "source": f"HackerNews (Trending)",
                            "published": datetime.fromtimestamp(story.get("time", 0)).strftime("%Y-%m-%d"),
                            "image": "https://news.ycombinator.com/y18.svg",
                            "type": "hackernews",
                            "score": story.get("score", 0),
                        }
                        articles.append(article)
    except Exception as e:
        print(f"  ✗ Error fetching HackerNews: {str(e)[:50]}")
    
    return articles

def clean_html(text):
    """Remove HTML tags from text"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

def extract_image(entry):
    """Extract image from RSS entry if available"""
    try:
        if hasattr(entry, "media_content") and entry.media_content:
            return entry.media_content[0].get("url", "")
        elif hasattr(entry, "image"):
            return entry.image.get("href", "")
    except:
        pass
    return "https://via.placeholder.com/300x200?text=Article"

def score_article(article):
    """Score article for relevance and recency"""
    score = 0
    
    # Recency boost (published today = +10)
    try:
        pub_date = datetime.fromisoformat(article["published"].replace('Z', '+00:00'))
        days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
        if days_old == 0:
            score += 10
        elif days_old == 1:
            score += 5
    except:
        pass
    
    # Source authority boost
    trusted_sources = [
        "HackerNews", "TechCrunch", "Reuters", "MIT Technology Review",
        "Bloomberg", "The Verge", "CNBC", "FastCompany", "Google News"
    ]
    if any(source in article["source"] for source in trusted_sources):
        score += 3
    
    # Topic relevance
    title_lower = article["title"].lower()
    for topic in TOPICS:
        if topic in title_lower:
            score += 5
    
    # HackerNews engagement boost
    if article.get("score"):
        score += min(article["score"] // 10, 5)
    
    article["_score"] = score
    return article

def filter_and_rank_articles(articles):
    """Filter by topic relevance and rank by score"""
    filtered = []
    seen_titles = set()
    
    for article in articles:
        # Skip if we've seen this title
        normalized_title = article["title"].lower().strip()
        if normalized_title in seen_titles:
            continue
        
        # Check if article is relevant to our topics
        title_lower = article["title"].lower()
        summary_lower = article["summary"].lower()
        content = title_lower + " " + summary_lower
        
        is_relevant = any(topic in content for topic in TOPICS)
        
        if is_relevant or article.get("type") == "hackernews":
            seen_titles.add(normalized_title)
            article = score_article(article)
            filtered.append(article)
    
    # Sort by score (descending)
    filtered.sort(key=lambda x: x.get("_score", 0), reverse=True)
    
    return filtered

def select_top_articles(articles, count=7):
    """Select top N articles"""
    return articles[:count]

def create_email_html(articles):
    """Create beautiful HTML email with articles"""
    article_cards = ""
    
    for i, article in enumerate(articles, 1):
        # Determine badge color based on source
        if "HackerNews" in article["source"]:
            badge_color = "#ff6600"
            badge_text = "🔥 Trending"
        elif "Google News" in article["source"]:
            badge_color = "#4285f4"
            badge_text = "📰 Latest"
        else:
            badge_color = "#667eea"
            badge_text = "⭐ Featured"
        
        article_cards += f"""
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; background: #fff; overflow: hidden;">
            <div style="display: flex; gap: 15px;">
                <img src="{article['image']}" alt="Article" style="width: 120px; height: 100px; border-radius: 6px; object-fit: cover; flex-shrink: 0;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <span style="display: inline-block; background: {badge_color}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">
                            {badge_text}
                        </span>
                    </div>
                    <h3 style="margin: 0 0 8px 0; color: #1a1a1a; font-size: 16px; line-height: 1.4; font-weight: 600;">
                        {article['title']}
                    </h3>
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 13px;">
                        <strong>{article['source']}</strong> • {article['published'][:10] if article['published'] else 'Today'}
                    </p>
                    <p style="margin: 0 0 12px 0; color: #555; font-size: 13px; line-height: 1.5;">
                        {article['summary']}
                    </p>
                    <a href="{article['link']}" target="_blank" style="color: #fff; text-decoration: none; font-weight: 500; font-size: 13px; background: #667eea; padding: 8px 16px; border-radius: 4px; display: inline-block;">
                        Read Full Article →
                    </a>
                </div>
            </div>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Daily Trending Newsletter</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5;">
        <div style="max-width: 700px; margin: 0 auto; padding: 20px; background: #ffffff;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 40px 30px; text-align: center; margin-bottom: 30px; color: white; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                <h1 style="margin: 0 0 15px 0; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">
                    📰 Trending Today
                </h1>
                <p style="margin: 0 0 5px 0; font-size: 16px; font-weight: 500; opacity: 0.95;">
                    Your Daily Curated Newsletter
                </p>
                <p style="margin: 5px 0 0 0; font-size: 13px; opacity: 0.85;">
                    AI • Product Management • Business Strategy
                </p>
            </div>
            
            <!-- Date & Intro -->
            <div style="background: #f9f9f9; border-left: 4px solid #667eea; padding: 16px; border-radius: 4px; margin-bottom: 25px;">
                <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">
                    <strong>Good morning! ☀️</strong> Here are today's <strong>hottest trending articles</strong> curated from HackerNews, Google News, and major tech publications. Every article is ranked by relevance and real-time engagement.
                </p>
                <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">
                    {datetime.now().strftime('%B %d, %Y')} • {len(articles)} articles
                </p>
            </div>
            
            <!-- Articles -->
            {article_cards}
            
            <!-- Footer -->
            <div style="border-top: 2px solid #e0e0e0; margin-top: 40px; padding-top: 20px; text-align: center;">
                <p style="margin: 0 0 15px 0; color: #999; font-size: 13px;">
                    🚀 <strong>What makes this special:</strong> We fetch from HackerNews, Google News, and premium publications. Articles are ranked by real-time trending scores + relevance to your interests.
                </p>
                <p style="margin: 0 0 10px 0; color: #999; font-size: 12px;">
                    You're receiving this because you subscribed to trending articles on AI, PM, and Strategy.
                </p>
                <p style="margin: 0; font-size: 11px;">
                    <a href="#" style="color: #667eea; text-decoration: none;">Manage preferences</a> • 
                    <a href="#" style="color: #667eea; text-decoration: none;">Unsubscribe</a>
                </p>
            </div>
            
        </div>
    </body>
    </html>
    """
    return html

def send_email_resend(recipient_email, subject, html_content):
    """Send email via Resend API"""
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "from": "Newsletter <onboarding@resend.dev>",
            "to": recipient_email,
            "subject": subject,
            "html": html_content
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            print(f"\n✅ Email sent successfully via Resend!")
            return True
        else:
            print(f"\n❌ Error sending email: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\n❌ Error sending email: {e}")
        return False

def main():
    """Main function to orchestrate newsletter generation"""
    print("\n" + "="*60)
    print("🚀 TRENDING NEWSLETTER GENERATOR")
    print("="*60)
    
    all_articles = []
    
    # Fetch from all sources
    print("\n📥 Fetching articles from multiple sources...")
    print("  (This may take 30-60 seconds)\n")
    
    # RSS feeds
    all_articles.extend(fetch_rss_articles())
    
    # NewsAPI (optional)
    all_articles.extend(fetch_newsapi_articles())
    
    # HackerNews real-time trending
    all_articles.extend(fetch_hackernews_top())
    
    print(f"\n📊 Total articles fetched: {len(all_articles)}")
    
    # Filter, rank, and select
    print("🔍 Filtering and ranking by relevance & trending score...")
    filtered = filter_and_rank_articles(all_articles)
    print(f"✓ Relevant articles found: {len(filtered)}")
    
    selected = select_top_articles(filtered, count=7)
    print(f"✓ Top articles selected: {len(selected)}\n")
    
    if not selected:
        print("❌ No relevant articles found. Skipping email send.")
        return
    
    # Display selected articles
    print("📰 SELECTED ARTICLES FOR TODAY:")
    print("-" * 60)
    for i, article in enumerate(selected, 1):
        print(f"\n{i}. {article['title'][:60]}...")
        print(f"   Source: {article['source']}")
        print(f"   Score: {article.get('_score', 0)}")
    print("\n" + "-" * 60)
    
    # Create and send email
    print("\n🎨 Creating email HTML...")
    html_content = create_email_html(selected)
    
    print("📧 Sending email via Resend...")
    subject = f"Trending Today - {datetime.now().strftime('%B %d, %Y')} | AI • PM • Strategy"
    send_email_resend(RECIPIENT_EMAIL, subject, html_content)
    
    print("\n" + "="*60)
    print("✅ Newsletter generation complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
