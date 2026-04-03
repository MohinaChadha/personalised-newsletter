# 📰 Trending Newsletter - Setup Guide

This is a **cost-effective, fully automated** newsletter that delivers curated articles on AI, Product Management, and Business Strategy to your inbox every day at 9 AM.

## 🚀 Quick Start (5 minutes)

### Step 1: Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Create a public repository named `trending-newsletter`
3. Clone it locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/trending-newsletter.git
   cd trending-newsletter
   ```

### Step 2: Set Up SendGrid (Free)

1. Sign up for free at [sendgrid.com](https://sendgrid.com)
2. Create an **API Key**:
   - Go to Settings → API Keys → Create API Key
   - Copy your API key
3. Add it as a GitHub Secret:
   - Go to your repo → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `SENDGRID_API_KEY`
   - Value: Paste your SendGrid API key

### Step 3: Add the Files

1. Download the following files from this repo:
   - `newsletter_generator.py`
   - `requirements.txt`
   - `.github/workflows/newsletter.yml`

2. Add them to your repository:
   ```bash
   git add .
   git commit -m "Initial newsletter setup"
   git push origin main
   ```

### Step 4: Verify Setup

1. Go to your repo → Actions tab
2. Click "Daily Newsletter" workflow
3. Click "Run workflow" (manual test)
4. Check your inbox in a few seconds!

### Step 5: Schedule It

Once you confirm it works, the workflow will automatically:
- ✅ Run every day at 9:00 AM UTC
- ✅ Fetch the latest trending articles
- ✅ Send you a beautiful email with 5-7 curated articles

---

## 📧 What You'll Receive

A beautiful HTML email with:
- 📌 Top 5-7 trending articles on AI, PM, and Business Strategy
- 🖼️ Article thumbnails
- 📰 Source attribution and publish date
- 🔗 Direct links to read full articles
- 💜 Professional gradient design

---

## 🔧 Customization

### Change Topics
Edit `TOPICS` in `newsletter_generator.py`:
```python
TOPICS = ["artificial intelligence", "machine learning", "startups"]
```

### Change Send Time
Edit the cron schedule in `.github/workflows/newsletter.yml`:
```yaml
cron: '0 14 * * *'  # 2 PM UTC
```

**Common Timezones (UTC):**
- 9 AM EST = `14 * * *` (UTC)
- 9 AM PST = `17 * * *` (UTC)
- 9 AM IST = `3 30 * * *` (UTC)

### Change Email Recipient
Edit `RECIPIENT_EMAIL` in `newsletter_generator.py`:
```python
RECIPIENT_EMAIL = "your-email@example.com"
```

### Add More RSS Feeds
Add URLs to the `RSS_FEEDS` list:
```python
RSS_FEEDS = [
    "https://your-feed-url.com/rss",
    # ... more feeds
]
```

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| GitHub (repo + Actions) | FREE | 2,000 free actions minutes/month |
| SendGrid | FREE | 100 free emails/day |
| RSS Feeds | FREE | Public feeds, no auth needed |
| **Total** | **$0/month** | 🎉 |

---

## 🆘 Troubleshooting

### Email not arriving?
1. Check GitHub Actions logs: repo → Actions → Daily Newsletter
2. Verify SendGrid API key is correct in repo secrets
3. Check spam folder (add newsletter@trending-reads.com to contacts)

### No articles selected?
1. Check if RSS feeds are working (visit URLs manually)
2. Verify topic keywords match article titles/content
3. Run workflow manually to see console logs

### Want to test immediately?
Go to repo → Actions → Daily Newsletter → "Run workflow" (manual trigger)

---

## 📝 Next Steps

1. ✅ Create GitHub repo
2. ✅ Set up SendGrid account and API key
3. ✅ Add files to repo
4. ✅ Test manually via GitHub Actions
5. ✅ Receive your first newsletter! 📰

---

## 📞 Support

For issues:
- Check GitHub Actions logs for error messages
- Verify environment variables are set correctly
- Test SendGrid API key independently

Enjoy your daily curated newsletter! 🚀
