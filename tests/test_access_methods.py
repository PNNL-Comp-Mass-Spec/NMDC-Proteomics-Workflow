from unittest.mock import patch, MagicMock


from src.access_methods.direct_access.DMSDatabase import DMSDatabase
from src.access_methods.direct_access.query import Query
from src.access_methods.direct_access.secure import Config

class TestAccessMethods:

    @patch('mypackage.mymodule.pymysql')
    def test_dms_connection(self, mock_sql):
        self.assertIs(.pymysql, mock_sql)

        #TODO: Need to fix.
        conn = Mock()
        mock_sql.connect.return_value = conn

        cursor      = MagicMock()
        mock_result = MagicMock()

        cursor.__enter__.return_value = mock_result
        cursor.__exit___              = MagicMock()

        conn.cursor.return_value = cursor

        DMSDatabase.open_connection()

        mock_sql.connect.assert_called_with(host=,
                                            user=,
                                            password=,
                                            db=)
        mock_result.execute.assert_called_with("sql request", ("user", "pass"))



