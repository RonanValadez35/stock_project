import os
from ollama import ChatResponse
from ollama import Client
import re
import textwrap

# Use filtered_data.json  
def buildRequestPrompt(articles: list[dict], tickers: list[str]) -> str:
    prompt = f"""
                YOUR ROLE:
    
                Your job is to summarize a list of article titles and their corresponding content into one
                summary document. Each article will be listed numerically starting at 1 with its title and content following.
                Read the title and content and then create one document that summarizes all the information you were given.

                DOCUMENT GUIDELINES START:
                1. Divide the document into sections by stock ticker symbol. The only ticker symbols to include are:
                   {tickers}
                   Each ticker section must contain a summary followed by a key-points section.
                   The summary must be one to three paragraphs long, with a blank line between paragraphs.

                   Use this exact structure for every ticker:

                   Ticker Symbol: SYMBOL

                   Summary paragraph.

                   Keypoints:
                   * First key point.
                   * Second key point.

                   STRICT FORMATTING RULES FOR KEY POINTS:
                   - Write the heading exactly as "Keypoints:" on its own line.
                   - Begin every bullet with a literal asterisk followed by one space: "* ".
                   - Do not escape the asterisk and do not output "\\*".
                   - Put every bullet on a separate new line.
                   - Never place two bullet points on the same line.
                   - Write exactly one sentence per bullet point.
                   - Add a blank line after the final bullet before the next ticker section.

                2. Keep each line at most 80 characters long. Continue long bullet points on an indented
                   line without adding another bullet marker.

                3. Only use information explicitly stated in the articles. Do not invent numbers, projections, or partnerships.
                   If you are uncertain about something, say "I am uncertain."
                
                DOCUMENT GUIDELINES END

                Below is the list of article titles and corresponding content:\n"""
    for i, article in enumerate(articles, start=1):
        prompt += f"""
        {i}.
        Headline: {article['title']}
        Summary: {article['content']}
        """
    return prompt

def getResponse(prompt: str) -> ChatResponse:

    client = Client(
        host="https://ollama.com",
        headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
    )

    messages = [
        {
            'role': 'user',
            'content': prompt,
        },
    ]

    response:ChatResponse = client.chat('gemma4:31b-cloud', messages=messages, options={"temperature": 0.0})

    return response

def _normalize_keypoint_bullets(response: str) -> str:
    """Put every key point on its own line with a plain ``* `` marker."""
    response = response.replace("\r\n", "\n").replace("\r", "\n")

    # Match each key-points section up to the next ticker heading. This also
    # handles a model returning an entire ticker section on a single line.
    keypoint_section = re.compile(
        r"Key\s*points?\s*:\s*(.*?)(?=Ticker\s+Symbol\s*:|\Z)",
        flags=re.IGNORECASE | re.DOTALL,
    )
    bullet_marker = re.compile(r"(?:^|\s+)(?:\\?\*|•|-|\d+[.)])\s+")

    def normalize_section(match: re.Match[str]) -> str:
        content = match.group(1).strip()
        points = [part.strip() for part in bullet_marker.split(content) if part.strip()]

        # Even if the model omitted the marker, keep the key-points section in
        # the requested bullet format rather than leaving it as prose.
        if not points and content:
            points = [content]

        normalized_points = []
        for point in points:
            # Model-generated line wrapping is not meaningful here; wrapping
            # is applied consistently by formatDoc below.
            point = " ".join(point.replace(r"\*", "*").split())
            normalized_points.append(f"* {point}")

        if not normalized_points:
            return "Keypoints:"
        return "Keypoints:\n" + "\n".join(normalized_points) + "\n\n"

    return keypoint_section.sub(normalize_section, response).strip()


def formatDoc(response: str, max_length: int = 80) -> None:
    """
    Normalize summary formatting and write it to ``response.txt``.
    
    Args:
        response (str): Model-generated summary text
        max_length (int): Maximum allowed line length (default: 80)
    """
    normalized = _normalize_keypoint_bullets(response)
    wrapped_lines = []

    for line in normalized.splitlines():
        stripped = line.strip()
        if not stripped:
            # Avoid accumulating more than one blank separator line.
            if wrapped_lines and wrapped_lines[-1] != "":
                wrapped_lines.append("")
        elif stripped.startswith("* "):
            wrapped_lines.append(
                textwrap.fill(
                    stripped[2:],
                    width=max_length,
                    initial_indent="* ",
                    subsequent_indent="  ",
                )
            )
        else:
            wrapped_lines.append(textwrap.fill(stripped, width=max_length))

    new_content = "\n".join(wrapped_lines).rstrip() + "\n"

    with open("response.txt", "w", encoding="utf-8") as f:
        f.write(new_content)
