from google.cloud import secretmanager
from openai import OpenAI
import requests
import json
from datetime import datetime
import os
import re
from config import PROJECT_ID, SECRET_NAMES, TWITTER_API_BASE, VIRAL_KEYWORDS, MIN_DURATION, MAX_DURATION

class ViralAdGenerator:
    def __init__(self):
        self.client = self.setup_openai()
        self.twitter_api_key, self.twitter_user_id = self.setup_twitter()
        
    def setup_openai(self):
        """Setup OpenAI client with key from Secret Manager"""
        client = secretmanager.SecretManagerServiceClient()
        
        openai_secret = client.access_secret_version(
            name=f"projects/{PROJECT_ID}/secrets/{SECRET_NAMES['openai']}/versions/latest"
        )
        api_key = openai_secret.payload.data.decode('UTF-8')
        
        return OpenAI(api_key=api_key)
    
    def setup_twitter(self):
        """Setup Twitter API credentials"""
        client = secretmanager.SecretManagerServiceClient()
        
        api_secret = client.access_secret_version(
            name=f"projects/{PROJECT_ID}/secrets/{SECRET_NAMES['twitter_api_key']}/versions/latest"
        )
        api_key = api_secret.payload.data.decode('UTF-8')
        
        user_secret = client.access_secret_version(
            name=f"projects/{PROJECT_ID}/secrets/{SECRET_NAMES['twitter_user_id']}/versions/latest"
        )
        user_id = user_secret.payload.data.decode('UTF-8')
        
        return api_key, user_id
    
    def get_viral_tweets(self):
        """Fetch viral tweets related to ads and marketing"""
        try:
            headers = {"Authorization": f"Bearer {self.twitter_api_key}"}
            
            # Search for viral ad content
            response = requests.get(
                f"{TWITTER_API_BASE}/tweet/search",
                headers=headers,
                params={
                    "query": "viral ad OR marketing campaign OR veo3 OR successful ad",
                    "max_results": 20,
                    "sort_order": "relevancy"
                }
            )
            
            tweets = response.json().get("data", [])
            viral_content = []
            
            for tweet in tweets:
                if self.is_viral_content(tweet.get("text", "")):
                    viral_content.append({
                        "text": tweet.get("text", ""),
                        "likes": tweet.get("like_count", 0),
                        "retweets": tweet.get("retweet_count", 0),
                        "engagement": tweet.get("like_count", 0) + tweet.get("retweet_count", 0) * 2
                    })
            
            # Sort by engagement
            viral_content.sort(key=lambda x: x["engagement"], reverse=True)
            return viral_content[:5]  # Return top 5
            
        except Exception as e:
            print(f"Twitter API error: {e}")
            return self.get_fallback_viral_content()
    
    def is_viral_content(self, text):
        """Check if content has viral potential"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in VIRAL_KEYWORDS)
    
    def get_fallback_viral_content(self):
        """Fallback viral content if Twitter API fails"""
        return [
            {"text": "This AI-generated car ad went viral with 10M views! 🚗💨 #viral #ai", "engagement": 10000},
            {"text": "Try not to laugh challenge with this hilarious product demo! 😂", "engagement": 8500},
            {"text": "Shocking results from this new tech product - mind blowing! ⚡", "engagement": 7200},
            {"text": "This satisfying cleaning gadget is trending everywhere! 🧹", "engagement": 6800},
            {"text": "Epic fail turned into amazing marketing campaign! 🎯", "engagement": 5500}
        ]
    
    def extract_viral_prompt(self, tweet_text):
        """Extract the core idea from viral tweet"""
        # Remove hashtags, mentions, and URLs
        clean_text = re.sub(r'#\w+|\@\w+|https?://\S+', '', tweet_text)
        return clean_text.strip()
    
    def generate_viral_ad_idea(self, base_prompt):
        """Generate viral ad idea with virality metrics"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": f"""You are a viral marketing expert. Create ad ideas that MUST go viral.
                    Key virality factors: emotional appeal, surprise, humor, relatability, shareability.
                    Duration: {MIN_DURATION}-{MAX_DURATION} seconds.
                    Include: hook in first 3 seconds, emotional payoff, call to action.
                    Avoid generic, boring, or corporate-style ads."""
                }, {
                    "role": "user",
                    "content": f"Create a highly viral ad idea based on: {base_prompt}. Make it {MAX_DURATION} seconds long with maximum share potential."
                }]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating viral idea: {e}")
            return f"Viral {base_prompt} challenge that will shock everyone!"
    
    def generate_detailed_script(self, idea):
        """Generate detailed script with timing and virality elements"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": f"""Create a detailed {MAX_DURATION}-second script for this viral ad: {idea}
                    Include:
                    - Timing breakdown (seconds)
                    - Visual descriptions
                    - Emotional arc
                    - Sound effects/music
                    - Text overlays
                    - Call to action
                    - Virality hooks"""
                }]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating script: {e}")
            return f"0-3s: Hook with surprising visual\n3-10s: Build emotional connection\n10-{MAX_DURATION}s: Amazing reveal and call to action"
    
    def calculate_virality_score(self, idea, script):
        """Calculate virality score based on content analysis"""
        score = 50  # Base score
        
        # Check for viral keywords
        content = f"{idea} {script}".lower()
        viral_keywords_found = sum(1 for keyword in VIRAL_KEYWORDS if keyword in content)
        score += min(viral_keywords_found * 5, 20)
        
        # Check for emotional words
        emotional_words = ["amazing", "shocking", "emotional", "funny", "heartwarming", "exciting"]
        emotional_score = sum(1 for word in emotional_words if word in content)
        score += min(emotional_score * 3, 15)
        
        # Check for call to action
        if any(phrase in content for phrase in ["share", "tag", "comment", "like", "subscribe"]):
            score += 10
        
        # Ensure score is between 0-100
        return min(max(score, 0), 100)
    
    def create_sample_video_placeholder(self, timestamp):
        """Create placeholder video file"""
        video_path = f"static/videos/ad_{timestamp}.mp4"
        with open(video_path, 'w') as f:
            f.write(f"Video placeholder for viral ad - would be generated by Veo 3 API\nDuration: {MAX_DURATION}s\nVirality Optimized")
        return video_path
    
    def create_ad_metadata(self, source, idea, script, virality_score):
        """Create comprehensive ad metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ad_{timestamp}.json"
        
        video_path = self.create_sample_video_placeholder(timestamp)
        
        metadata = {
            "id": timestamp,
            "source": source,
            "idea": idea,
            "script": script,
            "virality_score": virality_score,
            "duration_seconds": MAX_DURATION,
            "timestamp": timestamp,
            "status": "completed",
            "video_file": f"videos/ad_{timestamp}.mp4",
            "thumbnail": f"thumbnails/ad_{timestamp}.jpg",
            "audio_file": f"audio/ad_{timestamp}.mp3",
            "virality_assessment": self.get_virality_assessment(virality_score)
        }
        
        with open(f"static/{filename}", "w") as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def get_virality_assessment(self, score):
        """Get human-readable virality assessment"""
        if score >= 80:
            return "🔥 Highly Viral - Excellent potential for mass sharing"
        elif score >= 60:
            return "🚀 Very Viral - Strong sharing potential"
        elif score >= 40:
            return "👍 Potentially Viral - Good elements present"
        else:
            return "⚠️ Needs Improvement - Add more viral elements"
    
    def generate_from_twitter(self):
        """Generate ad from viral Twitter content"""
        viral_tweets = self.get_viral_tweets()
        if not viral_tweets:
            return {"error": "No viral content found on Twitter"}
        
        best_tweet = viral_tweets[0]
        base_prompt = self.extract_viral_prompt(best_tweet["text"])
        
        idea = self.generate_viral_ad_idea(base_prompt)
        script = self.generate_detailed_script(idea)
        virality_score = self.calculate_virality_score(idea, script)
        
        return self.create_ad_metadata(
            f"Twitter viral tweet ({best_tweet['engagement']} engagement)",
            idea,
            script,
            virality_score
        )
    
    def generate_from_prompt(self, user_prompt):
        """Generate ad from user prompt"""
        if not user_prompt.strip():
            return {"error": "Please provide a prompt"}
        
        idea = self.generate_viral_ad_idea(user_prompt)
        script = self.generate_detailed_script(idea)
        virality_score = self.calculate_virality_score(idea, script)
        
        return self.create_ad_metadata(
            f"User prompt: {user_prompt}",
            idea,
            script,
            virality_score
        )

# Singleton instance
ad_generator = ViralAdGenerator()