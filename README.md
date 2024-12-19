# Keycloak Realm User and Role Management

This project is designed to fetch data about users, groups, and roles and then create or update these entities in a Keycloak realm. It aims to streamline the process of synchronizing external data sources with Keycloak's identity and access management system.


## Usage

1. **Run the script:**
   ```bash
   python main.py
   ```

2. **Command-line options:**
   - `--user`: create/update users.
   - `--groups`: create/update groups.
   - `--roles`: create/update roles.
   - `--delete`: delete all parts.
   - Example:
     ```bash
     python main.py
     ```
