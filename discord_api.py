import requests

def discord_send(webhook_url, uid, val, threshold, duration, t12, ts):
    if not webhook_url: 
        return
    
    mention = f"<@{uid}>" if uid else ""
    
    embed = {
        "title": "🚨 Auto-Clicker Triggered! 🚨",
        "description": "The Clicker successfully detected a value exceeding your threshold. A click was executed at the target location. 🎯",
        "color": 5763719,
        "fields": [
            {"name": "📊 Detected Value", "value": f"**> {val}**", "inline": True},
            {"name": "📈 Threshold", "value": f"**> {threshold}**", "inline": True},
            {"name": "\u200b", "value": "\u200b", "inline": False},
            {"name": "⏱️ Time", "value": f"**> {t12} (<t:{ts}:R>)**", "inline": True},
            {"name": "⏳ Bot Active For", "value": f"**> {duration}**", "inline": True},
        ],
        "footer": {"text": "Auto-Clicker Pro"}
    }
    
    p = {
        "content": f"🔔 {mention} **Action Required!**".strip(),
        "embeds": [embed],
    }
    
    try:
        requests.post(webhook_url, json=p, timeout=10)
    except Exception as e:
        print(f"Webhook failed: {e}")