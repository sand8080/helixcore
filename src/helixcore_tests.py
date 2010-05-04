import unittest

from helixcore.test.valik.tests import (AnyOfTestCase, ArbitraryDictTestCase, DecimalTextTestCase, #IGNORE:W0611 @UnusedImport
    DictTestCase, IsoDatetimeTestCase, JobRelatedTestCase, ListTestCase, SamplesTestCase, #IGNORE:W0611 @UnusedImport
    SchemeTestCase, TextTestCase, ValueValidatorTestCase) #IGNORE:W0611 @UnusedImport

from helixcore.test.db.test_sql import SqlTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_wrapper import WrapperTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_deadlock_detector import DeadlockDetectorTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_db_blocking import DbBlockingTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.mapping.test_mapping import MappingTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.mapping.test_arrays import ArraysTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.install.test_install import PatchProcessorTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.install.test_filtering import FilteringTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.server.api.test_api import RequestHandlingTestCase #IGNORE:W0611 @UnusedImport


if __name__ == '__main__':
    unittest.main()
