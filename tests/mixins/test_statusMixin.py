# -*- coding: utf-8 -*-
# Copyright (c) 2009-2012, Erkan Ozgur Yilmaz
# 
# This module is part of Stalker and is released under the BSD 2
# License: http://www.opensource.org/licenses/BSD-2-Clause

import unittest
import transaction
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import orm
from stalker import db
from stalker.models.mixins import StatusMixin
from stalker.db.session import DBSession
from stalker.models.status import Status, StatusList
from stalker.models.entity import SimpleEntity

class StatMixClass(SimpleEntity, StatusMixin):
    __tablename__ = "StatMixClasses"
    __mapper_args__ = {"polymorphic_identity": "StatMixClass"}
    StatMixClass_id = Column("id", Integer, ForeignKey("SimpleEntities.id"),
                             primary_key=True)

    def __init__(self, **kwargs):
        super(StatMixClass, self).__init__(**kwargs)
        StatusMixin.__init__(self, **kwargs)

class StatusMixinTester(unittest.TestCase):
    """tests the StatusMixin class
    """
    
    def setUp(self):
        """setup the test
        """
        self.test_status1 = Status(name="Status1", code="STS1")
        self.test_status2 = Status(name="Status2", code="STS2")
        self.test_status3 = Status(name="Status3", code="STS3")
        self.test_status4 = Status(name="Status4", code="STS4")
        self.test_status5 = Status(name="Status5", code="STS5")

        # a test StatusList object
        self.test_status_list1 = StatusList(
            name="Test Status List 1",
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4,
                self.test_status5,
                ],
            target_entity_type="StatMixClass",
            )

        # another test StatusList object
        self.test_status_list2 = StatusList(
            name="Test Status List 2",
            statuses=[
                self.test_status1,
                self.test_status2,
                self.test_status3,
                self.test_status4,
                self.test_status5,
                ],
            target_entity_type="StatMixClass",
            )

        self.kwargs = {
            "name": "Test Class",
            "status_list": self.test_status_list1,
            "status": 0,
            }

        self.test_mixed_obj = StatMixClass(**self.kwargs)
        self.test_mixed_obj.status_list = self.test_status_list1

        # create another one without status_list set to something
        self.test_mixed_obj2 = StatMixClass(**self.kwargs)
    
    def tearDown(self):
        """clean up the test
        """
        DBSession.remove()

    def test_status_list_init_with_something_else_then_StatusList_1(self):
        """testing if TypeError is going to be raised when trying to
        initialize status_list with something other than a StatusList
        """
        testValues = [100, "", 100.2]
        for testValue in testValues:
            self.kwargs["status_list"] = testValue
            self.assertRaises(TypeError, StatMixClass, **self.kwargs)

    def test_status_list_init_with_something_else_then_StatusList_2(self):
        """testing if TypeError is going to be raised when trying to
        initialize status_list with None
        """
        self.kwargs["status_list"] = None
        self.assertRaises(TypeError, StatMixClass, **self.kwargs)

    def test_status_list_attribute_set_to_something_other_than_StatusList(self):
        """testing if TypeError is going to be raised when trying to set the
        status_list to something else than a StatusList object
        """
        test_values = ["a string", 1.0, 1, {"a": "statusList"}]

        for test_value in test_values:
            # now try to set it
            self.assertRaises(
                TypeError,
                setattr,
                self.test_mixed_obj,
                "status_list",
                test_value
            )

    def test_status_list_attribute_set_to_None(self):
        """testing if TypeError is going to be raised when trying to set the
        status_list to None
        """

        self.assertRaises(
            TypeError,
            setattr,
            self.test_mixed_obj,
            "status_list",
            None
        )

    def test_status_list_argument_being_omited(self):
        """testing if a TypeError going to be raised when omiting the
        status_list argument
        """
        self.kwargs.pop("status_list")
        self.assertRaises(TypeError, StatMixClass, **self.kwargs)

    def test_status_list_argument_suitable_for_the_current_class(self):
        """testing if a TypeError will be raised when the
        Status.target_entity_class is not compatible with the current
        class
        """
        # create a new status list suitable for another class with different
        # entity_type

        new_status_list = StatusList(
            name="Sequence Statuses",
            statuses=[
                Status(name="On Hold", code="OH"),
                Status(name="Complete", code="CMPLT"),
                ],
            target_entity_type="Sequence"
        )

        self.assertRaises(
            TypeError,
            setattr,
            self.test_mixed_obj,
            "status_list",
            new_status_list
        )

        new_suitable_list = StatusList(
            name="Suitable Statuses",
            statuses=[
                Status(name="On Hold", code="OH"),
                Status(name="Complete", code="CMPLT"),
                ],
            target_entity_type="StatMixClass"
        )

        # this shouldn't raise any error
        self.test_mixed_obj.status_list = new_suitable_list

    def test_status_argument_set_to_None(self):
        """testing if the first Status in the status_list attribute will be
        used when the status argument is None
        """
        self.kwargs["status"] = None
        new_obj = StatMixClass(**self.kwargs)
        self.assertEqual(new_obj.status, new_obj.status_list[0])
    
    def test_status_attribute_set_to_None(self):
        """testing if the first Status in the status_list attribute will be
        used when setting the status attribute to None
        """
        self.test_mixed_obj.status = None
        self.assertEqual(
            self.test_mixed_obj.status,
            self.test_mixed_obj.status_list[0]
        )

    def test_status_argument_different_than_an_Status_or_int(self):
        """testing if a TypeError is going to be raised if trying to
        initialize status with something else than an integer
        """
        # with a string
        test_values = ["0", 1.2, [0]]

        for test_value in test_values:
            self.kwargs["status"] = test_value
            self.assertRaises(TypeError, StatMixClass, **self.kwargs)

    def test_status_attribute_set_to_other_than_Status_or_int(self):
        """testing if TypeError going to be raised when trying to set the
        current status to something other than an integer
        """
        test_values = ["a string", 1.2, [1], {"a": "status"}]
        for test_value in test_values:
            self.assertRaises(
                TypeError,
                setattr,
                self.test_mixed_obj,
                "status",
                test_value
            )

    def test_status_attribute_set_to_too_high(self):
        """testing if a ValueError is going to be raised when trying to set the
        current status to something higher than it is allowed to, that is it
        couldn't be set a value higher than len(statusList.statuses - 1)
        """
        test_value = len(self.test_status_list1.statuses)
        self.assertRaises(
            ValueError,
            setattr,
            self.test_mixed_obj,
            "status",
            test_value
        )

    def test_status_attribute_set_to_too_low(self):
        """testing if a ValueError is going to be raised when trying to set the
        current status to something lower than it is allowed to, that is it
        couldn't be set to value lower than 0
        """
        test_value = -1
        self.assertRaises(
            ValueError,
            setattr,
            self.test_mixed_obj,
            "status",
            test_value
        )

    def test_status_attribute_works_properly(self):
        """testing if the status attribute works properly
        """
        test_value = 1

        self.test_mixed_obj.status = test_value
        self.assertEqual(
            self.test_mixed_obj.status,
            self.test_mixed_obj.status_list[test_value]
        )

    def test_status_attribute_can_be_set_with_a_Status_object(self):
        """testing if the status of the mixed in object can be set with a
        Status instance
        """
        self.test_mixed_obj.status = self.test_status2
        self.assertEqual(self.test_mixed_obj.status, self.test_status2)
    
    def test_status_attribute_is_set_with_a_Status_which_is_not_in_the_StatusList(self):
        """testing if a ValueError will be raised when the status of an object
        is set with a Status instance which is not in the status_list of the
        mixed in object
        """
        self.assertRaises(ValueError, setattr, self.test_mixed_obj, 'status',
                          Status(name='Temp', code='TEMP'))
    
    def test_status_attribute_holds_a_Status_instance(self):
        """testing if the status attribute holds a Status instance
        """
        self.assertTrue(isinstance(self.test_mixed_obj.status, Status))

