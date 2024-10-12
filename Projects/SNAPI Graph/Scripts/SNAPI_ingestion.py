# This Python script is designed to fetch spaceflight news articles from an API, process them using Langchain and OpenAI, and ingest them into a Neo4j graph database.
# Here's a breakdown of its main components and functions:

# Setup and Imports:
# - The script imports necessary libraries including Langchain components.
# - It sets up logging and loads environment variables for Neo4j and OpenAI API connections.
# - It establishes a connection to the Neo4j database.

# Data Models:
# - KeywordTopic: Defines the structure for a keyword and its associated topic.
# - ArticleAnalysis: Defines the structure for the overall analysis of an article, containing a list of KeywordTopics.

# Langchain Setup:
# - Initializes a ChatOpenAI model and a PydanticOutputParser for structured output.
# - Creates a ChatPromptTemplate for article analysis.

# fetch_articles():
# - Makes a GET request to the Spaceflight News API and retrieves a list of articles.

# process_article(article):
# - Uses Langchain to analyze an article and extract keywords and topics.
# - Formats the prompt with the article content and invokes the language model.
# - Parses the output into a structured ArticleAnalysis object.

# ingest_articles(articles):
# - Processes each fetched article using process_article().
# - Creates or updates an Article node in the Neo4j database for each article.
# - Creates Keyword and Topic nodes based on the analysis, and establishes relationships between Article, Keyword, and Topic nodes.
# - Logs the ingestion process, including any errors.

# verify_ingestion():
# - Checks the number of Article nodes in the database to verify the ingestion process.

# Main execution:
# - Fetches articles from the API.
# - Processes and ingests the articles into the database.
# - Verifies the ingestion by counting the articles in the database.
# - Handles exceptions and logs any errors that occur during the process.
# - Closes the database connection.

# This script automates the process of collecting spaceflight news articles, analyzing their content using AI, and organizing the results in a graph database. This approach allows for more sophisticated analysis of article content, including extraction of relevant keywords and topics, which can be useful for content categorization, trend analysis, and creating meaningful relationships between articles.

