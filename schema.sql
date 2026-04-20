-- ============================================================
-- AI Fake Internship & Job Detector — Database Schema (SQLite)
-- This file is used to initialize the job_detector.db
-- ============================================================

-- ──────────────────────────────────
-- Table: users
-- ──────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER      NOT NULL PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(120) NOT NULL,
    email      VARCHAR(180) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ──────────────────────────────────
-- Table: jobs
-- ──────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    id         INTEGER      NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER      NOT NULL,
    job_text   TEXT         NOT NULL,
    scam_score INTEGER      NOT NULL DEFAULT 0,
    result     VARCHAR(20)  NOT NULL DEFAULT 'Safe',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ──────────────────────────────────
-- Table: flags
-- ──────────────────────────────────
CREATE TABLE IF NOT EXISTS flags (
    id          INTEGER      NOT NULL PRIMARY KEY AUTOINCREMENT,
    job_id      INTEGER      NOT NULL,
    flag_reason VARCHAR(255) NOT NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_jobs_user ON jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_result ON jobs(result);
CREATE INDEX IF NOT EXISTS idx_flags_job ON flags(job_id);
