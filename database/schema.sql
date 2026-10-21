-- SBI-ADS — MySQL schema (optional)
--
-- The application creates this table automatically on startup for both
-- SQLite (default) and MySQL. Run this script manually only if your
-- MySQL user lacks CREATE privileges and a DBA must provision it.
--
-- Activate MySQL with:
--   SBI_DB_DRIVER=mysql SBI_DB_HOST=... SBI_DB_USER=... SBI_DB_PASSWORD=... SBI_DB_NAME=sbi_ads

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id        INT AUTO_INCREMENT PRIMARY KEY,
    file_name         VARCHAR(255) NOT NULL,
    file_path         VARCHAR(512) NOT NULL,
    file_type         VARCHAR(16)  NOT NULL,
    upload_date       DATETIME DEFAULT CURRENT_TIMESTAMP,
    row_count         INT DEFAULT 0,
    column_count      INT DEFAULT 0,
    processing_status VARCHAR(32) DEFAULT 'Uploaded'
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;
