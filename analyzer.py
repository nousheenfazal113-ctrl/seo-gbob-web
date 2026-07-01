# analyzer.py
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def detect_cms(soup, html_text):
    """Website ka CMS detect karta hai."""
    html_text_lower = html_text.lower()
    if "wp-content" in html_text_lower or "wp-includes" in html_text_lower:
        return "WordPress"
    elif "shopify.com/assets" in html_text_lower or "cdn.shopify.com" in html_text_lower:
        return "Shopify"
    elif "webflow" in html_text_lower:
        return "Webflow"
    elif "wix.com" in html_text_lower:
        return "Wix"
    return "Custom / Unknown"

def find_outreach_pages(soup, base_url):
    """Website par Write for Us, Guest Post aur Contact pages dhoondta hai."""
    pages = {"Write for Us": "Not Found", "Guest Post": "Not Found", "Contact Page": "Not Found"}
    keywords = {
        "Write for Us": ["write for us", "write-for-us", "contribute", "submit-an-article"],
        "Guest Post": ["guest post", "guest-guidelines", "submit post"],
        "Contact Page": ["contact", "contact-us", "get in touch"]
    }
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"].strip()
        text = link.get_text().lower()
        absolute_url = urljoin(base_url, href)
        for category, key_list in keywords.items():
            if pages[category] == "Not Found":
                if any(key in text or key in href.lower() for key in key_list):
                    pages[category] = absolute_url
    return pages

def extract_social_links(soup):
    """Website se social media handles extract karta hai."""
    social_profiles = []
    platforms = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com", "youtube.com"]
    
    links = soup.find_all("a", href=True)
    for link in links:
        href = link["href"].strip()
        if any(platform in href.lower() for platform in platforms):
            if href not in social_profiles:
                social_profiles.append(href)
                
    return ", ".join(social_profiles) if social_profiles else "None Found"

def analyze_seo_and_gbob(html_text, url):
    """SaaS Level Complete SEO & GBOB Analyzer Engine"""
    if not html_text:
        return {"Website URL": url, "Website Title": "Failed to Fetch", "Accepts Guest Posts": "Error"}
        
    soup = BeautifulSoup(html_text, "lxml")
    
    # Basic SEO Data
    title = soup.title.string.strip() if soup.title else "N/A"
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag.get("content").strip() if meta_desc_tag else "N/A"
    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href").strip() if canonical_tag else "N/A"
    h1_count = len(soup.find_all("h1"))
    
    # CMS & GBOB Outreach Pages
    cms = detect_cms(soup, html_text)
    outreach_data = find_outreach_pages(soup, url)
    
    # Links Counting
    all_links = soup.find_all("a", href=True)
    internal_count = sum(1 for l in all_links if l["href"].startswith("/") or url in l["href"])
    external_count = sum(1 for l in all_links if l["href"].startswith("http") and url not in l["href"])
    
    # Visible Word Count
    for script in soup(["script", "style"]): 
        script.extract()
    visible_text = soup.get_text()
    words = re.findall(r'\w+', visible_text)
    word_count = len(words)
    
    # Image & Alt Spacing
    images = soup.find_all("img")
    image_count = len(images)
    alt_count = sum(1 for img in images if img.get("alt") and img["alt"].strip())
    alt_coverage = f"{alt_count}/{image_count}" if image_count > 0 else "0/0"
    
    # OpenGraph & Schema Markup
    has_og = "Yes" if soup.find("meta", property=re.compile(r'^og:')) else "No"
    
    has_schema = "No"
    if soup.find("script", type="application/ld+json"):
        has_schema = "Yes (JSON-LD)"
    elif soup.find(attrs={"itemscope": True}):
        has_schema = "Yes (Microdata)"
        
    # --- NEW FEATURE: Social Extraction ---
    social_media = extract_social_links(soup)
        
    accepts_guest_post = "Likely" if outreach_data["Write for Us"] != "Not Found" or outreach_data["Guest Post"] != "Not Found" else "Unlikely"
    
    return {
        "Website URL": url,
        "Website Title": title,
        "Meta Description": meta_desc,
        "Canonical URL": canonical,
        "H1 Count": h1_count,
        "Word Count": word_count,
        "Image Count": image_count,
        "Alt Text Coverage": alt_coverage,
        "Has Open Graph": has_og,
        "Has Schema Markup": has_schema,
        "Internal Links": internal_count,
        "External Links": external_count,
        "CMS": cms,
        "Contact Page": outreach_data["Contact Page"],
        "Write for Us Page": outreach_data["Write for Us"],
        "Guest Post Page": outreach_data["Guest Post"],
        "Social Media Links": social_media,
        "Accepts Guest Posts": accepts_guest_post
    }