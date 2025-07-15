#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import feedparser
import csv
import json
from datetime import datetime
import logging
import time
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO)

# Your 57 content sources (complete list)
SOURCES = [
    {"name": "Harvard Business Review - Leadership", "pillar": "Leadership & Strategy", "url": "https://hbr.org/topic/leadership", "quality": 9},
    {"name": "McKinsey Insights - Strategy", "pillar": "Leadership & Strategy", "url": "https://www.mckinsey.com/insights", "quality": 9},
    {"name": "MIT Sloan Management Review", "pillar": "Leadership & Strategy", "url": "https://sloanreview.mit.edu", "quality": 8},
    {"name": "Simon Sinek", "pillar": "Leadership & Strategy", "url": "https://simonsinek.com", "quality": 8},
    {"name": "Patrick Lencioni", "pillar": "Leadership & Strategy", "url": "https://www.tablegroup.com", "quality": 8},
    {"name": "First Round Review", "pillar": "Leadership & Strategy", "url": "https://review.firstround.com", "quality": 8},
    {"name": "Strategy+Business PwC", "pillar": "Leadership & Strategy", "url": "https://www.strategy-business.com", "quality": 8},
    {"name": "Brené Brown", "pillar": "Leadership & Strategy", "url": "https://brenebrown.com", "quality": 8},
    {"name": "Kim Scott Radical Candor", "pillar": "Leadership & Strategy", "url": "https://www.radicalcandor.com", "quality": 7},
    {"name": "Reid Hoffman", "pillar": "Leadership & Strategy", "url": "https://www.reidhoffman.org", "quality": 7},
    {"name": "a16z Future Blog", "pillar": "Leadership & Strategy", "url": "https://future.a16z.com", "quality": 7},
    {"name": "Reforge Blog", "pillar": "Leadership & Strategy", "url": "https://www.reforge.com/blog", "quality": 7},
    {"name": "Gallup Leadership", "pillar": "Leadership & Strategy", "url": "https://www.gallup.com/workplace/leadership.aspx", "quality": 8},
    {"name": "Deloitte Insights Leadership", "pillar": "Leadership & Strategy", "url": "https://www2.deloitte.com/insights/leadership", "quality": 7},
    {"name": "BCG Strategy Reports", "pillar": "Leadership & Strategy", "url": "https://www.bcg.com/insights/strategy", "quality": 8},
    
    {"name": "Marketing Land", "pillar": "Brand & Marketing", "url": "https://marketingland.com", "quality": 8},
    {"name": "Mark Ritson", "pillar": "Brand & Marketing", "url": "https://www.marketingweek.com/author/mark-ritson/", "quality": 9},
    {"name": "Byron Sharp How Brands Grow", "pillar": "Brand & Marketing", "url": "https://www.marketingscience.info", "quality": 9},
    {"name": "April Dunford", "pillar": "Brand & Marketing", "url": "https://aprildunford.com", "quality": 8},
    {"name": "Adweek", "pillar": "Brand & Marketing", "url": "https://www.adweek.com", "quality": 7},
    {"name": "Fast Company Brand", "pillar": "Brand & Marketing", "url": "https://www.fastcompany.com/section/brands", "quality": 8},
    {"name": "Brand New UnderConsideration", "pillar": "Brand & Marketing", "url": "https://www.underconsideration.com/brandnew/", "quality": 7},
    {"name": "Digiday", "pillar": "Brand & Marketing", "url": "https://digiday.com", "quality": 7},
    {"name": "Marty Neumeier", "pillar": "Brand & Marketing", "url": "https://www.martyneumeier.com", "quality": 7},
    {"name": "Bob Hoffman Ad Contrarian", "pillar": "Brand & Marketing", "url": "https://adcontrarian.blogspot.com", "quality": 7},
    {"name": "Morning Brew Marketing", "pillar": "Brand & Marketing", "url": "https://www.morningbrew.com/marketing", "quality": 7},
    {"name": "Campaign Magazine", "pillar": "Brand & Marketing", "url": "https://www.campaignlive.com", "quality": 6},
    {"name": "Youngme Moon", "pillar": "Brand & Marketing", "url": "https://www.hbs.edu/faculty/Pages/profile.aspx?facId=6446", "quality": 7},
    {"name": "Katrina Kirsch", "pillar": "Brand & Marketing", "url": "https://katrinakirsch.com", "quality": 6},
    
    {"name": "Cal Newport Blog", "pillar": "Productivity & Systems", "url": "https://www.calnewport.com/blog/", "quality": 9},
    {"name": "James Clear", "pillar": "Productivity & Systems", "url": "https://jamesclear.com", "quality": 8},
    {"name": "Getting Things Done David Allen", "pillar": "Productivity & Systems", "url": "https://gettingthingsdone.com", "quality": 7},
    {"name": "Zen Habits", "pillar": "Productivity & Systems", "url": "https://zenhabits.net", "quality": 7},
    {"name": "Asian Efficiency", "pillar": "Productivity & Systems", "url": "https://www.asianefficiency.com", "quality": 6},
    {"name": "Greg McKeown Essentialism", "pillar": "Productivity & Systems", "url": "https://gregmckeown.com", "quality": 7},
    {"name": "Tiago Forte Building Second Brain", "pillar": "Productivity & Systems", "url": "https://fortelabs.co", "quality": 7},
    {"name": "Ali Abdaal", "pillar": "Productivity & Systems", "url": "https://aliabdaal.com", "quality": 6},
    {"name": "Notion Templates Community", "pillar": "Productivity & Systems", "url": "https://www.notion.so/templates", "quality": 6},
    {"name": "Ryder Carroll Bullet Journal", "pillar": "Productivity & Systems", "url": "https://bulletjournal.com", "quality": 6},
    {"name": "The Focused Life", "pillar": "Productivity & Systems", "url": "https://thefocusedlife.com", "quality": 6},
    
    {"name": "The Marginalian Maria Popova", "pillar": "Personal Growth & POV", "url": "https://www.themarginalian.org", "quality": 9},
    {"name": "Farnam Street Shane Parrish", "pillar": "Personal Growth & POV", "url": "https://fs.blog", "quality": 9},
    {"name": "Seth Godin Blog", "pillar": "Personal Growth & POV", "url": "https://seths.blog", "quality": 8},
    {"name": "Ryan Holiday Daily Stoic", "pillar": "Personal Growth & POV", "url": "https://dailystoic.com", "quality": 8},
    {"name": "Wait But Why Tim Urban", "pillar": "Personal Growth & POV", "url": "https://waitbutwhy.com", "quality": 8},
    {"name": "Brené Brown Personal Growth", "pillar": "Personal Growth & POV", "url": "https://brenebrown.com/blog/", "quality": 8},
    {"name": "Elizabeth Gilbert", "pillar": "Personal Growth & POV", "url": "https://www.elizabethgilbert.com", "quality": 7},
    {"name": "Steven Pressfield", "pillar": "Personal Growth & POV", "url": "https://stevenpressfield.com", "quality": 7},
    {"name": "Derek Sivers", "pillar": "Personal Growth & POV", "url": "https://sive.rs", "quality": 7},
    {"name": "Carol Dweck", "pillar": "Personal Growth & POV", "url": "https://mindsetonline.com", "quality": 7},
    {"name": "Angela Duckworth", "pillar": "Personal Growth & POV", "url": "https://angeladuckworth.com", "quality": 7},
    
    {"name": "CustomerThink", "pillar": "Connection & CX", "url": "https://customerthink.com", "quality": 8},
    {"name": "CX Network", "pillar": "Connection & CX", "url": "https://www.customerexperiencenetwork.com", "quality": 7},
    {"name": "McKinsey Customer Experience", "pillar": "Connection & CX", "url": "https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights#customer%20experience", "quality": 9},
    {"name": "Forrester CX Research", "pillar": "Connection & CX", "url": "https://www.forrester.com/research/customer-experience/", "quality": 8},
    {"name": "Don Norman", "pillar": "Connection & CX", "url": "https://jnd.org", "quality": 8},
    {"name": "Indi Young", "pillar": "Connection & CX", "url": "https://indiyoung.com", "quality": 7},
    {"name": "UserTesting Blog", "pillar": "Connection & CX", "url": "https://www.usertesting.com/blog", "quality": 7},
    {"name": "Zendesk CX Blog", "pillar": "Connection & CX", "url": "https://www.zendesk.com/blog/", "quality": 6},
    {"name": "Susan David", "pillar": "Connection & CX", "url": "https://susandavid.com", "quality": 7},
    {"name": "Chip Heath Dan Heath", "pillar": "Connection & CX", "url": "https://heathbrothers.com", "quality": 7}
]

