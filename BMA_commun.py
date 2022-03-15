#
#
# rename 'Commnunity Code' to ID4
#
#
import numpy as np
import pandas as pd
import geopandas as gpd
import argparse
from tabulate import tabulate

COMMU_FILE = './BMA20k/Community/community.shp'

dfComm = gpd.read_file( COMMU_FILE , encoding='tis-620'  )
dfComm['ID4'] =dfComm['COMM_ID'].str[-4:]
for distr, commu in  dfComm.groupby(['DCODE'] ):
    print( distr, commu )
    #print( distr, len(commu) )

dfComm.to_file('dfComm_ID4.gpkg', layer='Commnunity', driver='GPKG' )
import pdb; pdb.set_trace()

