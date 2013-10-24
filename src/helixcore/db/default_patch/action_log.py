from helixcore.install.install import is_table_exists, is_sequence_exists

table = 'action_log'
sequence = '%s_seq' % table
env_idx = '%s_env_id_idx' % table
env_actor_idx = '%s_env_id_actor_id_idx' % table
env_session_idx = '%s_env_id_sess_id_idx' % table
env_action_idx = '%s_env_id_action_idx' % table


def apply(curs, logger):
    logger.info("Creating table %s" % table)
    curs.execute('CREATE TABLE %(table)s (id INTEGER NOT NULL, environment_id INTEGER NOT NULL, '
                 'session_id VARCHAR2(128 CHAR), custom_actor_info VARCHAR2(2000 CHAR), '
                 'actor_user_id INTEGER,  action VARCHAR2(128 CHAR) NOT NULL, '
                 'request_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,'
                 'remote_addr VARCHAR2(128 CHAR) NOT NULL, '
                 'request CLOB NOT NULL, response CLOB NOT NULL, '
                 'CONSTRAINT %(table)s_pk PRIMARY KEY(id))' % {'table': table})
    logger.info("Creating sequence %s" % sequence)
    curs.execute('CREATE SEQUENCE %s' % sequence)

    logger.info("Creating index %s" % env_idx)
    curs.execute('CREATE INDEX %s ON %s(environment_id)' % (env_idx, table))

    logger.info("Creating index %s" % env_actor_idx)
    curs.execute('CREATE INDEX %s ON %s(environment_id, actor_user_id)' % (env_actor_idx, table))

    logger.info("Creating index %s" % env_session_idx)
    curs.execute('CREATE INDEX %s ON %s(environment_id, session_id)' % (env_session_idx, table))

    logger.info("Creating index %s" % env_action_idx)
    curs.execute('CREATE INDEX %s ON %s(environment_id, action)' % (env_action_idx, table))


def revert(curs, logger):
    if is_sequence_exists(curs, sequence):
        logger.info("Dropping sequence %s" % sequence)
        curs.execute('DROP SEQUENCE %s' % sequence)
    if is_table_exists(curs, table):
        logger.info("Dropping table %s" % table)
        curs.execute('DROP TABLE %s' % table)
