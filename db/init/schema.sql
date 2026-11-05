-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum for dataset target classification
CREATE TYPE class_category AS ENUM ('whale_species', 'noise');

-- Enum for ML training pipeline partitioning
CREATE TYPE dataset_split AS ENUM ('train', 'validation', 'test', 'unassigned');

-- 1. Class Taxonomy Table (Species & Noise types)
CREATE TABLE species_classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    common_name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(100),
    category class_category NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Hydrophone / Recording Station Metadata
CREATE TABLE audio_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_name VARCHAR(150) NOT NULL,
    latitude NUMERIC(8, 6),
    longitude NUMERIC(9, 6),
    depth_meters NUMERIC(6, 2),
    hardware_info TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Audio File Registry (Points to object storage files)
CREATE TABLE audio_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES audio_sources(id) ON DELETE SET NULL,
    storage_path TEXT NOT NULL UNIQUE, -- e.g., s3://whale-audio-bucket/2024/01/hydrophone_01.wav
    file_format VARCHAR(10) NOT NULL DEFAULT 'wav',
    duration_seconds REAL NOT NULL CHECK (duration_seconds > 0),
    sample_rate_hz INT NOT NULL CHECK (sample_rate_hz > 0),
    channels INT NOT NULL DEFAULT 1 CHECK (channels > 0),
    md5_checksum VARCHAR(32),
    recorded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Audio Clip Annotations (Bounding boxes for AI training)
CREATE TABLE annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audio_file_id UUID NOT NULL REFERENCES audio_files(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES species_classes(id) ON DELETE RESTRICT,
    start_time_seconds REAL NOT NULL CHECK (start_time_seconds >= 0),
    end_time_seconds REAL NOT NULL,
    min_frequency_hz REAL CHECK (min_frequency_hz >= 0),
    max_frequency_hz REAL,
    confidence_score REAL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    split dataset_split NOT NULL DEFAULT 'unassigned',
    annotator_info TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    
    -- Logical Constraints
    CONSTRAINT chk_time_window CHECK (end_time_seconds > start_time_seconds),
    CONSTRAINT chk_freq_window CHECK (max_frequency_hz IS NULL OR max_frequency_hz > min_frequency_hz)
);