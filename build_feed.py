import json
import urllib.request
from jinja2 import Template
import datetime
from collections import defaultdict

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

def fetch_batch_posts(subreddit_batch):
    # Join subreddits with '+' to fetch in a single HTTP request
    joined_subs = "+".join(subreddit_batch)
    url = f"https://www.reddit.com/r/{joined_subs}/top.json?t=day&limit=100"
    
    headers = {
        'User-Agent': 'script:daily-reddit-digest:v1.0 (by /u/marshall19913-code)'
    }
    
    req = urllib.request.Request(url, headers=headers)
    
    batch_posts = defaultdict(list)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            children = data.get('data', {}).get('children', [])
            
            for child in children:
                post_data = child.get('data', {})
                sub = post_data.get('subreddit')
                
                # Filter to top N per subreddit
                if len(batch_posts[sub]) < TOP_N:
                    batch_posts[sub].append({
                        'title': post_data.get('title', 'No Title'),
                        'link': f"https://reddit.com{post_data.get('permalink', '#')}",
                        'author': f"u/{post_data.get('author', 'Unknown')}"
                    })
    except Exception as e:
        print(f"Error fetching batch: {e}")
        
    return batch_posts

# Divide 55 subreddits into batches of 20
CHUNK_SIZE = 20
batches = [SUBREDDITS[i:i + CHUNK_SIZE] for i in range(0, len(SUBREDDITS), CHUNK_SIZE)]

all_posts = {sub: [] for sub in SUBREDDITS}

# Fetch all batches (only 3 total web calls)
for batch in batches:
    fetched_data = fetch_batch_posts(batch)
    for sub, posts in fetched_data.items():
        # Match case-insensitively to maintain user's defined order
        for original_sub in SUBREDDITS:
            if original_sub.lower() == sub.lower():
                all_posts[original_sub] = posts

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
            <p class="empty-notice">No top posts loaded for this subreddit today.</p>
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
