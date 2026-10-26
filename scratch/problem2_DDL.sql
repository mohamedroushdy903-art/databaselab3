-- =========================================================================
-- Alexandria National University (ANU) - Faculty of Engineering
-- Course: Introduction to Database Systems (Fall 2026)
-- Lab 3: Foreign Keys and Simple SQL
-- PART II · PROBLEM 2 · Library: Books and Authors
-- Script: problem2_DDL.sql (Data Definition Language)
-- =========================================================================

-- 1. Database Creation (Clean Environment Setup)
-- WARNING: This is a destructive reset script for clean environment evaluation.
-- Do NOT execute this script against an existing populated production database.
DROP DATABASE IF EXISTS library;
CREATE DATABASE library CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE library;

-- 2. Table: AUTHOR (Created FIRST because BOOK has a foreign key referencing AUTHOR)
-- Relational Schema: AUTHOR (author_id, name, country, [photo_path])
-- Requirements:
-- - author_id is the primary key (INT AUTO_INCREMENT).
-- - name and country are mandatory text fields (VARCHAR).
-- - photo_path is the relative path for the bonus portrait image upload.
CREATE TABLE author (
    author_id INT AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    photo_path VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (author_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Table: BOOK (Created SECOND, references AUTHOR.author_id)
-- Relational Schema: BOOK (book_id, title, price, author_id, [cover_path])
-- Requirements:
-- - book_id is the primary key (INT AUTO_INCREMENT).
-- - title is mandatory text (VARCHAR(255)).
-- - price uses MySQL DECIMAL(10, 2) for exact currency precision.
-- - author_id is INT, referencing author(author_id).
-- - ON DELETE CASCADE: When an author is deleted, all books belonging to that
--   author are automatically deleted by MySQL's storage engine.
-- - cover_path is the relative path for the bonus book cover image upload.
CREATE TABLE book (
    book_id INT AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    author_id INT NOT NULL,
    cover_path VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (book_id),
    CONSTRAINT fk_book_author
        FOREIGN KEY (author_id)
        REFERENCES author (author_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
