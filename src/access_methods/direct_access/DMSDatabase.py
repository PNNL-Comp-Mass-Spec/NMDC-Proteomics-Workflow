import pymssql

import logging
import sys

class DMSDatabase:
    ''' Database connection class'''
    def __init__(self, config):
        self.SERVER = config.db_server
        self.USER = config.db_user
        self.PASSWORD = config.db_password
        self.DATABASE_NAME = config.db_name
        self.conn = None


    def open_connection(self):
        '''
        Connection to DMS MS sqlserver i.e DMS5 or DMS_Data_Package
        '''
        try:
            if self.conn is None:
                self.conn = pymssql.connect(server = self.SERVER,
                                            user = self.USER,
                                            password = self.PASSWORD,
                                            database= self.DATABASE_NAME)
        except pymssql.MySQLError as conn_err:
            logging.error(conn_err)
            sys.exit()
        finally:
            logging.info("Connection opened successfully")

    def run_query(self, query):
        '''Execute SQL query.
        '''
        try:
            self.open_connection()
            # Create cursor
            cursor = self.conn.cursor()
            # Get resultset
            cursor.execute(query)
            # Get result printed
            folder_name = self.print_result_set(cursor)

        except pymssql.MySQLError as e:
            print(e)
        finally:
            if self.conn:
                self.conn.close()
                self.conn=None
                logging.info("Database connection closed")
        return folder_name

    def print_result_set(self, cursor):
        ''' Pretty print the resultset
        :param cursor: pointer to database object
        :return: folder_name
        '''
        # Get header
        header = [col_name for col_name, *_ in cursor.description]

        # store the generator, else it will exhaust after single use.
        result_set = list(cursor)

        # Formatting
        col_longest_lens = [max(len(str(row[col_num])) for row in result_set) for col_num in range(len(header))]
        fmt = ' '.join('{:<%d}' % l for l in col_longest_lens)

        print('-' * (sum(col_longest_lens) + len(col_longest_lens) - 1))
        print(fmt.format(*header))
        print('-' * (sum(col_longest_lens) + len(col_longest_lens) - 1))

        for row in result_set:
            result= row
            # print(fmt.format(*row))

        print('-' * (sum(col_longest_lens) + len(col_longest_lens) - 1))
        return result[0]