from config_lib import ConfigManager

# 🔧 Custom schema for configuration validation
custom_schema = {
    "database": {
        "type": dict,
        "required": True,
        "schema": {
            "host": {"type": str, "required": True},
            "port": {"type": int, "required": True, "default": 30},
            "user": {"type": str, "required": True},
        },
    },
    "logging": {
        "type": dict,
        "required": True,
        "schema": {
            "level": {"type": str, "required": True},
        },
    },
    "network": {
        "type": dict,
        "required": True,
        "schema": {
            "retries": {"type": int, "required": True},
        },
    },
}


def example_valid_config():
    try:
        # To start using ConfigManager, create an instance of this class.
        # You need to provide the location of the configuration file to the class.
        manager = ConfigManager("example.yaml")
    except Exception as e:
        print(e)  # If an error occurs while parsing the file, the program will notify you.
        return

    try:
        print("\n------------------ Example: Basic Usage ------------------")

        # Now you can try to display the contents of the configuration file.
        print("\n🔹 Example of configuration output:")
        manager.print_config()

        # You can also specify which fields should be masked when displayed.
        print("\n🔹 Example of configuration output with masking:")
        manager.print_config(["database.password"])

        # Now you can try to validate your configuration against the default schema.
        print("\n✅ Example of a successful validation result:")
        manager.validate()

        # You can also get a dictionary of the current config for further use.
        config = manager.get_config()
        print("\n📦 Output of the previously saved config:")
        print(config)
    except (ValueError, TypeError) as e:
        print(e)


def example_custom_schema():
    try:
        # You can also pass a custom validation schema when creating an instance of the class.
        manager = ConfigManager("example.ini", custom_schema)
    except Exception as e:
        print(e)
        return

    try:
        print("\n\n------------------ Example: Custom Schema ------------------")

        # We can try performing validation according to the provided schema.
        print("\n✅ Example of successful validation according to the provided schema:")
        manager.validate()
    except (ValueError, TypeError) as e:
        print(e)


def example_extra_field():
    try:
        # Let's create a class with an invalid file.
        manager = ConfigManager("example_extra_field.json")
    except Exception as e:
        print(e)
        return

    try:
        print("\n\n------------------ Example: Extra Fields ------------------")

        # The validator will notify us that an extra field was detected in the database object.
        print("\n❌ Example of failed validation result (extra field):")
        manager.validate()
    except (ValueError, TypeError) as e:
        print(e)


def example_missing_field():
    try:
        # Let's create a class with an invalid file.
        manager = ConfigManager("example_missing_field.json")
    except Exception as e:
        print(e)
        return

    try:
        print("\n\n------------------ Example: Missing Fields ------------------")

        # The current file is missing the port field in the database object.
        print("\n❌ Example of failed validation result (missing field):")
        manager.validate()
    except (ValueError, TypeError) as e:
        print(e)


def example_apply_defaults():
    try:
        manager = ConfigManager("example_missing_field.json")
    except Exception as e:
        print(e)
        return

    try:
        print("\n\n------------------ Example: Applying Defaults ------------------")

        # But we can use the function to fill in default values from the schema.
        print("\nℹ️ Filling missing fields with defaults...")
        manager.apply_defaults()

        # Now let's try to run the validation.
        print("✅ Example of successful validation after filling in default values:")
        manager.validate()
    except (ValueError, TypeError) as e:
        print(e)


def example_mongodb_operations():
    try:
        manager = ConfigManager("example.toml")
        # When creating an instance of the class, you may omit specifying the file location.
        manager2 = ConfigManager()
    except Exception as e:
        print(e)
        return

    try:
        print("\n\n------------------ Example: MongoDB Usage ------------------")

        # You can save the current config to the database MongoDB.
        # For this, you need to provide the config name, the connection URI, and the db name.
        print("\n💾 Saving the config in the database:")
        manager.save_to_db(
            name="production_config",
            mongo_uri="mongodb://admin:secret@localhost:27017",
            db_name="myconfigs"
        )

        # Let's try using the second class to retrieve the config from the database.
        print("\n📥 Loading the config from the database:")
        manager2.load_from_db(
            name="production_config",
            mongo_uri="mongodb://admin:secret@localhost:27017",
            db_name="myconfigs"
        )
        print("🔹 Output of the config loaded from the database:")
        manager2.print_config()

        # Now let's try deleting the value from the database.
        print("\n🗑️ Deleting the config from the database:")
        manager2.delete_from_db(
            name="production_config",
            mongo_uri="mongodb://admin:secret@localhost:27017",
            db_name="myconfigs"
        )

        # Now, when we try to get the config from the database, we will receive an error message.
        print("\n❌ Failed attempt to load from the database:")
        manager2.load_from_db(
            name="production_config",
            mongo_uri="mongodb://admin:secret@localhost:27017",
            db_name="myconfigs"
        )

    except (ValueError, TypeError) as e:
        print(e)


if __name__ == "__main__":
    example_valid_config()
    example_custom_schema()
    example_extra_field()
    example_missing_field()
    example_apply_defaults()
    example_mongodb_operations()
