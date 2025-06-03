# config_lib

## Description
config_lib is a flexible Python-library for loading, validating, and managing 
configuration files in various formats. It supports JSON, YAML, INI, and TOML formats, 
and includes features like schema validation, default values, secure printing, and MongoDB 
persistence.

## Features
- Unified interface for parsing JSON, YAML, INI, and TOML.
- Schema-based validation with nested structures.
- Default value filling.
- Secure config printing with masked fields.
- MongoDB integration for saving/loading configs.
- Custom schema support.

## Installation
First, clone the repository and navigate into the project directory:
```
git clone https://github.com/dk872/config-lib
```
```
cd config-lib
```

Install the library and required dependencies using pip:
```
pip install .
```

Now you can import the main ConfigManager class in your projects as follows:
```py
from config_lib import ConfigManager
```

## Configuring MongoDB integration
If you want to use a MongoDB database with the library, you need to install and configure it beforehand.

- Run MongoDB **locally**:
  - Install MongoDB on your computer.
  - After installation, run the MongoDB server by executing this сommand:
    ```
    mongod
    ```
    This starts the MongoDB server locally on the default port (27017).
- Alternatively, you can use **Docker** to run MongoDB:
  - Make sure you have Docker installed.
  - Enter the following command to run a MongoDB container on port 27017 and set 
    the root login to *admin* and the root password to *secret* (you can change these values):
    ```
    docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret mongo
    ```
  - Now you can access the database using the URI:
    ```
    mongodb://admin:secret@localhost:27017
    ```

## Examples of using the library
The ConfigManager class provides a unified interface for loading, validating, manipulating, 
and persisting configuration files across different formats (JSON, YAML, INI, TOML). It also supports 
working with MongoDB for configuration persistence.

### Creating an instance of the class
When creating an instance the class, you can pass the path to the configuration file:
```py
try:
    manager = ConfigManager("example.json")
except Exception as e:
    print(e)
```
When creating an instance of the class, the library will automatically attempt to parse the file.


You can also provide a custom schema for validation:
```py
try:
    manager = ConfigManager("example.json", custom_schema)
except Exception as e:
    print(e)
```

You don’t need to specify the file location if you’re going to use MongoDB:
```py
manager = ConfigManager()
```

### validate()
This function validates the currently loaded configuration against the schema.
Raises an exception if the configuration is invalid or missing.

After successfully loading the config, you can use this function as follows:
```py
try:
   manager.validate()
except (ValueError, TypeError) as e:
   print(e)
```

### get_config()
This function returns the internal configuration as a dictionary.
Useful for accessing the parsed data programmatically.

After successfully loading the config, you can use this function as follows:
```py
config = manager.get_config()
```

### print_config()
This function prints the configuration.

After successfully loading the config, you can use this function as follows:
```py
manager.print_config()
```

You can also specify which field values should be masked with '***' when displayed:
```py
manager.print_config(["database.password"])
```

### apply_defaults()
This function fills in any missing fields in the loaded configuration with default 
values defined in the schema.

After successfully loading the config, you can use this function as follows:
```py
try:
   manager.apply_defaults()
except (ValueError, TypeError) as e:
   print(e)
```

### save_to_db()
This function saves the current configuration to a MongoDB collection.

The function can accept the following parameters:
- name - identifier under which the config will be stored.
- mongo_uri - MongoDB connection string.
- db_name - name of the MongoDB database.
- collection_name - optional name of the collection (default is "configs")

After successfully loading the config, you can use this function as follows:
```py
try:
   manager.save_to_db(
    name="production_config",
    mongo_uri="mongodb://admin:secret@localhost:27017",
    db_name="myconfigs"
)
except (ValueError, TypeError) as e:
   print(e)
```

### load_from_db()
This function loads a configuration from MongoDB by its name and stores it internally.
Same parameters as save_to_db.

You can use this function as follows:
```py
try:
   manager.load_from_db(
    name="production_config",
    mongo_uri="mongodb://admin:secret@localhost:27017",
    db_name="myconfigs"
)
except (ValueError, TypeError) as e:
   print(e)
```

### delete_from_db()
This function deletes a stored configuration from MongoDB by its name.
Same parameters as save_to_db.

You can use this function as follows:
```py
try:
   manager.delete_from_db(
    name="production_config",
    mongo_uri="mongodb://admin:secret@localhost:27017",
    db_name="myconfigs"
)
except (ValueError, TypeError) as e:
   print(e)
```

### save_to_file()
This function saves the current config to a file of the specified format (JSON, YAML, TOML, INI).
A new file will be created in the same directory as the program that calls this function.

You can use this function as follows:
```py
try:
   manager.save_to_file("out.yaml")
except (ValueError, TypeError) as e:
   print(e)
```

### Running the demo file
You can review the prepared file with usage examples.
Before running the demo file, be sure to start the MongoDB container with the command:
```
docker run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret mongo
```

To run demo file, follow these instructions:
- Navigate into the `example` directory:
```
cd example
```
- Run the example file:
  - **On Linux:**
    - Make sure you have Python installed. You can check with:
      ```
      python3 --version
      ```
    - Run the program:
      ```
      python3 example_main.py
      ```

  - **On Windows:**
    - Make sure Python is installed and added to the system PATH. You can check with:
      ```
      python --version
      ```
      - Run the program:
      ```
      python example_main.py
      ```
    
### Running the tests
This project contains a set of various tests to verify the functionality of the library. 
You can find them in the `tests` directory.

To run the tests, follow these instructions:
- Make sure you are in the root directory of the repository.
- Install the required dependencies to run the tests:
    ```
    pip install -r requirements.txt
    ```
- Now you can run the tests using the following command:
    ```
    pytest tests
    ```
  
## Appendices
### Design document
[At the link](https://docs.google.com/document/d/1z7FNHYIxTzVIjSywQnOcPnc9AAUoxCI3fU7kj6e8Jec), you can review the design document of our project, 
which details the program’s functionality, library architecture, 
and business logic scenarios.

### Authors info

- Dmytro Kulyk, a student of group IM-32
- Samoilenko Mariia, a student of group IM-32
- Kaliberda Anton, a student of group IM-32
- Vakhnina Yulianna, a student of group IM-32
