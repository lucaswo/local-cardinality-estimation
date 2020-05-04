from typing import Tuple, List, Dict

import yaml


class Crawler:

    def read_sql_file(self, file_path: str):
        with open(file_path) as file:
            sql_file = file.read()

        sql_commands = sql_file.split(";\n")

        command_dict = {}

        for index, command in enumerate(sql_commands):
            command = command.replace("SELECT COUNT(*) FROM ", "")
            command = command.split("WHERE")
            if len(command) > 1 and command[0] and command[1]:
                command[0] = command[0].strip()
                command[1] = command[1].strip()
                if command[0] not in command_dict:
                    command_dict[command[0]] = []

                command_dict[command[0]].append(command[1])

        solution_dict = {}

        i = 0
        for key, value in command_dict.items():
            table_names = []
            join_attributes = []
            selection_attributes = []
            tables = self.table_name_unpacker(key)
            join_attributes, selection_attributes = self.attribute_unpacker(value, tables)
            for (_, table_name) in tables:
                table_names.append(table_name)
            solution_dict[i] = {"table_names": table_names,
                                "join_attributes": join_attributes,
                                "selection_attributes": selection_attributes}

            i += 1

        self.save_solution_dict(solution_dict)

    def table_name_unpacker(self, from_string: str) -> List[Tuple[str, str]]:
        tables = []
        table_names = from_string.split(",")
        for table in table_names:
            table = table.strip()
            table = table.split(" ")
            if len(table) == 2:
                tables.append((table[1], table[0]))
            elif len(table) == 1:
                tables.append(("", table[0]))

        return tables

    def attribute_unpacker(self, where_string_list, tables: List[Tuple[str, str]]):
        join_attributes_set: set = None
        selection_attributes_set: set = None
        attribute_set: set = None

        for where_string in where_string_list:
            attrs = where_string.split("AND")
            for attr in attrs:
                attr = attr.strip()
                if attribute_set is None:
                    attribute_set = {attr}
                else:
                    attribute_set.add(attr)

        operators = ["<=", "!=", ">=", "=", "<", ">"]

        for attr in attribute_set:
            for operator in operators:
                if operator in attr:
                    if self.is_join_attribute(attr, operator):
                        if join_attributes_set is None:
                            join_attributes_set = {attr}
                        else:
                            join_attributes_set.add(attr)
                        break
                    else:
                        attr = attr.split(operator)[0].strip()
                        if selection_attributes_set is None:
                            selection_attributes_set = {attr}
                        else:
                            selection_attributes_set.add(attr)
                        break

        for shortname, table in tables:
            for join_attribute in join_attributes_set:
                join_attributes_set.remove(join_attribute)
                join_attributes_set.add(join_attribute.replace(shortname + ".", table + "."))
            for selection_attribute in selection_attributes_set:
                selection_attributes_set.remove(selection_attribute)
                selection_attributes_set.add(selection_attribute.replace(shortname + ".", table + "."))

        return list(join_attributes_set), list(selection_attributes_set)

    def is_join_attribute(self, clause: str, operator: str):
        return not clause.split(operator)[1].isnumeric()

    def save_solution_dict(self, solution_dict: Dict[int, Dict[str, List[str]]]):
        with open("solution_dict.yaml", "w") as file:
            yaml.safe_dump(solution_dict, file)


cra = Crawler()
cra.read_sql_file("job-light.sql")
