import json
from ollama import chat
from ollama import ChatResponse

# Use filtered_data.json  
def buildRequestPrompt(articles: list[dict]) -> str:
    prompt = """You're job is to summarize a list of article headlines and their corresponding summaries into one 
                summary document.

                Each articles will be listed numerically starting at 1 with its headline and summary following.
                
                Memorize the headlines and summaries and then create one document that summarizes all the information you were given.

                Have each line be no longer than 80 characters.
                
                Bellow is the list of article headlines and summaries:\n"""
    for i, article in enumerate(articles, start=1):
        prompt += f"""
        {i}.
        Headline: {article['headline']}
        Summary: {article['summary']}
        """
    return prompt

def getResponse(prompt: str) -> ChatResponse:
    response: ChatResponse = chat(model='llama3:8b', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    return response

with open('filtered_data.json') as json_file:
    articles = json.load(json_file)


prompt = buildRequestPrompt(articles)
response = getResponse(prompt)
# print(buildRequestPrompt(articles))

with open("response.txt", "w") as f:
    print(response.message.content, file=f)

with open("response.json", "w") as f:
    json.dump(response.model_dump(),f, indent=2)
