# Instagram & TikTok Influencer & Creator Email Finder

Find verified social media influencers, content creators, and brand ambassadors with public contact emails, follower stats, and niche keywords for influencer marketing and outreach.

## 🚀 Features

- **Multi-Platform:** Finds creators on **Instagram**, **TikTok**, **YouTube**, and **X (Twitter)**.
- **Email Detection:** Automatically filters and captures public collaboration emails from bios.
- **Niche Targeted:** Search by any niche, city, or language (Fitness, Gaming, Fashion, Tech, Beauty, Crypto).
- **Export Ready:** Download clean datasets in **Excel (XLSX)**, **CSV**, and **JSON**.

## 📥 Input Example

```json
{
  "keywords": [
    "Fitness coach Miami",
    "Tech reviewer New York",
    "Moda sustentable Madrid"
  ],
  "platforms": ["instagram", "tiktok"],
  "maxResults": 50,
  "requireEmail": false
}
```

## 📤 Output Format

Each record in the dataset includes:
- `platform`: Instagram / TikTok / YouTube / X
- `handle`: Creator @handle
- `name`: Profile display name
- `email`: Public business email
- `niche`: Searched keyword
- `followersApprox`: Estimated follower count
- `profileUrl`: Direct link to social profile
- `bioSnippet`: Full bio and collaboration info
