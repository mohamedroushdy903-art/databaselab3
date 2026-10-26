# Image Credits & Public Domain Media Attributions

Alexandria National University (ANU) — Faculty of Engineering  
Introduction to Database Systems — Lab 3 (Fall 2026)  
Part II / Problem 2: Library Database System  

---

## Overview
All author portraits and book cover images included in this project have been sourced from **Wikimedia Commons** and public domain archives, verified for historical accuracy and appropriate licensing. All files are stored locally in the project repository under `static/uploads/authors/` and `static/uploads/books/` to ensure offline reliability without fragile external hotlinks.

---

## 1. Author Portraits

| Author | File Path | Source | License / Public Domain Status |
| :--- | :--- | :--- | :--- |
| **George Orwell** | `static/uploads/authors/george_orwell.jpg` | [Wikimedia Commons: George Orwell Press Photo](https://commons.wikimedia.org/wiki/File:George_Orwell_press_photo.jpg) | Public Domain (Press photograph taken in 1943 by the Branch of the National Union of Journalists) |
| **Jane Austen** | `static/uploads/authors/jane_austen.jpg` | [Wikimedia Commons: Jane Austen 1870 Portrait](https://commons.wikimedia.org/wiki/File:Jane_Austen%2C_from_A_Memoir_of_Jane_Austen_%281870%29.jpg) | Public Domain (Published in 1870 in *A Memoir of Jane Austen* by James Edward Austen-Leigh) |
| **Arthur Conan Doyle** | `static/uploads/authors/arthur_conan_doyle.jpg` | [Wikimedia Commons: Sir Arthur Conan Doyle](https://commons.wikimedia.org/wiki/File:Conan_doyle.jpg) | Public Domain (Studio photograph c. 1914 by Arnold Genthe) |
| **Naguib Mahfouz** | `static/uploads/authors/naguib_mahfouz.jpg` | [Wikimedia Commons: Naguib Mahfouz HR](https://commons.wikimedia.org/wiki/File:Naguib_Mahfouz_HR.jpg) | Wikimedia Commons / CC BY-SA (Historical portrait of Egypt's Nobel laureate in Literature) |

---

## 2. Book Covers

| Book Title | Author | File Path | Source / Design Attribution | License |
| :--- | :--- | :--- | :--- | :--- |
| **Nineteen Eighty-Four** | George Orwell | `static/uploads/books/1984.jpg` | [Wikimedia Commons: 1984 First Edition Cover](https://commons.wikimedia.org/wiki/File:1984_first_edition_cover.jpg) | Public Domain (First UK edition dust jacket, Secker & Warburg, 1949) |
| **Animal Farm** | George Orwell | `static/uploads/books/animal_farm.jpg` | [Wikimedia Commons: Animal Farm 1st Edition](https://commons.wikimedia.org/wiki/File:Animal_Farm_-_1st_edition.jpg) | Public Domain (First UK edition dust jacket, Secker & Warburg, 1945) |
| **Pride and Prejudice** | Jane Austen | `static/uploads/books/pride_and_prejudice.jpg` | [Wikimedia Commons: Hugh Thomson Peacock Cover](https://commons.wikimedia.org/wiki/File:AUSTEN%281894%29_Pride_and_prejudice_%2815811958311%29.jpg) | Public Domain (British Library 1894 Peacock edition illustrated by Hugh Thomson) |
| **Sense and Sensibility** | Jane Austen | `static/uploads/books/sense_and_sensibility.jpg` | [Wikimedia Commons: Sense and Sensibility](https://commons.wikimedia.org/wiki/File:Sense_and_Sensibility_by_Jane_Austen.jpg) | Public Domain (Classic historical edition cover) |
| **A Study in Scarlet** | Arthur Conan Doyle | `static/uploads/books/a_study_in_scarlet.jpg` | [Wikimedia Commons: A Study in Scarlet](https://commons.wikimedia.org/wiki/File:A_Study_in_Scarlet.jpg) | Public Domain (Ward, Lock & Co. historical edition cover) |
| **The Sign of the Four** | Arthur Conan Doyle | `static/uploads/books/sign_of_the_four.jpg` | [Wikimedia Commons: The Sign of Four 1892](https://commons.wikimedia.org/wiki/File:Arthur_Conan_Doyle_-_The_Sign_of_Four%2C_cover_1892.jpg) | Public Domain (Spencer Blackett / George Newnes 1892 cover) |
| **Palace Walk** (*Bayn al-Qasrayn*) | Naguib Mahfouz | `static/uploads/books/palace_walk.jpg` | Custom classic typographic design honoring Naguib Mahfouz's masterpiece | Public Domain / CC0 (Generated in accordance with assignment specification for classic typographic fallback) |
| **The Thief and the Dogs** (*Al-Liss wa al-Kilab*) | Naguib Mahfouz | `static/uploads/books/thief_and_dogs.jpg` | Custom classic typographic design honoring Naguib Mahfouz's psychological drama | Public Domain / CC0 (Generated in accordance with assignment specification for classic typographic fallback) |

---

## 3. Storage Architecture
- Local storage directory for author portraits: `static/uploads/authors/`
- Local storage directory for book covers: `static/uploads/books/`
- All images are locally hosted; the website operates fully offline without any dependence on remote image CDNs.
- Future user uploads via the website form are saved into these exact directories with cryptographically unique UUID filenames to prevent collisions and overwrite risks.
