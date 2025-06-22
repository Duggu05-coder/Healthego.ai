import random
from typing import Dict, List

class RemedyGenerator:
    def __init__(self):
        """Initialize remedy generator with comprehensive therapeutic techniques"""
        
        # Immediate coping techniques by emotion
        self.immediate_remedies = {
            'anxious': [
                "Try the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste",
                "Practice box breathing: Inhale for 4 counts, hold for 4, exhale for 4, hold for 4. Repeat 4 times",
                "Apply progressive muscle relaxation: Tense each muscle group for 5 seconds, then relax",
                "Use the STOP technique: Stop, Take a breath, Observe your thoughts, Proceed with intention"
            ],
            'sad': [
                "Try the 4-7-8 breathing: Inhale for 4, hold for 7, exhale for 8. Repeat 3 times",
                "Engage in gentle movement like a 5-minute walk or light stretching",
                "Practice self-compassion: Talk to yourself as you would a good friend",
                "Listen to uplifting music or nature sounds for 10 minutes"
            ],
            'angry': [
                "Count backwards from 100 by 7s to engage your prefrontal cortex",
                "Do 10 jumping jacks or push-ups to release physical tension",
                "Practice the TIPP technique: Temperature (cold water), Intense exercise, Paced breathing, Paired muscle relaxation",
                "Write your feelings on paper for 5 minutes without editing"
            ],
            'fear': [
                "Ground yourself: Feel your feet on the floor and take 3 deep breaths",
                "Use the RAIN technique: Recognize, Allow, Investigate, Nurture the feeling",
                "Break your fear into smaller, manageable parts and tackle one at a time",
                "Practice the mantra: 'This feeling is temporary and I am safe right now'"
            ],
            'happy': [
                "Practice gratitude: Write down 3 specific things you're grateful for",
                "Share your joy with someone you care about",
                "Engage in a creative activity to channel this positive energy",
                "Take a moment to mindfully savor this feeling"
            ],
            'neutral': [
                "Set one small, achievable intention for the next hour",
                "Practice mindful breathing for 3 minutes",
                "Do a quick body scan to check in with yourself",
                "Engage in a brief gratitude practice"
            ]
        }
        
        # Longer-term strategies
        self.long_term_strategies = {
            'anxious': [
                "Establish a daily meditation practice, even 5 minutes helps",
                "Create a worry journal - write worries down and schedule time to address them",
                "Build a calming evening routine to improve sleep quality",
                "Practice saying 'no' to reduce overwhelming commitments"
            ],
            'sad': [
                "Establish a routine that includes activities you used to enjoy",
                "Connect with supportive friends or family members regularly",
                "Consider keeping a mood diary to identify patterns",
                "Engage in acts of kindness for others to boost your own mood"
            ],
            'angry': [
                "Develop assertiveness skills to express needs without aggression",
                "Create physical outlets like regular exercise or sports",
                "Practice identifying anger triggers and early warning signs",
                "Learn conflict resolution techniques for better relationships"
            ],
            'fear': [
                "Gradually expose yourself to feared situations in small, manageable steps",
                "Build confidence through setting and achieving small goals",
                "Develop a support network you can reach out to when afraid",
                "Practice visualization techniques to rehearse positive outcomes"
            ],
            'happy': [
                "Maintain positive habits that contribute to your wellbeing",
                "Build on this momentum to tackle challenging goals",
                "Practice savoring positive experiences to extend their impact",
                "Share your strategies with others who might benefit"
            ]
        }
        
        # Physical wellness remedies
        self.physical_remedies = {
            'anxious': [
                "Try yoga poses like child's pose or legs up the wall",
                "Take a warm bath with Epsom salts",
                "Practice gentle neck and shoulder stretches",
                "Drink chamomile tea or warm water with lemon"
            ],
            'sad': [
                "Go for a walk in nature, even 10 minutes helps",
                "Try gentle yoga or tai chi movements",
                "Ensure you're getting adequate sleep (7-9 hours)",
                "Eat nourishing foods and stay hydrated"
            ],
            'angry': [
                "Do high-intensity exercise like running or boxing",
                "Try cold shower therapy to reset your nervous system",
                "Practice martial arts or kickboxing",
                "Engage in vigorous cleaning or organizing"
            ],
            'fear': [
                "Practice grounding through physical touch (hold a textured object)",
                "Try gentle movement like walking or stretching",
                "Use aromatherapy with calming scents like lavender",
                "Practice progressive muscle relaxation"
            ]
        }
        
        # Cognitive remedies
        self.cognitive_remedies = {
            'anxious': [
                "Challenge catastrophic thoughts with 'What's the most likely outcome?'",
                "Practice the 'So what?' technique to reduce worry impact",
                "Use thought stopping: Say 'STOP' when anxious thoughts arise",
                "Reframe situations: 'This is challenging' instead of 'This is terrible'"
            ],
            'sad': [
                "Challenge negative self-talk with evidence-based thinking",
                "Practice self-compassion statements",
                "Focus on what you can control in your current situation",
                "Remember past times you've overcome difficulties"
            ],
            'angry': [
                "Question the story you're telling yourself about the situation",
                "Practice perspective-taking: Consider others' viewpoints",
                "Use 'I' statements instead of 'you' statements",
                "Focus on problem-solving rather than blame"
            ],
            'fear': [
                "Examine evidence for and against your feared outcome",
                "Practice positive self-talk and affirmations",
                "Focus on your past successes and strengths",
                "Visualize yourself handling the situation successfully"
            ]
        }
        
        # Mindfulness and spiritual remedies
        self.mindfulness_remedies = {
            'anxious': [
                "Practice loving-kindness meditation for yourself",
                "Try a body scan meditation",
                "Engage in mindful breathing while walking",
                "Practice acceptance meditation"
            ],
            'sad': [
                "Try gratitude meditation focusing on small daily pleasures",
                "Practice mindful self-compassion",
                "Engage in walking meditation in nature",
                "Try loving-kindness meditation for yourself and others"
            ],
            'angry': [
                "Practice forgiveness meditation (for yourself and others)",
                "Try mindful breathing to create space between trigger and response",
                "Engage in compassion meditation",
                "Practice acceptance of what you cannot control"
            ],
            'fear': [
                "Try courage-building visualization meditation",
                "Practice present-moment awareness",
                "Engage in protective visualization exercises",
                "Try mantra meditation with calming phrases"
            ]
        }
    
    def get_comprehensive_remedy(self, emotion: str, situation: str = None) -> Dict[str, List[str]]:
        """Get a comprehensive remedy package for the given emotion"""
        emotion = emotion.lower()
        
        # Default to neutral if emotion not found
        if emotion not in self.immediate_remedies:
            emotion = 'neutral'
        
        remedy_package = {
            'immediate': random.sample(self.immediate_remedies.get(emotion, self.immediate_remedies['neutral']), 
                                     min(2, len(self.immediate_remedies.get(emotion, self.immediate_remedies['neutral'])))),
            'physical': random.sample(self.physical_remedies.get(emotion, []), 
                                    min(2, len(self.physical_remedies.get(emotion, [])))),
            'cognitive': random.sample(self.cognitive_remedies.get(emotion, []), 
                                     min(2, len(self.cognitive_remedies.get(emotion, [])))),
            'mindfulness': random.sample(self.mindfulness_remedies.get(emotion, []), 
                                       min(1, len(self.mindfulness_remedies.get(emotion, [])))),
            'long_term': random.sample(self.long_term_strategies.get(emotion, []), 
                                     min(2, len(self.long_term_strategies.get(emotion, []))))
        }
        
        return remedy_package
    
    def get_quick_remedy(self, emotion: str) -> str:
        """Get one quick remedy for immediate use"""
        emotion = emotion.lower()
        remedies = self.immediate_remedies.get(emotion, self.immediate_remedies['neutral'])
        return random.choice(remedies)
    
    def format_remedy_response(self, emotion: str, situation: str = None) -> str:
        """Format a complete remedy response"""
        remedies = self.get_comprehensive_remedy(emotion, situation)
        
        response = f"Here are some practical techniques to help with {emotion} feelings:\n\n"
        
        response += "🚨 **Try Right Now:**\n"
        for remedy in remedies['immediate']:
            response += f"• {remedy}\n"
        
        if remedies['physical']:
            response += "\n💪 **Physical Techniques:**\n"
            for remedy in remedies['physical']:
                response += f"• {remedy}\n"
        
        if remedies['cognitive']:
            response += "\n🧠 **Mental Strategies:**\n"
            for remedy in remedies['cognitive']:
                response += f"• {remedy}\n"
        
        if remedies['mindfulness']:
            response += "\n🧘 **Mindfulness Practice:**\n"
            for remedy in remedies['mindfulness']:
                response += f"• {remedy}\n"
        
        if remedies['long_term']:
            response += "\n📈 **For Long-term Wellbeing:**\n"
            for remedy in remedies['long_term']:
                response += f"• {remedy}\n"
        
        response += "\nRemember: Start with one technique that feels manageable. You don't need to try everything at once."
        
        return response