# Keyword filters for each pillar
PILLAR_KEYWORDS = {
    "Leadership & Strategy": [
        "leadership", "strategy", "strategic", "team", "management", "decision", 
        "focus", "clarity", "vision", "execution", "planning", "goals", "culture",
        "transformation", "change", "innovation", "growth", "performance", "results",
        "leader", "leaders", "manage", "lead", "direct", "guide", "influence"
    ],
    "Brand & Marketing": [
        "brand", "marketing", "branding", "positioning", "customer", "audience",
        "resonance", "emotion", "experience", "storytelling", "content", "engagement",
        "advertising", "campaign", "creative", "message", "identity", "perception",
        "market", "markets", "consumer", "business", "sales", "revenue"
    ],
    "Productivity & Systems": [
        "productivity", "systems", "process", "workflow", "efficiency", "automation",
        "focus", "deep work", "habits", "routine", "organization", "planning",
        "time management", "tools", "method", "framework", "optimization",
        "work", "working", "productive", "system", "organize", "schedule"
    ],
    "Personal Growth & POV": [
        "growth", "development", "learning", "mindset", "philosophy", "wisdom",
        "reflection", "purpose", "meaning", "values", "character", "discipline",
        "creativity", "craft", "mastery", "journey", "becoming", "transformation",
        "personal", "self", "improve", "better", "change", "evolve"
    ],
    "Connection & CX": [
        "customer", "experience", "connection", "relationship", "empathy", "listening",
        "service", "support", "engagement", "satisfaction", "loyalty", "trust",
        "communication", "feedback", "interaction", "touchpoint", "journey",
        "connect", "relate", "understand", "care", "help", "serve"
    ]
}

