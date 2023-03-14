import sys
import json
import os

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

    # Extract index names
    indexes = []
    for line in table_def.split("\n"):
        line = line.strip()
        if line.startswith("CREATE INDEX"):
            index_name = line.split(" ")[2]
            indexes.append(index_name)

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

    for index_name in indexes:
        index = {
            "key": index_name,
            "type": "unique",
            "status": "available",
            "attributes": [],
            "orders": []
        }
        json_schema["indexes"].append(index)

    # Append JSON schema to list of collections
    collections.append(json_schema)

# Create master JSON schema with list of collections
master_schema = {
    "projectId": "",
    "projectName": "",
    "collections": collections
}

# Write master JSON schema to file
output_file = f"{input_file.split('.')[0]}.json"
with open(output_file, "w") as f:
    json.dump(master_schema, f, indent=4)
    
with open(output_file, 'r') as f:
    data = json.load(f)

for collection in data['collections']:
    attributes = collection['attributes']
    collection['attributes'] = [attr for attr in attributes if attr['key'] not in ['created_at', 'last_update', 'ID',  'FOREIGN']]

with open(output_file, 'w') as f:
    json.dump(data, f, indent=4)

# Load the original JSON schema
with open("appwrite.json", "r") as f:
    original_schema = json.load(f)

# Load the new JSON schema
with open(output_file, "r") as f:
    new_schema = json.load(f)

# Merge the collections
original_collections = original_schema["collections"]
new_collections = new_schema["collections"]
merged_collections = original_collections + [new_collection for new_collection in new_collections if new_collection["name"] not in [collection["name"] for collection in original_collections]]

# Update the original schema with the merged collections
original_schema["collections"] = merged_collections

# Write the updated schema to file
with open("appwrite.json", "w") as f:
    json.dump(original_schema, f, indent=4)

# Delete the new schema file
os.remove("new_appwrite.json")

print(f"Merged JSON schema written to {output_file}")