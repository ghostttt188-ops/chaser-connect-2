from datetime import datetime
import os
from flask import (
    Flask,
    flash,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "vortex-chaser-connect-persistent-auth-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chaser_social.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(
    os.path.dirname(__file__), "static", "uploads"
)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)


# --- Database Models ---
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  display_name = db.Column(db.String(80), nullable=True)
  handle = db.Column(db.String(80), unique=True, nullable=True)
  role = db.Column(db.String(50), default="Verified Storm Spotter")
  bio = db.Column(
      db.String(300),
      default="Tracking severe weather and capturing nature's fury in the field.",
  )
  avatar = db.Column(
      db.String(200),
      default="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
  )
  cover_photo = db.Column(
      db.String(200),
      default="https://images.unsplash.com/photo-1527482797697-8795b05813fe?w=1000",
  )
  accent = db.Column(db.String(20), default="blue")
  pinned_post_id = db.Column(db.Integer, nullable=True)
  skywarn_certified = db.Column(db.Boolean, default=False)
  fema_certified = db.Column(db.Boolean, default=False)
  field_years = db.Column(db.String(20), default="1-3 Years")
  posts = db.relationship(
      "Post", backref="user_owner", lazy=True, cascade="all, delete-orphan"
  )


class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(
      db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
  )
  author = db.Column(db.String(80), nullable=False)
  handle = db.Column(db.String(80), nullable=False)
  avatar = db.Column(db.String(200), nullable=False)
  location = db.Column(db.String(120), nullable=True)
  threat_tag = db.Column(db.String(50), default="⚡ Field Update")
  content = db.Column(db.Text, nullable=False)
  image_file = db.Column(db.String(200), nullable=True)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  reactions_bolt = db.Column(db.Integer, default=0)
  reactions_radar = db.Column(db.Integer, default=0)
  reactions_siren = db.Column(db.Integer, default=0)
  reactions_capture = db.Column(db.Integer, default=0)
  is_shared = db.Column(db.Boolean, default=False)
  shared_from = db.Column(db.String(80), nullable=True)
  is_emergency_broadcast = db.Column(db.Boolean, default=False)


