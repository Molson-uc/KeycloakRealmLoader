import requests
import logging
from keycloak_client import KeycloakClient
from config import Config


class KeycloakAdminHandler:

    def __init__(self) -> None:
        self.__config = Config()
        self.__token_type, self.__access_token = self.__authorize_admin()
        self.__client = KeycloakClient(
            self.__config.host,
            self.__config.realm,
            self.__token_type,
            self.__access_token,
        )
        logging.basicConfig(
            filename="logs.log",
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            level=logging.INFO,
        )
        self.__logger = logging.getLogger(__name__)

    def __authorize_admin(self) -> tuple[str | None, str | None]:
        auth_endpoint = (
            self.__config.host + "/realms/master/protocol/openid-connect/token"
        )
        admin_data = {
            "username": self.__config.admin_name,
            "password": self.__config.admin_password,
            "client_id": "admin-cli",
            "grant_type": "password",
        }

        try:
            response = requests.post(auth_endpoint, data=admin_data)
            response.raise_for_status()
            data = response.json()
            access_token = data["access_token"]
            token_type = data["token_type"]
            return (token_type, access_token)
        except requests.HTTPError as e:
            print(f"HTTP Error: {str(e)}")
        except requests.ConnectionError as e:
            print(f"Connection Error: {str(e)}")
        except requests.RequestException as e:
            print(f"Request Exception: {str(e)}")
        except Exception as e:
            print(f"Exception: {str(e)}")
        return None, None

    def __get_headers(self) -> dict:
        headers = {
            "Authorization": f"{self.__token_type} {self.__access_token}",
            "Content-Type": "application/json",
        }
        return headers

    def __create_object(self, object_data: dict, endpoint: str) -> bool:
        response = self.__client.post(endpoint, object_data)

    def __create_role(self, role_name: str, role_desc: str = "") -> None:
        roles_endpoint = f"/admin/realms/{self.__config.realm}/roles"
        data = {"name": role_name, "description": role_desc}
        self.__create_object(data, roles_endpoint)

    def manage_users(self, users_data: list[dict]) -> None:
        users_endpoint = f"/admin/realms/{self.__config.realm}/users"
        users = self.__get_objects(users_endpoint)
        for user in users_data:
            try:
                self.__process_single_user(user, users, users_endpoint)
            except KeyError as e:
                self.__logger.error(f"Manage users - missing key in data: {str(e)}")
            except ValueError as e:
                self.__logger.error(f"Manage users - data format error: {str(e)}")
            except Exception as e:
                self.__logger.error(f"Manage roles: {str(e)}")

    def __process_single_user(self, user_data: dict, users: list, users_endpoint: str):
        existing_user = next(
            (user for user in users if user["username"] == user_data["Username"]),
            None,
        )

        try:
            firstname, lastname = user_data["Name"].split(" ")
        except KeyError as e:
            self.__logger.error(f"Process user - no key 'Name': {str(e)}")
        except Exception as e:
            self.__logger.error(f"Process user: {str(e)}")

        data = {
            "username": user_data["Username"],
            "firstName": firstname,
            "lastName": lastname,
            "enabled": True,
            "credentials": [
                {
                    "type": "password",
                    "value": "password",
                    "temporary": False,
                }
            ],
        }
        if existing_user:
            user_id = existing_user["id"]
            user_endpoint = users_endpoint + "/" + user_id
            self.__update_object(data, user_endpoint)
        else:
            self.__create_object(data, users_endpoint)
            self.__assign_groups_to_user(user_data, users_endpoint)

    def __assign_groups_to_user(self, user_data: dict, endpoint: str):
        user_id = self.__get_object_id(endpoint, user_data["Username"], "username")
        for role in user_data["Role"]:
            group_name = f'{user_data["Group"]}-{role}'
            self.__update_user_groups(user_id, group_name)

    def manage_groups(self, groups_data: list[dict]) -> None:
        groups_endpoint = f"/admin/realms/{self.__config.realm}/groups"
        groups_list = self.__get_objects(groups_endpoint)
        for group_data in groups_data:
            try:
                self.__process_single_group(group_data, groups_endpoint, groups_list)
            except KeyError as e:
                self.__logger.error(f"Manage group - missing key in data: {str(e)}")
            except ValueError as e:
                self.__logger.error(f"Manage group - data format error: {str(e)}")
            except Exception as e:
                self.__logger.error(f"Manage roles: {str(e)}")

    def __process_single_group(
        self, group_data: dict, groups_endpoint: str, groups_list: list
    ):
        existing_group = next(
            (group for group in groups_list if group["name"] == group_data["Name"]),
            None,
        )
        data = {
            "name": group_data["Name"],
            "attributes": {"name": [group_data["Description"]]},
        }
        if existing_group:
            group_id = existing_group["id"]
            group_endpoint = groups_endpoint + f"/{group_id}"
            self.__update_object(data, group_endpoint)
            try:
                roles = group_data["Role"].split("\n")
                for role in roles:
                    self.__update_assigned_roles(
                        group_endpoint=groups_endpoint,
                        group=data,
                        role=role,
                    )
            except KeyError as e:
                self.__logger.error(f"Process single group - no key: {str(e)}")
            except Exception as e:
                self.__logger.error(f"Process single group: {str(e)}")
        else:
            self.__create_object(data, groups_endpoint)
            try:
                roles = group_data["Role"].split("\n")
                for role in roles:
                    self.__update_assigned_roles(
                        group_endpoint=groups_endpoint,
                        group=data,
                        role=role,
                    )
            except KeyError as e:
                self.__logger.error(f"Process single group - no key: {str(e)}")
            except Exception as e:
                self.__logger.error(f"Process single group: {str(e)}")

    def handle_roles(
        self, roles: list[dict], name_key: str, desc_key: str | None = None
    ) -> None:
        roles_endpoint = f"/admin/realms/{self.__config.realm}/roles"
        roles_list = self.__get_objects(roles_endpoint)
        try:
            for role in roles:
                existed = False
                for role in roles_list:
                    if role["name"] == role[name_key]:
                        existed = True
                        break

                if existed:
                    updated_role = {
                        "name": role["name"],
                        "description": role.get(desc_key, ""),
                    }
                    role_endpoint = (
                        f"/admin/realms/{self.__config.realm}/roles/{role['name']}"
                    )

                    self.__update_object(updated_role, role_endpoint)
                else:
                    data = {
                        "name": role[name_key],
                        "description": role.get(desc_key, ""),
                    }
                    self.__create_object(data, roles_endpoint)
        except KeyError as e:
            self.__logger.error(f"Key Error: {str(e)}")
        except Exception as e:
            self.__logger.error(f"Exception: {str(e)}")

    def delete_groups(self) -> None:
        groups_endpoint = f"/admin/realms/{self.__config.realm}/groups/"
        groups_list = self.__get_objects(groups_endpoint)
        for group in groups_list:
            self.__delete_object(groups_endpoint, group["id"])

    def delete_users(self) -> None:
        users_endpoint = f"/admin/realms/{self.__config.realm}/users/"
        users = self.__get_objects(users_endpoint)
        for user in users:
            self.__delete_object(users_endpoint, user["id"])

    def delete_roles(self) -> None:
        roles_endpoint = f"/admin/realms/{self.__config.realm}/roles"
        roles_list = self.__get_objects(roles_endpoint)
        for role in roles_list:
            roles_endpoint = f"/admin/realms/{self.__config.realm}/roles-by-id/"
            self.__delete_object(roles_endpoint, role["id"])

    def __delete_object(self, endpoint: str, object_id: str) -> None:
        response = self.__client.delete(endpoint, object_id)

    def __update_object(self, object_data: dict, endpoint: str) -> None:
        response = self.__client.put(endpoint, object_data)

    def __get_assigned_roles(self, group_id: str) -> list:
        group_endpoint = f"/admin/realms/{self.__config.realm}/groups/{group_id}"
        response = self.__client.get(group_endpoint)
        return response.get("realmRoles", [])

    def __get_assigned_groups_users(self, user_id: str) -> list:
        group_endpoint = f"/admin/realms/{self.__config.realm}/users/{user_id}/groups"
        response = self.__client.get(group_endpoint)
        return response

    def __update_assigned_roles(
        self, group_endpoint: str, group: dict, role: str
    ) -> None:
        group_id = self.__get_object_id(group_endpoint, group["name"], "name")
        assigned_list = self.__get_assigned_roles(group_id)
        is_assigned = role in assigned_list
        if not is_assigned:
            role_endpoint = f"/admin/realms/{self.__config.realm}/roles/{role}"
            role_response = self.__client.get(role_endpoint)
            assign_endpoint = f"/admin/realms/{self.__config.realm}/groups/{group_id}/role-mappings/realm"
            try:
                data = [{"id": role_response["id"], "name": role_response["name"]}]
            except Exception as e:
                self.__logger.error(f"Update assigned roles: {str(e)}")
                response = self.__client.post(assign_endpoint, data=data)

    def __update_user_groups(self, user_id: str, group_name: str) -> None:
        assigned_list = self.__get_assigned_groups_users(user_id)
        try:
            groups_names = [group["name"] for group in assigned_list]
        except KeyError as e:
            self.__logger.error(
                f"Update user's groups - there is no key 'name': {str(e)}"
            )
        except Exception as e:
            self.__logger.error(f"Update user's groups: {str(e)}")

        is_assigned = group_name in groups_names
        if not is_assigned:
            groups_endpoint = f"/admin/realms/{self.__config.realm}/groups"
            groups_data = self.__client.get(
                groups_endpoint, params={"search": group_name}
            )
            try:
                for data in groups_data:
                    assign_endpoint = f"/admin/realms/{self.__config.realm}/users/{user_id}/groups/{data['id']}"
                    response = self.__client.put(assign_endpoint)
            except RuntimeError as e:
                self.__logger.error(
                    f"Update user's groups - there is no data: {str(e)}"
                )
            except Exception as e:
                self.__logger.error(f"Update user's groups: {str(e)}")

    def __get_objects(self, endpoint: str) -> list:
        try:
            response = self.__client.get(endpoint)
        except Exception as e:
            self.__logger.error(f"Get objects: {str(e)}")
        return response

    def __get_object_id(self, endpoint: str, object_name: str, key: str) -> str:
        objects = self.__client.get(endpoint)
        try:
            for object in objects:
                if object[key] == object_name:
                    return object["id"]
        except KeyError as e:
            self.__logger.error(f"Response does not contain expected key: {str(e)}")
        except Exception as e:
            self.__logger.error(f"Get object id: {str(e)}")
