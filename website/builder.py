import os

PUBLIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "public"))
os.makedirs(PUBLIC_DIR, exist_ok=True)

with open(os.path.join(PUBLIC_DIR, "index.html"), "r", encoding="utf-8") as f:
    HTML_CONTENT = f.read()

# Verify that HTML_CONTENT has required markers
assert "info@omnigateos.com" in HTML_CONTENT
assert "id=\"contact\"" in HTML_CONTENT
assert "id=\"dag-visualizer-container\"" in HTML_CONTENT
assert "ActiveGraph" not in HTML_CONTENT

# Re-write index.html from template
with open(os.path.join(PUBLIC_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML_CONTENT)

print("index.html successfully updated and verified in builder.py!")
