from sqlalchemy import Column, Integer, Float, String, ForeignKey, desc
from sqlalchemy.orm import relationship, backref

from av.database.base import Base


class ContinuanceTable(Base):
    __tablename__ = 'continuance_tables'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    membership = Column(Integer)
    avg_cost = Column(Float)

    def __interpolate_values(self, session, value, columns):
        lower_row_query = ("maximum <= {0} and continuance_table_id = {1}".
                           format(value, self.id))
        lower_row = (session.query(ContinuanceTableRow).
                     filter(lower_row_query).
                     order_by(desc(ContinuanceTableRow.maximum)).first())
        lower_values = [getattr(lower_row, column) for column in columns]
        if lower_row.maximum != value:
            upper_row_query = ("maximum > {0} and continuance_table_id = {1}".
                               format(value, self.id))
            upper_row = (session.query(ContinuanceTableRow).
                         filter(upper_row_query).
                         order_by(ContinuanceTableRow.maximum).first())
            upper_values = [getattr(upper_row, column) for column in columns]
            slice_values = [(value - lower_row.maximum) /
                            (upper_row.maximum - lower_row.maximum) *
                            (upper_value - lower_value) + lower_value
                            for (upper_value, lower_value) in
                            zip(upper_values, lower_values)]
        else:
            slice_values = lower_values
        return slice_values

    def __repr__(self):
        return "<ContinuanceTable id={0}, name={1}>".format(self.id, self.name)

    @classmethod
    def find(cls, session, table_name):
        return (session.query(ContinuanceTable).
                filter(ContinuanceTable.name == table_name).first())

    def add_value(self, session, **kwargs):
        new_row = ContinuanceTableRow()
        new_row.continuance_table = self
        for column, value in kwargs.items():
            setattr(new_row, column, value)
        session.add(new_row)
        session.commit()

    def inverse(self, session, inverse_value):
        lower_row_query = ("maxed_value <= {0} and continuance_table_id = {1}".
                           format(inverse_value, self.id))
        lower_row = (session.query(ContinuanceTableRow).
                     filter(lower_row_query).
                     order_by(desc(ContinuanceTableRow.maxed_value)).first())
        if lower_row.maxed_value == inverse_value:
            inverse = lower_row.maximum
        else:
            upper_row_query = ("maxed_value > {0} and continuance_table_id = "
                               "{1}".format(inverse_value, self.id))
            upper_row = (session.query(ContinuanceTableRow).
                         filter(upper_row_query).
                         order_by(ContinuanceTableRow.maxed_value).
                         first())
            inverse = ((inverse_value - lower_row.maxed_value) /
                       (upper_row.maxed_value - lower_row.maxed_value) *
                       (upper_row.maximum - lower_row.maximum) +
                       lower_row.maximum)
        return inverse

    def slice(self, session, high, low=0, columns=['maxed_value']):
        high_values = self.__interpolate_values(session, high, columns)
        if low != 0:
            low_values = self.__interpolate_values(session, low, columns)
        else:
            low_values = [0] * len(columns)
        return (
            [upper - lower for (upper, lower) in zip(high_values, low_values)])


class ContinuanceTableRow(Base):
    __tablename__ = 'continuance_table_rows'

    id = Column(Integer, primary_key=True)
    continuance_table_id = Column(Integer, ForeignKey('continuance_tables.id'))
    er_value = Column(Float)
    er_utilization = Column(Float)
    generic_value = Column(Float)
    generic_utilization = Column(Float)
    imaging_value = Column(Float)
    imaging_utilization = Column(Float)
    ip_value = Column(Float)
    ip_admits = Column(Float)
    laboratory_value = Column(Float)
    laboratory_utilization = Column(Float)
    maximum = Column(Integer)
    maxed_value = Column(Float)
    membership = Column(Integer)
    mental_health_value = Column(Float)
    mental_health_utilization = Column(Float)
    non_preferred_value = Column(Float)
    non_preferred_utilization = Column(Float)
    occupation_physical_therapy_value = Column(Float)
    occupation_physical_therapy_utilization = Column(Float)
    preferred_value = Column(Float)
    preferred_utilization = Column(Float)
    preventive_care_value = Column(Float)
    preventive_care_utilization = Column(Float)
    primary_care_value = Column(Float)
    primary_care_utilization = Column(Float)
    skilled_nursing_value = Column(Float)
    skilled_nursing_utilization = Column(Float)
    specialist_value = Column(Float)
    specialist_utilization = Column(Float)
    specialty_value = Column(Float)
    specialty_utilization = Column(Float)
    speech_value = Column(Float)
    speech_utilization = Column(Float)
    x_rays_value = Column(Float)
    x_ray_utilization = Column(Float)

    continuance_table = (
        relationship("ContinuanceTable",
                     backref=backref('continuance_table_rows', order_by=id)))
