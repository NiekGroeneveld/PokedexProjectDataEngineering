"""Domain-specific Pokemon logic and business rules"""
from typing import Optional, List



def parse_abilities_from_string(abilities_str: str) -> List[str]:
    """Parse abilities from a comma-separated string
    
    Args:
        abilities_str: Comma-separated ability names (may include URIs)
        
    Returns:
        List of cleaned, formatted ability names
    """
    abilities = []
    for ability in abilities_str.split(","):
        ability = ability.strip()
        if ability:
            # Extract ability name from URI if needed
            if "/" in ability:
                ability = ability.split("/")[-1]
            # Replace underscores/hyphens with spaces and title case
            ability = ability.replace("_", " ").replace("-", " ").title()
            abilities.append(ability)
    return abilities
