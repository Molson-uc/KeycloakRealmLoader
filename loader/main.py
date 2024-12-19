import json
import argparse
from dotenv import load_dotenv
from file_reader import FileHandler
from manage_keycloak import KeycloakAdminHandler


def create_roles(file_handler: FileHandler, keycloak_handler: KeycloakAdminHandler):
    roles = file_handler.get_fields("Role", "Role description")
    keycloak_handler.handle_roles(roles, "Role", "Role description")


def create_groups(file_handler: FileHandler, keycloak_handler: KeycloakAdminHandler):

    file_handler.sheet = "Groups"
    groups = file_handler.get_fields("Name", "Description", "Role")

    unique_json = set(json.dumps(d, sort_keys=True) for d in groups)
    unique_groups = [json.loads(js) for js in unique_json]
    keycloak_handler.manage_groups(unique_groups)
    file_handler.sheet = "Roles"
    df_roles = file_handler.get_dataframe()
    file_handler.sheet = "Groups"
    file_handler.dataframe_merge(df_roles, key="Role")
    groups = file_handler.get_fields("Name", "Description", "Role")
    keycloak_handler.manage_groups(groups)


def create_users(file_handler: FileHandler, keycloak_handler: KeycloakAdminHandler):
    file_handler.sheet = "Users"
    users = file_handler.get_fields("Username", "Name", "Group")
    keycloak_handler.manage_users(users)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--groups", help="update groups", action="store_true")
    parser.add_argument("-d", "--delete", help="delete", action="store_true")
    parser.add_argument("-u", "--users", help="update users", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    file_handler = FileHandler("realm.xlsx")
    keycloak_handler = KeycloakAdminHandler()

    if args.groups:
        create_groups(file_handler, keycloak_handler)

    if args.users:
        create_users(file_handler, keycloak_handler)

    if args.delete:
        keycloak_handler.delete_groups()
        keycloak_handler.delete_users()
        keycloak_handler.delete_roles()

    if args.groups == False and args.users == False and args.delete == False:
        create_roles(file_handler, keycloak_handler)
        create_groups(file_handler, keycloak_handler)
        create_users(file_handler, keycloak_handler)


if __name__ == "__main__":
    main()