class StatusListAutoAddClass(SimpleEntity, StatusMixin):
    """It is a class derived from stalker.core.models.SimpleEntity for testing
    purposes.
    """

    __tablename__ = "StatusListAutoAddClass"
    __mapper_args__ = {"polymorphic_identity": "StatusListAutoAddClass"}
    statusListAutoAddClass_id = Column("id", Integer,
                                       ForeignKey("SimpleEntities.id"),
                                       primary_key=True)


    def __init__(self, **kwargs):
        super(SimpleEntity, self).__init__(**kwargs)
        StatusMixin.__init__(self, **kwargs)


    @orm.reconstructor
    def __init_on_load__(self):
        """the init function for instances loaded from the db
        """
        super(StatusListAutoAddClass, self).__init_on_load__()


class StatusListNoAutoAddClass(SimpleEntity, StatusMixin):
    """It is a class derived from stalker.core.models.SimpleEntity for testing
    purposes.
    """

    __tablename__ = "StatusListNoAutoAddClass"
    __mapper_args__ = {"polymorphic_identity": "StatusListNoAutoAddClass"}
    statusListNoAutoAddClass_id = Column("id", Integer,
                                         ForeignKey("SimpleEntities.id"),
                                         primary_key=True)


    def __init__(self, **kwargs):
        super(SimpleEntity, self).__init__(**kwargs)
        StatusMixin.__init__(self, **kwargs)


    @orm.reconstructor
    def __init_on_load__(self):
        """the init function for instances loaded from the db
        """
        super(StatusListAutoAddClass, self).__init_on_load__()


