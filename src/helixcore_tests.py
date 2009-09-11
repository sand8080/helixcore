import unittest

from helixcore.test.validol.tests import AnyOfTestCase, BaseValidatorTestCase, DictTestCase, JobRelatedTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.validol.tests import ListTestCase, OptionalTestCase, SamplesTestCase, SchemeTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.db.test_cond import CondTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_query_builder import QueryBuilderTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_wrapper import WrapperTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_deadlock_detector import DeadlockDetectorTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_buildhelpers import BuildhelpersTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.mapping.test_actions import ActionsTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.mapping.test_arrays import ArraysTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.install.test_install import PatchProcessorTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.install.test_filtering import FilteringTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.server.api.test_api import RequestHandlingTestCase #IGNORE:W0611 @UnusedImport

if __name__ == '__main__':
    unittest.main()
