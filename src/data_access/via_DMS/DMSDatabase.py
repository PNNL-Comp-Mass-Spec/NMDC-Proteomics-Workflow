
import pymssql
import logging
import sys

class DMSDatabase:
    ''' Database connection class'''
    def __init__(self, config):
        '''

        :param config:
        '''
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
            cursor = self.conn.cursor(as_dict=True)
            cursor.execute(query) # generator object.
            return cursor

        except Exception as e:
            print(e)
        # FIXME: Close connection and test again!
        # finally:
        #     if self.conn:
        #         self.conn.close()
        #         self.conn=None
        #         logging.info("Database connection closed")
