from nose.tools import assert_almost_equal

from av.database.base import Base
from av.continuancetable import ContinuanceTable, ContinuanceTableRow
from av.test.basedatatest import BaseDataTest

class TestContinuanceTable(BaseDataTest):

    def setUp(self):
        super(TestContinuanceTable, self).setUp()
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def check_continuance_value(self, test_values, columns=None):
        if test_values[1] == None:
            if columns == None:
                slice_value = self.test_continuance_table.slice(self.session, test_values[0])
            else:
                slice_value = self.test_continuance_table.slice(self.session, test_values[0], columns=columns)
        else:
            if columns == None:
                slice_value = self.test_continuance_table.slice(self.session, test_values[0], test_values[1])
            else:
                slice_value = self.test_continuance_table.slice(self.session, test_values[0], test_values[1],
                                                                columns=columns)
        for test, expected in zip(slice_value, test_values[2]):
            assert_almost_equal(test,
                                expected,
                                2,
                                "Slice with with value is not correct. Actual {0} should be {1}".
                                format(test,
                                       expected))

    def create_basic_table(self):
        self.test_continuance_table = ContinuanceTable(name='Test', membership=1000, avg_cost=1000)
        self.test_continuance_table.add_value(self.session, maximum=0, membership=1000, maxed_value=0)
        self.test_continuance_table.add_value(self.session, maximum=500, membership=500, maxed_value=450)
        self.test_continuance_table.add_value(self.session, maximum=1000, membership=250, maxed_value=750)

    #Class methods
    def test_find(self):
        test_table1 = ContinuanceTable(name='Test1', membership=1000, avg_cost=1000)
        test_table2 = ContinuanceTable(name='Test2', membership=1500, avg_cost=100)
        self.session.add(test_table1)
        self.session.add(test_table2)
        self.session.commit()
        found_table = ContinuanceTable.find(self.session, "Test1")
        assert found_table.id == test_table1.id, 'Table was not found'

    #Private methods
    def test_repr(self):
        test_table = ContinuanceTable(name='Test1')
        self.session.add(test_table)
        self.session.commit()
        assert repr(test_table) == "<ContinuanceTable id={0}, name={1}>".format(test_table.id, test_table.name), \
            "Test representation not correct, actual representation {0}".format(test_table)

    #Instance methods
    def test_add_value(self):
        self.test_continuance_table = ContinuanceTable(name='Test', membership=1000, avg_cost=1000)
        self.test_continuance_table.add_value(self.session, maximum=0, membership=1000, maxed_value=0)
        table = self.session.query(ContinuanceTable).filter(ContinuanceTable.name == 'Test').one()
        assert self.session.query(ContinuanceTableRow).filter(ContinuanceTableRow.continuance_table_id == table.id,
                                                            ContinuanceTableRow.maximum == 0).count() == 1, \
            'Value was not added'

    def test_slice_values_high(self):
        self.create_basic_table()
        test_values = [[500, None, [450]], [600, None, [510]]]
        for value in test_values:
            self.check_continuance_value(value)

    def test_slice_values_high_and_low(self):
        self.create_basic_table()
        test_values = [[1000, 500, [300]], [1000, 600, [240]], [600, 500, [60]]]
        for value in test_values:
            self.check_continuance_value(value)

    def test_slice_values_preventive(self):
        self.test_continuance_table = ContinuanceTable(name='Test', membership=1000, avg_cost=1000)
        self.test_continuance_table.add_value(self.session, maximum=0, membership=1000, maxed_value=0,
                                              preventive_care_value=0)
        self.test_continuance_table.add_value(self.session, maximum=500, membership=500, maxed_value=450,
                                              preventive_care_value=50)
        self.test_continuance_table.add_value(self.session, maximum=1000, membership=250, maxed_value=750,
                                              preventive_care_value=75)
        test_values = [[500, None, [50]], [600, None, [55]], [1000, 500, [25]], [1000, 600, [20]], [600, 500, [5]]]
        for value in test_values:
            self.check_continuance_value(value, ['preventive_care_value'])

    def test_slice_values_multiple_columns(self):
        self.test_continuance_table = ContinuanceTable(name='Test', membership=1000, avg_cost=1000)
        self.test_continuance_table.add_value(self.session, maximum=0, membership=1000, maxed_value=0, generic_value=0,
                                              preferred_value=0, non_preferred_value=0, specialty_value=0)
        self.test_continuance_table.add_value(self.session, maximum=500, membership=500, maxed_value=450,
                                              generic_value=15, preferred_value=5, non_preferred_value=3,
                                              specialty_value=0.1)
        self.test_continuance_table.add_value(self.session, maximum=1000, membership=1000, maxed_value=750,
                                              generic_value=25, preferred_value=7, non_preferred_value=5,
                                              specialty_value=5)
        test_values = [[500, None, [15, 5, 3, 0.1]],
                       [600, None, [17, 5.4, 3.4, 1.08]],
                       [1000, 500, [10, 2, 2, 4.9]],
                       [1000, 600, [8, 1.6, 1.6, 3.92]],
                       [600, 500, [2, .4, .4, .98]]]
        for value in test_values:
            self.check_continuance_value(value, ['generic_value', 'preferred_value', 'non_preferred_value',
                                         'specialty_value'])