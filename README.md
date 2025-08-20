# Study Abroad AI Assistant

A FastAPI-based RAG-powered AI assistant that helps Ethiopian students find and apply for international study opportunities.

## Features

- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **PostgreSQL Database**: Robust data storage with pgAdmin for management
- **Docker Containerization**: Easy deployment and development setup
- **RAG-Powered AI**: Intelligent responses using LangChain and vector databases
- **Web Scraping**: Automated data collection from scholarship websites

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Groq API key (for LLM responses)
- OpenAI API key (for embeddings - very cheap, ~$0.10/month for typical usage)
- GROQ API key

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Assignment-Uno
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your Groq API key
   ```

3. **Start the services**
   ```bash
   docker-compose up --build
   ```

4. **Access the services**
   - **FastAPI App**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **pgAdmin**: http://localhost:5050 (admin@admin.com / admin)
   - **PostgreSQL**: localhost:5432

## API Endpoints

- `GET /` - Health check
- `GET /health` - Service status
- `GET /countries` - List available countries
- `GET /countries/{country_id}` - Get country details
- `POST /assistant/chat` - Chat with AI assistant

## Database Connection

- **Host**: localhost (or `db` from within Docker)
- **Port**: 5432
- **Database**: study_abroad_db
- **Username**: postgres
- **Password**: password

## Development

### Running locally (without Docker)
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Database migrations
```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Project Structure

```
Assignment-Uno/
├── app/                   # Main application package
│   ├── api/              # API routes and endpoints
│   ├── core/             # Configuration and settings
│   ├── crud/             # Database CRUD operations
│   ├── db/               # Database configuration
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic and services
│   ├── utils/            # Utility functions
│   └── main.py           # FastAPI application
├── migrations/           # Database migrations
├── config_files/         # Configuration files
├── scripts/              # Utility scripts
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Multi-service setup
├── alembic.ini          # Database migration config
├── .env                 # Environment variables
├── .dockerignore        # Docker ignore file
└── README.md           # This file
```

## Data Collection

### Scraping Czech Scholarships
To collect scholarship data from the Czech Ministry of Education website:

```bash
# Scrape Czech scholarship data
make scrape-czech

# Clean scraped data
make clean-data

# Scrape all available countries (currently only Czech)
make scrape-all
```

The scraped data will be saved in the `data/` directory as JSON files with timestamps.

## Next Steps

1. ✅ Set up database models and migrations
2. ✅ Implement web scraping for Czech scholarships
3. Build RAG pipeline with vector database
4. Create AI assistant endpoints
5. Add user authentication and sessions
6. Build frontend interface

## Troubleshooting

- If containers fail to start, check if ports 8000, 5432, and 5050 are available
- Ensure your GROQ API key is properly set in the .env file
- Check Docker logs: `docker-compose logs app`
