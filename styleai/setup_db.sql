CREATE DATABASE IF NOT EXISTS styleai;
USE styleai;
 
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100)        NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255)        NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
CREATE TABLE IF NOT EXISTS preferences (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT UNIQUE NOT NULL,
    metal           VARCHAR(50)  DEFAULT 'Gold',
    earring_style   VARCHAR(50)  DEFAULT 'Any',
    styling_level   VARCHAR(50)  DEFAULT 'Minimal',
    occasion        VARCHAR(50)  DEFAULT 'Casual',
    budget          VARCHAR(50)  DEFAULT '₹500–₹1,500',
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    earrings_budget INT          DEFAULT 500,
    earrings_source VARCHAR(20)  DEFAULT 'both',
    necklace_budget INT          DEFAULT 1000,
    necklace_source VARCHAR(20)  DEFAULT 'both',
    bracelet_budget INT          DEFAULT 700,
    bracelet_source VARCHAR(20)  DEFAULT 'both',
    ring_budget     INT          DEFAULT 500,
    ring_source     VARCHAR(20)  DEFAULT 'both',
    handbag_budget  INT          DEFAULT 2000,
    handbag_source  VARCHAR(20)  DEFAULT 'both',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
 
CREATE TABLE IF NOT EXISTS accessories (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT          NOT NULL,
    type         VARCHAR(50)  NOT NULL,
    image_url    VARCHAR(500) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    color        VARCHAR(100),
    material     VARCHAR(100),
    style        VARCHAR(100),
    occasion     VARCHAR(100),
    name         VARCHAR(255),
    metal_type   VARCHAR(30),
    earring_type VARCHAR(30),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
 
CREATE TABLE IF NOT EXISTS analysis_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    mood        VARCHAR(50),
    summary     TEXT,
    result_json JSON,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_url   TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
 
CREATE TABLE IF NOT EXISTS user_preference_learning (
    user_id         INT PRIMARY KEY,
    gold_count      INT DEFAULT 0,
    silver_count    INT DEFAULT 0,
    rose_gold_count INT DEFAULT 0,
    stud_count      INT DEFAULT 0,
    hoop_count      INT DEFAULT 0,
    long_count      INT DEFAULT 0,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
 
SHOW TABLES;