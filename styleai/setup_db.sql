-- ─────────────────────────────────────────────────────────────────
--  STYLEAI  —  MySQL Database Setup
--  Run this ONCE to create all the tables you need.
--
--  How to run:
--    1. Open MySQL in terminal:   mysql -u root -p
--    2. Then run this file:       source setup_db.sql
-- ─────────────────────────────────────────────────────────────────

-- Create the database
CREATE DATABASE IF NOT EXISTS styleai;
USE styleai;

-- ── USERS ────────────────────────────────────────────────────────
-- Stores everyone who registers on the app
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100)        NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,   -- UNIQUE means no duplicate emails
    password_hash VARCHAR(255)        NOT NULL,   -- NEVER store plain passwords!
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── PREFERENCES ──────────────────────────────────────────────────
-- One row per user — their saved style settings
CREATE TABLE IF NOT EXISTS preferences (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT UNIQUE NOT NULL,            -- UNIQUE: one preference row per user
    metal         VARCHAR(50)  DEFAULT 'Gold',
    earring_style VARCHAR(50)  DEFAULT 'Any',
    styling_level VARCHAR(50)  DEFAULT 'Minimal',
    occasion      VARCHAR(50)  DEFAULT 'Casual',
    budget        VARCHAR(50)  DEFAULT '₹500–₹1,500',
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    -- ON DELETE CASCADE: if user is deleted, their preferences are deleted too
);

-- ── ACCESSORIES ──────────────────────────────────────────────────
-- Stores each accessory a user adds to their wardrobe
CREATE TABLE IF NOT EXISTS accessories (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    type        VARCHAR(50)  NOT NULL,            -- e.g. Earrings, Watch, Handbag
    image_url   VARCHAR(500) NOT NULL,            -- Cloudinary URL
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── ANALYSIS HISTORY ─────────────────────────────────────────────
-- Saves every outfit analysis so users can look back
CREATE TABLE IF NOT EXISTS analysis_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    mood        VARCHAR(50),                       -- e.g. Boho, Chic, Romantic
    summary     TEXT,                              -- AI's outfit description
    result_json JSON,                              -- full AI response stored as JSON
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
ALTER TABLE accessories
ADD COLUMN color VARCHAR(100);

ALTER TABLE accessories
ADD COLUMN material VARCHAR(100);

ALTER TABLE accessories
ADD COLUMN style VARCHAR(100);

ALTER TABLE accessories
ADD COLUMN occasion VARCHAR(100);

ALTER TABLE accessories
ADD COLUMN name VARCHAR(255);

-- Confirm tables were created
SHOW TABLES;

