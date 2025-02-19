from dotenv import load_dotenv
import os

import json
import requests
# Load environment variables from the .env file
load_dotenv()

# Access variables
API_KEY = os.getenv("harris_real_estate")
BASE_URL = "https://api.beehiiv.com/v1"


# Replace with your Beehiiv API Key and Publication ID

PUBLICATION_ID = "pub_1e0f23b2-b82e-44b6-b572-53b4fe61096f"

# Beehiiv API endpoint
API_URL = f"https://api.beehiiv.com/v2/publications/{PUBLICATION_ID}/posts"

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}



data = {
     
  "title": "The Kitchen Sink Post (refactored version)",
  "blocks": [
    {
      "type": "heading",
      "level": "2",
      "text": "This is my block!!!",
      "anchorHeader": False,
      "anchorIncludeInToc": False,
      "textAlignment": "center"
    },
    {
      "type": "list",
      "items": [
        "a",
        "b",
        "c"
      ],
      "listType": "ordered"
    },
    {
      "type": "list",
      "items": [
        "d",
        "e",
        "f"
      ],
      "listType": "ordered",
      "startNumber": 4
    },
    {
      "type": "list",
      "items": [
        "g",
        "h",
        "i"
      ],
      "listType": "unordered",
      "startNumber": 4
    },
    {
      "type": "table",
      "rows": [
        [
          {
            "text": "A"
          },
          {
            "text": "B",
            "alignment": "center"
          },
          {
            "text": "C",
            "alignment": "right"
          }
        ],
        [
          {
            "text": "D",
            "alignment": "right"
          },
          {
            "text": "E",
            "alignment": "center"
          },
          {
            "text": "F",
            "alignment": "left"
          }
        ]
      ],
      "headerColumn": True,
      "headerRow": True
    },
    {
      "type": "table",
      "rows": [
        [
          {
            "text": "A"
          },
          {
            "text": "B"
          },
          {
            "text": "C"
          }
        ],
        [
          {
            "text": "D"
          },
          {
            "text": "E"
          },
          {
            "text": "F"
          }
        ]
      ]
    },
    {
      "type": "table",
      "rows": [
        [
          {
            "text": "A"
          },
          {
            "text": "B"
          },
          {
            "text": "C"
          }
        ],
        [
          {
            "text": "D"
          },
          {
            "text": "E"
          },
          {
            "text": "F"
          }
        ]
      ],
      "headerRow": False
    },
    {
      "type": "columns",
      "columns": [
        {
          "blocks": [
            {
              "type": "paragraph",
              "plaintext": "Marble Column 1 {{email}}"
            }
          ]
        },
        {
          "blocks": [
            {
              "type": "image",
              "imageUrl": "https://cdn.britannica.com/89/164789-050-D6B5E2C7/Barack-Obama-2012.jpg",
              "alt_text": "A picture of Barry Obama",
              "caption": "One Cool President",
              "captionAlignment": "center",
              "imageAlignment": "right",
              "title": "Barry O",
              "url": "https://www.whitehouse.gov/",
              "width": 75
            }
          ]
        }
      ]
    },
    {
      "type": "advertisement",
      "opportunity_id": "d8dfa6be-24b5-4cad-8350-ae44366dbd4c"
    },
    {
      "type": "image",
      "imageUrl": "https://cdn.britannica.com/89/164789-050-D6B5E2C7/Barack-Obama-2012.jpg",
      "alt_text": "A picture of Barry Obama",
      "caption": "One Cool President",
      "captionAlignment": "center",
      "imageAlignment": "right",
      "title": "Barry O",
      "url": "https://www.whitehouse.gov/",
      "width": 75
    },
    {
      "type": "paragraph",
      "formattedText": [
        {
          "text": "This is going to be "
        },
        {
          "text": "a really, really awesome time ",
          "styling": [
            "bold"
          ]
        },
        {
          "text": "Are you ready for this?",
          "styling": [
            "italic",
            "bold"
          ]
        }
      ]
    },
    {
      "type": "button",
      "href": "/subscribe",
      "text": "Subscribe",
      "alignment": "center",
      "size": "large",
      "target": "_blank"
    },
    {
      "type": "button",
      "href": "/signup",
      "text": "Sign Up",
      "alignment": "right",
      "size": "small",
      "target": "_blank"
    },
    {
      "type": "button",
      "href": "/",
      "text": "View Posts",
      "target": "_blank"
    },
    {
      "type": "heading",
      "level": "4",
      "text": "This is my block!!!",
      "anchorHeader": True,
      "anchorIncludeInToc": True,
      "textAlignment": "right"
    }
  ],
  "subtitle": "Contains lots of examples of each block type and the various settings you could use",
  "post_template_id": "post_template_00000000-0000-0000-0000-000000000000",
  "scheduled_at": "2026-12-25T12:00:00Z",
  "custom_link_tracking_enabled": True,
  "email_capture_type_override": "none",
  "override_scheduled_at": "2026-10-26T14:01:16Z",
  "social_share": "comments_and_likes_only",
  "thumbnail_image_url": "https://images.squarespace-cdn.com/content/v1/56e4ca0540261d39b90e4b18/1605047208324-PONGEYKEAKTMM1LANHJ5/1ED706BF-A70B-4F26-B3D5-266B449DDA8A_1_105_c.jpeg",
  "recipients": {
    "web": {
      "tier_ids": [
        "premium"
      ]
    },
    "email": {
      "tier_ids": [
        "premium"
      ],
      "include_segment_ids": [
        "seg_6426b403-39f5-42bd-86e9-9533fb0099e7"
      ],
      "exclude_segment_ids": [
        "seg_e34b4085-aef6-449f-a699-7563f915f852"
      ]
    }
  },
  "email_settings": {
    "from_address": "from_address",
    "custom_live_url": "https://beehiiv.com",
    "display_title_in_email": True,
    "display_byline_in_email": True,
    "display_subtitle_in_email": True,
    "email_header_engagement_buttons": "email_header_engagement_buttons",
    "email_header_social_share": "email_header_social_share",
    "email_preview_text": "email_preview_text",
    "email_subject_line": "email_subject_line"
  },
  "web_settings": {
    "display_thumbnail_on_web": True,
    "hide_from_feed": True,
    "slug": "and-this-is-gonna-rock"
  },
  "seo_settings": {
    "default_description": "default_description",
    "default_title": "default_title",
    "og_description": "OpenGraph description",
    "og_title": "Opengraph Title",
    "twitter_description": "Twitter Stuff",
    "twitter_title": "My Twitter Article"
  },
  "content_tags": [
    "Obama",
    "Care",
    "Rocks",
    "Healthcare"
  ]
}

# Send POST request
response = requests.post(API_URL, headers=headers, json=data)

# Print response
if response.status_code == 200:
    print("Custom field created successfully!")
    print(json.dumps(response.json(), indent=4))
else:
    print(f"Error: {response.status_code}")
    print(response.text)