class Reel(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  author = db.Column(db.String(80), nullable=False)
  handle = db.Column(db.String(80), nullable=False)
  avatar = db.Column(db.String(200), nullable=False)
  caption = db.Column(db.String(200), nullable=False)
  video_file = db.Column(db.String(200), nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  post_id = db.Column(
      db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable=False
  )
  author = db.Column(db.String(80), nullable=False)
  handle = db.Column(db.String(80), nullable=False)
  text = db.Column(db.Text, nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class DirectMessage(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  sender = db.Column(db.String(80), nullable=False)
  recipient = db.Column(db.String(80), nullable=False)
  message = db.Column(db.Text, nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  is_read = db.Column(db.Boolean, default=False)


class GroupChat(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  admin = db.Column(db.String(80), nullable=False)
  avatar = db.Column(
      db.String(200),
      default="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150",
  )
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class GroupMember(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  group_id = db.Column(
      db.Integer,
      db.ForeignKey("group_chat.id", ondelete="CASCADE"),
      nullable=False,
  )
  username = db.Column(db.String(80), nullable=False)


class GroupMessage(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  group_id = db.Column(
      db.Integer,
      db.ForeignKey("group_chat.id", ondelete="CASCADE"),
      nullable=False,
  )
  sender = db.Column(db.String(80), nullable=False)
  message = db.Column(db.Text, nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class CommunityGroup(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  description = db.Column(db.Text, nullable=False)
  admin = db.Column(db.String(80), nullable=False)
  avatar = db.Column(
      db.String(200),
      default="https://images.unsplash.com/photo-1527482797697-8795b05813fe?w=150",
  )
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class CommunityPost(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  community_id = db.Column(
      db.Integer,
      db.ForeignKey("community_group.id", ondelete="CASCADE"),
      nullable=False,
  )
  author = db.Column(db.String(80), nullable=False)
  handle = db.Column(db.String(80), nullable=False)
  avatar = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class MarketplaceItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  seller = db.Column(db.String(80), nullable=False)
  handle = db.Column(db.String(80), nullable=False)
  title = db.Column(db.String(120), nullable=False)
  price = db.Column(db.String(50), nullable=False)
  category = db.Column(db.String(50), default="Gear & Equipment")
  location = db.Column(db.String(100), nullable=False)
  description = db.Column(db.Text, nullable=False)
  image_file = db.Column(db.String(200), nullable=True)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  recipient = db.Column(db.String(80), nullable=False)
  actor = db.Column(db.String(80), nullable=False)
  action = db.Column(db.String(100), nullable=False)
  target_text = db.Column(db.String(200), nullable=True)
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  is_read = db.Column(db.Boolean, default=False)


with app.app_context():
 # db.drop_all()
 db.create_all()


# --- Helper: Live NWS Feed & Warning Detection ---
def get_live_nws_alerts():
  try:
    headers = {"User-Agent": "ChaserConnect/13.0 (unique-auth)"}
    res = requests.get(
        "https://api.weather.gov/alerts/active?limit=8",
        headers=headers,
        timeout=3,
    )
    if res.status_code == 200:
      data = res.json()
      features = data.get("features", [])
      alerts = []
      for f in features:
        props = f.get("properties", {})
        event = props.get("event", "Weather Alert")
        area = props.get("areaDesc", "Multiple Counties")
        alerts.append(f"{event}: {area}")
      if alerts:
        return " • ".join(alerts)
  except Exception:
    pass
  return "LIVE NWS FEED: Monitoring active severe weather across regional watch boxes..."


def check_tornado_warning_active():
  try:
    headers = {"User-Agent": "ChaserConnect/13.0 (unique-auth)"}
    res = requests.get(
        "https://api.weather.gov/alerts/active?event=Tornado Warning",
        headers=headers,
        timeout=2,
    )
    if res.status_code == 200:
      data = res.json()
      return len(data.get("features", [])) > 0
  except Exception:
    pass
  return False


# --- Helper: Format Mentions (@username) ---
def format_mentions(text):
  import re

  def replace_mention(match):
    name = match.group(1)
    return (
        f'<a href="/?tab=messages&with={name}" class="text-accent font-bold'
        f' hover:underline">@{name}</a>'
    )

  return re.sub(r"@([a-zA-Z0-9_]+)", replace_mention, text)


app.jinja_env.filters["mentions"] = format_mentions


# --- Master UI Template ---
TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark" data-accent="{{ user_accent }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChaserConnect | Public Social Weather Network</title>
    <script src="https://cdn.tailwindcss.com"></script> 
 <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
       /* Mobile overflow protection */
        *, *::before, *::after { box-sizing: border-box; }
        html, body { width: 100%; max-width: 100vw; overflow-x: hidden; margin: 0; padding: 0; }
 
       :root {
            --bg-main: #0f1117;
            --card-bg: rgba(24, 28, 36, 0.95);
            --text-main: #e5e7eb;
            --border-color: rgba(255, 255, 255, 0.08);
            --input-bg: rgba(0, 0, 0, 0.4);
        }
        [data-theme="light"] {
            --bg-main: #f0f2f5;
            --card-bg: rgba(255, 255, 255, 0.98);
            --text-main: #1f2937;
            --border-color: rgba(0, 0, 0, 0.1);
            --input-bg: rgba(0, 0, 0, 0.03);
        }

        [data-accent="blue"] { --accent-primary: #3b82f6; --accent-gradient: linear-gradient(135deg, #3b82f6, #1d4ed8); }
        [data-accent="red"] { --accent-primary: #ef4444; --accent-gradient: linear-gradient(135deg, #ef4444, #991b1b); }
        [data-accent="amber"] { --accent-primary: #f59e0b; --accent-gradient: linear-gradient(135deg, #f59e0b, #b45309); }
        [data-accent="emerald"] { --accent-primary: #10b981; --accent-gradient: linear-gradient(135deg, #10b981, #047857); }

        body { background-color: var(--bg-main); color: var(--text-main); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; transition: background 0.3s, color 0.3s; }
        .glass-card { background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-color); }
        .custom-input { background: var(--input-bg); border: 1px solid var(--border-color); color: var(--text-main); }
        .btn-action { background: var(--accent-gradient); color: #fff; font-weight: 600; transition: all 0.2s; }
        .btn-action:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }
        .text-accent { color: var(--accent-primary); }
        .border-accent { border-color: var(--accent-primary); }
        
        .tornado-glow { border: 2px solid #ef4444 !important; box-shadow: 0 0 25px rgba(239, 68, 68, 0.4); animation: warningPulse 2s infinite; }
        @keyframes warningPulse { 0% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); } 50% { box-shadow: 0 0 35px rgba(239, 68, 68, 0.7); } 100% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); } }

        marquee { background: #161b22; color: var(--accent-primary); border-bottom: 1px solid rgba(255,255,255,0.08); font-weight: 600; padding: 8px 0; font-size: 13px; }
        .story-ring { background: linear-gradient(45deg, #f59e0b, #3b82f6, #ec4899); padding: 2px; border-radius: 9999px; }
        
        .reaction-container { position: relative; display: inline-block; }
        .reaction-popup { display: none; position: absolute; bottom: 100%; left: 0; background: rgba(20, 24, 33, 0.95); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.15); border-radius: 9999px; padding: 6px 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); z-index: 50; gap: 10px; align-items: center; }
        .reaction-container:hover .reaction-popup { display: flex; animation: fadeInUp 0.2s ease-in-out; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .reaction-btn { font-size: 1.25rem; transition: transform 0.2s; background: none; border: none; cursor: pointer; }
        .reaction-btn:hover { transform: scale(1.3); }
    </style>
    <script>
        document.addEventListener("DOMContentLoaded", () => {
            const savedTheme = localStorage.getItem("chaser_theme") || "dark";
            document.documentElement.setAttribute("data-theme", savedTheme);
            updateThemeIcon(savedTheme);
        });
        function toggleTheme() {
            const current = document.documentElement.getAttribute("data-theme");
            const next = current === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", next);
            localStorage.setItem("chaser_theme", next);
            updateThemeIcon(next);
        }
        function updateThemeIcon(theme) {
            const btn = document.getElementById("theme-icon");
            if(btn) btn.className = theme === "dark" ? "fa-solid fa-sun text-amber-400 text-lg" : "fa-solid fa-moon text-indigo-600 text-lg";
        }
        function updateCharCount(el) {
            const len = el.value.length;
            document.getElementById('char-counter').innerText = len + " / 280";
        }
        function filterFeed(tag) {
            const posts = document.querySelectorAll('.feed-post');
            const pills = document.querySelectorAll('.filter-pill');
            pills.forEach(p => p.classList.remove('bg-accent', 'text-white'));
            event.target.classList.add('bg-accent', 'text-white');
            posts.forEach(p => {
                if(tag === 'all' || p.dataset.tag.toLowerCase().includes(tag.toLowerCase())) {
                    p.style.display = 'block';
                } else {
                    p.style.display = 'none';
                }
            });
        }
        function openStory(author, avatar, content, image, tag, time) {
            document.getElementById('story-author').innerText = author;
            document.getElementById('story-avatar').src = avatar;
            document.getElementById('story-tag').innerText = tag;
            document.getElementById('story-content').innerText = content;
            document.getElementById('story-time').innerText = time;
            const imgEl = document.getElementById('story-image');
            if(image && image !== 'None') {
                imgEl.src = "/static/uploads/" + image;
                imgEl.classList.remove('hidden');
            } else {
                imgEl.classList.add('hidden');
            }
            document.getElementById('story-modal').classList.remove('hidden');
        }
        function closeStory() {
            document.getElementById('story-modal').classList.add('hidden');
        }
        function openLightbox(imgSrc) {
            document.getElementById('lightbox-img').src = imgSrc;
            document.getElementById('lightbox-modal').classList.remove('hidden');
        }
        function closeLightbox() {
            document.getElementById('lightbox-modal').classList.add('hidden');
        }
    </script>
</head>
<body class="min-h-screen flex flex-col">

    <!-- Top Breaking Weather Ticker -->
    <marquee scrollamount="6">
        <i class="fa-solid fa-bolt mr-2 text-accent"></i> {{ live_nws_ticker }}
    </marquee>

    <!-- Navigation Header -->
    <nav class="glass-card sticky top-0 z-50 px-3 md:px-6 flex items-center justify-between border-b {{ 'tornado-glow' if tornado_active else 'border-gray-800' }}">
        <div class="flex items-center space-x-3">
            <a href="/?tab=feed" class="flex items-center space-x-2.5">
                <div class="w-10 h-10 rounded-xl btn-action flex items-center justify-center shadow-lg">
                    <i class="fa-solid fa-cloud-bolt text-white text-lg"></i>
                </div>
                <span class="text-xl font-black tracking-tight">Chaser<span class="text-accent">Connect</span></span>
            </a>
        </div>

        {% if session.get('user') %}
        <div class="flex items-center space-x-1 md:space-x-3 text-sm font-semibold">
            <a href="/?tab=feed" class="p-2 md:px-3 md:py-2 rounded-xl hover:bg-gray-800/20 {{ 'text-accent bg-accent/10' if active_tab == 'feed' else '' }} transition flex items-center gap-1.5"><i class="fa-solid fa-house text-base"></i><span class="hidden md:inline">Home</span></a>
            <a href="/?tab=communities" class="p-2 md:px-3 md:py-2 rounded-xl hover:bg-gray-800/20 {{ 'text-accent bg-accent/10' if active_tab in ['communities', 'community_detail'] else '' }} transition flex items-center gap-1.5"><i class="fa-solid fa-users-rectangle text-base"></i><span class="hidden md:inline">Groups</span></a>
            <a href="/?tab=marketplace" class="p-2 md:px-3 md:py-2 rounded-xl hover:bg-gray-800/20 {{ 'text-accent bg-accent/10' if active_tab == 'marketplace' else '' }} transition flex items-center gap-1.5"><i class="fa-solid fa-store text-base"></i><span class="hidden md:inline">Market</span></a>
            <a href="/?tab=reels" class="p-2 md:px-3 md:py-2 rounded-xl hover:bg-gray-800/20 {{ 'text-accent bg-accent/10' if active_tab == 'reels' else '' }} transition flex items-center gap-1.5"><i class="fa-solid fa-video text-base"></i><span class="hidden md:inline">Reels</span></a>
            
            <a href="/?tab=notifications" class="relative p-2 md:px-3 md:py-2 rounded-xl hover:bg-gray-800/20 {{ 'text-accent bg-accent/10' if active_tab == 'notifications' else '' }} transition flex items-center gap-1.5">
                <i class="fa-solid fa-bell text-base"></i>
                <span class="hidden md:inline">Alerts</span>
                {% if unread_notif_count > 0 %}
                <span class="absolute top-1 right-1 bg-amber-500 text-black text-[10px] font-black w-4 h-4 rounded-full flex items-center justify-center animate-pulse">{{ unread_notif_count }}</span>
                {% endif %}
            </a>

            <a href="/?tab=messages" class="relative p-2 md:px-3 md:py-2 rounded-xl hover:bg-gray-800/20 {{ 'text-accent bg-accent/10' if active_tab in ['messages', 'group_chat'] else '' }} transition flex items-center gap-1.5">
                <i class="fa-solid fa-message text-base"></i>
                <span class="hidden md:inline">Chat</span>
                {% if unread_count > 0 %}
                <span class="absolute top-1 right-1 bg-red-600 text-white text-[10px] font-black w-4 h-4 rounded-full flex items-center justify-center animate-pulse">{{ unread_count }}</span>
                {% endif %}
            </a>

            <button onclick="toggleTheme()" class="p-2.5 rounded-xl hover:bg-gray-800/20 transition" title="Toggle Mode">
                <i id="theme-icon" class="fa-solid fa-sun text-amber-400 text-base"></i>
            </button>
            
            <div class="h-5 w-[1px] bg-gray-500/30 mx-0.5"></div>

            <a href="/?tab=profile" class="flex items-center gap-2 hover:opacity-85 transition">
                <img src="{{ session.get('avatar') }}" class="w-8 h-8 rounded-full border border-accent object-cover">
            </a>
            <a href="/logout" class="bg-red-500/10 text-red-400 border border-red-500/20 px-2.5 py-1.5 rounded-xl hover:bg-red-500 hover:text-white transition text-xs font-bold"><i class="fa-solid fa-right-from-bracket"></i></a>
        </div>
        {% endif %}
    </nav>

    <!-- Main Container Layout -->
    <main class="flex-1 w-full max-w-full px-3 py-4 md:p-6 relative overflow-hidden">
        
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for cat, msg in messages %}
              <div class="mb-4 p-4 rounded-xl border {{ 'bg-red-950/50 border-red-500 text-red-200' if cat == 'error' else 'bg-blue-950/50 border-blue-500 text-blue-200' }}">
                {{ msg }}
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- UNLOGGED: LOGIN / SIGNUP -->
        {% if not session.get('user') %}
        <div class="max-w-md mx-auto glass-card p-8 rounded-3xl shadow-2xl mt-16 text-center space-y-6">
            <div class="w-16 h-16 bg-accent/20 text-accent rounded-2xl flex items-center justify-center mx-auto text-2xl border border-accent/30">
                <i class="fa-solid fa-cloud-bolt"></i>
            </div>
            <div>
                <h1 class="text-2xl font-black">Welcome to ChaserConnect</h1>
                <p class="text-xs mt-1 opacity-80">Connect with storm spotters, share live field media, and follow severe weather updates.</p>
            </div>
            
            <form method="POST" action="/login" class="space-y-4 text-left">
                <div>
                    <label class="block text-xs uppercase font-bold mb-1 opacity-75">Username</label>
                    <input type="text" name="username" required class="w-full custom-input rounded-xl px-4 py-3 focus:border-accent focus:outline-none text-sm">
                </div>
                <div>
                    <label class="block text-xs uppercase font-bold mb-1 opacity-75">Password</label>
                    <input type="password" name="password" required class="w-full custom-input rounded-xl px-4 py-3 focus:border-accent focus:outline-none text-sm">
                </div>
                <div class="flex gap-3 pt-2">
                    <button type="submit" class="flex-1 btn-action py-3 rounded-xl shadow-lg text-sm">Log In</button>
                    <button type="submit" formaction="/register" class="flex-1 bg-gray-800 hover:bg-gray-700 text-white font-bold py-3 rounded-xl border border-gray-700 transition text-sm">Sign Up</button>
                </div>
            </form>
        </div>

        <!-- LOGGED IN VIEWS -->
        {% else %}

            <!-- TAB: FEED -->
            {% if active_tab == 'feed' %}

            <!-- Stories Bar -->
            <div class="glass-card p-4 rounded-2xl mb-6 shadow-xl overflow-x-auto flex items-center space-x-4 no-scrollbar">
                {% for post in posts %}
                <div onclick="openStory('{{ post.author }}', '{{ post.avatar }}', '{{ post.content|replace("'", "\\'") }}', '{{ post.image_file }}', '{{ post.threat_tag }}', '{{ post.timestamp.strftime('%b %d, %H:%M') }}')" class="flex flex-col items-center cursor-pointer shrink-0 group">
                    <div class="story-ring">
                        <img src="{{ post.avatar }}" class="w-14 h-14 rounded-full object-cover border-2 border-gray-900 group-hover:scale-105 transition">
                    </div>
                    <span class="text-[11px] font-bold mt-1.5 truncate w-16 text-center">{{ post.author }}</span>
                </div>
                {% endfor %}
                {% if not posts %}
                <div class="text-xs opacity-60 text-center w-full py-2">Share a post to appear in live story bubbles above!</div>
                {% endif %}
            </div>

            <!-- Threat Trend Counter Widget -->
            <div class="glass-card p-3 rounded-2xl mb-4 shadow-lg flex items-center justify-between text-xs overflow-x-auto gap-4">
                <div class="flex items-center gap-1.5 text-accent font-bold shrink-0">
                    <i class="fa-solid fa-chart-line"></i> Live Threat Metrics:
                </div>
                <div class="flex items-center gap-3 shrink-0">
                    <span class="bg-red-950 text-red-300 border border-red-800 px-2.5 py-1 rounded-full font-bold">🔴 Tornado Warnings: {{ count_tornado }}</span>
                    <span class="bg-amber-950 text-amber-300 border border-amber-800 px-2.5 py-1 rounded-full font-bold">📸 Storm Photos: {{ count_photo }}</span>
                    <span class="bg-blue-950 text-blue-300 border border-blue-800 px-2.5 py-1 rounded-full font-bold">⚡ Field Updates: {{ count_general }}</span>
                </div>
            </div>

            <!-- Quick-Filter Threat Pill Buttons -->
            <div class="flex items-center gap-2 overflow-x-auto pb-4 mb-2">
                <button onclick="filterFeed('all')" class="filter-pill bg-accent text-white px-4 py-1.5 rounded-full text-xs font-bold shrink-0 transition shadow">🌍 All Updates</button>
                <button onclick="filterFeed('Tornado')" class="filter-pill custom-input px-4 py-1.5 rounded-full text-xs font-bold shrink-0 transition shadow hover:border-red-500">🔴 Tornado Warnings</button>
                <button onclick="filterFeed('Photo')" class="filter-pill custom-input px-4 py-1.5 rounded-full text-xs font-bold shrink-0 transition shadow hover:border-amber-500">📸 Storm Photos</button>
                <button onclick="filterFeed('Flood')" class="filter-pill custom-input px-4 py-1.5 rounded-full text-xs font-bold shrink-0 transition shadow hover:border-blue-500">🌊 Flash Floods</button>
                <button onclick="filterFeed('Clear')" class="filter-pill custom-input px-4 py-1.5 rounded-full text-xs font-bold shrink-0 transition shadow hover:border-emerald-500">🟢 All Clear</button>
            </div>

            <!-- Post Composer -->
            <div class="glass-card p-4 rounded-2xl mb-6 shadow-xl">
                <form action="/post" method="POST" enctype="multipart/form-data" class="space-y-3">
                    <div class="flex items-start space-x-3">
                        <img src="{{ session.get('avatar') }}" class="w-10 h-10 rounded-full border border-accent object-cover mt-1">
                        <textarea name="content" rows="2" maxlength="280" oninput="updateCharCount(this)" placeholder="What's happening in the field? (Tip: use @username to mention spotters)" required class="flex-1 bg-transparent border-none placeholder-gray-500 focus:outline-none resize-none text-base"></textarea>
                    </div>
                    <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-gray-500/20">
                        <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                            <input type="text" name="location" placeholder="📍 Add location" class="custom-input rounded-lg px-3 py-1.5 text-xs placeholder-gray-500 focus:outline-none">
                            <select name="threat_tag" class="custom-input rounded-lg px-3 py-1.5 text-xs text-accent font-bold">
                                <option value="⚡ Field Update">⚡ Field Update</option>
                                <option value="🔴 TORNADO WARNING">🔴 TORNADO WARNING</option>
                                <option value="📸 STORM PHOTO">📸 STORM PHOTO</option>
                                <option value="🌊 FLASH FLOOD">🌊 FLASH FLOOD</option>
                                <option value="🟢 ALL CLEAR">🟢 ALL CLEAR</option>
                            </select>
                            <label class="cursor-pointer bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs px-3 py-1.5 rounded-lg border border-gray-700 flex items-center gap-1.5">
                                <i class="fa-solid fa-image text-accent"></i> Media <input type="file" name="image" class="hidden">
                            </label>
                        </div>
                        <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
                            <span id="char-counter" class="text-[11px] opacity-60">0 / 280</span>
                            <button type="submit" class="btn-action px-6 py-2 rounded-xl text-xs font-bold shadow-md">Post</button>
                        </div>
                    </div>
                </form>
            </div>

            <!-- Feed Stream -->
            <div class="space-y-4" id="feed-stream">
                {% if not posts %}
                <div class="glass-card p-8 rounded-2xl text-center space-y-2">
                    <i class="fa-solid fa-wind text-3xl text-accent/40"></i>
                    <p class="text-sm font-bold">No field reports yet!</p>
                    <p class="text-xs opacity-75">Be the first storm spotter to share an update using the post box above.</p>
                </div>
                {% endif %}
                
                {% for post in posts %}
                <div class="glass-card rounded-2xl p-5 shadow-lg feed-post relative border {{ 'border-red-500 bg-red-950/20 shadow-red-500/10' if post.is_emergency_broadcast else '' }}" data-tag="{{ post.threat_tag }}">
                    
                    {% if post.is_emergency_broadcast %}
                    <div class="mb-3 bg-red-600 text-white px-3 py-1.5 rounded-xl text-xs font-black flex items-center gap-2 shadow-lg animate-pulse">
                        <i class="fa-solid fa-triangle-exclamation text-base"></i> EMERGENCY BROADCAST: VERIFIED WARNING AMPLIFICATION
                    </div>
                    {% endif %}

                    {% if user_obj.pinned_post_id == post.id %}
                    <div class="absolute top-3 right-12 bg-accent/20 text-accent border border-accent/40 px-2 py-0.5 rounded-full text-[10px] font-bold flex items-center gap-1">
                        <i class="fa-solid fa-thumbtack"></i> Pinned Report
                    </div>
                    {% endif %}

                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center space-x-3">
                            <img src="{{ post.avatar }}" class="w-11 h-11 rounded-full border border-accent/50 object-cover">
                            <div>
                                <div class="flex items-center gap-1.5">
                                    <span class="font-bold text-sm">{{ post.author }}</span>
                                    <i class="fa-solid fa-circle-check text-accent text-xs"></i>
                                    <span class="opacity-60 text-xs">@{{ post.handle }}</span>
                                </div>
                                <div class="flex items-center gap-2 mt-0.5 text-xs opacity-80">
                                    {% if post.location %}<span><i class="fa-solid fa-location-dot text-accent"></i> {{ post.location }}</span>{% endif %}
                                    <span class="px-2 py-0.5 rounded font-bold {{ 'bg-red-950 text-red-300 border border-red-800' if 'TORNADO' in post.threat_tag else 'bg-blue-950 text-blue-300 border border-blue-800' }}">{{ post.threat_tag }}</span>
                                    {% if post.is_shared %}
                                    <span class="bg-indigo-950 text-indigo-300 border border-indigo-800 px-2 py-0.5 rounded font-bold">🔄 Shared from @{{ post.shared_from }}</span>
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center gap-3">
                            <span class="text-xs opacity-60">{{ post.timestamp.strftime('%b %d, %H:%M') }}</span>
                            {% if post.author == session.get('display_name') %}
                            <form action="/pin_post/{{ post.id }}" method="POST" class="inline">
                                <button type="submit" class="opacity-70 hover:text-accent text-xs" title="Pin / Unpin to Profile"><i class="fa-solid fa-thumbtack"></i></button>
                            </form>
                            <form action="/delete_post/{{ post.id }}" method="POST" onsubmit="return confirm('Delete post?');" class="inline">
                                <button type="submit" class="opacity-70 hover:text-red-400 text-xs"><i class="fa-solid fa-trash"></i></button>
                            </form>
                            {% endif %}
                        </div>
                    </div>

                    <p class="text-sm mb-3 leading-relaxed">{{ post.content | mentions | safe }}</p>

                    {% if post.image_file %}
                    <div onclick="openLightbox('{{ url_for('static', filename='uploads/' + post.image_file) }}')" class="mb-4 rounded-xl overflow-hidden border border-gray-500/20 max-h-[420px] bg-black flex justify-center shadow-md cursor-pointer group relative">
                        <img src="{{ url_for('static', filename='uploads/' + post.image_file) }}" class="object-contain max-h-[420px] w-full group-hover:scale-102 transition">
                        <div class="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white text-xs font-bold gap-2">
                            <i class="fa-solid fa-expand text-lg"></i> Click to Expand Lightbox
                        </div>
                    </div>
                    {% endif %}

                    <!-- Reactions & Share -->
                    <div class="flex items-center justify-between pt-3 border-t border-gray-500/20 text-xs opacity-85">
                        <div class="flex items-center gap-4">
                            <div class="reaction-container">
                                <button class="flex items-center gap-1.5 hover:text-accent transition font-bold bg-black/20 px-3 py-1.5 rounded-xl border border-gray-500/20">
                                    <span>⚡ {{ post.reactions_bolt }}</span>
                                    <span>📡 {{ post.reactions_radar }}</span>
                                    <span>🚨 {{ post.reactions_siren }}</span>
                                    <span>📸 {{ post.reactions_capture }}</span>
                                    <span class="ml-1 text-[10px] opacity-75">React ▼</span>
                                </button>
                                <div class="reaction-popup">
                                    <form action="/react/{{ post.id }}/bolt" method="POST"><button type="submit" class="reaction-btn" title="Storm Bolt">⚡</button></form>
                                    <form action="/react/{{ post.id }}/radar" method="POST"><button type="submit" class="reaction-btn" title="Radar Sweep">📡</button></form>
                                    <form action="/react/{{ post.id }}/siren" method="POST"><button type="submit" class="reaction-btn" title="Siren Alert">🚨</button></form>
                                    <form action="/react/{{ post.id }}/capture" method="POST"><button type="submit" class="reaction-btn" title="Awesome Capture">📸</button></form>
                                </div>
                            </div>

                            <form action="/share_post/{{ post.id }}" method="POST">
                                <button type="submit" class="flex items-center gap-1.5 hover:text-accent font-semibold bg-black/20 px-3 py-1.5 rounded-xl border border-gray-500/20 transition" title="Amplify as Emergency Broadcast">
                                    <i class="fa-solid fa-bullhorn text-red-400"></i> Broadcast Share
                                </button>
                            </form>
                        </div>

                        <div class="flex items-center gap-4">
                            <span><i class="fa-regular fa-comment mr-1"></i> {{ comments_map[post.id]|length }} replies</span>
                            <a href="/?tab=messages&with={{ post.author }}" class="hover:text-accent"><i class="fa-solid fa-envelope"></i> Message</a>
                        </div>
                    </div>

                    <!-- Comments Section -->
                    <div class="mt-4 space-y-2 pt-3 border-t border-gray-500/10">
                        {% for comment in comments_map[post.id] %}
                        <div class="bg-black/20 p-2.5 rounded-xl border border-gray-500/10 text-xs flex justify-between items-center">
                            <div>
                                <span class="font-bold text-accent">@{{ comment.handle }}:</span> <span class="opacity-90">{{ comment.text | mentions | safe }}</span>
                            </div>
                            <span class="text-[10px] opacity-60">{{ comment.timestamp.strftime('%H:%M') }}</span>
                        </div>
                        {% endfor %}
                        <form action="/comment/{{ post.id }}" method="POST" class="flex gap-2 mt-2">
                            <input type="text" name="text" placeholder="Write a reply..." required class="flex-1 custom-input rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:border-accent">
                            <button type="submit" class="bg-gray-800 text-accent px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-gray-700">Reply</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            <!-- TAB: COMMUNITIES -->
            {% if active_tab == 'communities' %}
            <div class="space-y-6">
                <div class="glass-card p-6 rounded-2xl flex items-center justify-between shadow-xl">
                    <div>
                        <h2 class="text-lg font-black"><i class="fa-solid fa-users-rectangle text-accent mr-2"></i> Weather Communities & Groups</h2>
                        <p class="text-xs opacity-75 mt-0.5">Join regional spotter networks, photography clubs, and research hubs.</p>
                    </div>
                    <button onclick="document.getElementById('create-community-modal').classList.remove('hidden')" class="btn-action px-4 py-2 rounded-xl text-xs font-bold shadow-md flex items-center gap-1.5">
                        <i class="fa-solid fa-plus"></i> Create Group
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {% for c in communities %}
                    <div class="glass-card rounded-2xl overflow-hidden shadow-lg border border-gray-700 flex flex-col justify-between">
                        <div class="p-5 space-y-3">
                            <div class="flex items-center space-x-3">
                                <img src="{{ c.avatar }}" class="w-12 h-12 rounded-full object-cover border-2 border-accent">
                                <div>
                                    <h3 class="font-black text-sm">{{ c.name }}</h3>
                                    <span class="text-[10px] opacity-75">Admin: @{{ c.admin }}</span>
                                </div>
                            </div>
                            <p class="text-xs leading-relaxed opacity-90">{{ c.description }}</p>
                        </div>
                        <div class="p-3 bg-black/20 border-t border-gray-500/10 flex justify-end">
                            <a href="/?tab=community_detail&id={{ c.id }}" class="btn-action px-4 py-1.5 rounded-xl text-xs font-bold shadow">Visit Group Feed</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- TAB: COMMUNITY DETAIL FEED -->
            {% if active_tab == 'community_detail' and active_community %}
            <div class="space-y-6">
                <div class="glass-card p-6 rounded-2xl shadow-xl flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <img src="{{ active_community.avatar }}" class="w-16 h-16 rounded-full object-cover border-2 border-accent shadow-md">
                        <div>
                            <h2 class="text-xl font-black">{{ active_community.name }}</h2>
                            <p class="text-xs opacity-75 mt-0.5">Admin: <span class="text-accent font-bold">@{{ active_community.admin }}</span></p>
                            <p class="text-xs mt-2 leading-relaxed max-w-md">{{ active_community.description }}</p>
                        </div>
                    </div>
                    <a href="/?tab=communities" class="bg-gray-800 hover:bg-gray-700 text-xs px-3.5 py-2 rounded-xl border border-gray-700 font-bold transition">← All Groups</a>
                </div>

                <div class="glass-card p-4 rounded-2xl shadow-xl">
                    <form action="/post_community/{{ active_community.id }}" method="POST" class="space-y-3">
                        <textarea name="content" rows="2" placeholder="Post an update inside {{ active_community.name }}..." required class="w-full custom-input rounded-xl p-3 text-xs focus:outline-none focus:border-accent resize-none"></textarea>
                        <div class="flex justify-end">
                            <button type="submit" class="btn-action px-5 py-2 rounded-xl text-xs font-bold shadow-md">Post to Group</button>
                        </div>
                    </form>
                </div>

                <div class="space-y-3">
                    {% for cp in community_posts %}
                    <div class="glass-card p-4 rounded-2xl shadow-md space-y-2">
                        <div class="flex items-center justify-between text-xs">
                            <div class="flex items-center space-x-2.5">
                                <img src="{{ cp.avatar }}" class="w-8 h-8 rounded-full border border-accent object-cover">
                                <span class="font-bold">{{ cp.author }} <span class="opacity-60">@{{ cp.handle }}</span></span>
                            </div>
                            <span class="opacity-60 text-[10px]">{{ cp.timestamp.strftime('%b %d, %H:%M') }}</span>
                        </div>
                        <p class="text-xs leading-relaxed pl-10">{{ cp.content | mentions | safe }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- TAB: MARKETPLACE -->
            {% if active_tab == 'marketplace' %}
            <div class="space-y-6">
                <div class="glass-card p-6 rounded-2xl flex items-center justify-between shadow-xl">
                    <div>
                        <h2 class="text-lg font-black"><i class="fa-solid fa-store text-accent mr-2"></i> Storm Chaser Marketplace & Gear Exchange</h2>
                        <p class="text-xs opacity-75 mt-0.5">Buy, sell, or trade weather radios, cameras, and field equipment.</p>
                    </div>
                    <button onclick="document.getElementById('create-market-modal').classList.remove('hidden')" class="btn-action px-4 py-2 rounded-xl text-xs font-bold shadow-md flex items-center gap-1.5">
                        <i class="fa-solid fa-tag"></i> List Item
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {% for item in market_items %}
                    <div class="glass-card rounded-2xl overflow-hidden shadow-lg border border-gray-700 flex flex-col justify-between">
                        {% if item.image_file %}
                        <div class="h-48 bg-black overflow-hidden relative">
                            <img src="{{ url_for('static', filename='uploads/' + item.image_file) }}" class="w-full h-full object-cover">
                            <div class="absolute top-3 left-3 bg-accent text-white px-2.5 py-1 rounded-lg text-xs font-black shadow-lg">
                                ${{ item.price }}
                            </div>
                        </div>
                        {% endif %}
                        <div class="p-5 space-y-2">
                            <div class="flex justify-between items-start">
                                <h3 class="font-black text-sm">{{ item.title }}</h3>
                                {% if not item.image_file %}
                                <span class="bg-accent text-white px-2.5 py-1 rounded-lg text-xs font-black">${{ item.price }}</span>
                                {% endif %}
                            </div>
                            <div class="flex items-center gap-2 text-[11px] opacity-75">
                                <span><i class="fa-solid fa-location-dot text-accent"></i> {{ item.location }}</span>
                                <span>•</span>
                                <span class="bg-gray-800 px-2 py-0.5 rounded text-accent font-bold">{{ item.category }}</span>
                            </div>
                            <p class="text-xs leading-relaxed opacity-90 pt-1">{{ item.description }}</p>
                        </div>
                        <div class="p-3 bg-black/20 border-t border-gray-500/10 flex items-center justify-between text-xs">
                            <span class="opacity-75">Seller: <span class="text-accent font-bold">@{{ item.handle }}</span></span>
                            <a href="/?tab=messages&with={{ item.seller }}" class="btn-action px-3 py-1.5 rounded-xl font-bold shadow">Contact Seller</a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- TAB: REELS -->
            {% if active_tab == 'reels' %}
            <div class="space-y-6 max-w-md mx-auto">
                <div class="glass-card p-5 rounded-2xl shadow-xl">
                    <h3 class="font-bold text-sm mb-3"><i class="fa-solid fa-video text-accent mr-2"></i> Share a Field Reel / Video</h3>
                    <form action="/upload_reel" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs">
                        <div>
                            <label class="block font-bold mb-1 opacity-75">Caption / Description</label>
                            <input type="text" name="caption" placeholder="e.g., Massive rotating wall cloud near Sylacauga!" required class="w-full custom-input rounded-xl px-3 py-2">
                        </div>
                        <div>
                            <label class="block font-bold mb-1 opacity-75">Select Video File (.mp4)</label>
                            <input type="file" name="video" accept="video/*" required class="w-full custom-input rounded-xl px-3 py-2">
                        </div>
                        <button type="submit" class="w-full btn-action py-2.5 rounded-xl font-bold">Publish Reel</button>
                    </form>
                </div>

                <div class="space-y-6">
                    {% for reel in reels %}
                    <div class="glass-card rounded-3xl overflow-hidden shadow-2xl border border-gray-700">
                        <div class="p-3 flex items-center justify-between border-b border-gray-500/10">
                            <div class="flex items-center space-x-2.5">
                                <img src="{{ reel.avatar }}" class="w-8 h-8 rounded-full border border-accent object-cover">
                                <div>
                                    <span class="font-bold text-xs block">{{ reel.author }}</span>
                                    <span class="text-[10px] opacity-60">@{{ reel.handle }}</span>
                                </div>
                            </div>
                            <span class="text-[10px] opacity-60">{{ reel.timestamp.strftime('%b %d, %H:%M') }}</span>
                        </div>
                        <div class="bg-black aspect-[9/16] max-h-[480px] flex items-center justify-center relative">
                            <video src="{{ url_for('static', filename='uploads/' + reel.video_file) }}" controls autoplay muted loop class="w-full h-full object-contain"></video>
                        </div>
                        <div class="p-4 text-xs">
                            <p class="leading-relaxed">{{ reel.caption | mentions | safe }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- TAB: NOTIFICATIONS -->
            {% if active_tab == 'notifications' %}
            <div class="glass-card p-6 rounded-2xl space-y-4">
                <div class="flex items-center justify-between mb-2">
                    <h2 class="text-lg font-bold"><i class="fa-solid fa-bell text-amber-400 mr-2"></i> Activity Alerts</h2>
                    <span class="text-xs opacity-75">Recent likes, comments & shares</span>
                </div>
                <div class="space-y-3">
                    {% for n in notifications %}
                    <div class="bg-black/20 p-4 rounded-xl border border-gray-500/10 flex items-center justify-between text-xs">
                        <div class="flex items-center gap-3">
                            <div class="w-9 h-9 rounded-full bg-accent/20 border border-accent/30 text-accent flex items-center justify-center font-bold">
                                <i class="fa-solid fa-bell"></i>
                            </div>
                            <div>
                                <span class="font-bold text-white">@{{ n.actor }}</span> {{ n.action }}
                                {% if n.target_text %}<p class="opacity-75 italic mt-0.5">"{{ n.target_text }}"</p>{% endif %}
                            </div>
                        </div>
                        <span class="text-[10px] opacity-60">{{ n.timestamp.strftime('%b %d, %H:%M') }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- TAB: MESSAGES -->
            {% if active_tab in ['messages', 'group_chat'] %}
            <div class="glass-card p-4 rounded-2xl grid grid-cols-1 md:grid-cols-3 gap-4 h-[78vh]">
                <div class="border-r border-gray-500/20 pr-3 overflow-y-auto space-y-4">
                    <div class="flex items-center justify-between">
                        <h3 class="font-bold text-sm">Messenger</h3>
                        <button onclick="document.getElementById('create-group-modal').classList.remove('hidden')" class="btn-action px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1">
                            <i class="fa-solid fa-user-group"></i> New Chat
                        </button>
                    </div>

                    <div class="space-y-1.5">
                        <div class="text-[10px] uppercase font-bold opacity-60 tracking-wider">Private Group Chats</div>
                        {% for g in group_chats %}
                        <a href="/?tab=group_chat&group_id={{ g.id }}" class="block p-2.5 rounded-xl {{ 'bg-accent/20 border-accent/50' if active_tab == 'group_chat' and active_group and active_group.id == g.id else 'bg-black/20 border-gray-500/10' }} border transition">
                            <div class="flex items-center space-x-2.5">
                                <img src="{{ g.avatar }}" class="w-8 h-8 rounded-full object-cover border border-gray-700">
                                <div class="truncate">
                                    <div class="font-bold text-xs truncate">{{ g.name }} <i class="fa-solid fa-lock text-[10px] text-amber-400 ml-1"></i></div>
                                    <div class="text-[10px] opacity-75">Admin: @{{ g.admin }}</div>
                                </div>
                            </div>
                        </a>
                        {% endfor %}
                    </div>

                    <div class="space-y-1.5 pt-2">
                        <div class="text-[10px] uppercase font-bold opacity-60 tracking-wider">Direct Messages</div>
                        {% for u in users %}
                          {% set u_name = u.display_name or u.username %}
                          {% if u.username != session.get('user') %}
                          <a href="/?tab=messages&with={{ u_name }}" class="block p-2.5 rounded-xl {{ 'bg-accent/20 border-accent/50' if active_tab == 'messages' and recipient == u_name else 'bg-black/20 border-gray-500/10' }} border transition">
                              <div class="flex items-center space-x-2.5">
                                  <img src="{{ u.avatar }}" class="w-8 h-8 rounded-full object-cover border border-gray-700">
                                  <div class="truncate">
                                      <div class="font-bold text-xs truncate">{{ u_name }}</div>
                                      <div class="text-[10px] opacity-75">@{{ u.handle }}</div>
                                  </div>
                              </div>
                          </a>
                          {% endif %}
                        {% endfor %}
                    </div>
                </div>

                <div class="md:col-span-2 flex flex-col justify-between">
                    {% if active_tab == 'group_chat' and active_group %}
                    <div class="border-b border-gray-500/20 pb-2 mb-2 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <img src="{{ active_group.avatar }}" class="w-9 h-9 rounded-full object-cover border border-accent">
                            <div>
                                <span class="font-bold text-sm block">{{ active_group.name }} <i class="fa-solid fa-lock text-xs text-amber-400 ml-1"></i></span>
                                <span class="text-[10px] opacity-75">Admin: <span class="text-accent font-bold">@{{ active_group.admin }}</span> • {{ group_members|length }} members</span>
                            </div>
                        </div>
                        {% if active_group.admin == session.get('display_name') %}
                        <button onclick="document.getElementById('edit-group-modal').classList.remove('hidden')" class="bg-gray-800 hover:bg-gray-700 text-xs px-3 py-1.5 rounded-lg border border-gray-700 text-accent font-bold transition flex items-center gap-1">
                            <i class="fa-solid fa-gear"></i> Settings
                        </button>
                        {% endif %}
                    </div>

                    <div class="flex-1 overflow-y-auto space-y-3 pr-2 mb-3 bg-black/10 p-3 rounded-xl border border-gray-500/10">
                        {% for gm in group_messages %}
                        <div class="p-3 rounded-xl max-w-[80%] {{ 'ml-auto btn-action shadow-md' if gm.sender == session.get('display_name') else 'bg-gray-800 text-gray-200' }}">
                            <div class="text-[10px] opacity-75 mb-0.5 flex justify-between gap-4">
                                <span class="font-bold">{{ gm.sender }}</span>
                                <span>{{ gm.timestamp.strftime('%H:%M') }}</span>
                            </div>
                            <p class="text-xs leading-relaxed">{{ gm.message | mentions | safe }}</p>
                        </div>
                        {% endfor %}
                    </div>

                    <form action="/send_group_msg" method="POST" class="flex gap-2">
                        <input type="hidden" name="group_id" value="{{ active_group.id }}">
                        <input type="text" name="message" placeholder="Message private group..." required class="flex-1 custom-input rounded-xl px-4 py-2 text-xs focus:outline-none focus:border-accent">
                        <button type="submit" class="btn-action px-5 py-2 rounded-xl text-xs font-bold shadow-md">Send</button>
                    </form>

                    {% elif recipient %}
                    <div class="border-b border-gray-500/20 pb-2 mb-2 flex items-center gap-2">
                        <span class="font-bold text-sm">Conversation with <span class="text-accent">{{ recipient }}</span></span>
                    </div>
                    <div class="flex-1 overflow-y-auto space-y-3 pr-2 mb-3 bg-black/10 p-3 rounded-xl border border-gray-500/10">
                        {% for dm in dms %}
                        <div class="p-3 rounded-xl max-w-[80%] {{ 'ml-auto btn-action shadow-md' if dm.sender == session.get('display_name') else 'bg-gray-800 text-gray-200' }}">
                            <div class="text-[10px] opacity-75 mb-0.5">{{ dm.sender }} • {{ dm.timestamp.strftime('%H:%M') }}</div>
                            <p class="text-xs leading-relaxed">{{ dm.message | mentions | safe }}</p>
                        </div>
                        {% endfor %}
                    </div>
                    <form action="/send_dm" method="POST" class="flex gap-2">
                        <input type="hidden" name="recipient" value="{{ recipient }}">
                        <input type="text" name="message" placeholder="Type a message..." required class="flex-1 custom-input rounded-xl px-4 py-2 text-xs focus:outline-none focus:border-accent">
                        <button type="submit" class="btn-action px-5 py-2 rounded-xl text-xs font-bold shadow-md">Send</button>
                    </form>
                    {% else %}
                    <div class="flex-1 flex flex-col items-center justify-center opacity-60 space-y-2">
                        <i class="fa-solid fa-comments text-3xl text-accent/30"></i>
                        <p class="text-xs">Select a private group chat or direct message on the left.</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endif %}

            <!-- TAB: EXPLORE -->
            {% if active_tab == 'explore' %}
            <div class="glass-card p-6 rounded-2xl space-y-4">
                <div class="flex items-center justify-between mb-2">
                    <h2 class="text-lg font-bold"><i class="fa-solid fa-compass text-accent mr-2"></i> Explore Storm Media</h2>
                    <span class="text-xs opacity-75">Recent field captures</span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {% for post in posts_with_images %}
                    <div onclick="openLightbox('{{ url_for('static', filename='uploads/' + post.image_file) }}')" class="group relative bg-black rounded-xl overflow-hidden border border-gray-500/20 aspect-square cursor-pointer">
                        <img src="{{ url_for('static', filename='uploads/' + post.image_file) }}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent opacity-0 group-hover:opacity-100 transition flex flex-col justify-end p-3 text-xs">
                            <span class="font-bold text-white">@{{ post.handle }}</span>
                            <span class="text-accent text-[10px]">{{ post.threat_tag }}</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- TAB: PROFILE (Persistent User Posts & Ribbons) -->
            {% if active_tab == 'profile' %}
            <div class="glass-card rounded-2xl overflow-hidden shadow-2xl max-w-xl mx-auto space-y-6">
                <div class="h-36 bg-cover bg-center relative" style="background-image: url('{{ user_obj.cover_photo }}');">
                    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent"></div>
                </div>
                <div class="px-6 pb-6 relative">
                    <div class="flex justify-between items-end -mt-12 mb-4">
                        <img src="{{ user_obj.avatar }}" class="w-24 h-24 rounded-full border-4 border-gray-900 object-cover shadow-xl">
                        <a href="/?tab=profile_edit" class="bg-gray-800 hover:bg-gray-700 text-white text-xs font-bold px-4 py-2 rounded-xl border border-gray-700 transition">Edit Profile</a>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <h2 class="text-xl font-black">{{ user_obj.display_name }}</h2>
                            <i class="fa-solid fa-circle-check text-accent text-sm" title="Verified Spotter"></i>
                        </div>
                        <p class="text-xs opacity-75">@{{ user_obj.handle }} • {{ user_obj.role }}</p>
                        
                        <!-- Professional Rank Ribbons -->
                        <div class="flex flex-wrap gap-2 mt-3">
                            {% if user_obj.skywarn_certified %}
                            <span class="bg-gradient-to-r from-blue-900 to-indigo-900 text-blue-200 border border-blue-500/40 px-3 py-1 rounded-lg text-[11px] font-bold flex items-center gap-1.5 shadow-md">
                                <i class="fa-solid fa-medal text-amber-400"></i> NWS SKYWARN Certified Spotter
                            </span>
                            {% endif %}
                            {% if user_obj.fema_certified %}
                            <span class="bg-gradient-to-r from-emerald-900 to-teal-900 text-emerald-200 border border-emerald-500/40 px-3 py-1 rounded-lg text-[11px] font-bold flex items-center gap-1.5 shadow-md">
                                <i class="fa-solid fa-shield-halved text-emerald-400"></i> FEMA Emergency Mgmt (IS-100)
                            </span>
                            {% endif %}
                            <span class="bg-gradient-to-r from-zinc-800 to-zinc-900 text-zinc-300 border border-zinc-700 px-3 py-1 rounded-lg text-[11px] font-bold flex items-center gap-1.5 shadow-md">
                                <i class="fa-solid fa-star text-accent"></i> {{ user_obj.field_years }} Field Veteran
                            </span>
                        </div>

                        <p class="text-xs mt-3 leading-relaxed bg-black/20 p-3 rounded-xl border border-gray-500/10">{{ user_obj.bio | mentions | safe }}</p>
                    </div>

                    <!-- Pinned Post Section -->
                    {% if pinned_post %}
                    <div class="mt-6 pt-6 border-t border-gray-500/20">
                        <div class="flex items-center gap-2 mb-2 text-xs font-bold text-accent">
                            <i class="fa-solid fa-thumbtack"></i> Pinned Weather Report
                        </div>
                        <div class="bg-black/30 p-4 rounded-xl border border-accent/30 text-xs space-y-2">
                            <div class="flex justify-between font-bold">
                                <span>{{ pinned_post.threat_tag }}</span>
                                <span class="opacity-60">{{ pinned_post.timestamp.strftime('%b %d, %H:%M') }}</span>
                            </div>
                            <p class="leading-relaxed">{{ pinned_post.content | mentions | safe }}</p>
                            {% if pinned_post.image_file %}
                            <div onclick="openLightbox('{{ url_for('static', filename='uploads/' + pinned_post.image_file) }}')" class="rounded-lg overflow-hidden max-h-40 bg-black flex justify-center cursor-pointer">
                                <img src="{{ url_for('static', filename='uploads/' + pinned_post.image_file) }}" class="object-contain max-h-40 w-full">
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endif %}

                    <!-- Instagram Style Gallery Grid (Linked via user_id) -->
                    <div class="mt-6 pt-6 border-t border-gray-500/20">
                        <div class="flex items-center justify-between mb-3 text-xs font-bold uppercase tracking-wider opacity-80">
                            <span><i class="fa-solid fa-grid mr-1.5 text-accent"></i> Field Media Grid</span>
                            <span>{{ user_media_posts|length }} Captures</span>
                        </div>
                        <div class="grid grid-cols-3 gap-2">
                            {% for post in user_media_posts %}
                            <div onclick="openLightbox('{{ url_for('static', filename='uploads/' + post.image_file) }}')" class="aspect-square bg-black rounded-lg overflow-hidden border border-gray-700 cursor-pointer group relative">
                                <img src="{{ url_for('static', filename='uploads/' + post.image_file) }}" class="w-full h-full object-cover group-hover:scale-105 transition">
                                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white text-xs">
                                    <i class="fa-solid fa-magnifying-glass-plus"></i>
                                </div>
                            </div>
                            {% endfor %}
                            {% if not user_media_posts %}
                            <div class="col-span-3 text-center py-8 text-xs opacity-60">No photos posted to grid yet.</div>
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}

            <!-- TAB: PROFILE EDIT -->
            {% if active_tab == 'profile_edit' %}
            <div class="glass-card p-6 rounded-2xl shadow-xl max-w-lg mx-auto">
                <h2 class="text-lg font-bold mb-4"><i class="fa-solid fa-user-gear mr-2 text-accent"></i> Edit Profile & Rank Ribbons</h2>
                <form action="/profile" method="POST" enctype="multipart/form-data" class="space-y-4 text-xs">
                    <div>
                        <label class="block font-bold mb-1 opacity-75">Display Name</label>
                        <input type="text" name="display_name" value="{{ user_obj.display_name }}" class="w-full custom-input rounded-xl px-4 py-2">
                    </div>
                    <div>
                        <label class="block font-bold mb-1 opacity-75">Role / Title</label>
                        <input type="text" name="role" value="{{ user_obj.role }}" class="w-full custom-input rounded-xl px-4 py-2">
                    </div>
                    <div>
                        <label class="block font-bold mb-1 opacity-75">Bio</label>
                        <textarea name="bio" rows="3" class="w-full custom-input rounded-xl px-4 py-2 resize-none">{{ user_obj.bio }}</textarea>
                    </div>

                    <!-- Credibility Checkboxes -->
                    <div class="space-y-2 pt-2 border-t border-gray-500/20">
                        <label class="block font-bold text-accent uppercase tracking-wider">Spotter Rank Ribbons & Certifications</label>
                        <div class="flex items-center gap-2">
                            <input type="checkbox" name="skywarn" id="skywarn" value="yes" {{ 'checked' if user_obj.skywarn_certified else '' }} class="w-4 h-4 rounded">
                            <label for="skywarn" class="font-bold">NWS SKYWARN Certified Spotter</label>
                        </div>
                        <div class="flex items-center gap-2">
                            <input type="checkbox" name="fema" id="fema" value="yes" {{ 'checked' if user_obj.fema_certified else '' }} class="w-4 h-4 rounded">
                            <label for="fema" class="font-bold">FEMA Emergency Management (IS-100 or Equivalent)</label>
                        </div>
                        <div>
                            <label class="block font-bold mb-1 opacity-75 pt-1">Field Experience Years</label>
                            <select name="field_years" class="w-full custom-input rounded-xl px-3 py-2 font-bold">
                                <option value="1-3 Years" {{ 'selected' if user_obj.field_years == '1-3 Years' else '' }}>1-3 Years</option>
                                <option value="3-5 Years" {{ 'selected' if user_obj.field_years == '3-5 Years' else '' }}>3-5 Years</option>
                                <option value="5-10 Years" {{ 'selected' if user_obj.field_years == '5-10 Years' else '' }}>5-10 Years</option>
                                <option value="10+ Years" {{ 'selected' if user_obj.field_years == '10+ Years' else '' }}>10+ Years (Veteran Chaser)</option>
                            </select>
                        </div>
                    </div>

                    <div class="pt-2 border-t border-gray-500/20">
                        <label class="block font-bold mb-1 opacity-75">UI Accent Theme</label>
                        <select name="accent" class="w-full custom-input rounded-xl px-4 py-2 font-bold">
                            <option value="blue" {{ 'selected' if user_obj.accent == 'blue' else '' }}>📡 Radar Blue (Default)</option>
                            <option value="red" {{ 'selected' if user_obj.accent == 'red' else '' }}>🔴 Severe Red</option>
                            <option value="amber" {{ 'selected' if user_obj.accent == 'amber' else '' }}>⚠️ Warning Amber</option>
                            <option value="emerald" {{ 'selected' if user_obj.accent == 'emerald' else '' }}>🟢 Emerald Clear</option>
                        </select>
                    </div>
                    <div>
                        <label class="block font-bold mb-1 opacity-75">Profile Avatar Image</label>
                        <input type="file" name="avatar" class="opacity-75">
                    </div>
                    <button type="submit" class="w-full btn-action py-2.5 rounded-xl text-xs font-bold shadow-md">Save Profile & Ribbons</button>
                </form>
            </div>
            {% endif %}

        {% endif %}
    </main>

    <!-- Modals -->
    <div id="create-group-modal" class="fixed inset-0 z-50 bg-black/90 backdrop-blur-md hidden flex items-center justify-center p-4">
        <div class="glass-card max-w-md w-full rounded-3xl p-6 relative border border-gray-700 space-y-4">
            <button onclick="document.getElementById('create-group-modal').classList.add('hidden')" class="absolute top-4 right-4 bg-gray-800 text-white w-8 h-8 rounded-full flex items-center justify-center hover:bg-red-600 transition"><i class="fa-solid fa-xmark"></i></button>
            <h3 class="font-bold text-base"><i class="fa-solid fa-users text-accent mr-2"></i> Create Private Group Chat</h3>
            <form action="/create_group" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs">
                <div>
                    <label class="block font-bold mb-1 opacity-75">Group Name</label>
                    <input type="text" name="name" placeholder="e.g., Dixie Alley Chase Team" required class="w-full custom-input rounded-xl px-4 py-2.5">
                </div>
                <div>
                    <label class="block font-bold mb-1 opacity-75">Group Picture (Select from Gallery)</label>
                    <input type="file" name="avatar_file" class="w-full custom-input rounded-xl px-3 py-2">
                </div>
                <button type="submit" class="w-full btn-action py-2.5 rounded-xl font-bold">Create Private Group</button>
            </form>
        </div>
    </div>

    <div id="create-community-modal" class="fixed inset-0 z-50 bg-black/90 backdrop-blur-md hidden flex items-center justify-center p-4">
        <div class="glass-card max-w-md w-full rounded-3xl p-6 relative border border-gray-700 space-y-4">
            <button onclick="document.getElementById('create-community-modal').classList.add('hidden')" class="absolute top-4 right-4 bg-gray-800 text-white w-8 h-8 rounded-full flex items-center justify-center hover:bg-red-600 transition"><i class="fa-solid fa-xmark"></i></button>
            <h3 class="font-bold text-base"><i class="fa-solid fa-users-rectangle text-accent mr-2"></i> Create Weather Community Group</h3>
            <form action="/create_community" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs">
                <div>
                    <label class="block font-bold mb-1 opacity-75">Community Name</label>
                    <input type="text" name="name" placeholder="e.g., Alabama Spotter Network" required class="w-full custom-input rounded-xl px-4 py-2.5">
                </div>
                <div>
                    <label class="block font-bold mb-1 opacity-75">Description</label>
                    <textarea name="description" rows="3" placeholder="What is this community group about?" required class="w-full custom-input rounded-xl px-4 py-2.5 resize-none"></textarea>
                </div>
                <div>
                    <label class="block font-bold mb-1 opacity-75">Group Banner / Logo</label>
                    <input type="file" name="avatar_file" class="w-full custom-input rounded-xl px-3 py-2">
                </div>
                <button type="submit" class="w-full btn-action py-2.5 rounded-xl font-bold">Launch Community</button>
            </form>
        </div>
    </div>

    <div id="create-market-modal" class="fixed inset-0 z-50 bg-black/90 backdrop-blur-md hidden flex items-center justify-center p-4">
        <div class="glass-card max-w-md w-full rounded-3xl p-6 relative border border-gray-700 space-y-4 max-h-[90vh] overflow-y-auto">
            <button onclick="document.getElementById('create-market-modal').classList.add('hidden')" class="absolute top-4 right-4 bg-gray-800 text-white w-8 h-8 rounded-full flex items-center justify-center hover:bg-red-600 transition"><i class="fa-solid fa-xmark"></i></button>
            <h3 class="font-bold text-base"><i class="fa-solid fa-store text-accent mr-2"></i> List Gear on Marketplace</h3>
            <form action="/create_marketplace_item" method="POST" enctype="multipart/form-data" class="space-y-3 text-xs">
                <div>
                    <label class="block font-bold mb-1 opacity-75">Item Title</label>
                    <input type="text" name="title" placeholder="e.g., Midland NOAA Weather Radio / Dash Camera" required class="w-full custom-input rounded-xl px-4 py-2.5">
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="block font-bold mb-1 opacity-75">Price ($)</label>
                        <input type="text" name="price" placeholder="120" required class="w-full custom-input rounded-xl px-4 py-2.5">
                    </div>
                    <div>
                        <label class="block font-bold mb-1 opacity-75">Category</label>
                        <select name="category" class="w-full custom-input rounded-xl px-3 py-2.5 font-bold">
                            <option value="Gear & Equipment">Gear & Equipment</option>
                            <option value="Cameras & Optics">Cameras & Optics</option>
                            <option value="Radios & Comms">Radios & Comms</option>
                            <option value="Vehicle Mounts">Vehicle Mounts</option>
                        </select>
                    </div>
                </div>
                <div>
                    <label class="block font-bold mb-1 opacity-75">Location</label>
                    <input type="text" name="location" placeholder="e.g., Sylacauga, AL" required class="w-full custom-input rounded-xl px-4 py-2.5">
                </div>
                <div>
                    <label class="block font-bold mb-1 opacity-75">Description</label>
                    <textarea name="description" rows="3" placeholder="Condition, specs, meetup or shipping details..." required class="w-full custom-input rounded-xl px-4 py-2.5 resize-none"></textarea>
                </div>
                <div>
                    <label class="block font-bold mb-1 opacity-75">Item Photo</label>
                    <input type="file" name="image" class="w-full custom-input rounded-xl px-3 py-2">
                </div>
                <button type="submit" class="w-full btn-action py-2.5 rounded-xl font-bold">Publish Listing</button>
            </form>
        </div>
    </div>

    <!-- Stories Modal -->
    <div id="story-modal" class="fixed inset-0 z-50 bg-black/90 backdrop-blur-md hidden flex items-center justify-center p-4">
        <div class="glass-card max-w-md w-full rounded-3xl overflow-hidden relative p-6 border border-gray-700 shadow-2xl space-y-4">
            <button onclick="closeStory()" class="absolute top-4 right-4 bg-gray-800 text-white w-8 h-8 rounded-full flex items-center justify-center hover:bg-red-600 transition"><i class="fa-solid fa-xmark"></i></button>
            <div class="flex items-center space-x-3">
                <img id="story-avatar" class="w-10 h-10 rounded-full border border-accent object-cover">
                <div>
                    <div id="story-author" class="font-bold text-sm text-white"></div>
                    <div id="story-time" class="text-[10px] text-gray-400"></div>
                </div>
            </div>
            <div class="inline-block px-2.5 py-1 rounded text-xs font-bold bg-blue-950 text-blue-300 border border-blue-800" id="story-tag"></div>
            <p id="story-content" class="text-sm text-gray-200 leading-relaxed"></p>
            <div id="story-image-container" class="rounded-xl overflow-hidden max-h-80 bg-black flex justify-center border border-gray-800">
                <img id="story-image" class="object-contain max-h-80 w-full hidden">
            </div>
        </div>
    </div>

    <!-- Lightbox Modal -->
    <div id="lightbox-modal" class="fixed inset-0 z-50 bg-black/95 backdrop-blur-lg hidden flex items-center justify-center p-4" onclick="closeLightbox()">
        <div class="relative max-w-5xl max-h-[90vh] w-full flex items-center justify-center">
            <button onclick="closeLightbox()" class="absolute -top-12 right-0 text-white bg-gray-800 hover:bg-red-600 w-10 h-10 rounded-full flex items-center justify-center text-lg transition"><i class="fa-solid fa-xmark"></i></button>
            <img id="lightbox-img" class="max-w-full max-h-[85vh] object-contain rounded-2xl shadow-2xl border border-gray-700">
        </div>
    </div>

    <footer class="text-center py-6 text-xs opacity-60 border-t border-gray-500/20 mt-auto">
        ChaserConnect • Public Social Weather Network
    </footer>
</body>
</html>
"""


# --- Unified Controller Route ---
@app.route("/")
def index():
  tornado_active = check_tornado_warning_active()
  live_ticker = get_live_nws_alerts()

  if not session.get("user"):
    return render_template_string(
        TEMPLATE,
        active_tab="feed",
        live_nws_ticker=live_ticker,
        tornado_active=tornado_active,
        user_accent="blue",
    )

  tab = request.args.get("tab", "feed")
  posts = Post.query.order_by(Post.timestamp.desc()).all()
  reels = Reel.query.order_by(Reel.timestamp.desc()).all()
  communities = CommunityGroup.query.order_by(
      CommunityGroup.timestamp.desc()
  ).all()
  market_items = MarketplaceItem.query.order_by(
      MarketplaceItem.timestamp.desc()
  ).all()

  comments_map = {
      p.id: Comment.query.filter_by(post_id=p.id)
      .order_by(Comment.timestamp.asc())
      .all()
      for p in posts
  }
  posts_with_images = [p for p in posts if p.image_file]
  users = User.query.all()
  my_name = session.get("display_name")
  user_obj = User.query.filter_by(username=session["user"]).first()
  user_accent = user_obj.accent if user_obj else "blue"

  pinned_post = None
  if user_obj and user_obj.pinned_post_id:
    pinned_post = Post.query.get(user_obj.pinned_post_id)

  # Fetch posts via persistent user_id foreign key relationship
  user_media_posts = []
  if user_obj:
    user_media_posts = (
        Post.query.filter_by(user_id=user_obj.id)
        .filter(Post.image_file != None)
        .order_by(Post.timestamp.desc())
        .all()
    )

  group_chats = (
      GroupChat.query.join(GroupMember, GroupChat.id == GroupMember.group_id)
      .filter((GroupMember.username == my_name) | (GroupChat.admin == my_name))
      .distinct()
      .order_by(GroupChat.timestamp.desc())
      .all()
  )

  recipient = request.args.get("with")
  group_id = request.args.get("group_id")
  community_id = request.args.get("id")

  count_tornado = sum(1 for p in posts if "TORNADO" in p.threat_tag)
  count_photo = sum(1 for p in posts if "PHOTO" in p.threat_tag)
  count_general = len(posts) - count_tornado - count_photo

  unread_count = DirectMessage.query.filter_by(
      recipient=my_name, is_read=False
  ).count()

  if tab == "notifications":
    unread_notifs = Notification.query.filter_by(
        recipient=my_name, is_read=False
    ).all()
    for n in unread_notifs:
      n.is_read = True
    db.session.commit()

  unread_notif_count = Notification.query.filter_by(
      recipient=my_name, is_read=False
  ).count()
  notifications = (
      Notification.query.filter_by(recipient=my_name)
      .order_by(Notification.timestamp.desc())
      .all()
  )

  dms = []
  if recipient:
    unread_msgs = DirectMessage.query.filter_by(
        sender=recipient, recipient=my_name, is_read=False
    ).all()
    for msg in unread_msgs:
      msg.is_read = True
    db.session.commit()

    dms = (
        DirectMessage.query.filter(
            ((DirectMessage.sender == my_name)
             & (DirectMessage.recipient == recipient))
            | ((DirectMessage.sender == recipient)
               & (DirectMessage.recipient == my_name))
        )
        .order_by(DirectMessage.timestamp.asc())
        .all()
    )

  active_group = None
  group_messages = []
  group_members = []
  if tab == "group_chat" and group_id:
    group_obj = GroupChat.query.get(group_id)
    is_member = GroupMember.query.filter_by(
        group_id=group_id, username=my_name
    ).first()
    if group_obj and (group_obj.admin == my_name or is_member):
      active_group = group_obj
      group_messages = (
          GroupMessage.query.filter_by(group_id=active_group.id)
          .order_by(GroupMessage.timestamp.asc())
          .all()
      )
      group_members = GroupMember.query.filter_by(
          group_id=active_group.id
      ).all()
    else:
      flash(
          "Access denied: You are not a member of this private group chat.",
          "error",
      )
      return redirect("/?tab=messages")

  active_community = None
  community_posts = []
  if tab == "community_detail" and community_id:
    active_community = CommunityGroup.query.get(community_id)
    if active_community:
      community_posts = (
          CommunityPost.query.filter_by(community_id=active_community.id)
          .order_by(CommunityPost.timestamp.desc())
          .all()
      )

  return render_template_string(
      TEMPLATE,
      active_tab=tab,
      posts=posts,
      reels=reels,
      communities=communities,
      market_items=market_items,
      comments_map=comments_map,
      posts_with_images=posts_with_images,
      users=users,
      group_chats=group_chats,
      recipient=recipient,
      active_group=active_group,
      group_messages=group_messages,
      group_members=group_members,
      active_community=active_community,
      community_posts=community_posts,
      dms=dms,
      user_obj=user_obj,
      user_accent=user_accent,
      pinned_post=pinned_post,
      user_media_posts=user_media_posts,
      unread_count=unread_count,
      unread_notif_count=unread_notif_count,
      notifications=notifications,
      live_nws_ticker=live_ticker,
      tornado_active=tornado_active,
      count_tornado=count_tornado,
      count_photo=count_photo,
      count_general=count_general,
  )


# --- Action Endpoints ---
@app.route("/login", methods=["POST"])
def login():
  username_input = request.form.get("username").strip().lower()
  u = User.query.filter_by(username=username_input).first()
  if u and u.password == request.form.get("password"):
    session["user"] = u.username
    session["display_name"] = u.display_name
    session["handle"] = u.handle
    session["avatar"] = u.avatar
  else:
    flash("Invalid username or password.", "error")
  return redirect("/")


@app.route("/register", methods=["POST"])
def register():
  uname = request.form.get("username").strip().lower()
  existing = User.query.filter_by(username=uname).first()
  if existing:
    flash(
        "Username already exists! Please choose a different name or log in.",
        "error",
    )
  else:
    nu = User(
        username=uname,
        password=request.form.get("password"),
        display_name=request.form.get("username").strip(),
        handle=uname,
        accent="blue",
    )
    db.session.add(nu)
    db.session.commit()
    session["user"] = nu.username
    session["display_name"] = nu.display_name
    session["handle"] = nu.handle
    session["avatar"] = nu.avatar
  return redirect("/")


@app.route("/logout")
def logout():
  session.clear()
  return redirect("/")


@app.route("/post", methods=["POST"])
def create_post():
  if not session.get("user"):
    return redirect("/")
  u = User.query.filter_by(username=session["user"]).first()
  file = request.files.get("image")
  filename = None
  if file and file.filename != "":
    filename = (
        f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    )
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

  p = Post(
      user_id=u.id,
      author=u.display_name,
      handle=u.handle,
      avatar=u.avatar,
      content=request.form.get("content"),
      location=request.form.get("location"),
      threat_tag=request.form.get("threat_tag"),
      image_file=filename,
  )
  db.session.add(p)
  db.session.commit()
  return redirect("/?tab=feed")


@app.route("/pin_post/<int:post_id>", methods=["POST"])
def pin_post(post_id):
  if not session.get("user"):
    return redirect("/")
  u = User.query.filter_by(username=session["user"]).first()
  p = Post.query.get_or_404(post_id)
  if p.user_id == u.id:
    if u.pinned_post_id == post_id:
      u.pinned_post_id = None
    else:
      u.pinned_post_id = post_id
    db.session.commit()
  return redirect("/?tab=feed")


@app.route("/create_community", methods=["POST"])
def create_community():
  if session.get("user"):
    u = User.query.filter_by(username=session["user"]).first()
    avatar_url = "https://images.unsplash.com/photo-1527482797697-8795b05813fe?w=150"

    file = request.files.get("avatar_file")
    if file and file.filename != "":
      filename = f"comm_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
      file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
      avatar_url = url_for("static", filename=f"uploads/{filename}")

    c = CommunityGroup(
        name=request.form.get("name").strip(),
        description=request.form.get("description").strip(),
        admin=u.display_name,
        avatar=avatar_url,
    )
    db.session.add(c)
    db.session.commit()
    return redirect(f"/?tab=community_detail&id={c.id}")
  return redirect("/")


@app.route("/post_community/<int:community_id>", methods=["POST"])
def post_community(community_id):
  if not session.get("user"):
    return redirect("/")
  u = User.query.filter_by(username=session["user"]).first()
  cp = CommunityPost(
      community_id=community_id,
      author=u.display_name,
      handle=u.handle,
      avatar=u.avatar,
      content=request.form.get("content"),
  )
  db.session.add(cp)
  db.session.commit()
  return redirect(f"/?tab=community_detail&id={community_id}")


@app.route("/create_marketplace_item", methods=["POST"])
def create_marketplace_item():
  if not session.get("user"):
    return redirect("/")
  u = User.query.filter_by(username=session["user"]).first()
  file = request.files.get("image")
  filename = None
  if file and file.filename != "":
    filename = f"market_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

  item = MarketplaceItem(
      seller=u.display_name,
      handle=u.handle,
      title=request.form.get("title").strip(),
      price=request.form.get("price").strip(),
      category=request.form.get("category"),
      location=request.form.get("location").strip(),
      description=request.form.get("description").strip(),
      image_file=filename,
  )
  db.session.add(item)
  db.session.commit()
  return redirect("/?tab=marketplace")


@app.route("/upload_reel", methods=["POST"])
def upload_reel():
  if not session.get("user"):
    return redirect("/")
  file = request.files.get("video")
  if file and file.filename != "":
    filename = f"reel_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    u = User.query.filter_by(username=session["user"]).first()
    r = Reel(
        author=u.display_name,
        handle=u.handle,
        avatar=u.avatar,
        caption=request.form.get("caption"),
        video_file=filename,
    )
    db.session.add(r)
    db.session.commit()
  return redirect("/?tab=reels")


@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
  p = Post.query.get_or_404(post_id)
  u = User.query.filter_by(username=session["user"]).first()
  if p.user_id == u.id:
    if u.pinned_post_id == p.id:
      u.pinned_post_id = None
    db.session.delete(p)
    db.session.commit()
  return redirect("/?tab=feed")


@app.route("/react/<int:post_id>/<reaction_type>", methods=["POST"])
def react(post_id, reaction_type):
  p = Post.query.get_or_404(post_id)
  if reaction_type == "bolt":
    p.reactions_bolt += 1
  elif reaction_type == "radar":
    p.reactions_radar += 1
  elif reaction_type == "siren":
    p.reactions_siren += 1
  elif reaction_type == "capture":
    p.reactions_capture += 1
  db.session.commit()

  u = User.query.filter_by(username=session.get("user")).first()
  if u and p.user_id != u.id:
    notif = Notification(
        recipient=p.author,
        actor=u.display_name,
        action=f"reacted with {reaction_type.upper()}",
        target_text=p.content[:40] + "...",
    )
    db.session.add(notif)
    db.session.commit()

  return redirect("/?tab=feed")


@app.route("/share_post/<int:post_id>", methods=["POST"])
def share_post(post_id):
  if not session.get("user"):
    return redirect("/")
  original = Post.query.get_or_404(post_id)
  u = User.query.filter_by(username=session["user"]).first()

  is_warning = "TORNADO" in original.threat_tag

  shared = Post(
      user_id=u.id,
      author=u.display_name,
      handle=u.handle,
      avatar=u.avatar,
      location=original.location,
      threat_tag=original.threat_tag,
      content=original.content,
      image_file=original.image_file,
      is_shared=True,
      shared_from=original.author,
      is_emergency_broadcast=is_warning,
  )
  db.session.add(shared)

  if original.user_id != u.id:
    notif = Notification(
        recipient=original.author,
        actor=u.display_name,
        action="amplified your post as an Emergency Broadcast",
        target_text=original.content[:40] + "...",
    )
    db.session.add(notif)

  db.session.commit()
  return redirect("/?tab=feed")


@app.route("/send_dm", methods=["POST"])
def send_dm():
  if session.get("user") and request.form.get("recipient"):
    dm = DirectMessage(
        sender=session.get("display_name"),
        recipient=request.form.get("recipient"),
        message=request.form.get("message"),
        is_read=False,
    )
    db.session.add(dm)
    db.session.commit()
    return redirect(
        f"/?tab=messages&with={request.form.get('recipient')}"
    )
  return redirect("/?tab=messages")


@app.route("/create_group", methods=["POST"])
def create_group():
  if session.get("user"):
    u = User.query.filter_by(username=session["user"]).first()
    avatar_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150"

    file = request.files.get("avatar_file")
    if file and file.filename != "":
      filename = f"group_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
      file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
      avatar_url = url_for("static", filename=f"uploads/{filename}")

    g = GroupChat(
        name=request.form.get("name").strip(),
        admin=u.display_name,
        avatar=avatar_url,
    )
    db.session.add(g)
    db.session.commit()

    gm = GroupMember(group_id=g.id, username=u.display_name)
    db.session.add(gm)
    db.session.commit()

    return redirect(f"/?tab=group_chat&group_id={g.id}")
  return redirect("/")


@app.route("/update_group/<int:group_id>", methods=["POST"])
def update_group(group_id):
  g = GroupChat.query.get_or_404(group_id)
  if session.get("user") and g.admin == session.get("display_name"):
    g.name = request.form.get("name").strip()

    file = request.files.get("avatar_file")
    if file and file.filename != "":
      filename = f"group_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
      file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
      g.avatar = url_for("static", filename=f"uploads/{filename}")

    db.session.commit()
  return redirect(f"/?tab=group_chat&group_id={g.id}")


@app.route("/add_member/<int:group_id>", methods=["POST"])
def add_member(group_id):
  g = GroupChat.query.get_or_404(group_id)
  if session.get("user") and g.admin == session.get("display_name"):
    new_member = request.form.get("username").strip()
    existing = GroupMember.query.filter_by(
        group_id=g.id, username=new_member
    ).first()
    if not existing:
      gm = GroupMember(group_id=g.id, username=new_member)
      db.session.add(gm)
      db.session.commit()
  return redirect(f"/?tab=group_chat&group_id={g.id}")


@app.route("/remove_member/<int:group_id>", methods=["POST"])
def remove_member(group_id):
  g = GroupChat.query.get_or_404(group_id)
  if session.get("user") and g.admin == session.get("display_name"):
    target_member = request.form.get("username").strip()
    if target_member != g.admin:
      GroupMember.query.filter_by(group_id=g.id, username=target_member).delete()
      db.session.commit()
  return redirect(f"/?tab=group_chat&group_id={g.id}")


@app.route("/send_group_msg", methods=["POST"])
def send_group_msg():
  if session.get("user") and request.form.get("group_id"):
    gid = request.form.get("group_id")
    my_name = session.get("display_name")
    g = GroupChat.query.get(gid)
    is_member = GroupMember.query.filter_by(
        group_id=gid, username=my_name
    ).first()

    if g and (g.admin == my_name or is_member):
      gm = GroupMessage(
          group_id=gid,
          sender=my_name,
          message=request.form.get("message"),
      )
      db.session.add(gm)
      db.session.commit()
    return redirect(f"/?tab=group_chat&group_id={gid}")
  return redirect("/")


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
  if session.get("user"):
    u = User.query.filter_by(username=session["user"]).first()
    p = Post.query.get_or_404(post_id)
    c = Comment(
        post_id=post_id,
        author=u.display_name,
        handle=u.handle,
        text=request.form.get("text"),
    )
    db.session.add(c)

    if p.user_id != u.id:
      notif = Notification(
          recipient=p.author,
          actor=u.display_name,
          action="commented on your post",
          target_text=request.form.get("text")[:40],
      )
      db.session.add(notif)

    db.session.commit()
  return redirect("/?tab=feed")


@app.route("/profile", methods=["POST"])
def profile():
  if session.get("user"):
    u = User.query.filter_by(username=session["user"]).first()
    u.display_name = request.form.get("display_name").strip()
    u.role = request.form.get("role")
    u.bio = request.form.get("bio")
    u.accent = request.form.get("accent", "blue")
    u.skywarn_certified = True if request.form.get("skywarn") == "yes" else False
    u.fema_certified = True if request.form.get("fema") == "yes" else False
    u.field_years = request.form.get("field_years", "1-3 Years")

    session["display_name"] = u.display_name
    file = request.files.get("avatar")
    if file and file.filename != "":
      filename = f"avatar_{u.username}_{file.filename}"
      file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
      u.avatar = url_for("static", filename=f"uploads/{filename}")
      session["avatar"] = u.avatar
    db.session.commit()
  return redirect("/?tab=profile")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
