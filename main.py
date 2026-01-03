from get_paper_content import fetch_paper_content
from create_feed import generate_feed
import json

def main():
    paper_url_content = fetch_paper_content()
    recommendations = generate_feed(paper_url_content)
    if recommendations:
        # save recommendations
        json.dump(recommendations,open("data/recommendations.json","w"))
        
        # update recommendations file (track all papers)
        old_recommendations = json.load(open("data/all_recommendations.json","r"))        
        all_recommendations = old_recommendations + recommendations
        json.dump(all_recommendations, open("data/all_recommendations.json","w"))

if __name__ == "__main__":
    main()