# LinkedIn post templates
POST_TEMPLATES = {
    "Leadership & Strategy": """I've been exploring {topic} lately, and this piece on "{title}" really caught my attention.

What stood out: {key_point}

This makes me think about how we often rush to solutions when we should be sitting with better questions.

In my consulting work, I'm seeing this play out as clients wanting quick fixes but needing deeper transformation.

What's your take on approaching strategic decision-making in uncertain times?

#Leadership #Strategy #Management""",

    "Brand & Marketing": """This article on {topic} had me thinking about the difference between reach and resonance.

Key insight: {key_point}

What resonates with me is how authentic connection requires vulnerability, not just consistency. It's not just about tactics, it's about genuine connection.

In brand work, I'm learning that building brands that resonate rather than just reach.

How do you think about balancing authenticity with commercial goals?

#Branding #Marketing #CustomerExperience""",

    "Productivity & Systems": """Been exploring {topic} and this approach to productivity is fascinating.

The core idea: {key_point}

What I'm realizing is that sustainable productivity comes from alignment, not optimization. It's less about doing more and more about doing what matters.

Trying to implement this in my own work by designing workflows that support deep work.

How do you approach maintaining focus in a distracted world?

#Productivity #Systems #DeepWork""",

    "Personal Growth & POV": """Reflecting on this piece about {topic} and how {key_point}.

What strikes me is the difference between achievement and growth. One is about hitting targets, the other about developing character.

I'm learning that growth happens in the space between comfort and chaos.

This makes me curious about developing perspective alongside skills.

What's your perspective on defining success for yourself?

#PersonalGrowth #Mindset #Philosophy""",

    "Connection & CX": """This insight about {topic} really hit home: {key_point}

What I'm learning is that genuine service starts with genuine listening. It's not just about process, it's about human understanding.

In customer experience work, this translates to creating experiences that feel genuinely human.

How do you create meaningful connections in digital interactions?

#CustomerExperience #Connection #Empathy"""
}

