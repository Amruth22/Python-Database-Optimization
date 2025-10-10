# MCQ Questions - Database Optimization

## Instructions
Choose the best answer for each question. Each question has only one correct answer.

---

### Question 1: Connection Pooling
What is the primary benefit of database connection pooling?

A) It encrypts database connections  
B) It reuses existing connections instead of creating new ones, reducing overhead and improving performance  
C) It backs up the database automatically  
D) It compresses database queries  

**Answer: B**

---

### Question 2: Database Index
What is a database index?

A) A backup of the database  
B) A data structure that improves the speed of data retrieval operations on a table  
C) A type of database query  
D) A database user role  

**Answer: B**

---

### Question 3: Query Caching
What does query caching do?

A) Deletes old queries  
B) Stores query results in memory to avoid re-executing the same query  
C) Encrypts queries  
D) Compiles queries  

**Answer: B**

---

### Question 4: EXPLAIN Statement
What does the EXPLAIN statement do in SQL?

A) Executes a query faster  
B) Shows the execution plan and how the database will execute a query  
C) Deletes query results  
D) Creates a backup  

**Answer: B**

---

### Question 5: N+1 Query Problem
What is the N+1 query problem?

A) A syntax error in SQL  
B) Executing N+1 separate queries instead of one optimized query, causing performance issues  
C) Having too many database connections  
D) A database indexing error  

**Answer: B**

---

### Question 6: Index Trade-off
What is a trade-off of adding indexes to database tables?

A) Indexes have no downsides  
B) Indexes speed up reads but slow down writes (INSERT, UPDATE, DELETE)  
C) Indexes make the database smaller  
D) Indexes only work with small tables  

**Answer: B**

---

### Question 7: Cache Invalidation
When should you invalidate a query cache?

A) Never, caches should persist forever  
B) When the underlying data changes to prevent serving stale data  
C) Every second  
D) Only when the server restarts  

**Answer: B**

---

### Question 8: SELECT * Problem
Why is using SELECT * generally discouraged?

A) It's a syntax error  
B) It retrieves all columns even if not needed, wasting bandwidth and memory  
C) It doesn't work with indexes  
D) It's slower to type  

**Answer: B**

---

### Question 9: Connection Pool Size
How should you determine the optimal connection pool size?

A) Always use the maximum possible  
B) Based on application load, concurrent users, and database capacity  
C) Always use exactly 10 connections  
D) Pool size doesn't matter  

**Answer: B**

---

### Question 10: TTL in Caching
What does TTL (Time To Live) mean in query caching?

A) The time it takes to execute a query  
B) How long cached data remains valid before expiring  
C) The database connection timeout  
D) The time to create an index  

**Answer: B**

---

### Question 11: Full Table Scan
What is a full table scan and why is it slow?

A) A security scan of the database  
B) Reading every row in a table to find matches, which is slow for large tables  
C) A backup operation  
D) An index creation process  

**Answer: B**

---

### Question 12: Composite Index
What is a composite index?

A) An index made of multiple materials  
B) An index on multiple columns together  
C) An index that compresses data  
D) A temporary index  

**Answer: B**

---

### Question 13: Query Optimization
Which query is generally faster?

A) SELECT * FROM users WHERE name LIKE '%john%'  
B) SELECT id, name FROM users WHERE name = 'john' (with index on name)  
C) Both are equally fast  
D) Speed depends only on hardware  

**Answer: B**

---

### Question 14: Connection Overhead
Approximately how much time does creating a new database connection typically take?

A) Microseconds (negligible)  
B) Milliseconds to tens of milliseconds (significant overhead)  
C) Several seconds  
D) Minutes  

**Answer: B**

---

### Question 15: Cache Hit Rate
What does a cache hit rate of 80% mean?

A) 80% of queries failed  
B) 80% of requests were served from cache without hitting the database  
C) The cache is 80% full  
D) 80% of data is cached  

**Answer: B**

---

## Answer Key Summary

1. B - Reuse connections for better performance  
2. B - Data structure for faster retrieval  
3. B - Store results to avoid re-execution  
4. B - Shows query execution plan  
5. B - N+1 separate queries instead of one  
6. B - Indexes speed reads, slow writes  
7. B - Invalidate when data changes  
8. B - Retrieves unnecessary columns  
9. B - Based on load and capacity  
10. B - How long cache remains valid  
11. B - Reading every row is slow  
12. B - Index on multiple columns  
13. B - Specific columns with index  
14. B - Milliseconds overhead  
15. B - 80% served from cache  

---

**Total Questions: 15**  
**Topics Covered:** Connection pooling, Database indexes, Query caching, EXPLAIN statement, N+1 problem, Query optimization, Cache invalidation, TTL, Full table scan, Performance trade-offs

**Difficulty Level:** Beginner to Intermediate  
**Passing Score:** 80% (12/15 correct answers)
