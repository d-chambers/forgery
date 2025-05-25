"""
A project to answer the Fervo interview prompts.
"""

from pathlib import Path

here = Path(__file__).parent
input_path = here / "inputs"
output_path = here / "outputs"
output_path.mkdir(parents=True, exist_ok=True)

forge_events_path = input_path / "forge_events.csv"


blog_post_path = output_path / "blog"
blog_post_path.mkdir(parents=True, exist_ok=True)

clean_forge_events_path = blog_post_path / "a010_clean_forge_events.csv"
