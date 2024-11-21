# The Joy of Painting API

## Description

A Flask-based API that allows users to filter through Bob Ross's "The Joy of Painting" episodes based on colors used, subjects painted, and broadcast months.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**

```bash
git clone [repository-url]
cd atlas-the-joy-of-painting-api
```

2. **Install dependencies**

```bash
pip install Flask psycopg2-binary python-dotenv Flask-CORS
```

3. **Environment Configuration**
   Create a `.env` file in the root directory:

```bash
DB_NAME=joy_of_painting
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
```

4. **Database Setup**

```bash
# Create database
psql -U postgres -c "CREATE DATABASE joy_of_painting;"

# Import schema
psql -d joy_of_painting -f schema.sql

# Import data
python3 import_data.py
```

## Usage

1. **Start the server**

```bash
python3 api.py
```

Server will run on `http://localhost:5000`

2. **Example API Calls**

```bash
# Get all episodes using specific colors
curl http://localhost:5000/api/episodes?color=Bright%20Red

# Get episodes with multiple filters
curl http://localhost:5000/api/episodes?color=Bright%20Red&subject=TREE&month=1
```

## API Endpoints

### Get Episodes

`GET /api/episodes`

Parameters:

- `color`: Filter by colors used (can specify multiple)
- `subject`: Filter by subjects painted (can specify multiple)
- `month`: Filter by broadcast month (can specify multiple)
- `filter_type`: 'AND' or 'OR' (default: 'AND')

Example Response:

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
      "subjects": ["TREE", "MOUNTAIN"],
      "colors": ["Bright Red", "Titanium White"]
    }
  ]
}
```

### Get Available Filters

`GET /api/filters`

Returns all available:

- Colors with hex codes
- Subjects with categories
- Months with episodes

## Database Schema

```sql
-- Episodes table
CREATE TABLE Episodes (
    episode_id SERIAL PRIMARY KEY,
    season VARCHAR(10) NOT NULL,
    episode VARCHAR(10) NOT NULL,
    title VARCHAR(100) NOT NULL,
    air_date DATE NOT NULL,
    youtube_src TEXT,
    UNIQUE (season, episode)
);

-- Colors table
CREATE TABLE Colors (
    color_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    hex_code CHAR(7) NULL
);

-- Subjects table
CREATE TABLE Subjects (
    subject_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL
);

-- Relationship tables
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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## Security Notes

- Database credentials should be stored in environment variables
- The `.env` file should never be committed to version control
- This is a development server and should not be used in production without proper security measures

## License

This project is licensed under the MIT License - see the LICENSE file for details.
