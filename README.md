# Spaceflight News Graph Project

## Overview

This project utilizes a Neo4j graph database to store and analyze structured data from the [Spaceflight News API](https://api.spaceflightnewsapi.net/v3/documentation). The goal is to extract important details from each new article and store them in a graph database for processing with OpenAI's models, ultimately generating content for a weekly newsletter.

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
