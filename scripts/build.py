#!/usr/bin/env python3
"""
Convert Markdown dataset files to HTML using a template.
"""
import os
import re
import yaml
import markdown
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

def parse_markdown_file(md_path):
    """Parse a Markdown file with YAML frontmatter."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter and content
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError(f"No frontmatter found in {md_path}")
    
    frontmatter = yaml.safe_load(match.group(1))
    markdown_content = match.group(2).strip()
    
    # Convert markdown to HTML if there's content
    html_content = None
    if markdown_content:
        html_content = markdown.markdown(markdown_content, extensions=['extra', 'nl2br'])
    
    return frontmatter, html_content

def build_datasets():
    """Convert all Markdown dataset files to HTML."""
    base_dir = Path(__file__).parent.parent
    datasets_dir = base_dir / 'datasets'
    templates_dir = base_dir / 'templates'
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template('dataset-template.html')
    
    # Process all markdown files (excluding README.md)
    md_files = [f for f in datasets_dir.glob('*.md') if f.name != 'README.md']
    if not md_files:
        print("No markdown files found in datasets/ directory")
        return
    
    for md_file in sorted(md_files):
        print(f"Processing {md_file.name}...")
        
        try:
            # Parse markdown
            frontmatter, html_content = parse_markdown_file(md_file)
            
            # Add content to frontmatter if it exists
            if html_content:
                frontmatter['content'] = html_content
            
            # Render HTML
            html_output = template.render(**frontmatter)
            
            # Write HTML file
            html_file = datasets_dir / f"{md_file.stem}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_output)
            
            print(f"  → Generated {html_file.name}")
        except Exception as e:
            print(f"  ✗ Error processing {md_file.name}: {e}")
            raise

if __name__ == '__main__':
    build_datasets()

