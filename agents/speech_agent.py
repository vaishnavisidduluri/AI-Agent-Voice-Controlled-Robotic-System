import speech_recognition as sr
import google.generativeai as genai
import json
from typing import Dict, Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import GEMINI_API_KEY, SPEECH_CONFIG
from utils.message_format import create_message

class SpeechAgent:
    """
    Listens to voice commands and extracts intent
    Uses hybrid approach: Fast keywords + Gemini AI fallback
    """
    
    def __init__(self):
        print("👂 Initializing Speech Agent...")
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Gemini AI setup
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.use_gemini = SPEECH_CONFIG["use_gemini"]
        else:
            print("⚠️ No Gemini API key - using keywords only")
            self.use_gemini = False
        
        # Simple keyword database
        self.action_keywords = {
            "pick": ["pick", "grab", "take", "get", "pickup"],
            "place": ["place", "put", "drop", "set", "release"],
            "move": ["move", "shift", "transfer"],
            "show": ["show", "display", "list", "find"],
            "stop": ["stop", "halt", "cancel", "abort"]
        }
        
        self.known_objects = [
            "bottle", "cup", "glass", "bowl", "can",
            "phone", "book", "pen", "remote", "ball",
            "banana", "apple", "orange", "box"
        ]
        
        # Calibrate for noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Speech Agent ready!")
    
    def listen(self) -> Optional[str]:
        """
        Capture voice and convert to text
        Returns: Text string or None if failed
        """
        print("\n🎤 Listening... Speak now!")
        
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source, 
                    timeout=SPEECH_CONFIG["timeout"],
                    phrase_time_limit=SPEECH_CONFIG["timeout"]
                )
                
                print("🔄 Processing speech...")
                text = self.recognizer.recognize_google(audio)
                print(f"📝 You said: '{text}'")
                return text.lower()
                
            except sr.WaitTimeoutError:
                print("⏱️ Timeout - no speech detected")
                return None
            except sr.UnknownValueError:
                print("❌ Could not understand audio")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")
                return None
    
    def extract_keywords(self, text: str) -> Dict:
        """
        Fast keyword matching
        Returns: {action, object, confidence}
        """
        result = {
            "action": None,
            "object": None,
            "confidence": 0.0
        }
        
        # Find action
        for action, keywords in self.action_keywords.items():
            if any(keyword in text for keyword in keywords):
                result["action"] = action
                result["confidence"] += 0.5
                break
        
        # Find object
        for obj in self.known_objects:
            if obj in text:
                result["object"] = obj
                result["confidence"] += 0.5
                break
        
        return result
    
    def extract_with_gemini(self, text: str) -> Dict:
        """
        Use Gemini AI for natural language understanding
        Returns: {action, object, confidence}
        """
        try:
            prompt = f"""
Extract the ACTION and OBJECT from this command: "{text}"

Actions: pick, place, move, show, stop
Objects: Any graspable object mentioned

Return ONLY JSON format:
{{"action": "action_name", "object": "object_name", "confidence": 0.0-1.0}}

Example:
Input: "Could you grab that bottle?"
Output: {{"action": "pick", "object": "bottle", "confidence": 0.9}}
"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean JSON
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"⚠️ Gemini error: {e}")
            return {"action": None, "object": None, "confidence": 0.0}
    
    def get_command(self) -> Dict:
        """
        Main method: Get user command
        Returns: Standardized message format
        """
        # Step 1: Listen
        text = self.listen()
        if not text:
            return create_message(
                "speech_agent",
                "intent",
                {"error": "No speech detected"},
                "error"
            )
        
        # Step 2: Try fast keyword matching
        keyword_result = self.extract_keywords(text)
        
        # Step 3: Use Gemini if confidence is low
        if keyword_result["confidence"] < SPEECH_CONFIG["confidence_threshold"] and self.use_gemini:
            print("Using Gemini AI for better understanding...")
            result = self.extract_with_gemini(text)
        else:
            result = keyword_result
        
        # Step 4: Return formatted message
        return create_message(
            "speech_agent",
            "intent",
            {
                "action": result.get("action"),
                "object": result.get("object"),
                "confidence": result.get("confidence", 0.0),
                "raw_text": text
            },
            "success" if result.get("action") else "error"
        )


# Test the agent
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING SPEECH AGENT")
    print("="*60)
    
    agent = SpeechAgent()
    
    print("\nTry saying:")
    print("  - 'Pick up the bottle'")
    print("  - 'Grab the cup'")
    print("  - 'Show me objects'")
    print("="*60)
    
    while True:
        result = agent.get_command()
        
        print(f"\n📊 Result:")
        print(f"   Action: {result['data'].get('action')}")
        print(f"   Object: {result['data'].get('object')}")
        print(f"   Confidence: {result['data'].get('confidence')}")
        
        cont = input("\n🔄 Test again? (y/n): ")
        if cont.lower() != 'y':
            break

from flask import Flask, jsonify
from speech_agent import SpeechAgent

app = Flask(__name__)
speech_agent = SpeechAgent()

@app.route('/speech/latest', methods=['GET'])
def get_latest_speech():
    result = speech_agent.listen_and_understand()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
