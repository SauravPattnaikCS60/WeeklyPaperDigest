from dotenv import load_dotenv
import os
import json
from tavily import TavilyClient
from dateutil.relativedelta import relativedelta
import datetime
from prompts import generate_research_topic_prompt
from groq_call import run_groq_api

# load_dotenv()
NUMBER_OF_PAPERS = 1
DOMAINS = ["https://arxiv.org/abs/"]
MAX_RETRYS = 3

def get_start_and_end_dates():
    end = datetime.datetime.now()
    start = end - relativedelta(months=6)
    
    start_date = f"{start.year}-{start.month}-{start.day}"
    end_date = f"{end.year}-{end.month}-{end.day}"

    return (start_date, end_date)

# def validate_paper_urls(urls):
#     clean_urls = []
    
#     for url in urls:
#         if url.startswith('https') and "arxiv" in url:
#             clean_urls.append(url)
    
#     return clean_urls

def fetch_paper_content():
    
    # create the tavily client
    tavily_key = os.getenv('TAVILY')
    tavily_client = TavilyClient(api_key=tavily_key)
    
    retry = 0
    while retry < MAX_RETRYS:
        try:
            prompt = generate_research_topic_prompt()
            topic = run_groq_api(prompt)
            
            # pull 3 articles for the topic
            paper_urls = f"""In the context of {topic}, return exactly {NUMBER_OF_PAPERS} research paper URLs. Select papers that are either seminal and highly cited, or recent and rapidly trending. Return only the url, with no extra text."""
            response = tavily_client.search(paper_urls,max_results=1,include_answer=True,include_domains=DOMAINS)
            # print(topic)
            # print(response)
            paper_title = response["answer"]
            paper_title = str(paper_title)
            # paper_title = validate_paper_urls(paper_title)
            
            # fetch content for the same topic
            paper_url_content = {}
            response = tavily_client.extract(paper_title,extract_depth="advanced",format="text")
            paper_url_content[paper_title] = response
            
            json.dump(paper_url_content, open("data/paper_content.json","w"))
            
            # update topic only when we get paper content
            with open ("data/topic.txt","w") as f:
                f.write(topic)
            
            return paper_url_content
        except Exception as e:
            retry += 1
            continue


if __name__ == "__main__":
    fetch_paper_content()