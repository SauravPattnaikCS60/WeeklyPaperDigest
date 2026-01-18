from dotenv import load_dotenv
import os
import json
from tavily import TavilyClient
from dateutil.relativedelta import relativedelta
import datetime
from prompts import generate_research_topic_prompt
from groq_call import run_groq_api

# load_dotenv()
NUMBER_OF_PAPERS = 3
DOMAINS = ["https://arxiv.org/abs/"]
MAX_RETRYS = 3

def get_start_and_end_dates():
    end = datetime.datetime.now()
    start = end - relativedelta(months=6)
    
    start_date = f"{start.year}-{start.month}-{start.day}"
    end_date = f"{end.year}-{end.month}-{end.day}"

    return (start_date, end_date)

def validate_paper_urls(urls):
    clean_urls = []
    
    for url in urls:
        if url.startswith('https') and "arxiv" in url:
            clean_urls.append(url)
    
    return clean_urls

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
            paper_urls = f"""
            In the context of {topic}, return exactly {NUMBER_OF_PAPERS} research paper URLs.
            Select papers that are either seminal and highly cited, or recent and rapidly trending.
            Only include arXiv links (https://arxiv.org/abs/...).
            Return only a valid Python list in the form ["url1", "url2", "url3"], with no extra text.
            """
            
            response = tavily_client.search(paper_urls,max_results=3,include_answer=True,include_domains=DOMAINS)

            paper_titles = response["answer"]
            paper_titles = eval(paper_titles)
            paper_titles = validate_paper_urls(paper_titles)
            
            # fetch content for the same topics
            paper_url_content = {}
            for paper_title in paper_titles:        
                response = tavily_client.extract(paper_title,extract_depth="advanced",format="text")
                paper_url_content[paper_title] = response
                
            json.dump(paper_url_content, open("data/paper_content.json","w"))
            
            # update topic only when we get paper content
            with open ("data/topic.txt","w") as f:
                f.write(topic)
            
            return paper_url_content
        except:
            retry += 1
            continue


if __name__ == "__main__":
    fetch_paper_content()