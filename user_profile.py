import os
import json

PROFILE_FILE = "user_profile.json"

def load_user_profile():
    """Loads the user's level and XP from a file."""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default starting values
        return {"level": 1, "xp": 0}

def save_user_profile(profile):
    """Saves the user's level and XP to a file."""
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f)

def get_xp_for_next_level(level):
    """Calculates the XP needed to reach the next level."""
    # Exponential growth for leveling up
    return int(100 * (1.5 ** (level - 1)))

def add_xp(profile, amount):
    """Adds XP to the user's profile and checks for level ups."""
    profile['xp'] += amount
    xp_needed = get_xp_for_next_level(profile['level'])
    leveled_up = False
    while profile['xp'] >= xp_needed:
        profile['level'] += 1
        profile['xp'] -= xp_needed
        xp_needed = get_xp_for_next_level(profile['level'])
        leveled_up = True
    return leveled_up