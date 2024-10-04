import os
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
import openai

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def generate_newsletter():
    with driver.session() as session:
        # Retrieve the most relevant articles
        articles = session.run(
            """
            MATCH (a:Article)
            WHERE a.published_at >= datetime() - duration('P7D')
            RETURN a.id AS id, a.title AS title, a.summary AS summary
            ORDER BY a.published_at DESC
            LIMIT 5
            """
        )
        newsletter_sections = []
        for record in articles:
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=f"Create a brief and engaging newsletter section based on the following article summary:\n\nTitle: {record['title']}\nSummary: {record['summary']}\n\nNewsletter Section:",
                    max_tokens=150,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
                section = response.choices[0].text.strip()
                newsletter_sections.append(section)
            except Exception as e:
                print(f"Error generating newsletter section for article {record['id']}: {e}")

        # Combine sections into full content
        newsletter_content = "\n\n---\n\n".join(newsletter_sections)

        # Store the newsletter in the database
        session.run(
            """
            CREATE (n:NewsletterIssue {
                issue_date: date($issue_date),
                content: $content,
                created_at: datetime($created_at)
            })
            """,
            issue_date=datetime.now().date().isoformat(),
            content=newsletter_content,
            created_at=datetime.now().isoformat()
        )
        print("Newsletter generated and stored in the database.")

if __name__ == "__main__":
    generate_newsletter()
