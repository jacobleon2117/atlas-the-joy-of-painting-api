# The Joy of Painting API

## Description

A Flask-based API providing programmatic access to Bob Ross's "The Joy of Painting" episodes. Filter through episodes based on colors used, subjects painted, and broadcast months. Access episode details including YouTube links and color palettes.

## Features

- RESTful API endpoints
- Filter episodes by colors, subjects, and months
- Support for AND/OR logic in filters
- Color information with hex codes
- Subject categorization (Landscape, Water, Nature, etc.)
- PostgreSQL database with optimized queries

## Prerequisites

- Python 3.x
- PostgreSQL 14+
- pip (Python package manager)

## Installation

1. **Clone the repository**

```bash
git clone [repository-url]
cd atlas-the-joy-of-painting-api
```

2. **Install dependencies**

```bash
pip install flask psycopg2-binary flask-cors python-dotenv pandas numpy
```

3. **Configure environment**
   Create `.env` file:

```bash
DB_NAME=joy_of_painting
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
```

4. **Database setup**

```bash
# Start PostgreSQL service
brew services start postgresql@14

# Create database
psql postgres -c "CREATE DATABASE joy_of_painting;"

# Import schema and initial data
psql joy_of_painting < schema.sql
python3 import_data.py
```

## Data Files

- `episode_data.txt`: Episode titles and air dates
- `subject_data.csv`: Episode-subject mappings
- `color_data.csv`: Episode-color relationships and YouTube links

## Usage

1. **Start the server**

```bash
python3 app.py
```

Server runs at `http://localhost:5000`

2. **Example API calls**

```bash
# Get all episodes
curl http://localhost:5000/api/episodes

# Filter by color
curl http://localhost:5000/api/episodes?color=Bright%20Red

# Multiple filters
curl http://localhost:5000/api/episodes?subject=TREE&color=Bright%20Red&month=1

# Get available filters
curl http://localhost:5000/api/filters
```

## API Endpoints

### Get Episodes

`GET /api/episodes`

Parameters:

- `color`: Filter by colors (multiple allowed)
- `subject`: Filter by subjects (multiple allowed)
- `month`: Filter by broadcast month (multiple allowed)
- `filter_type`: 'AND' or 'OR' (default: 'AND')

Response:

```json
{
  "total_episodes": 1,
  "episodes": [
    {
      "episode_id": 1,
      "title": "A Walk in the Woods",
      "season": "S01",
      "episode": "E01",
      "air_date": "1983-01-11",
      "youtube_src": "https://youtube.com/...",
      "subjects": ["TREE", "MOUNTAIN"],
      "colors": ["Bright Red", "Titanium White"]
    }
  ],
  "debug": {
    "filters_received": {
      "colors": ["Bright Red"],
      "subjects": ["TREE"],
      "months": [1]
    }
  }
}
```

### Get Filters

`GET /api/filters`

Returns available:

- Colors with hex codes
- Subjects with categories
- Months with episodes
- Example usage

## Database Schema

```sql
CREATE TABLE Episodes (
    episode_id SERIAL PRIMARY KEY,
    season VARCHAR(10) NOT NULL,
    episode VARCHAR(10) NOT NULL,
    title VARCHAR(100) NOT NULL,
    air_date DATE NOT NULL,
    youtube_src TEXT,
    UNIQUE (season, episode)
);

CREATE TABLE Colors (
    color_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    hex_code CHAR(7) NULL
);

CREATE TABLE Subjects (
    subject_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL
);

CREATE TABLE EpisodeSubjects (
    episode_id INTEGER REFERENCES Episodes(episode_id),
    subject_id INTEGER REFERENCES Subjects(subject_id),
    PRIMARY KEY (episode_id, subject_id)
);

CREATE TABLE EpisodeColors (
    episode_id INTEGER REFERENCES Episodes(episode_id),
    color_id INTEGER REFERENCES Colors(color_id),
    PRIMARY KEY (episode_id, color_id)
);
```

## Testing

Run the test suite:

```bash
python3 test_setup.py
```

Tests verify:

- Data file presence and format
- Database table population
- Table relationships
- Query functionality
- Data integrity

## Future Development

1. **Frontend Interface**

   - Interactive color and subject filters
   - Episode gallery with thumbnails
   - Color palette visualization
   - Responsive design

2. **API Enhancements**

   - Advanced search capabilities
   - Statistical analysis endpoints
   - Batch operations
   - Rate limiting
   - Authentication

3. **Data Expansion**
   - Paint technique tracking
   - Episode transcripts
   - Painting difficulty ratings
   - User annotations

## Security Notes

- Store credentials in environment variables
- Never commit `.env` file
- Development server only - not production-ready
- Use proper security measures for deployment

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open Pull Request

## License

MIT License - see LICENSE file for details
