# Glossary

This glossary organizes SQL-related terms used in this tutorial in alphabetical order. Each term includes links to related lessons for deeper study.

---

## A

### Aggregate Function
A function that computes a single result from multiple rows. Includes COUNT, SUM, AVG, MIN, MAX, etc. Related lesson: [Lesson 4](../beginner/04-aggregates.md)

### Alias
A temporary name assigned to a table or column. Uses the AS keyword and improves query readability. Related lesson: [Lesson 1](../beginner/01-select.md)

---

## C

### CASE (Conditional Expression)
An expression in SQL that returns different values based on conditions. Similar to if-else in programming. Related lesson: [Lesson 7](../beginner/07-case.md)

### COMMIT
A command that finalizes all changes made within a transaction and permanently saves them. Related lesson: [Lesson 17](../intermediate/17-transactions.md)

### Composite Index
An index created by combining two or more columns. Column order has a significant impact on performance. Related lesson: [Lesson 23](../advanced/23-indexes.md)

### Concurrency
A situation where multiple users or processes access and operate on a database simultaneously. Data integrity is ensured through transactions and locks. Related lesson: [Appendix - Concurrency](dba-concurrency.md)

### Constraint
A rule that ensures data integrity in a table. Includes PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK, etc. Related lesson: [Lesson 16](../intermediate/16-ddl.md)

### Correlated Subquery
A subquery that references columns from the outer query and executes repeatedly for each row of the outer query. Related lesson: [Lesson 10](../intermediate/10-subqueries.md)

### Covering Index
An index that includes all columns needed by a query, allowing results to be returned from the index alone without accessing the table. Related lesson: [Lesson 23](../advanced/23-indexes.md)

### CTE (Common Table Expression)
A temporary named result set using the WITH clause. Improves query readability and reusability. Recursive CTEs can also represent hierarchical structures. Related lesson: [Lesson 19](../advanced/19-cte.md)

### Cursor
A database object that allows processing a query result set one row at a time sequentially. Related lesson: [Lesson 26](../advanced/26-stored-procedures.md)

---

## D

### DCL (Data Control Language)
A category of SQL statements that grant (GRANT) or revoke (REVOKE) user permissions. Related lesson: [Appendix - Security](dba-security.md)

### DDL (Data Definition Language)
A category of SQL statements that create (CREATE), alter (ALTER), or drop (DROP) database structures such as tables, indexes, and views. Related lesson: [Lesson 16](../intermediate/16-ddl.md)

### Deadlock
A state where two transactions are each waiting for the lock held by the other, resulting in indefinite waiting. Related lesson: [Appendix - Concurrency](dba-concurrency.md)

### DELETE
A DML statement that removes rows from a table matching a condition. Using it without a WHERE clause deletes all rows. Related lesson: [Lesson 15](../intermediate/15-dml.md)

### DISTINCT
A keyword that removes duplicate rows from SELECT results and returns only unique values. Related lesson: [Lesson 1](../beginner/01-select.md)

### DML (Data Manipulation Language)
A category of SQL statements that insert (INSERT), query (SELECT), update (UPDATE), or delete (DELETE) data in tables. Related lesson: [Lesson 15](../intermediate/15-dml.md)

---

## E

### EXCEPT (Set Difference)
A set operator that excludes rows from the first query result that are present in the second query result. Related lesson: [Lesson 14](../intermediate/14-union.md)

### EXISTS
A conditional operator that returns TRUE if the subquery returns one or more rows. Used with correlated subqueries to check for existence. Related lesson: [Lesson 20](../advanced/20-exists.md)

---

## F

### Filtering (WHERE)
A clause that specifies conditions to include only desired rows in the result. Uses comparison operators, logical operators, LIKE, IN, BETWEEN, etc. Related lesson: [Lesson 2](../beginner/02-where.md)

### Foreign Key
A column that references the primary key of another table. Defines relationships between tables and ensures referential integrity. Related lesson: [Lesson 16](../intermediate/16-ddl.md)

### Function
A database object that accepts input, performs calculations, and returns a result. Divided into built-in functions and user-defined functions. Related lesson: [Lesson 13](../intermediate/13-utility-functions.md)

---

## G

### GROUP BY
A clause that groups rows with identical values together, enabling aggregate functions to be applied. Related lesson: [Lesson 5](../beginner/05-group-by.md)

---

## H

### HAVING
A clause that applies conditions to grouped results from GROUP BY. While WHERE filters individual rows, HAVING filters groups. Related lesson: [Lesson 5](../beginner/05-group-by.md)

---

## I

### Index
A data structure for fast data retrieval in a table. Like a book's index, it helps quickly locate desired data. Related lesson: [Lesson 23](../advanced/23-indexes.md)

### INNER JOIN
A join method that includes only rows satisfying the join condition from both tables. Non-matching rows are excluded. Related lesson: [Lesson 8](../intermediate/08-inner-join.md)

### INSERT
A DML statement that adds new rows to a table. Related lesson: [Lesson 15](../intermediate/15-dml.md)

