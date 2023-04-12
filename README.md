# NLP-from-scratch
This contains NLP process from scratch. This was the assignment project from web data process course from Vrije Universiteit Amsterdam alone.

# Introduction
The goal of the assignment is to implement a program that recognize, and link entities mentioned in web pages.

# Pre-Process
## Extracting raw data from HTML and Getting Named Entity Recognition.
First problem of pre-process is to get the raw texts from html and refine them with provided WARC file. Once WARC files were extracted, I removed not related tags such as headers, styles, etc using the package BeautifulSoup to refine the raw text. Second problem is to do Name Entity Recognition (NER) with the refined text. The package NLTK and SpaCy were used. SpaCy provided tokenization, stopword removal, POS tags, and parsing and I mostly relied on these functions to get named entities.

# Entity Linking
Entity linking usually requires three big steps: candidate entity generation, candidate entity ranking, and unlinkable candidate entity. Instead of following traditional linking methods, I tried to think about efficient and creative ways to achieve the linking part.


## Candidate Entity Generation
Candidate entity generation is the first step to Named Entity Linking. Since dictionary-based method mentioned on the starter_code requires 80GB entity lists from the official Wikipedia website, I decided to use the ‘search engine method’ which does not require any offline documentation. Package Wikipedia was used to get lists of entities that show up when you click the search button on the website.


## Candidate Entity Ranking
The ranking is necessary to decide which candidate entity is the right entity to link. I got an idea from the 'vectorization comparison method' to rank them. I extracted all the lists of candidate entities from the previous step and get all the entities (I wrote them as ‘sub- entities’ for better clarification) of the Wikipedia website of candidate entities. And I compared the sub-entities of original entity and sub-entities of candidate entity by counting how much they overlap by vector formats. I assumed that if the sub-entities of the Wikipedia website of candidate entity match a lot of sub-entities of the Wikipedia of the original entity, then they are the same entity in high chance. Furthermore, I scored them
based on fixed size of original entity because size of sub-entities could be various and
different, and it could influence the score. The equation of score is followed as:
Score= ∑(Sub−entitiesoforiginalentity & Sub−entitiesofcandidateentity)/∑ Sub−entities of original entity

## Unlinkable Candidate Entities
While checking the candidate results and linked candidates, there were cases that some entities don't have suitable candidate entities. I decided to ignore the problem and assume that candidate entities are empty and not possible to link.
