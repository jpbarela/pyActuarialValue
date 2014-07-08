from sqlalchemy import Column, Integer, Float, String, ForeignKey, desc
from sqlalchemy.orm import relationship, backref

from av.database.base import Base

class ContinuanceTable(Base):
    __tablename__ = 'continuance_tables'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    membership = Column(Integer)
    avg_cost = Column(Float)

    def __interpolate_value(self, session, value, column):
        value_filter_query = "maximum <= {0} and continuance_table_id = {1}".format(value, self.id)
        lower_row = session.query(ContinuanceTableRow).filter(value_filter_query).\
            order_by(desc(ContinuanceTableRow.maximum)).first()
        low_value = getattr(lower_row, column)
        if lower_row.maximum != value:
            upper_row_query = "maximum > {0} and continuance_table_id = {1}".format(value, self.id)
            upper_row = session.query(ContinuanceTableRow).filter(upper_row_query).\
                order_by(ContinuanceTableRow.maximum).first()
            upper_value = getattr(upper_row, column)
            maxed_value = (value - lower_row.maximum)/(upper_row.maximum - lower_row.maximum) * \
                          (upper_value - low_value) + low_value
        else:
            maxed_value = low_value
        return maxed_value

    @classmethod
    def find(cls, session, table_name):
        return session.query(ContinuanceTable).filter(ContinuanceTable.name == table_name).first()

    def add_value(self, session, **kwargs):
        new_row = ContinuanceTableRow()
        new_row.continuance_table = self
        for column, value in kwargs.items():
            setattr(new_row, column, value)
        session.add(new_row)
        session.commit()

    def slice(self, session, high, low=0, column='maxed_value'):
        high_value = self.__interpolate_value(session, high, column)
        if low != 0:
            low_value = self.__interpolate_value(session, low, column)
        else:
            low_value = 0
        return high_value - low_value

class ContinuanceTableRow(Base):
    __tablename__ = 'continuance_table_rows'

    id = Column(Integer, primary_key=True)
    maximum = Column(Integer)
    membership = Column(Integer)
    maxed_value = Column(Float)
    continuance_table_id = Column(Integer, ForeignKey('continuance_tables.id'))
    preventive_care_value = Column(Float)
    preventive_care_utilization = Column(Float)

    continuance_table = relationship("ContinuanceTable", backref=backref('continuance_table_rows', order_by=id))
