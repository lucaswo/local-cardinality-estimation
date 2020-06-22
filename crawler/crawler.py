from typing import Tuple, List, Dict

import yaml


class Crawler:
    """
    Class for the crawler. This is responsible of reading a given file and return a file containing the aggregated
    informations of this file.
    """

    operators = ["<=", "!=", ">=", "=", "<", ">"]

    def read_file(self, file_path: str) -> Tuple[Dict, str]:
        """
        Generic Method for reading the sql statements from a given .sql or a .csv file.

        :param file_path: Path to the file containing the sql statements. This path has to end with .csv or .sql. No
            other file types are supported at the moment.
        """

        if file_path and file_path.split(".")[-1] == "csv":
            return self.read_csv_file(file_path)
        elif file_path and file_path.split(".")[-1] == "sql":
            return self.read_sql_file(file_path)
        else:
            raise ValueError("The given file-path points neither to a .csv nor a .sql file. Please correct this!")

    @staticmethod
    def read_sql_file(file_path: str) -> Tuple[Dict, str]:
        """
        Read the sql statements from given sql file.

        :param file_path: Path to the file containing the sql statements.
        """

        if not file_path or file_path.split(".")[-1] != "sql":
            raise ValueError("The given file-path doesn't point to a .sql file. Please correct this!")

        with open(file_path) as file:
            sql_file = file.read()

        sql_commands = sql_file.split(";\n")

        command_dict = {}

        for command in sql_commands:
            command = command.replace("SELECT COUNT(*) FROM ", "")
            command = command.split("WHERE")
            if len(command) > 1 and command[0] and command[1]:
                tables = command[0].strip().split(",")
                tables.sort()
                command[0] = ",".join(tables)
                command[1] = command[1].strip()
                if command[0] not in command_dict:
                    command_dict[command[0]] = []

                command_dict[command[0]].append(command[1])

        return command_dict, "sql"

    @staticmethod
    def read_csv_file(file_path: str) -> Tuple[Dict, str]:
        """
        Read the csv formatted sql statements from given file.

        :param file_path: Path to the file containing the sql statements formatted as csv.
        """

        if not file_path or file_path.split(".")[-1] != "csv":
            raise ValueError("The given file-path doesn't point to a .csv file. Please correct this!")

        with open(file_path) as file:
            csv_file = file.read()

        csv_commands = csv_file.split("\n")

        command_dict = {}

        for command in csv_commands:
            command = command.split("#")
            if len(command) > 2 and command[0] and command[1] and command[2]:
                tables = command[0].strip().split(",")
                tables.sort()
                command[0] = ",".join(tables)
                command[1] = command[1].strip()
                command[2] = command[2].strip()

                if command[0] not in command_dict:
                    command_dict[command[0]] = []

                command_dict[command[0]].append((command[1], command[2]))

        return command_dict, "csv"

    def create_solution_dict(self, command_dict: Dict[str, List[str] or List[Tuple[str, str]]], file_type: str) \
            -> Dict[int, Dict[str, List[str or Tuple[str, str]]]]:
        """
        Method for building the solution dict.

        :param command_dict: Dict with a alphabetical sorted string of the joining tables as key and a list of where
            clauses as string if the file type is sql or a list of tuples containing the join-attribute-string in first
            and the selection-attribute-string in second place.
        :param file_type: String with 'csv' or 'sql' which tells the file type of the read file.
        :return The solution dict containing 'table_names', 'join_attributes' and 'selection_attributes'.
        """

        if not file_type or not file_type.strip():
            raise ValueError("The string containing the file format is missing or empty.")

        if not command_dict:
            raise ValueError("The dict containing the split up command is missing.")

        solution_dict = {}

        i = 0
        for key, value in command_dict.items():
            tables = self.table_name_unpacker(key)
            if file_type == "sql":
                join_attributes, selection_attributes = self.sql_attribute_unpacker(value, len(tables) - 1)
            elif file_type == "csv":
                join_attributes, selection_attributes = self.csv_attribute_unpacker(value)
            else:
                raise ValueError("Incorrect file type. Only the file types 'csv' and 'sql' are supported!")
            solution_dict[i] = {"table_names": tables,
                                "join_attributes": join_attributes,
                                "selection_attributes": selection_attributes}

            i += 1

        return solution_dict

    @staticmethod
    def table_name_unpacker(from_string: str) -> List[Tuple[str, str]]:
        """
        Takes the sorted string of the from clause and extracts the tables with there aliases.

        :param from_string: Alphabetical ordered string containing all tables to join, separated by ','.
        :return: List of tuples where the first element of the tuple is the table name and the second one is the alias.
        """

        if not from_string or not from_string.strip():
            raise ValueError("The string containing the from clause is missing or empty.")

        tables = []
        table_names = from_string.split(",")
        for table in table_names:
            table = table.strip()
            table = table.split(" ")
            if len(table) == 2:
                tables.append((table[0], table[1]))
            elif len(table) == 1:
                tables.append((table[0], ""))

        return tables

    def sql_attribute_unpacker(self, where_string_list: List[str], amount_join_attributes: int) \
            -> Tuple[List[str], List[str]]:
        """
        Unpack the attribute strings from sql-file into sets containing the attributes.

        :param where_string_list: A list of strings from the where clauses. These have to be separated into join- and
            selection-attributes.
        :param amount_join_attributes: The amount of join-attributes. (Number of joining tables -1)
        :return: A tuple containing the list of join-attributes in first and the list of selection-attributes in second
            place.
        """

        if not where_string_list or len(where_string_list) == 0:
            raise ValueError("The list of strings containing the attributes is missing.")

        join_attributes_set: set = set()
        selection_attributes_set: set = set()

        for where_string in where_string_list:
            attrs = where_string.split("AND")

            for index, attr in enumerate(attrs):
                if index < amount_join_attributes:
                    join_attributes_set.add(attrs[index].strip())
                else:
                    for operator in self.operators:
                        if operator in attr:
                            attr = attr.split(operator)[0].strip()
                            selection_attributes_set.add(attr)
                            break

        return list(join_attributes_set), list(selection_attributes_set)

    def csv_attribute_unpacker(self, attribute_tuples: List[Tuple[str, str]]) -> Tuple[List[str], List[str]]:
        """
        Unpack the attribute strings from csv-file into sets containing the attributes.

        :param attribute_tuples: A list of tuples of strings where the first string is the string for all
            join-attributes, while the second string contains all selection-attributes.
        :return: A tuple containing the list of join-attributes in first and the list of selection-attributes in second
            place.
        """

        if not attribute_tuples:
            raise ValueError("The list of tuples containing the attributes is missing.")

        join_attributes_set: set = set()
        selection_attributes_set: set = set()

        for j_attribute_string, s_attribute_string in attribute_tuples:
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

        return list(join_attributes_set), list(selection_attributes_set)

    @staticmethod
    def save_solution_dict(solution_dict: Dict[int, Dict[str, List[str or Tuple[str, str]]]],
                           save_file_path: str = "solution_dict"):
        """
        Save the solution to file with specified filename.

        :param solution_dict: The dict containing the data to save.
        :param save_file_path: The path for the file in which the data should be saved. The .yaml ending is added
        automatically.
        """

        if not solution_dict:
            raise ValueError("There is no dict containing the solution given.")

        if save_file_path.endswith(".yaml"):
            save_file_path = save_file_path.replace(".yaml", "")

        with open("{}.yaml".format(save_file_path), "w") as file:
            yaml.safe_dump(solution_dict, file)

    def run(self, file_path: str, save_file_path: str) -> Dict[int, Dict[str, List[str or Tuple[str, str]]]]:
        """
        Method for the whole crawling process.

        :param file_path: The file in to read which the sql-statements are saved.
        :param save_file_path: The path where to save the results.
        :return:
        """

        command_dict, file_type = self.read_file(file_path=file_path)
        solution_dict = self.create_solution_dict(command_dict=command_dict, file_type=file_type)
        self.save_solution_dict(solution_dict=solution_dict, save_file_path=save_file_path)

        return solution_dict
