import os
import csv

import av
from av.continuancetable import ContinuanceTable
from av.database.connection import Session, engine
from av.database.base import Base


def load_file(file_name, session, field_names):
    data_path = os.path.join(os.path.dirname(__file__), 'data', file_name)

    table_name = file_name.replace('.csv', '').title().replace('_', '')

    table = ContinuanceTable(name=table_name)

    with open(data_path, newline='') as csvfile:
        table_rows = csv.reader(csvfile)
        for row in table_rows:
            if row[0] != 'Maximum':
                fields = {}

                if row[0] != 'Unlimited':
                    if row[0] == '0':
                        table.membership = row[1]
                    fields = {}
                    for index, value in enumerate(field_names):
                        fields[value] = row[index]
                    table.add_value(session, **fields)
                else:
                    table.avg_cost = row[2]
                    for index, value in enumerate(field_names):
                        fields[value] = row[index]
                    fields['maximum'] = av.MAX_VALUE
                    table.add_value(session, **fields)

        session.add(table)
        session.commit()


def seed_data():
    session = Session()

    Base.metadata.create_all(engine)

    files = ['bronze_integrated.csv',
             'gold_integrated.csv',
             'platinum_integrated.csv',
             'silver_integrated.csv']
    integrated_fields = ['maximum',
                         'membership',
                         'maxed_value',
                         'er_value',
                         'er_utilization',
                         'ip_value',
                         'ip_admits',
                         'primary_care_value',
                         'primary_care_utilization',
                         'specialist_value',
                         'specialist_utilization',
                         'mental_health_value',
                         'mental_health_utilization',
                         'imaging_value',
                         'imaging_utilization',
                         'speech_value',
                         'speech_utilization',
                         'occupation_physical_therapy_value',
                         'occupation_physical_therapy_utilization',
                         'preventive_care_value',
                         'preventive_care_utilization',
                         'laboratory_value',
                         'laboratory_utilization',
                         'x_rays_value',
                         'x_ray_utilization',
                         'skilled_nursing_value',
                         'skilled_nursing_utilization',
                         'generic_value',
                         'generic_utilization',
                         'preferred_value',
                         'preferred_utilization',
                         'non_preferred_value',
                         'non_preferred_utilization',
                         'specialty_value',
                         'specialty_utilization']
    for file in files:
        load_file(file, session, integrated_fields)

    medical_files = ['bronze_medical.csv',
                     'gold_medical.csv',
                     'platinum_medical.csv',
                     'silver_medical.csv']
    medical_fields = ['maximum',
                      'membership',
                      'maxed_value',
                      'er_value',
                      'er_utilization',
                      'ip_value',
                      'ip_admits',
                      'primary_care_value',
                      'primary_care_utilization',
                      'specialist_value',
                      'specialist_utilization',
                      'mental_health_value',
                      'mental_health_utilization',
                      'imaging_value',
                      'imaging_utilization',
                      'speech_value',
                      'speech_utilization',
                      'occupation_physical_therapy_value',
                      'occupation_physical_therapy_utilization',
                      'preventive_care_value',
                      'preventive_care_utilization',
                      'laboratory_value',
                      'laboratory_utilization',
                      'x_rays_value',
                      'x_ray_utilization',
                      'skilled_nursing_value',
                      'skilled_nursing_utilization']
    for file in medical_files:
        load_file(file, session, medical_fields)

    drug_files = ['bronze_drug.csv',
                  'gold_drug.csv',
                  'platinum_drug.csv',
                  'silver_drug.csv']
    drug_fields = ['maximum',
                   'membership',
                   'maxed_value',
                   'generic_value',
                   'generic_utilization',
                   'preferred_value',
                   'preferred_utilization',
                   'non_preferred_value',
                   'non_preferred_utilization',
                   'specialty_value',
                   'specialty_utilization']
    for file in drug_files:
        load_file(file, session, drug_fields)
