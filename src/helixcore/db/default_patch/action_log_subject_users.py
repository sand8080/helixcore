from helixcore.install.install import is_table_exists, is_sequence_exists


table = 'al_subj_id'
sequence = '%s_seq' % table
env_al_idx = '%s_al_idx' % table
env_al_subj_idx = '%s_al_subj_idx' % table


def apply(curs, logger):
    logger.info("Creating table %s" % table)
    curs.execute('CREATE TABLE %(table)s (id INTEGER NOT NULL, '
                 'environment_id INTEGER NOT NULL, '
                 'action_log_id INTEGER NOT NULL, '
                 'FOREIGN KEY (action_log_id) REFERENCES action_log(id),'
                 'subject_user_id INTEGER NOT NULL,'
                 'CONSTRAINT %(table)s_pk PRIMARY KEY(id))' % {'table': table})
    logger.info("Creating sequence %s" % sequence)
    curs.execute('CREATE SEQUENCE %s' % sequence)

    logger.info("Creating index %s on %s" % (env_al_idx, table))
    curs.execute('CREATE INDEX %s ON %s(environment_id, action_log_id)' % (env_al_idx, table))

    logger.info("Creating unique index %s on %s" % (env_al_subj_idx, table))
    curs.execute('CREATE UNIQUE INDEX %s ON %s(environment_id, action_log_id, subject_user_id)' %
                 (env_al_subj_idx, table))


def revert(curs, logger):
    if is_sequence_exists(curs, sequence):
        logger.info("Dropping sequence %s" % sequence)
        curs.execute('DROP SEQUENCE %s' % sequence)
    if is_table_exists(curs, table):
        logger.info("Dropping table %s" % table)
        curs.execute('DROP TABLE %s' % table)
