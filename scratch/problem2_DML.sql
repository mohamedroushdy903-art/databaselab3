-- =========================================================================
-- Alexandria National University (ANU) - Faculty of Engineering
-- Course: Introduction to Database Systems (Fall 2026)
-- Lab 3: Foreign Keys and Simple SQL
-- PART II · PROBLEM 2 · Library: Books and Authors
-- Script: problem2_DML.sql (Data Manipulation Language - Seed Data)
-- =========================================================================

USE library;

-- -------------------------------------------------------------------------
-- 1. Seed Authors (4 real authors - exceeds minimum requirement of 3)
-- -------------------------------------------------------------------------
INSERT INTO author (author_id, name, country, photo_path) VALUES
(1, 'George Orwell', 'United Kingdom', 'static/uploads/authors/george_orwell.jpg'),
(2, 'Jane Austen', 'United Kingdom', 'static/uploads/authors/jane_austen.jpg'),
(3, 'Arthur Conan Doyle', 'United Kingdom', 'static/uploads/authors/arthur_conan_doyle.jpg'),
(4, 'Naguib Mahfouz', 'Egypt', 'static/uploads/authors/naguib_mahfouz.jpg');

-- -------------------------------------------------------------------------
-- 2. Seed Books (8 real books - exceeds minimum requirement of 6)
-- All books are linked to valid authors via author_id.
-- Note: Prices are sample academic dataset values in USD, stored as DECIMAL(10,2).
-- -------------------------------------------------------------------------
INSERT INTO book (book_id, title, price, author_id, cover_path) VALUES
(1, 'Nineteen Eighty-Four', 15.99, 1, 'static/uploads/books/1984.jpg'),
(2, 'Animal Farm', 10.50, 1, 'static/uploads/books/animal_farm.jpg'),
(3, 'Pride and Prejudice', 12.99, 2, 'static/uploads/books/pride_and_prejudice.jpg'),
(4, 'Sense and Sensibility', 11.50, 2, 'static/uploads/books/sense_and_sensibility.jpg'),
(5, 'A Study in Scarlet', 9.99, 3, 'static/uploads/books/a_study_in_scarlet.jpg'),
(6, 'The Sign of the Four', 10.25, 3, 'static/uploads/books/sign_of_the_four.jpg'),
(7, 'Palace Walk', 14.50, 4, 'static/uploads/books/palace_walk.jpg'),
(8, 'The Thief and the Dogs', 12.00, 4, 'static/uploads/books/thief_and_dogs.jpg');