class StatusMixinDBTester(unittest.TestCase):
    """tests the StatusMixin with a DB is already setup
    """


    def setUp(self):
        """setup the test
        """

        # create a database
        db.setup()
    
    def tearDown(self):
        """clean up the test
        """
        if DBSession:
            DBSession.remove()

        #db.session = None
    
    def test_status_list_attribute_is_skipped_and_there_is_a_db_setup(self):
        """testing if there will be no error and the status_list attribute is
        filled with the correct StatusList instance coming from the database
        if there is already a database setup and there is a StatusList instance
        defined for the StatusListAutoAddClass.
        """
        
        with transaction.manager:
            # create a StatusList for StatusListAutoAddClass
            test_status_list = StatusList(
                name="StatusListAutoAddClass Statuses",
                statuses=[
                    Status(name="Status1", code="Sts1"),
                    Status(name="Status2", code="Sts2"),
                    Status(name="Status3", code="Sts3"),
                    ],
                target_entity_type=StatusListAutoAddClass,
                )
            
            # add it to the db
            DBSession.add(test_status_list)
        
        # now try to create a StatusListAutoAddClass without a status_list 
        # argument
        test_StatusListAutoAddClass = StatusListAutoAddClass(
            name="Test StatusListAutoAddClass",
        )

        # now check if the status_list is equal to test_status_list
        self.assertEqual(
            test_StatusListAutoAddClass.status_list,
            test_status_list
        )


    def test_status_list_attribute_is_skipped_and_there_is_a_db_setup_but_no_suitable_StatusList(self):
        """testing if a TypeError will be raised even a database is setup 
        but there is no suitable StatusList for StatusListNoAutoAddClass in 
        the database
        """
        
        with transaction.manager:
            # create a StatusList for StatusListAutoAddClass
            test_status_list = StatusList(
                name="StatusListAutoAddClass Statuses",
                statuses=[
                    Status(name="Status1", code="Sts1"),
                    Status(name="Status2", code="Sts2"),
                    Status(name="Status3", code="Sts3"),
                    ],
                target_entity_type=StatusListAutoAddClass,
                )
    
            # add it to the db
            DBSession.add(test_status_list)
        
        # now try to create a StatusListAutoAddClass without a status_list 
        # argument
        
        self.assertRaises(
            TypeError,
            StatusListNoAutoAddClass,
            **{"name": "Test StatusListNoAutoAddClass"}
        )
    
