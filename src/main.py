"""
Instagram & TikTok Influencer & Creator Email Finder Actor for Apify
Extracts social creators, bios, public emails, and follower counts for marketing outreach.
"""

import asyncio
import re
import urllib.parse
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
from apify import Actor

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
HANDLE_REGEX = re.compile(r"@([a-zA-Z0-9_.]+)")
FOLLOWERS_REGEX = re.compile(r"(\d+(?:\.\d+)?\s?[kKmMbB]?)\s*(?:followers|seguidores|abonnés)", re.IGNORECASE)

async def search_social_creators(client: httpx.AsyncClient, keyword: str, platform: str, max_results: int) -> List[Dict[str, Any]]:
    """Finds indexed creator profiles across social networks."""
    domain_map = {
        "instagram": "site:instagram.com",
        "tiktok": "site:tiktok.com/@",
        "youtube": "site:youtube.com/@",
        "twitter": "site:twitter.com OR site:x.com"
    }
    
    site_filter = domain_map.get(platform.lower(), "site:instagram.com")
    query = f"{site_filter} {keyword} \"email\" OR \"contact\" OR \"collab\""
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    results = []
    try:
        resp = await client.get(url, headers=headers, timeout=12.0)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            snippets = soup.find_all("div", class_="result")
            
            for snip in snippets[:max_results]:
                title_elem = snip.find("a", class_="result__a")
                snippet_elem = snip.find("a", class_="result__snippet")
                url_elem = snip.find("a", class_="result__url")
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                raw_url = url_elem.get("href", "") if url_elem else ""
                
                clean_url = ""
                if "uddg=" in raw_url:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                    if "uddg" in parsed:
                        clean_url = parsed["uddg"][0]
                elif raw_url.startswith("http"):
                    clean_url = raw_url

                # Extract email
                combined_text = f"{title} {snippet}"
                emails = EMAIL_REGEX.findall(combined_text)
                clean_email = ""
                if emails:
                    valid_emails = [
                        e for e in emails 
                        if not e.endswith((".png", ".jpg", ".js", ".css"))
                        and not e.startswith(("info@instagram", "support@tiktok"))
                    ]
                    if valid_emails:
                        clean_email = valid_emails[0]

                # Extract handle
                handle_match = HANDLE_REGEX.search(title)
                handle = handle_match.group(1) if handle_match else title.split("•")[0].split("(")[0].strip()

                # Extract follower stats
                fol_match = FOLLOWERS_REGEX.search(snippet)
                followers = fol_match.group(1) if fol_match else "N/A"

                results.append({
                    "platform": platform.capitalize(),
                    "handle": handle,
                    "name": title.split("•")[0].strip(),
                    "email": clean_email or "Not in bio",
                    "niche": keyword,
                    "followersApprox": followers,
                    "profileUrl": clean_url,
                    "bioSnippet": snippet
                })
    except Exception as e:
        Actor.log.warning(f"Error searching creators on {platform} for '{keyword}': {e}")
        
    return results

async def main():
    async with Actor:
        actor_input = await Actor.get_input() or {}
        
        keywords = actor_input.get("keywords", ["Fitness coach Miami", "Beauty makeup Los Angeles"])
        platforms = actor_input.get("platforms", ["instagram", "tiktok"])
        max_results = actor_input.get("maxResults", 25)
        require_email = actor_input.get("requireEmail", False)
        
        Actor.log.info(f"Starting Social Leads Finder for {len(keywords)} keywords across {len(platforms)} platforms...")

        async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, follow_redirects=True) as client:
            total_creators = 0
            
            for kw in keywords:
                for plat in platforms:
                    Actor.log.info(f"Finding {plat} creators in niche: '{kw}'...")
                    creators = await search_social_creators(client, kw, plat, max_results)
                    
                    for c in creators:
                        if require_email and c["email"] == "Not in bio":
                            continue
                        await Actor.push_data(c)
                        total_creators += 1

            Actor.log.info(f"Done! Successfully extracted and saved {total_creators} creator leads to dataset.")

if __name__ == "__main__":
    asyncio.run(main())