import os
import requests
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError
from typing import List
import time
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the .env file (assuming it's in the parent directory)
dotenv_path = os.path.join(script_dir, '..', '.env')

# Load the .env file
load_dotenv(dotenv_path)

# Debug log the environment variables (mask the API key for security)
logger = logging.getLogger(__name__)
logger.debug(f"NEO4J_URI: {os.getenv('NEO4J_URI')}")
logger.debug(f"NEO4J_USER: {os.getenv('NEO4J_USER')}")
logger.debug(f"NEO4J_PASSWORD: {'*' * len(os.getenv('NEO4J_PASSWORD', ''))}")
logger.debug(f"OPENAI_API_KEY: {'*' * len(os.getenv('OPENAI_API_KEY', ''))}")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

SPACEFLIGHT_NEWS_API_URL = "https://api.spaceflightnewsapi.net/v4/articles"

# Define the output structure
class KeywordTopic(BaseModel):
    keyword: str = Field(description="A relevant keyword from the article")
    topic: str = Field(description="The broader topic that the keyword belongs to")
    relevance_score: float = Field(
        ge=0.0, le=1.0, description="Relevance score between 0 and 1"
    )
    context: str = Field(description="Describe how the keyword is relevant to the article")

class ArticleAnalysis(BaseModel):
    keywords_topics: List[KeywordTopic] = Field(
        description="List of keywords with their corresponding topics and metadata"
    )

# Set up the language model and output parser
llm = ChatOpenAI(temperature=0, model="gpt-4")
output_parser = PydanticOutputParser(pydantic_object=ArticleAnalysis)

# Update the prompt template
prompt = ChatPromptTemplate.from_template(
    "Analyze the following article and extract relevant keywords along with their corresponding topics. "
    "For each keyword, provide a relevance score between 0 and 1, and include a sentence from the article that provides context. "
    "Provide the output in the specified format.\n\n"
    "Important: Do not include time-related terms or date formats as keywords or topics. "
    "Focus on the substantive content of the article, and if the article is not substantive, skip it.\n\n"
    "Article: {article}\n\n"
    "{format_instructions}"
)
# Fetch articles from the Spaceflight News API within the last 7 days
def fetch_articles():
    all_articles = []
    page = 0
    limit = 100  # Maximum allowed by the API
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    while True:
        try:
            params = {
                'limit': limit,
                'offset': page * limit,
                'published_at_gte': start_date.isoformat(),
                'published_at_lte': end_date.isoformat(),
                'ordering': '-published_at'  # Latest articles first
            }
            response = requests.get(SPACEFLIGHT_NEWS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = data['results']
            all_articles.extend(articles)
            
            if len(articles) < limit:
                break  # No more articles to fetch
            
            page += 1
            
            # Respect rate limits (10 requests per second)
            time.sleep(0.1)
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching articles: {e}")
            break
    
    logging.info(f"Fetched {len(all_articles)} articles from the last 7 days.")
    return all_articles

# Process an article to extract keywords and topics
def process_article(article):
    try:
        # Combine title and summary for analysis
        article_text = f"{article['title']}\n\n{article['summary']}"
        
        # Format the prompt with the article and output instructions
        formatted_prompt = prompt.format(
            article=article_text,
            format_instructions=output_parser.get_format_instructions()
        )
        
        # Get the response from the language model
        response = llm.invoke(formatted_prompt)
        
        # Parse the output
        parsed_output = output_parser.parse(response.content)
        
        return parsed_output
    except ValidationError as ve:
        logging.error(f"Validation error processing article {article['id']}: {ve}")
        # Handle or re-raise exception as needed

# Ingest articles into the Neo4j database
def ingest_articles(articles):
    with driver.session() as session:
        for article in articles:
            try:
                # Check if the article already exists in the database
                result = session.run(
                    "MATCH (a:Article {id: $id}) RETURN a.id AS id",
                    id=article['id']
                )
                if result.single():
                    logging.info(f"Article with ID {article['id']} already exists. Skipping.")
                    continue

                # Process the article to extract keywords and topics
                analysis = process_article(article)
                
                # Create or update the Article node
                result = session.run(
                    """
                    MERGE (a:Article {id: $id})
                    SET a.title = $title,
                        a.url = $url,
                        a.image_url = $image_url,
                        a.news_site = $news_site,
                        a.summary = $summary,
                        a.published_at = datetime($published_at),
                        a.processed = true
                    RETURN a.id AS id
                    """,
                    id=article['id'],
                    title=article['title'],
                    url=article['url'],
                    image_url=article['image_url'],
                    news_site=article['news_site'],
                    summary=article['summary'],
                    published_at=article['published_at']
                )
                article_id = result.single()['id']
                
                # Create keyword and topic nodes, and relationships with properties
                for item in analysis.keywords_topics:
                    session.run(
                        """
                        MATCH (a:Article {id: $article_id})
                        MERGE (k:Keyword {word: $keyword})
                        MERGE (t:Topic {name: $topic})
                        MERGE (a)-[r:CONTAINS_KEYWORD]->(k)
                        SET r.relevance_score = $relevance_score,
                            r.context = $context
                        MERGE (k)-[b:BELONGS_TO]->(t)
                        """,
                        article_id=article_id,
                        keyword=item.keyword,
                        topic=item.topic,
                        relevance_score=item.relevance_score,
                        context=item.context
                    )
                
                logging.info(f"Processed and ingested article with ID: {article_id}")
            except Exception as e:
                logging.error(f"Error processing article {article['id']}: {e}")
    
    logging.info(f"Attempted to ingest {len(articles)} articles into the database.")

# Verify the ingestion by counting the articles in the database
def verify_ingestion():
    with driver.session() as session:
        result = session.run("MATCH (a:Article) RETURN count(a) AS article_count")
        article_count = result.single()['article_count']
        logging.info(f"Number of articles in the database: {article_count}")

# Main execution block
if __name__ == "__main__":
    try:
        articles = fetch_articles()
        logging.info(f"Fetched {len(articles)} articles from the API.")
        ingest_articles(articles)
        verify_ingestion()
        logging.info("Data ingestion completed successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching articles: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        driver.close()