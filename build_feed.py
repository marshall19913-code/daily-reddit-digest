import json
import urllib.request
from jinja2 import Template
import datetime
import time
from concurrent.futures import ThreadPoolExecutor

SUBREDDITS = [
    'LocalLLaMA', 'AI_Agents', 'vibecoding', 'mlops', 'MachineLearning',
    'LanguageTechnology', 'PromptEngineering', 'AIToolsandTips', 'artificial',
    'singularity', 'ArtificialIntelligence', 'LLMDevs', 'LangChain', 'AutoGPT',
    'n8n', 'ClaudeAI', 'aipromptprogramming', 'FluxAI', 'aivideo', 'AiVideos',
    'ControlProblem', 'accelerate', 'agi', 'robotics', 'robotlearning',
    'RoboticsEngineering', 'deeplearning', 'neuralnetworks', 'SideProject',
    'StableDiffusion', 'ChatGPT', 'OpenAI', 'worldnews', 'TrendForecast',
    'BuyItForLife', 'SkincareAddiction', 'Beauty', 'Hardware', 'SelfHosted',
    'Homelab', 'SupplyChain', 'SysAdmin', 'RenewableEnergy', 'EnergyStorage',
    '3Dprinting', 'Biohackers', 'GenZ', 'GenAlpha', 'streetwear', 'ThrowingFits',
    'BeautyGuruChatter', 'Tiktokfashion', 'gamedev', 'popheads', 'StanTwitter'
]

TOP_N = 10

def fetch_top_posts(subreddit, count=10):
    # Reddit's native JSON endpoint
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=day&limit={count}"
    
    # Custom Unique User-Agent header satisfies Reddit's API guidelines
    headers = {
        'User-Agent': f'script:daily-reddit-digest:v1.0 (by /u/marshall19913-code)'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    # Retry mechanism in case of temporary throttling
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                posts = []
                children = data.get('data', {}).get('children', [])
                for child in children[:count]:
                    post_data = child.get('data', {})
                    posts.append({
                        'title': post_data.get('title', 'No Title'),
                        'link': f"https://reddit.com{post_data.get('permalink', '#')}",
                        'author': f"u/{post_data.get('author', 'Unknown')}"
                    })
                return subreddit, posts
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))  # Pause before retry
            
    print(f"Failed to fetch r/{subreddit} after retries.")
    return subreddit, []

# Fetch in small batches (max_workers=3) to prevent triggering Reddit IP blocks
all_posts = {}
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(lambda sub: fetch_top_posts(sub, TOP_N), SUBREDDITS)
    for sub, posts in results:
        all_posts[sub] = posts

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Reddit Digest</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #ff4500;
            --link: #38bdf8;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { margin-bottom: 24px; border-bottom: 1px solid #334155; padding-bottom: 12px; }
        h1 { margin: 0 0 6px 0; font-size: 1.8rem; }
        .date { color: var(--text-muted); font-size: 0.875rem; }
        .section { background: var(--card-bg); border-radius: 10px; padding: 20px; margin-bottom: 20px; border: 1px solid #334155; }
        .section-title { margin-top: 0; color: var(--accent); font-size: 1.2rem; border-bottom: 1px solid #334155; padding-bottom: 8px; }
        .post-list { list-style: none; padding: 0; margin: 0; }
        .post-item { padding: 12px 0; border-bottom: 1px solid #334155; }
        .post-item:last-child { border-bottom: none; }
        .post-link { font-weight: 600; color: var(--link); text-decoration: none; font-size: 1.05rem; line-height: 1.4; display: block; }
        .post-link:hover { text-decoration: underline; }
        .post-meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 6px; }
        .empty-notice { color: var(--text-muted); font-style: italic; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Daily Reddit Digest</h1>
            <div class="date">Updated UTC: {{ date }}</div>
        </header>
        
        {% for sub, posts in feeds.items() %}
        <div class="section" id="{{ sub }}">
            <h2 class="section-title">r/{{ sub }}</h2>
            {% if posts %}
            <ul class="post-list">
                {% for post in posts %}
                <li class="post-item">
                    <a class="post-link" href="{{ post.link }}" target="_blank" rel="noopener">{{ post.title }}</a>
                    <div class="post-meta">Posted by {{ post.author }}</div>
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty-notice">No posts loaded for this subreddit today.</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

template = Template(HTML_TEMPLATE)
rendered_html = template.render(
    feeds=all_posts, 
    date=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(rendered_html)
