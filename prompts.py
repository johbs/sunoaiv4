from typing import Dict, Any
import json

def create_generation_request(title: str, tags: str, lyrics: str) -> Dict[str, Any]:
    """
    Creates a complete generation request for Suno API v4.
    
    Args:
        title (str): Song title
        tags (str): Space-separated tags describing the song style
        lyrics (str): Raw lyrics text with section markers
    
    Returns:
        Dict[str, Any]: Complete request body for the API
    """
    return {
        "title": title,
        "metadata": {
            "tags": tags,
            "prompt": lyrics,
            "type": "gen",
            "stream": True
        },
        "major_model_version": "v4",
        "model_name": "chirp-v4",
        "batch_size": 1
    }

# Example formats for different section types
SECTION_FORMATS = {
    "intro": "[Intro][{instrument}, {mood}]",
    "verse": "[Couplet {n}]",
    "chorus": "[Refrain]",
    "bridge": "[Pont][{mood}]",
    "outro": "[Outro][{instrument} {mood}]"
}

# Common musical directions
MUSICAL_DIRECTIONS = {
    "french_acoustic": {
        "intro_instrument": "Guitare douce",
        "intro_mood": "mélodie chaleureuse",
        "bridge_mood": "Moment acoustique émouvant",
        "outro_instrument": "Guitare",
        "outro_mood": "se dissipant doucement"
    }
}

def format_french_song(title: str, lyrics: str, style: str = "french_acoustic") -> Dict[str, Any]:
    """
    Formats a French song with appropriate musical directions and structure.
    
    Example usage:
    ```python
    song = format_french_song(
        title="Heaven, Mon Miracle Mon Amour",
        lyrics="Heaven, mon étoile, mon cœur\\nTout ton amour...",
        style="french_acoustic"
    )
    ```
    """
    directions = MUSICAL_DIRECTIONS[style]
    
    # Default tags for French acoustic style
    tags = "acoustic pop french female soft"
    
    # Format intro with musical directions
    intro = SECTION_FORMATS["intro"].format(
        instrument=directions["intro_instrument"],
        mood=directions["intro_mood"]
    )
    
    # Format outro with musical directions
    outro = SECTION_FORMATS["outro"].format(
        instrument=directions["outro_instrument"],
        mood=directions["outro_mood"]
    )
    
    # Ensure lyrics end with [end]
    if not lyrics.strip().endswith("[end]"):
        lyrics = f"{lyrics.strip()}\n[end]"
    
    # Combine all parts
    formatted_lyrics = f"{intro}\n\n{lyrics}"
    
    return create_generation_request(title, tags, formatted_lyrics)

# Example usage
example_input = {
    "title": "Heaven, Mon Miracle Mon Amour",
    "lyrics": """Heaven, mon étoile, mon cœur
Tout ton amour, c'est mon bonheur
Ma petite lumière dans la nuit
Tu es mon miracle, ma vie

[Couplet 1]

N'oublie jamais combien je t'aime
Dans mes bras, tu as ton emblème
Unique et forte, douce et vraie
Heaven, pour toi, je chanterai

[Refrain]

Joyeux anniversaire, ma princesse (oh, oh)
Chaque instant avec toi me bénisse (woah, woah)
Mon ange, mon cœur, mon trésor
Tu es l'amour qui m'accorde encore

[Pont][Moment acoustique émouvant]

Que la vie te porte avec douceur
Ton sourire garde toutes tes couleurs
Ta famille toujours derrière toi
Heaven, tu es notre joie

[Refrain]

Joyeux anniversaire, ma princesse (oh, oh)
Chaque instant avec toi me bénisse (woah, woah)
Mon ange, mon cœur, mon trésor
Tu es l'amour qui m'accorde encore

[Outro][Guitare se dissipant doucement]

Mon miracle, ma vie, mon amour
Heaven, pour toi, toujours"""
}

# Example system prompt
SYSTEM_PROMPT = """You are a music generation assistant. Your task is to format song requests into proper prompts for the Suno AI music generation system.

Follow these rules:
1. Always include [Intro] at the start if not provided
2. Always include [end] at the end if not provided
3. Use appropriate section markers: [Verse], [Chorus], [Bridge], [Outro]
4. Include musical direction in brackets where appropriate: [Soft guitar], [Building intensity], etc.
5. Format tags as space-separated keywords describing the style, mood, and instruments
6. Keep the title concise but descriptive

The output should be a JSON object with:
- title: The song title
- tags: Space-separated style descriptors
- prompt: The formatted lyrics with section markers"""

# Example user prompt
USER_PROMPT = """Please format this song for generation:
Title: {title}
Style Tags: {tags}
Lyrics:
{lyrics}"""
