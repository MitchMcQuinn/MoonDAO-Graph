# Spaceflight News Graph Project

## Overview

This project utilizes a Neo4j graph database to store and analyze structured data from the [Spaceflight News API]([https://api.spaceflightnewsapi.net/v3/documentation](https://github.com/TheSpaceDevs/spaceflightnewsapi)). The goal is to extract important details from each new article and store them in a graph database for processing with OpenAI's models, ultimately generating content for a weekly newsletter.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Graph Schema](#graph-schema)
- [Usage](#usage)
- [Automation](#automation)
- [Newsletter Generation](#newsletter-generation)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.8 or higher
- Neo4j Desktop or Neo4j Server
- VS Code with the Cursor extension
- OpenAI API key
- Git (for version control)

## Installation

1. **Clone the Repository**
```bash
   git clone https://github.com/yourusername/spaceflight-news-graph.git
   cd spaceflight-news-graph
```

3. Create a Virtual Environment
```bash
pip install -r requirements.txt
```

5.	Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration
1. Set Up Environment Variables
Create a .env file in the project root directory:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
OPENAI_API_KEY=your_openai_api_key
```
2. Configure Neo4j
```bash
	•	Start your Neo4j instance.
	•	Set the authentication details as specified in your .env file.
```
## Graph Schema

Nodes
1. Article
• title: String
• url: String
• publication_date: DateTime
• content: Text
• summary: Text
• relevance_score: Float
• source_name: String
• image_url: String

2. Topic
• name: String
• description: Text

3. Keyword
• word: String

4. Source
• name: String
• url: String
• credibility_score: Float

5. Event
• name: String
• date: DateTime
• location: String
• description: Text

6. Organization
• name: String
• type: String (e.g., company, agency)
• industry: String
• country: String

7. Person
• name: String
• role: String
• affiliation: String

8. NewsletterIssue
• issue_date: DateTime
• content: Text
• created_at: DateTime

Relationships
• (Article)-[:HAS_TOPIC]->(Topic)
• (Article)-[:CONTAINS_KEYWORD]->(Keyword)
• (Article)-[:FROM_SOURCE]->(Source)
• (Article)-[:MENTIONS]->(Organization|Person|Event)
• (Topic)-[:RELATED_TO]->(Topic)
• (Organization)-[:ASSOCIATED_WITH]->(Event)
• (Person)-[:AFFILIATED_WITH]->(Organization)
• (NewsletterIssue)-[:INCLUDES]->(Article)

## Usage

1. Data Ingestion
Run the data_ingestion.py script to fetch articles and populate the Neo4j database:
```bash
python data_ingestion.py
```

2. Content Processing
Process articles using OpenAI’s API to generate summaries and extract keywords:
```bash
python content_processing.py
```

3. Graph Exploration
Use Neo4j Browser or Neo4j Bloom to visualize and explore the graph.

## Automation

Schedule the data ingestion and content processing scripts using scheduler.py:
python scheduler.py

This script uses APScheduler to run tasks at specified intervals.

## Newsletter Generation

Generate the weekly newsletter content:
python generate_newsletter.py

This script will:
	•Retrieve the most relevant articles.
	•Use OpenAI’s models to create summaries and compose newsletter sections.
	•Store the newsletter content in the NewsletterIssue node.

## Additional Information

	•Indexes and Constraints:
	•Implement indexes on frequently queried properties like Article.title and Person.name.
	•Use constraints to ensure data uniqueness where appropriate.
	•Data Quality:
	•Implement validation checks during data ingestion.
	•Handle duplicate entries gracefully.

Security Considerations

	•API Keys and Credentials:
	•Keep your OpenAI API key and Neo4j credentials secure.
	•Do not commit the .env file to version control.
	•Error Handling:
	•Implement robust error handling in your scripts.
	•Log errors for troubleshooting.

Testing

	•Unit Tests:
	•Write tests for data ingestion, processing, and database interactions.
	•Use frameworks like unittest or pytest.

Deployment

	•Scaling:
	•Consider deploying the application using Docker for containerization.
	•Use cloud services like AWS, Azure, or GCP for scalability.
	•Monitoring:
	•Set up monitoring for the Neo4j database and your application scripts.
	•Use tools like Prometheus and Grafana for insights.


