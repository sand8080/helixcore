import unittest

from helixcore.test.db.test_cond import CondTestCase #IGNORE:W0611
from helixcore.test.db.test_query_builder import QueryBuilderTestCase #IGNORE:W0611
from helixcore.test.db.test_wrapper import WrapperTestCase #IGNORE:W0611
from helixcore.test.db.test_buildhelpers import BuildhelpersTestCase #IGNORE:W0611

from helixcore.test.mapping.test_actions import ActionsTestCase #IGNORE:W0611
from helixcore.test.install.test_install import PatchProcessorTestCase #IGNORE:W0611
from helixcore.test.install.test_filtering import FilteringTestCase #IGNORE:W0611

if __name__ == '__main__':
    unittest.main()
