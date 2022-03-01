#
#
# ReadBMA : read BMA bma_zone and district GIS files and 
#           product 'Zone_SEQ' code. 
#
#
import numpy as np
import pandas as pd
import geopandas as gpd
import argparse
from tabulate import tabulate
ABBR_FIX = {   '1016' : 'B_KokYai',
               '1020' : 'B_KokNoi',
               '1018' : 'Kl_Sann',
               '1046' : 'Kl_SamWa',
               '1033' : 'Kl_Toei',
               '1031' : 'B_Kolam',
            }

def Restructure(ZONE, DSTR): 
    dfZone = gpd.read_file( ZONE, encoding='tis-620' )
    dfDstr = gpd.read_file( DSTR, encoding='tis-620'  )

    def MakeAbbrev(row):
        abb = "".join( row.dname_e.split()) 
        MAX_CH = 8
        if len(abb)>MAX_CH:
            abb = abb[:MAX_CH]
        #import pdb; pdb.set_trace()
        if row.dcode in ABBR_FIX.keys(): abb=ABBR_FIX[row.dcode]
        return abb 

    dfDstr['DNAME_ABB'] = dfDstr.apply( MakeAbbrev, axis='columns' )
    dfAbbr = dfDstr[['dcode', 'dname', 'DNAME_ABB', 'no_male', 
                     'no_female', 'AREA', 'geometry' ]].copy()
    dfAbbr['AREA_KM'] = (dfAbbr['AREA']/1.E6).round(1)
    dfAbbr['geometry'] = dfAbbr['geometry'].centroid

    dfAbbrZone = gpd.sjoin( dfAbbr, dfZone, how='inner', predicate='intersects' )
    dfAbbrZone.drop( labels=['index_right','z_name_e', 'no_male_right', 'no_female_right',
                    'no_house','no_commu','z_area' ], axis='columns', inplace=True )
    dfAbbrZone.rename( columns={'no_male_left':'no_male', 'no_female_left':'no_female' } , 
                        inplace=True )
    dfAbbrZone['no_popu'] = dfAbbrZone['no_male'] + dfAbbrZone['no_female'] 
    #print( dfAbbrZone.z_code.value_counts() )
    print( 'Total district : ', dfAbbrZone.z_code.value_counts().sum() )
    dfAbbrZone['DNAME_SEQ'] = list(np.arange(1, len(dfDstr)+1))
    def MakeZoneSeq( row ):
        #import pdb; pdb.set_trace()
        return f'{row.z_code[1:]}{row.DNAME_SEQ:02d}'
    dfAbbrZone['ZONE_SEQ'] = dfAbbrZone.apply( MakeZoneSeq, axis='columns' )
    return dfAbbrZone

############################################################################

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-f', '--format', dest='tablefmt', default='pretty',
                    help='table formats : pretty, html ')

args = parser.parse_args()
ZONE = './BMA20k/BMAZone/bma_zone.shp'
DSTR = './BMA20k/District/district.shp'

dfAbbrZone = Restructure(ZONE, DSTR) 

for name,group in dfAbbrZone.groupby( ['z_code'] ):
    POPU = group.no_popu.sum()
    AREA = group.AREA_KM.sum()
    if args.tablefmt=='html':
        print( f'<header><h1>Zone: {name} Popu:{POPU:,d} Area: {AREA:.1f} SQ.KM.<ht></header>')
    else:
        print( f'===กลุ่มเขต: {name}   ประชากร:{POPU:,d} พื้นที่กลุ่มเขต: {AREA:.1f} ตร.กม. ===')
    tab =  group[['ZONE_SEQ','z_name','DNAME_ABB','dname','AREA_KM','no_popu']].copy()
    tab['no_popu'] = tab['no_popu'].map( '{:,d}'.format )
    print( tabulate( tab ,  tablefmt=args.tablefmt, headers=['CODE', 'District',
         'Zone','เขต','พื้นที่ ตร.กม.','ประชากร'  ], showindex=False) )
#import pdb; pdb.set_trace()
if 0:
    dfAbbrZone.to_file('dfAbbrZone.gpkg', layer='District', driver='GPKG' )