### Isolation Level
A level that determines how much concurrently executing transactions affect each other's work. There are 4 levels from READ UNCOMMITTED to SERIALIZABLE. Related lesson: [Lesson 17](../intermediate/17-transactions.md)

---

## J

### JOIN
An operation that connects two or more tables based on common columns to produce a single result set. Related lesson: [Lesson 8](../intermediate/08-inner-join.md)

### JSON
JavaScript Object Notation. Modern RDBMSs provide capabilities to store and query JSON data. Related lesson: [Lesson 25](../advanced/25-json.md)

---

## N

### Normalization
A design technique that splits tables to reduce data redundancy and improve integrity. Ranges from 1NF to 5NF. Related lesson: [Lesson 0](../beginner/00-introduction.md)

### NULL
A special marker indicating that a value does not exist or is unknown. Different from 0 or an empty string; compared using IS NULL / IS NOT NULL. Related lesson: [Lesson 6](../beginner/06-null.md)

---

## O

### ORDER BY (Sorting)
A clause that sorts query results in ascending (ASC) or descending (DESC) order based on specified columns. Related lesson: [Lesson 3](../beginner/03-sort-limit.md)

### Outer JOIN
A join method that includes non-matching rows in the result. There are three types: LEFT, RIGHT, and FULL. Related lesson: [Lesson 9](../intermediate/09-left-join.md)

---

## P

### Paging (Pagination)
A technique that retrieves large result sets in fixed-size portions. Implemented by combining LIMIT and OFFSET. Related lesson: [Lesson 3](../beginner/03-sort-limit.md)

### Parameter
An input or output value passed to a stored procedure or function. Types include IN, OUT, and INOUT. Related lesson: [Lesson 26](../advanced/26-stored-procedures.md)

### Partial Index
An index created only for rows satisfying a WHERE condition. Reduces index size and improves performance for specific queries. Related lesson: [Lesson 23](../advanced/23-indexes.md)

### Primary Key
A column or combination of columns that uniquely identifies each row in a table. Does not allow NULL and cannot be duplicated. Related lesson: [Lesson 16](../intermediate/16-ddl.md)

---

## Q

### Query
An SQL statement requesting information from a database. In the narrow sense, it refers to a SELECT statement. Related lesson: [Lesson 1](../beginner/01-select.md)

### Query Execution Plan
Information showing the strategy chosen by the database engine to execute an SQL statement. Checked using the EXPLAIN command. Related lesson: [Lesson 23](../advanced/23-indexes.md)

---

## R

### ROLLBACK
A command that cancels all changes made within a transaction and reverts to the state before the transaction began. Related lesson: [Lesson 17](../intermediate/17-transactions.md)

---

## S

### Schema
The blueprint that defines a database's structure. Refers to the overall structure including tables, columns, data types, constraints, and relationships. Related lesson: [Lesson 0](../beginner/00-introduction.md)

### SELF JOIN
A technique that joins a table with itself. Used to express relationships between rows within the same table. Related lesson: [Lesson 21](../advanced/21-self-cross-join.md)

### Sequence
A database object that generates automatically incrementing unique numbers. Primarily used for generating primary key values. Related lesson: [Lesson 16](../intermediate/16-ddl.md)

### Stored Procedure
A bundle of SQL statements stored in the database and callable by name. Can include logic such as variables, conditional branching, and loops. Related lesson: [Lesson 26](../advanced/26-stored-procedures.md)

### Subquery
A SELECT statement embedded within another SQL statement. Can be used in WHERE, FROM, SELECT clauses, etc. Related lesson: [Lesson 10](../intermediate/10-subqueries.md)

---

## T

### Table
A data storage unit consisting of rows and columns. The core structure of a relational database. Related lesson: [Lesson 0](../beginner/00-introduction.md)

### Transaction
A set of SQL statements grouped as a single logical unit of work. Guarantees atomicity -- either all succeed or all fail. Related lesson: [Lesson 17](../intermediate/17-transactions.md)

### Trigger
A stored procedure that executes automatically when INSERT, UPDATE, or DELETE occurs on a specific table. Related lesson: [Lesson 24](../advanced/24-triggers.md)

---

## U

### UNION (Set Union)
A set operator that combines results from two or more SELECT statements into one. UNION removes duplicates while UNION ALL allows them. Related lesson: [Lesson 14](../intermediate/14-union.md)

### UPDATE
A DML statement that modifies data in existing rows of a table. Related lesson: [Lesson 15](../intermediate/15-dml.md)

---

## V

### View
A database object that stores a SELECT statement and allows it to be used like a virtual table. Does not store data directly. Related lesson: [Lesson 22](../advanced/22-views.md)

---

## W

### Wildcard
A special character used for pattern matching with the LIKE operator. `%` represents any string, and `_` represents any single character. Related lesson: [Lesson 2](../beginner/02-where.md)

### Window Function
A function that performs calculations over a group of rows without reducing the result rows, appending the calculation result to each row. Used with the OVER clause. Related lesson: [Lesson 18](../advanced/18-window.md)
