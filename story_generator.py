import os
import json
import logging
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_vedic_story(prompt):
    """Generate a Vedic mythology story based on the given prompt"""
    try:
        # Check if OpenAI API is available
        if not OPENAI_API_KEY:
            logging.warning("OpenAI API key not found, using fallback story")
            return generate_fallback_story(prompt)
            
        system_prompt = """You are a master storyteller specializing in Vedic Hindu mythology. You have deep knowledge of the Ramayana, Mahabharata, Puranas, Vedas, and other sacred texts. 

Create engaging, authentic stories that:
- Draw from genuine Vedic traditions and characters
- Include moral lessons and spiritual insights
- Use appropriate Sanskrit terms and names
- Maintain cultural accuracy and respect
- Are suitable for all audiences
- Include vivid descriptions for visualization

Respond with JSON in this exact format:
{
    "title": "Story title",
    "content": "Full story content with multiple paragraphs",
    "scenes": ["Scene 1 description", "Scene 2 description", "Scene 3 description"],
    "characters": ["Character 1", "Character 2", "Character 3"],
    "moral": "Key moral or spiritual lesson"
}"""

        user_prompt = f"""Create a Vedic mythology story based on this prompt: {prompt}

The story should be engaging, authentic to Vedic traditions, and include:
- Rich character development
- Vivid scene descriptions
- Cultural and spiritual elements
- A meaningful conclusion with moral teachings

Make it approximately 800-1200 words long."""

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        story_data = json.loads(content)
        logging.info(f"Generated story: {story_data.get('title', 'Untitled')}")
        
        return story_data
        
    except Exception as e:
        logging.error(f"Story generation failed: {e}")
        # Fallback to template story if OpenAI fails
        return generate_fallback_story(prompt)

def extract_story_scenes(story_content):
    """Extract key scenes from story content for image generation"""
    try:
        system_prompt = """You are an expert at analyzing stories and identifying key visual scenes. 
        
        Analyze the given story and identify 3-4 key scenes that would make compelling images.
        Focus on:
        - Dramatic moments
        - Character interactions
        - Scenic descriptions
        - Symbolic elements
        
        Respond with JSON in this format:
        {
            "scenes": [
                "Detailed scene description 1",
                "Detailed scene description 2", 
                "Detailed scene description 3"
            ]
        }"""
        
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract key visual scenes from this story:\n\n{story_content}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        scenes_data = json.loads(content)
        return scenes_data.get('scenes', [])
        
    except Exception as e:
        logging.error(f"Scene extraction failed: {e}")
        return []

