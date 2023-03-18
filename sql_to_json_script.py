import sys
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} input_sql_file")
    sys.exit(1)

input_file = sys.argv[1]

with open(input_file, "r") as f:
    sql = f.read()

# Split SQL file into individual table definitions
table_defs = sql.split("CREATE TABLE")

# Remove first element of list since it is not a table definition
table_defs.pop(0)

# Initialize list of collections
collections = []

# Iterate over table definitions and generate JSON schema for each table
for table_def in table_defs:
    # Extract table name
    table_name = table_def.split("(")[0].strip()

    # Extract column names and data types
    columns = []
    for line in table_def.split("\n"):
        line = line.strip()
        if line.startswith("id"):
            continue
        if line.startswith("CONSTRAINT"):
            continue
        if line.startswith(")"):
            break
        parts = line.split(" ")
        column_name = parts[0].strip()
        data_type = parts[1].strip()
        not_null = "NOT NULL" in line
        columns.append((column_name, data_type, not_null))

    # Extract index names and column names
    indexes = []
    indexed_columns = []
    for line in table_def.split("\n"):
        line = line.strip()
        if line.startswith("CREATE INDEX"):
            index_name = line.split(" ")[2]
            index_columns = line.split("(")[1].split(")")[0].split(",")
            index_columns = [c.strip() for c in index_columns]
            indexes.append((index_name, index_columns, 'key'))
            indexed_columns += index_columns
        if line.startswith("CREATE UNIQUE INDEX"):
            index_name = line.split(" ")[3]
            index_columns = line.split("(")[1].split(")")[0].split(",")
            index_columns = [c.strip() for c in index_columns]
            indexes.append((index_name, index_columns, 'unique'))
            indexed_columns += index_columns



    # Generate JSON schema
    json_schema = {
        "$id": table_name,
        "$createdAt": "",
        "$updatedAt": "",
        "$permissions": [],
        "databaseId": "",
        "name": table_name,
        "enabled": True,
        "documentSecurity": True,
        "attributes": [],
        "indexes": []
    }

    for column in columns:
        column_name, data_type, not_null = column
        # Check if column name is the same as the table name
        if column_name.lower() == table_name.lower():
            continue
        attribute = {
            "key": column_name,
            "type": "string",
            "status": "available",
            "required": not_null,
            "array": False,
            "size": 255,
            "default": None
        }
        json_schema["attributes"].append(attribute)

    for index_name, index_columns, index_type in indexes:
        index = {
            "key": index_name,
            "type": index_type,
            "status": "available",
            "attributes": index_columns,
            "orders": ["ASC"]
        }
        json_schema["indexes"].append(index)

    # Append JSON schema to list of collections
    collections.append(json_schema)
# Get databaseId from the environment variable
databaseId = os.environ.get("DATABASE_ID")
projectId = os.environ.get("PROJECT_ID")
projectName = os.environ.get("PROJECT_NAME")

# Set the databaseId for each collection
for collection in collections:
    collection["databaseId"] = databaseId
# Create master JSON schema with list of collections
master_schema = {
    "projectId": projectId,
    "projectName": projectName,
    "collections": collections
}

# Write master JSON schema to file
output_file = f"{input_file.split('.')[0]}.json"
with open(output_file, "w") as f:
    json.dump(master_schema, f, indent=4)

with open(output_file, 'r') as f:
    data = json.load(f)

for collection in data['collections']:
    collection.pop("$createdAt", None)
    collection.pop("$updatedAt", None)
    attributes = collection['attributes']
    collection['attributes'] = [attr for attr in attributes if attr['key'] not in ['created_at', 'last_update', 'ID',  'FOREIGN']]

with open(output_file, 'w') as f:
    json.dump(data, f, indent=4)

    
# Print the output file name
print(f"Merged JSON schema written to {output_file}")