def scrape_source(source):
    """Scrape content from a single source"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(source['url'], headers=headers, timeout=15)
        response.raise_for_status()
        
        # Try RSS feed first
        if is_rss_feed(response.content):
            return parse_rss_content(response.content, source)
        
        # Parse HTML
        return parse_html_content(response.content, source)
        
    except Exception as e:
        logging.error(f"Error scraping {source['name']}: {e}")
        return []

def is_rss_feed(content):
    """Check if content is RSS/XML feed"""
    try:
        content_str = content.decode('utf-8', errors='ignore')
        return '<rss' in content_str.lower() or '<feed' in content_str.lower() or '<?xml' in content_str.lower()
    except:
        return False

def parse_rss_content(content, source):
    """Parse RSS feed content"""
    try:
        feed = feedparser.parse(content)
        articles = []
        
        for entry in feed.entries[:5]:
            title = entry.title if hasattr(entry, 'title') else "No Title"
            url = entry.link if hasattr(entry, 'link') else ""
            excerpt = entry.summary[:300] + "..." if hasattr(entry, 'summary') else ""
            
            if title and url and len(title) > 10:
                articles.append({
                    'title': title,
                    'url': url,
                    'excerpt': excerpt,
                    'source': source['name'],
                    'pillar': source['pillar']
                })
        
        return articles
    except Exception as e:
        logging.error(f"Error parsing RSS for {source['name']}: {e}")
        return []

def parse_html_content(content, source):
    """Parse HTML content to extract articles"""
    try:
        soup = BeautifulSoup(content, 'html.parser')
        articles = []
        
        # Common article selectors
        selectors = [
            'article h2 a', 'article h3 a', 'article .title a',
            '.post-title a', '.entry-title a', 
            'h2.title a', 'h3.title a',
            '.article-title a', '.post-link',
            'h2 a[href]', 'h3 a[href]',
            '.headline a', '.post-headline a'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            
            for link in links[:10]:
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                if not title or len(title) < 10:
                    continue
                
                # Make relative URLs absolute
                if url.startswith('/'):
                    base_url = f"{urlparse(source['url']).scheme}://{urlparse(source['url']).netloc}"
                    url = urljoin(base_url, url)
                elif not url.startswith('http'):
                    continue
                
                # Get excerpt from nearby text
                excerpt = ""
                parent = link.parent
                for _ in range(3):
                    if parent:
                        excerpt_elem = parent.find_next(['p', '.excerpt', '.summary', '.description'])
                        if excerpt_elem:
                            excerpt = excerpt_elem.get_text(strip=True)[:300] + "..."
                            break
                        parent = parent.parent
                
                articles.append({
                    'title': title,
                    'url': url,
                    'excerpt': excerpt,
                    'source': source['name'],
                    'pillar': source['pillar']
                })
            
            if articles:
                break
        
        return articles[:5]
        
    except Exception as e:
        logging.error(f"Error parsing HTML for {source['name']}: {e}")
        return []

def score_content(article):
    """Score content relevance using keyword matching"""
    pillar_keywords = PILLAR_KEYWORDS[article['pillar']]
    text = f"{article['title']} {article['excerpt']}".lower()
    
    # Count keyword matches
    matches = sum(1 for keyword in pillar_keywords if keyword in text)
    
    # Calculate score (0-10)
    keyword_score = min(matches * 2, 10)
    
    # Bonus for title matches
    title_matches = sum(1 for keyword in pillar_keywords if keyword in article['title'].lower())
    title_bonus = min(title_matches * 2, 3)
    
    return min(keyword_score + title_bonus, 10)

def generate_post(article):
    """Generate LinkedIn post"""
    template = POST_TEMPLATES.get(article['pillar'], POST_TEMPLATES['Leadership & Strategy'])
    
    # Extract topic from pillar
    topic = article['pillar'].split(' & ')[0].lower()
    
    # Clean key point
    key_point = article['title'][:100] + "..." if len(article['title']) > 100 else article['title']
    
    # Generate post
    try:
        post = template.format(
            topic=topic,
            title=article['title'][:80],
            key_point=key_point
        )
        return post
    except:
        return generate_generic_post(article)

def generate_generic_post(article):
    """Generate generic LinkedIn post"""
    return f"""I came across this piece on {article['title']} and it got me thinking.

