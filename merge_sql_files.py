import sys
import re

if len(sys.argv) != 3:
    print("Usage: python merge_sql_files.py <path/to/create_table.sql> <path/to/create_index.sql>")
    sys.exit(1)

table_file_path = sys.argv[1]
index_file_path = sys.argv[2]

with open(table_file_path, "r") as f1, open(index_file_path, "r") as f2:
    # Read the contents of both files
    table_sql = f1.read()
    index_sql = f2.read()

    # Define regular expressions to match CREATE TABLE, CREATE INDEX, and CREATE UNIQUE INDEX statements
    create_table_regex = re.compile(r'^\s*CREATE\s+TABLE\s+\S+\s*\(', re.IGNORECASE | re.MULTILINE)
    create_index_regex = re.compile(r'^\s*CREATE\s+INDEX\s+\S+\s+ON\s+\S+\s*\(', re.IGNORECASE | re.MULTILINE)
    create_unique_index_regex = re.compile(r'^\s*CREATE\s+UNIQUE\s+INDEX\s+\S+\s+ON\s+\S+\s*\(', re.IGNORECASE | re.MULTILINE)

    # Extract the CREATE TABLE, CREATE INDEX, and CREATE UNIQUE INDEX statements using regular expressions
    create_table_statements = create_table_regex.findall(table_sql)
    create_index_statements = create_index_regex.findall(index_sql)
    create_unique_index_statements = create_unique_index_regex.findall(index_sql)



    # Split each file into individual statements and combine them
    table_statements = table_sql.split(';')
    index_statements = index_sql.split(';')
    all_statements = table_statements[:-1] + index_statements[:-1]

    # Define a function to sort statements by type and table name
    def sort_key(statement):
        if "CREATE TABLE" in statement:
            return "a" + re.search(r"\b\S+\b", statement).group(0)
        elif "CREATE UNIQUE INDEX" in statement:
            return "c" + re.search(r"\b\S+\b", statement).group(0)
        else:
            return "b" + re.search(r"\b\S+\b ON (\S+)\b", statement).group(1) + re.search(r"\b\S+\b", statement).group(0)

    # Sort the statements and write them out to a new file
    with open("output.sql", "w") as f:
        for statement in sorted(all_statements, key=sort_key):
            f.write(statement.strip() + ";\n")


with open('output.sql') as f:
    input_sql = f.read()

# Find all CREATE TABLE statements
table_regex = r'CREATE TABLE\s+(\w+)\s+\((.*?)\);'
tables = re.findall(table_regex, input_sql, re.DOTALL)

# Find all CREATE INDEX statements
index_regex = r'CREATE UNIQUE INDEX\s+(\w+)\s+ON\s+(\w+)\s+\((.*?)\);'
indexes = re.findall(index_regex, input_sql, re.DOTALL)

# Rearrange the statements so that each CREATE INDEX statement comes after its corresponding CREATE TABLE statement
output_sql = ''
for table in tables:
    output_sql += f'CREATE TABLE {table[0]} ({table[1]});\n'
    for index in indexes:
        if index[1] == table[0]:
            output_sql += f'CREATE UNIQUE INDEX {index[0]} ON {index[1]} ({index[2]});\n'

# Write the modified SQL to a new file
with open('output.sql', 'w') as f:
    f.write(output_sql)

print("Merged SQL file written to merged_file.sql")
