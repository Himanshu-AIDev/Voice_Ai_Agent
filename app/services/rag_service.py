import os
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

KB_DIR = "app/data/kb"

class KnowledgeBase:
    def __init__(self):
        self.documents = []
        self.load_data()

    def load_data(self):
        """Loads all JSON files from the KB directory into memory."""
        if not os.path.exists(KB_DIR):
            logger.warning("Knowledge Base directory not found. Run scraper.py first.")
            return

        for filename in os.listdir(KB_DIR):
            if filename.endswith(".json"):
                path = os.path.join(KB_DIR, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.documents.append(data)
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
        
        logger.info(f"Loaded {len(self.documents)} documents into Knowledge Base.")

    def search(self, query: str, limit: int = 3) -> str:
        """
        Improved keyword search with stop-word filtering and scoring.
        """
        query = query.lower().strip()

        # Stop words to ignore during search
        STOP_WORDS = {
            "we", "are", "is", "am", "the", "a", "an", "for", "to",
            "do", "you", "have", "any", "very", "keen", "please", 
            "i", "want", "can", "tell", "me", "about"
        }

        # Filter query words: Remove stop words and short words
        query_words = [w for w in query.split() if w not in STOP_WORDS and len(w) > 2]
        
        results = []

        for doc in self.documents:
            content = doc.get("content", "").lower()
            score = 0
            
            # 1. Word Match Scoring
            for word in query_words:
                if word in content:
                    score += 2   # Stronger weighting for keywords

            # 2. Bonus if full query phrase exists (Exact Match)
            if query in content:
                score += 5

            if score > 0:
                results.append((score, doc))

        # Sort by score (highest match first)
        results.sort(key=lambda x: x[0], reverse=True)
        
        top_results = results[:limit]

        if not top_results:
            return "I could not find specific hospital information related to this query."

        context_text = "Here is the relevant information found from the hospital website:\n\n"
        
        for score, doc in top_results:
            context_text += f"--- Source: {doc.get('title')} ({doc.get('url')}) ---\n"
            # Truncate content to avoid overwhelming the AI (600 chars per doc)
            context_text += doc.get("content", "")[:600] + "...\n\n"

        # Limit total context size to prevent token overflow
        return context_text[:2000]

# Global instance
kb_engine = KnowledgeBase()