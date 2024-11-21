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

CREATE TABLE SpecialGuests (
    guest_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    relation VARCHAR(100) NULL
);

CREATE TABLE Episodes (
    episode_id SERIAL PRIMARY KEY,
    season VARCHAR(10) NOT NULL,
    episode VARCHAR(10) NOT NULL,
    title VARCHAR(100) NOT NULL,
    air_date DATE NOT NULL,
    youtube_src TEXT,
    guest_id INTEGER NULL REFERENCES SpecialGuests(guest_id),
    UNIQUE (season, episode)
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

CREATE INDEX idx_episode_airdate ON Episodes(air_date);
CREATE INDEX idx_episode_title ON Episodes(title);
CREATE INDEX idx_subject_name ON Subjects(name);
CREATE INDEX idx_color_name ON Colors(name);

INSERT INTO Subjects (name, category) VALUES
('MOUNTAIN', 'LANDSCAPE'),
('TREE', 'NATURE'),
('LAKE', 'WATER'),
('CABIN', 'STRUCTURE'),
('SNOW', 'WEATHER'),
('CLOUDS', 'SKY'),
('WATERFALL', 'WATER');

INSERT INTO Colors (name, hex_code) VALUES
('Alizarin Crimson', '#4E1500'),
('Bright Red', '#DB0000'),
('Cadmium Yellow', '#FFEC00'),
('Phthalo Blue', '#0C0040'),
('Prussian Blue', '#021E44'),
('Sap Green', '#0A3410'),
('Titanium White', '#FFFFFF'),
('Van Dyke Brown', '#221B15'),
('Yellow Ochre', '#C79B00'),
('Midnight Black', '#000000'),
('Dark Sienna', '#5F2E1F'),
('Indian Yellow', '#FFB800');