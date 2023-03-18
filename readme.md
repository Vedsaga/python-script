# Expected `.sql` format
```sql
CREATE TABLE type (
  id INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL
);
CREATE UNIQUE INDEX idx_type_name ON type (name);

CREATE TABLE status (
  id INT PRIMARY KEY,
  type_id INT NOT NULL,
  name VARCHAR(50) NOT NULL,
  FOREIGN KEY (type_id) REFERENCES type(id)
);
CREATE UNIQUE INDEX idx_status_type_id_name ON status (type_id, name);
```

So, as we can see the create index command should be below the create create table command.