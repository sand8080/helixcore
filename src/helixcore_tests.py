import unittest

from helixcore.test.json_validator.test_validator import (AnyOfTestCase, ArbitraryDictTestCase, #IGNORE:W0611 @UnusedImport
    DecimalTextTestCase, DictTestCase, IsoDatetimeTestCase, JobRelatedTestCase, ListTestCase, #IGNORE:W0611 @UnusedImport
    SamplesTestCase, SchemeTestCase, TextTestCase, ValueValidatorTestCase) #IGNORE:W0611 @UnusedImport

from helixcore.test.db.test_sql import SqlTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_wrapper import WrapperTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_deadlock_detector import DeadlockDetectorTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.db.test_db_blocking import DbBlockingTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.mapping.test_mapping import MappingTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.mapping.test_arrays import ArraysTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.install.test_install import PatchProcessorTestCase #IGNORE:W0611 @UnusedImport
from helixcore.test.install.test_filtering import FilteringTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.security.test_security import SecurityTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.server.api.test_api import RequestHandlingTestCase #IGNORE:W0611 @UnusedImport

from helixcore.test.misc.domain import DomainNameTestCase #IGNORE:W0611 @UnusedImport


if __name__ == '__main__':
    unittest.main()
