import os
import csv

from av.continuancetable import ContinuanceTable, ContinuanceTableRow
from av.database.connection import Session, engine
from av.database.base import Base

def load_file(file_name, session):
    data_path = os.path.join(os.path.dirname(__file__), 'data', file_name)

    table_name = file_name.replace('.csv', '').title().replace('_', '')

    table = ContinuanceTable(name=table_name)

    with open(data_path, newline='') as csvfile:
        table_rows = csv.reader(csvfile)
        for row in table_rows:
            if row[0] != 'Maximum':
                if row[0] != 'Unlimited':
                    if row[0] == '0':
                        table.membership = row[1]
                    table.add_value(session,
                                    maximum=row[0],
                                    membership=row[1],
                                    maxed_value=row[2],
                                    preventive_care_value=row[3],
                                    preventive_care_utilization=row[4])
                else:
                    table.avg_cost = row[2]
        session.add(table)
        session.commit()

def seed_data():
    session = Session()

    Base.metadata.create_all(engine)

    files = ['bronze_integrated.csv', 'gold_integrated.csv', 'platinum_integrated.csv', 'silver_integrated.csv']
    for file in files:
        load_file(file, session)