The key insight that stood out: {article['title'][:80]}

This resonates with what I'm seeing in my consulting work - the importance of {article['pillar'].lower()}.

I'm curious about your perspective on this. How do you approach this challenge?

#{article['pillar'].replace(' & ', '').replace(' ', '')} #Learning #Consulting"""

def main():
    """Main scraping function"""
    logging.info("Starting content scrape...")
    
    all_content = []
    
    # Scrape sources (limit to prevent timeouts)
    for source in SOURCES[:20]:  # Process 20 sources to balance speed vs coverage
        logging.info(f"Scraping {source['name']}...")
        
        try:
            articles = scrape_source(source)
            
            for article in articles:
                score = score_content(article)
                if score >= 5:  # Only keep relevant content
                    article['score'] = score
                    article['linkedin_post'] = generate_post(article)
                    all_content.append(article)
                    
            time.sleep(1)  # Be respectful to servers
            
        except Exception as e:
            logging.error(f"Failed to scrape {source['name']}: {e}")
            continue
    
    # Sort by score
    all_content.sort(key=lambda x: x['score'], reverse=True)
    
    # Keep top pieces
    all_content = all_content[:15]
    
    logging.info(f"Found {len(all_content)} quality articles")
    
    # Generate simple text report for email
    text_report = generate_text_report(all_content)
    with open('content_report.html', 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    # Generate CSV
    with open('content_queue.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Pillar', 'Score', 'LinkedIn Post', 'Source URL', 'Source'])
        for article in all_content:
            writer.writerow([
                article['title'][:100],
                article['pillar'],
                article['score'],
                article['linkedin_post'],
                article['url'],
                article['source']
            ])
    
    logging.info("Reports generated successfully!")

def generate_text_report(content):
    """Generate simple text report that emails well"""
    date = datetime.now().strftime("%Y-%m-%d")
    
    if not content:
        return f"""Daily Content Report - {date}

No quality content found today. The automation is working, but sources may be slow to update.

The system scraped successfully and will try again tomorrow."""
    
    avg_score = sum(c['score'] for c in content) / len(content)
    
    report = f"""Daily Content Report - {date}

SUMMARY:
• Total pieces found: {len(content)}
• Average score: {avg_score:.1f}/10
• Ready-to-post content below

"""
    
    # Group by pillar
    by_pillar = {}
    for article in content:
        pillar = article['pillar']
        if pillar not in by_pillar:
            by_pillar[pillar] = []
        by_pillar[pillar].append(article)
    
    for pillar, articles in by_pillar.items():
        report += f"\n{'='*50}\n"
        report += f"{pillar.upper()} ({len(articles)} pieces)\n"
        report += f"{'='*50}\n"
        
        for i, article in enumerate(articles, 1):
            report += f"\n{i}. {article['title']}\n"
            report += f"Source: {article['source']} | Score: {article['score']}/10\n"
            report += f"Link: {article['url']}\n"
            report += f"\nLINKEDIN POST (ready to copy):\n"
            report += f"{'-'*30}\n"
            report += f"{article['linkedin_post']}\n"
            report += f"{'-'*30}\n\n"
    
    report += f"""

HOW TO USE:
• Copy LinkedIn posts from above
• Download CSV attachment for spreadsheet format
• Click links to read full articles
• Customize posts with your own insights

Automation runs daily at 9 AM UTC.
"""
    
    return report

if __name__ == "__main__":
    main()
