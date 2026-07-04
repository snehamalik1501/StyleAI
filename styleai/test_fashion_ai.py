from ollama import chat

colors = """
RGB(223,215,204)
RGB(25,24,23)
RGB(171,156,139)
"""

prompt = f"""
You are a professional fashion stylist.

Dominant outfit colors:
{colors}

Style: Minimal Elegant
Budget: ₹500–₹1500

Return recommendations for:

1. Earrings
2. Necklace
3. Handbag
4. Footwear

For each recommendation provide:
- Item name
- Why it matches the outfit
- Approximate budget

Keep the answer concise.
"""

response = chat(
    model="qwen2.5vl",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(response["message"]["content"])
