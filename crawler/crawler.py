from typing import Tuple, List, Dict, Set

import yaml


class Crawler:
    operators = ["<=", "!=", ">=", "=", "<", ">"]

    def read_file(self, file_path: str):
        if file_path.split(".")[-1] == "csv":
            self.read_csv_file(file_path)
        elif file_path.split(".")[-1] == "sql":
            self.read_sql_file(file_path)
        else:
            raise ValueError("The given file-path points neither to a .csv nor a .sql file. Please correct this!")

    def read_sql_file(self, file_path: str):
        with open(file_path) as file:
            sql_file = file.read()

        sql_commands = sql_file.split(";\n")

        command_dict = {}

        for command in sql_commands:
            command = command.replace("SELECT COUNT(*) FROM ", "")
            command = command.split("WHERE")
            if len(command) > 1 and command[0] and command[1]:
                command[0] = command[0].strip()
                command[1] = command[1].strip()
                if command[0] not in command_dict:
                    command_dict[command[0]] = []

                command_dict[command[0]].append(command[1])

        self.create_solution_dict(command_dict, "sql")

    def read_csv_file(self, file_path: str):
        with open(file_path) as file:
            csv_file = file.read()

        csv_commands = csv_file.split("\n")

        command_dict = {}

        for command in csv_commands:
            command = command.split("#")
            if len(command) > 2 and command[0] and command[1] and command[2]:
                command[0] = command[0].strip()
                command[1] = command[1].strip()
                command[2] = command[2].strip()
                if command[0] not in command_dict:
                    command_dict[command[0]] = []

                command_dict[command[0]].append((command[1], command[2]))

        self.create_solution_dict(command_dict, "csv")

    def create_solution_dict(self, command_dict: Dict[str, List[str] or Tuple[str, str]], file_type: str):
        solution_dict = {}

        i = 0
        for key, value in command_dict.items():
            table_names = []
            tables = self.table_name_unpacker(key)
            if file_type == "sql":
                join_attributes, selection_attributes = self.sql_attribute_unpacker(value, tables)
            elif file_type == "csv":
                join_attributes, selection_attributes = self.csv_attribute_unpacker(value, tables)
            else:
                raise ValueError("Incorrect file type. Only the file types 'csv' and 'sql' are supported!")
            for (_, table_name) in tables:
                table_names.append(table_name)
            solution_dict[i] = {"table_names": table_names,
                                "join_attributes": join_attributes,
                                "selection_attributes": selection_attributes}

            i += 1

        self.save_solution_dict(solution_dict)

    @staticmethod
    def table_name_unpacker(from_string: str) -> List[Tuple[str, str]]:
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

    def sql_attribute_unpacker(self, where_string_list, tables: List[Tuple[str, str]]) -> (List[str], List[str]):
        join_attributes_set: set = set()
        selection_attributes_set: set = set()
        attribute_set: set = set()

        for where_string in where_string_list:
            attrs = where_string.split("AND")
            for attr in attrs:
                attribute_set.add(attr.strip())

        for attr in attribute_set:
            for operator in self.operators:
                if operator in attr:
                    if self.is_join_attribute(attr, operator):
                        join_attributes_set.add(attr)
                        break
                    else:
                        attr = attr.split(operator)[0].strip()
                        selection_attributes_set.add(attr)
                        break

        join_attributes_set, selection_attributes_set = self.shortname_extender(tables, join_attributes_set,
                                                                                selection_attributes_set)

        return list(join_attributes_set), list(selection_attributes_set)

    def csv_attribute_unpacker(self, join_attribute_tuples: List[Tuple[str, str]], tables: List[Tuple[str, str]]) \
            -> (List[str], List[str]):
        join_attributes_set: set = set()
        selection_attributes_set: set = set()

        for j_attribute_string, s_attribute_string in join_attribute_tuples:
            for j_attribute in j_attribute_string.split(","):
                join_attributes_set.add(j_attribute.strip())

            for operator in self.operators:
                s_attribute_string = s_attribute_string.replace("," + operator + ",", operator)

            for s_attribute in s_attribute_string.split(","):
                for operator in self.operators:
                    if operator in s_attribute:
                        s_attribute = s_attribute.split(operator)[0].strip()
                        selection_attributes_set.add(s_attribute)
                        break

        join_attributes_set, selection_attributes_set = self.shortname_extender(tables, join_attributes_set,
                                                                                selection_attributes_set)

        return list(join_attributes_set), list(selection_attributes_set)

    @staticmethod
    def shortname_extender(tables: List[Tuple[str, str]], join_attributes_set: Set[str],
                           selection_attributes_set: Set[str]) -> (Set[str], Set[str]):
        for shortname, table in tables:
            for join_attribute in join_attributes_set:
                join_attributes_set.remove(join_attribute)
                join_attributes_set.add(join_attribute.replace(shortname + ".", table + "."))
            for selection_attribute in selection_attributes_set:
                selection_attributes_set.remove(selection_attribute)
                selection_attributes_set.add(selection_attribute.replace(shortname + ".", table + "."))

        return join_attributes_set, selection_attributes_set

    @staticmethod
    def is_join_attribute(clause: str, operator: str) -> bool:
        return not clause.split(operator)[1].isnumeric()

    @staticmethod
    def save_solution_dict(solution_dict: Dict[int, Dict[str, List[str]]]):
        with open("solution_dict.yaml", "w") as file:
            yaml.safe_dump(solution_dict, file)


# TODO: add documentation, add typings where missing, add safety features where needed, try to improve code and
#  performance

cra = Crawler()
# cra.read_file("job-light.sql")
cra.read_file("job-light.csv")
