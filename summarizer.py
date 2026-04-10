import os
from ollama import ChatResponse
from ollama import Client
import textwrap

# Use filtered_data.json  
def buildRequestPrompt(articles: list[dict]) -> str:
    prompt = """
                YOUR ROLE:
    
                You're job is to summarize a list of article titles and their corresponding content into one 
                summary document. Each article will be listed numerically starting at 1 with its title and content following.
                Memorize the title and content and then create one document that summarizes all the information you were given.

                DOCUMENT GUIDELINES START:
                1. The document will contain two sections the first being a summary of all of the content and the second being a key
                    point section. The summary section will follow a paragraph structure and be anywhere to one to three paragraphs
                    in length. Have a new line to separate paragraphs.

                    The key point section will contain bullet points.

                    STRICT FORMATTING RULES FOR KEY POINTS:
                    - Each bullet point MUST be on its own line.
                    - Each bullet point MUST start with "* " (dash + space).
                    - There MUST be a newline after every bullet point.
                    - NEVER put multiple bullet points on the same line.
                    - Each bullet point must be exactly one sentence.

                2. Have each line be no longer than 80 characters. If a line is longer than 80 characters start on a new line.
                    This is very important.

                3. Only use information explicitly stated in the articles. Do not invent numbers, projections, or partnerships.
                    If you are uncertain on something say "I am Uncertain". 
                
                DOCUMENT GUIDELINES END

                Bellow is the list of article titles and corresponding content:\n"""
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

    response:ChatResponse = client.chat('gemma4:31b-cloud', messages=messages)

    return response

def formatDoc(response: str, max_length: int = 80) -> None:
    """
    Reads a file, wraps all lines to a maximum length, and overwrites the file.
    
    Args:
        file_path (str): Path to the file to edit
        max_length (int): Maximum allowed line length (default: 80)
    """
    # Split into paragraphs to preserve spacing
    paragraphs = response.split("\n\n")

    wrapped_paragraphs = []
    for para in paragraphs:
        # Handle lists or bullet points more cleanly
        if para.strip().startswith("*"):
            lines = para.split("\n")
            wrapped_lines = [
                textwrap.fill(line, width=max_length, subsequent_indent="  ")
                for line in lines
            ]
            wrapped_paragraphs.append("\n".join(wrapped_lines))
        else:
            wrapped_paragraphs.append(
                textwrap.fill(para, width=max_length)
            )

    new_content = "\n\n".join(wrapped_paragraphs)

    with open("response.txt", "w", encoding="utf-8") as f:
        f.write(new_content)