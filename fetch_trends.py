#!/usr/bin/env python3
"""
Trend Radar ID - Upgraded Fetcher
Better categorization for Beauty, F&B, Commerce, Entertainment Indonesia
"""

import json
import os
import time
from datetime import datetime
import requests

# ============================================
# CATEGORY KEYWORDS (Indonesia focused)
# ============================================
CATEGORY_KEYWORDS = {
    'beauty': [
        'skincare', 'makeup', 'kosmetik', 'kecantikan', 'lipstik', 'serum',
        'moisturizer', 'sunscreen', 'masker', 'foundation', 'eyeshadow',
        'blusher', 'concealer', 'toner', 'essence', 'vitamin c', 'retinol',
        'spf', 'bb cream', 'cushion', 'highlighter', 'contour', 'setting spray',
        'micellar', 'cleanser', 'face wash', 'peeling', 'exfoliant', 'acne',
        'jerawat', 'pori', 'glowing', 'cerah', 'whitening', 'brightening'
    ],
    'fnb': [
        'makanan', 'minuman', 'kuliner', 'resep', 'masak', 'restoran', 'cafe',
        'kopi', 'boba', 'milk tea', 'dessert', 'snack', 'jajanan', 'street food',
        'delivery', 'gofood', 'grabfood', 'shopeefood', 'warteg', 'warung',
        'nasi', 'mie', 'bakso', 'soto', 'rendang', 'ayam', 'seafood',
        'vegan', 'vegetarian', 'diet', 'healthy food', 'meal prep', 'catering',
        'food court', 'franchise', 'cloud kitchen', 'ghost kitchen', 'fnb'
    ],
    'commerce': [
        'shopee', 'tokopedia', 'lazada', 'tiktok shop', 'belanja', 'diskon',
        'flash sale', 'harbolnas', 'promo', 'voucher', 'cashback', 'gratis ongkir',
        'jualan', 'olshop', 'online shop', 'dropship', 'reseller', 'affiliate',
        'marketplace', 'e-commerce', 'live shopping', 'live selling', 'cod',
        'produk', 'brand lokal', 'umkm', 'bisnis online', 'digital marketing',
        'iklan', 'ads', 'roi', 'konversi', 'omzet', 'revenue'
    ],
    'entertainment': [
        'film', 'series', 'netflix', 'disney', 'youtube', 'tiktok', 'instagram',
        'viral', 'trending', 'meme', 'konten', 'creator', 'influencer', 'vtuber',
        'gaming', 'game', 'esports', 'streaming', 'podcast', 'musik', 'lagu',
        'konser', 'idol', 'kpop', 'anime', 'manga', 'webtoon', 'drakor',
        'drama', 'sinetron', 'variety show', 'reality show', 'stand up comedy'
    ],
    'fashion': [
        'fashion', 'style', 'outfit', 'ootd', 'baju', 'celana', 'dress',
        'hijab', 'kerudung', 'modest', 'streetwear', 'sneakers', 'sepatu',
        'tas', 'aksesoris', 'perhiasan', 'gelang', 'kalung', 'cincin',
        'thrift', 'preloved', 'vintage', 'batik', 'tenun', 'lurik',
        'sustainable fashion', 'fast fashion', 'brand lokal fashion'
    ],
    'tech': [
        'ai', 'artificial intelligence', 'chatgpt', 'teknologi', 'gadget',
        'smartphone', 'iphone', 'android', 'laptop', 'aplikasi', 'app',
        'startup', 'fintech', 'crypto', 'blockchain', 'nft', 'metaverse',
        'coding', 'programming', 'software', 'hardware', 'review', 'unboxing'
    ]
}

def categorize_term(term):
    term_lower = term.lower()
    
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in term_lower)
        if score > 0:
            scores[category] = score
    
    if scores:
        return max(scores, key=scores.get)
    return 'tech'  # default

def calculate_prediction(momentum, novelty):
    score = (momentum * 0.6) + (novelty * 0.4)
    if score >= 8.0:
        return 'viral_yes'
    elif score >= 6.5:
        return 'viral_likely'
    return 'viral_maybe'

# ============================================
# FETCH: GOOGLE TRENDS
# ============================================
def fetch_google_trends():
    trends = []
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='id-ID', tz=420)
        
        # Trending searches Indonesia
        trending = pytrends.trending_searches(pn='ID')
        terms = trending.head(20).values.flatten()
        
        print(f"  Google Trends: Found {len(terms)} trending searches")
        
        for idx, term in enumerate(terms):
            term_str = str(term).strip()
            if not term_str:
                continue
            
            momentum = round(8.5 - (idx * 0.2), 1)
            momentum = max(5.0, momentum)
            novelty = round(7.5 - (idx * 0.15), 1)
            novelty = max(5.0, novelty)
            
            trends.append({
                'term': term_str,
                'category': categorize_term(term_str),
                'source': 'google_trends',
                'momentum': momentum,
                'novelty': novelty,
                'searchVolume': int(200000 - (idx * 8000)),
                'change': f"+{int(momentum * 5)}%",
                'prediction': calculate_prediction(momentum, novelty),
                'alert': momentum >= 7.5,
                'content': f'Trending di Google Indonesia — posisi #{idx+1}'
            })
            
            time.sleep(0.5)  # Rate limit
        
        print(f"  ✅ Google Trends: {len(trends)} trends processed")
        
    except Exception as e:
        print(f"  ⚠️  Google Trends error: {e}")
    
    return trends

