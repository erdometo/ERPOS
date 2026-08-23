import os
import re

def verify_milestone_1():
    print("=== STARTING MILESTONE 1 VERIFICATION ===")
    
    website_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "website"))
    public_dir = os.path.join(website_dir, "public")
    html_file = os.path.join(public_dir, "index.html")
    css_file = os.path.join(public_dir, "styles.css")
    
    # Check directories and files exist
    assert os.path.isdir(public_dir), f"Public directory not found at {public_dir}"
    assert os.path.isfile(html_file), f"index.html not found at {html_file}"
    assert os.path.isfile(css_file), f"styles.css not found at {css_file}"
    print("[PASS] Directories and files exist.")
    
    # Read HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Verify required IDs
    required_ids = [
        "terminal-container",
        "ledger-container",
        "ephemeral-placeholder",
        "ephemeral-ui-container"
    ]
    
    for rid in required_ids:
        pattern = f'id="{rid}"'
        assert pattern in html_content, f"Required ID '{rid}' not found in index.html (expected: id=\"{rid}\")"
    print("[PASS] All required elements (IDs) are present in index.html.")
    
    # Read CSS content
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()
        
    # Verify custom properties for fonts and accents
    font_vars = ["font-heading", "font-body", "font-mono"]
    for fvar in font_vars:
        assert fvar in css_content, f"Font variable '{fvar}' not defined in styles.css"
        
    accent_vars = ["accent-violet", "accent-rose", "accent-emerald", "accent-amber"]
    for avar in accent_vars:
        assert avar in css_content, f"Accent variable '{avar}' not defined in styles.css"
        
    print("[PASS] Font and accent CSS variables are defined in styles.css.")
    
    # Verify glassmorphic properties
    glass_patterns = ["backdrop-filter", "border", "box-shadow"]
    for gp in glass_patterns:
        assert gp in css_content, f"Glassmorphism pattern '{gp}' not found in styles.css"
    print("[PASS] Glassmorphism rules are defined in styles.css.")
    
    # Verify animations
    animation_patterns = ["@keyframes", "pulse-success", "pulse-tampered"]
    for ap in animation_patterns:
        assert ap in css_content, f"Animation/Pulse pattern '{ap}' not found in styles.css"
    print("[PASS] Ambient glow animations and pulse indicators are defined in styles.css.")
    
    # Verify responsiveness
    responsive_patterns = ["@media", "max-width: 1024px", "max-width: 768px"]
    for rp in responsive_patterns:
        assert rp in css_content, f"Responsive media query rule '{rp}' not found in styles.css"
    print("[PASS] Responsive breakpoints and queries are defined in styles.css.")
    
    print("\n=== MILESTONE 1 VERIFICATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    verify_milestone_1()
