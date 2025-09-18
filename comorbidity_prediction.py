import pandas as pd
import time
import re
import pprint
import numpy as np
import multiprocessing
from multiprocessing import  Pool

# Create a connection to the working group's Neo4j database of MIMIC-III data
from neo4j import GraphDatabase
driver=GraphDatabase.driver(uri="neo4j://127.0.0.1:7687", auth=('neo4j','9867418080'))
session=driver.session()

def comorbidities_of(prob_list):
    query = '''
    MATCH (prob1:Problem)<-[:HAS_PROBLEM]-(pt:Patients)
    WHERE prob1.description in {prob_list}
    WITH distinct(pt) AS patients
    MATCH (patients)-[:HAS_PROBLEM]->(prob2:Problem)
    RETURN prob2.description as Description, prob2.cui AS CUI, count(prob2.description) as Number
    ORDER BY Number DESC
    '''.format(prob_list=prob_list)
    comorbidities = session.run(query)
    comorbidities = pd.DataFrame([dict(record) for record in comorbidities])
    
    query = '''
    MATCH (excluded:Problem)
    WHERE excluded.description in {prob_list}
    WITH collect(excluded) as excluded
    MATCH (pt:Patients)-[:HAS_PROBLEM]->(prob:Problem)
    WITH excluded, pt, collect(prob) as problems
    WHERE NONE (prob in problems where prob in excluded)
    MATCH (pt)-[:HAS_PROBLEM]-(prob2:Problem)
    RETURN prob2.description as Description, prob2.cui AS CUI, count(prob2.description) as Number
    ORDER BY Number DESC
    '''.format(prob_list=prob_list)
    gen_problems = session.run(query)
    gen_problems = pd.DataFrame([dict(record) for record in gen_problems])
    
    gen_pop_total = sum(gen_problems['Number'])
    gen_problems['Gen_pop_proportion'] = gen_problems['Number']/gen_pop_total
    
    comorb_total = sum(comorbidities['Number'])
    comorbidities['Comorbidities_proportion'] = comorbidities['Number']/comorb_total
    
    comorbidities = comorbidities[comorbidities['Number'] > 200/len(prob_list)]
    
    # Merge the "Gen_pop_proportion" column from gen_problems into comorbidities
    comorbidities = pd.merge(comorbidities, gen_problems, on=['CUI', 'Description'])
    
    comorbidities['Odds_Ratio'] = (comorbidities['Comorbidities_proportion']/comorbidities['Gen_pop_proportion'])
    comorbidities.sort_values(by='Odds_Ratio', ascending=False, inplace=True)
    
    return comorbidities.loc[:,['Description', 'Odds_Ratio']].head(20)

