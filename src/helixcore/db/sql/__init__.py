# """
# Importing sql generator
# """
from helixcore.db.sql import sql_profile

from helixcore.db.sql.sql_common import *

if sql_profile == 'oracle':
    from helixcore.db.sql.sql_oracle import *
elif sql_profile == 'postgres':
    from helixcore.db.sql.sql_postgres import *