def generate_fallback_story(prompt):
    """Generate a fallback story when OpenAI API is unavailable"""
    # Analyze prompt to choose appropriate story
    prompt_lower = prompt.lower()
    
    if "krishna" in prompt_lower or "butter" in prompt_lower:
        return {
            "title": "Krishna and the Butter Pot",
            "content": """In the blessed village of Vrindavan, where divine love flows like honey and every corner echoes with celestial melodies, lived young Krishna with his foster parents Yasoda and Nanda. Though appearing as an ordinary child, Krishna carried within him the essence of the supreme divine.

Every morning, mother Yasoda would churn fresh butter in large earthen pots, filling the house with the sweet aroma of fresh dairy. The golden butter, rich and creamy, was not just food but an offering of pure love and devotion.

Little Krishna, with his twinkling eyes and mischievous smile, was irresistibly drawn to these pots of butter. When Yasoda was busy with household chores, Krishna would gather his cowherd friends - Balarama, Sudama, and others. Together, they would form human pyramids, standing on each other's shoulders to reach the high-hanging butter pots.

One particular morning, as the sun painted the sky with hues of gold and pink, Krishna executed his most daring butter heist yet. He climbed onto Balarama's shoulders, reached for the largest pot, and began distributing the creamy treasure among his friends and even the monkeys who had gathered to watch.

When Yasoda discovered butter handprints on the walls and empty pots, she knew immediately who the culprit was. She found Krishna sitting innocently, his face and clothes covered in butter, trying to look as if nothing had happened.

"Krishna!" Yasoda called out with mock anger, though her heart was filled with overwhelming love. "Why do you steal butter when I would gladly give you all you want?"

Krishna looked up with his innocent, large eyes and replied, "Mother, when you give me butter, it tastes sweet. But when I take it myself with my friends, sharing our joy and laughter, it tastes like divine nectar. The love we share in that moment makes everything more delicious."

Yasoda understood then that Krishna's actions were not mere childish pranks, but divine play - what the sages call 'Leela.' Through his playful stealing, Krishna was teaching that divine love cannot be contained by rules or boundaries. True devotion flows freely, spontaneously, and joyfully.

The butter stealing also symbolized how the divine lovingly 'steals' the hearts of devotees, not through force, but through irresistible charm and love. Just as Krishna took butter with innocent joy, the divine takes our hearts filled with ego and transforms them into vessels of pure love.

From that day forward, Yasoda would leave butter pots at various heights, not to prevent Krishna from taking them, but to enjoy watching his divine play. She realized that in trying to catch Krishna, she was actually being caught by divine love herself.""",
            "scenes": [
                "Young Krishna with his friends forming a human pyramid to reach hanging butter pots in a traditional Vrindavan home",
                "Krishna distributing butter among his cowherd friends and monkeys in a sunlit courtyard",
                "Mother Yasoda discovering Krishna with butter-covered hands and clothes, showing both mock anger and overwhelming love"
            ],
            "characters": ["Krishna", "Yasoda", "Balarama", "Cowherd friends"],
            "moral": "Divine love flows freely and joyfully, beyond rules and boundaries. True devotion is spontaneous and transforms the heart through divine play and innocent charm."
        }
    
    elif "hanuman" in prompt_lower or "rama" in prompt_lower:
        return {
            "title": "Hanuman's Leap of Faith",
            "content": """In the golden age of Treta Yuga, when righteousness still flourished upon the earth, a great crisis befell Lord Rama and his devoted brother Lakshmana. During their exile in the Dandaka forest, the demon king Ravana had abducted Sita, Rama's beloved wife, and taken her across the vast ocean to his fortress kingdom of Lanka.

Rama, though divinely powerful, chose to face this challenge as a human prince, demonstrating the path of dharma for all beings. With heavy heart and unwavering determination, he sought allies to help rescue Sita. The forest led him to the monkey kingdom of Kishkindha, where he befriended Sugriva and gained the support of the mighty vanara army.

Among these devoted monkeys was Hanuman, son of the wind god Vayu, whose strength and devotion were unmatched. Yet Hanuman had forgotten his own divine powers due to a childhood curse. He lived humbly, unaware of the mighty abilities that lay dormant within him.

When the vanara army reached the shores of the southern ocean, they faced an seemingly impossible task. The vast waters stretched endlessly toward Lanka, and no ordinary being could cross such a distance. The monkeys despaired - how could they reach Sita?

It was then that the wise bear Jambavan approached Hanuman. "Oh mighty son of Vayu," he said, "do you not remember who you are? You possess the power to leap across oceans, to shrink or expand at will, to move faster than the wind itself."

As Jambavan spoke, the clouds of forgetfulness lifted from Hanuman's mind. He remembered his true nature - not just as a monkey, but as a divine being whose only purpose was service to the supreme. His love for Rama awakened every sleeping power within him.

Standing on the peak of Mount Mahendra, Hanuman grew to enormous size. His body became radiant like the rising sun, his tail stretched like a mighty club, and his face glowed with determination. The assembled vanaras watched in awe as their humble friend transformed into a being of cosmic power.

"For Rama's service, no ocean is too vast, no mountain too high," Hanuman declared. With this proclamation, he crouched low, gathering all his divine energy. Then, with a thunderous roar that shook the heavens, he leaped into the sky.

As Hanuman soared across the ocean, he faced many obstacles. Demons tried to capture him, a mountain-sized fish rose from the depths to swallow him, and divine serpents tested his resolve. But powered by pure devotion to Rama, he overcame every challenge with ease.

When Hanuman finally landed in Lanka and found Sita in the Ashoka grove, he realized that his leap was more than a physical journey - it was a leap of faith. Faith in his divine nature, faith in the power of selfless service, and faith in the supreme love that connected him to Rama.

His success gave hope to the entire vanara army and proved that when one acts with complete devotion and surrender, even impossible tasks become achievable. The leap across the ocean became a symbol that with faith and divine grace, any obstacle can be overcome.""",
            "scenes": [
                "Hanuman standing on Mount Mahendra in his enormous divine form, preparing to leap across the vast ocean",
                "Hanuman flying across the ocean, facing demons and sea creatures while maintaining focus on Rama",
                "Hanuman discovering Sita in the beautiful but sorrowful Ashoka grove in Lanka"
            ],
            "characters": ["Hanuman", "Rama", "Sita", "Jambavan", "Sugriva"],
            "moral": "With complete faith, devotion, and remembrance of our true divine nature, we can overcome any obstacle and achieve the impossible in service of righteousness."
        }
    
    else:
        # Default fallback story
        return {
            "title": "The Divine Lesson of the Sandalwood Tree",
            "content": """In ancient times, there grew a magnificent sandalwood tree in the Malaya mountains. This tree was special not just for its fragrant wood, but for the wisdom it would impart to seekers who came to rest in its shade.

One day, a young seeker named Vidya arrived at the tree, troubled by the ways of the world. She had seen good people suffer while the wicked prospered, and her faith was shaken.

The sandalwood tree, recognizing her pure heart, spoke to her in a gentle voice: "Child, why do you look so disturbed?"

Vidya explained her confusion about the apparent injustices in the world. The tree listened patiently, then shared its wisdom:

"Look around me, dear one. See how different creatures interact with me. The snakes wrap around my trunk, trying to poison me with their venom, yet I transform their poison into sweet fragrance. The bees come and take my essence to make honey. The woodcutters come to cut my branches, yet I give them my precious wood freely."

"But how do you remain peaceful through all this?" asked Vidya.

The tree replied, "Because I understand dharma - the eternal law. My nature is to give fragrance and healing, regardless of how others treat me. The snake cannot change my essence, only I can do that by forgetting my true nature."

"This is the secret, child. Each being has a divine essence that cannot be destroyed by external circumstances. When you act according to your highest nature - with love, compassion, and wisdom - you remain untouched by the apparent injustices around you."

Vidya realized that the tree was teaching her about detachment and duty without expectation of results, the core teaching of the Bhagavad Gita.

From that day forward, she dedicated herself to serving others with the same selfless spirit as the sandalwood tree, finding peace and purpose in righteous action regardless of outcomes.""",
            "scenes": [
                "A young seeker sitting beneath a majestic sandalwood tree in the Malaya mountains",
                "Various creatures - snakes, bees, and woodcutters - interacting with the wise sandalwood tree",
                "The seeker receiving enlightenment and walking away with peaceful determination"
            ],
            "characters": ["Vidya", "The Sandalwood Tree", "Various forest creatures"],
            "moral": "True peace comes from acting according to our highest nature with love and compassion, remaining unaffected by external circumstances while serving others selflessly."
        }
