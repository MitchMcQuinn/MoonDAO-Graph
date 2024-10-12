import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

class NewsletterGenerator:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    def fetch_top_articles(self):
        query = """
        // Top 5 Trending Article Identification Query
        // Step 1: Identify trends by finding articles that share topics through keywords
        MATCH (a1:Article)-[:CONTAINS_KEYWORD]->(k1:Keyword)-[:BELONGS_TO]->(t:Topic)<-[:BELONGS_TO]-(k2:Keyword)<-[:CONTAINS_KEYWORD]-(a2:Article)

        // Step 2: Count the number of distinct topics for each article identified
        WITH a1, COUNT(DISTINCT t) AS topicCount

        // Step 3: Filter articles that have more than 1 shared topics
        WHERE topicCount > 1

        // Step 4: For the filtered articles, gather all relevant keywords and topics.
        MATCH (a1)-[:CONTAINS_KEYWORD]->(k:Keyword)-[:BELONGS_TO]->(t:Topic)

        // Step 5: Return the articles, their keywords, topics, and the topic count
        RETURN a1 AS article, COLLECT(DISTINCT k.word) AS keywords, COLLECT(DISTINCT t.name) AS topics, topicCount

        // Step 6: Order the results by topic count in descending order.
        ORDER BY topicCount DESC
        
        // Step 7: Limit the results to the top 5 articles
        LIMIT 5
        """
        with self.driver.session() as session:
            result = session.run(query)
            articles = []
            for record in result:
                article = record['article']
                articles.append({
                    'title': article['title'],
                    'url': article['url'],
                    'image_url': article.get('image_url', ''),
                    'summary': article.get('summary', ''),
                    'keywords': record['keywords'],
                    'topics': record['topics']
                })
            return articles

    def generate_markdown(self, articles):
        content = "# Weekly Spaceflight News\n\n"
        content += f"*Date: {datetime.now().strftime('%B %d, %Y')}*\n\n"
        for idx, article in enumerate(articles, 1):
            content += f"## {idx}. [{article['title']}]({article['url']})\n\n"
            if article['image_url']:
                content += f"![Image]({article['image_url']})\n\n"
            content += f"{article['summary']}\n\n"
            content += f"**Topics:** {', '.join(article['topics'])}\n\n"
            content += f"**Keywords:** {', '.join(article['keywords'])}\n\n"
            content += "---\n\n"
        return content

    def save_markdown(self, content):
        output_dir = os.path.join(os.getcwd(), 'Outputs')
        os.makedirs(output_dir, exist_ok=True)
        base_filename = f"newsletter_{datetime.now().strftime('%Y%m%d')}.md"
        file_path = os.path.join(output_dir, base_filename)
        
        version = 1
        while os.path.exists(file_path):
            version += 1
            file_path = os.path.join(output_dir, f"newsletter_{datetime.now().strftime('%Y%m%d')}({version}).md")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Newsletter generated at {file_path}")

    def close(self):
        self.driver.close()

if __name__ == "__main__":
    generator = NewsletterGenerator()
    articles = generator.fetch_top_articles()
    if articles:
        markdown_content = generator.generate_markdown(articles)
        generator.save_markdown(markdown_content)
    else:
        print("No articles found.")
    generator.close()