# ============================================
# FETCH: BERITA INDONESIA (RSS - No API key needed!)
# ============================================
def fetch_news_rss():
    trends = []
    
    # Indonesian news RSS feeds (free, no API key needed!)
    rss_sources = [
        ('https://www.detik.com/rss/', 'detik'),
        ('https://rss.kompas.com/kompascom+xml+rss2.0+Lifestyle', 'kompas_lifestyle'),
        ('https://rss.kompas.com/kompascom+xml+rss2.0+Bisnis', 'kompas_bisnis'),
    ]
    
    for rss_url, source_name in rss_sources:
        try:
            response = requests.get(rss_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; TrendRadar/1.0)'
            })
            
            if response.status_code == 200:
                # Simple XML parsing (no external library needed)
                content = response.text
                
                # Extract titles between <title> tags
                titles = []
                start = 0
                skip_first = True
                
                while True:
                    start_tag = content.find('<title>', start)
                    if start_tag == -1:
                        break
                    end_tag = content.find('</title>', start_tag)
                    if end_tag == -1:
                        break
                    
                    title = content[start_tag + 7:end_tag].strip()
                    title = title.replace('<![CDATA[', '').replace(']]>', '')
                    
                    if skip_first:
                        skip_first = False
                    elif len(title) > 5 and len(title) < 200:
                        titles.append(title)
                    
                    start = end_tag + 8
                
                print(f"  {source_name}: Found {len(titles)} articles")
                
                for idx, title in enumerate(titles[:8]):
                    momentum = round(7.8 - (idx * 0.2), 1)
                    novelty = 8.5
                    
                    trends.append({
                        'term': title[:60],
                        'category': categorize_term(title),
                        'source': source_name,
                        'momentum': momentum,
                        'novelty': novelty,
                        'searchVolume': int(80000 - (idx * 5000)),
                        'change': f"+{int(momentum * 4)}%",
                        'prediction': calculate_prediction(momentum, novelty),
                        'alert': idx < 3,
                        'content': f'Breaking news dari {source_name.replace("_", " ").title()}'
                    })
            
            time.sleep(1)
            
        except Exception as e:
            print(f"  ⚠️  {source_name} RSS error: {e}")
    
    print(f"  ✅ News RSS: {len(trends)} trends from Indonesian news")
    return trends

# ============================================
# FETCH: NEWS API (jika ada key)
# ============================================
def fetch_news_api():
    trends = []
    api_key = os.getenv('NEWS_API_KEY', '')
    
    if not api_key:
        print("  ⚠️  NEWS_API_KEY not set - skipping")
        return trends
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=id&pageSize=20&apiKey={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            articles = response.json().get('articles', [])
            print(f"  News API: Found {len(articles)} articles")
            
            for idx, article in enumerate(articles[:15]):
                title = article.get('title', '')
                description = article.get('description', '') or ''
                
                if not title or title == '[Removed]':
                    continue
                
                combined_text = f"{title} {description}"
                momentum = round(8.0 - (idx * 0.2), 1)
                momentum = max(5.0, momentum)
                novelty = 9.0
                
                trends.append({
                    'term': title[:60],
                    'category': categorize_term(combined_text),
                    'source': 'news_api',
                    'momentum': momentum,
                    'novelty': novelty,
                    'searchVolume': int(100000 - (idx * 4000)),
                    'change': f"+{int(momentum * 4)}%",
                    'prediction': calculate_prediction(momentum, novelty),
                    'alert': idx < 5,
                    'content': description[:120] if description else f'Breaking: {title[:80]}'
                })
            
            print(f"  ✅ News API: {len(trends)} trends processed")
        else:
            print(f"  ⚠️  News API error: {response.status_code}")
            
    except Exception as e:
        print(f"  ⚠️  News API error: {e}")
    
    return trends

# ============================================
# MAIN
# ============================================
def main():
    print("🔍 Trend Radar ID - Fetching real data...\n")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_trends = []
    seen_terms = set()
    
    # 1. Google Trends
    print("📊 1. Google Trends Indonesia...")
    google_trends = fetch_google_trends()
    for t in google_trends:
        if t['term'].lower() not in seen_terms:
            seen_terms.add(t['term'].lower())
            all_trends.append(t)
    
    # 2. Indonesian News RSS (free!)
    print("\n📰 2. Indonesian News RSS...")
    rss_trends = fetch_news_rss()
    for t in rss_trends:
        if t['term'].lower() not in seen_terms:
            seen_terms.add(t['term'].lower())
            all_trends.append(t)
    
    # 3. News API (if key available)
    print("\n🌐 3. News API...")
    news_trends = fetch_news_api()
    for t in news_trends:
        if t['term'].lower() not in seen_terms:
            seen_terms.add(t['term'].lower())
            all_trends.append(t)
    
    # Add IDs
    for idx, trend in enumerate(all_trends):
        trend['id'] = idx + 1
    
    # Sort by momentum
    all_trends.sort(key=lambda x: x['momentum'], reverse=True)
    
    # Save to file
    os.makedirs('data', exist_ok=True)
    
    output = {
        'timestamp': datetime.now().isoformat(),
        'total_trends': len(all_trends),
        'trends': all_trends[:50]
    }
    
    with open('data/trends.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Total: {len(all_trends)} unique trends saved!")
    print(f"📁 Saved to data/trends.json")
    
    # Category breakdown
    from collections import Counter
    cats = Counter(t['category'] for t in all_trends)
    print("\n📊 Category breakdown:")
    for cat, count in cats.most_common():
        print(f"  {cat}: {count} trends")

if __name__ == '__main__':
    main()
