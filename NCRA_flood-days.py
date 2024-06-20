# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 09:07:15 2024

@author: bhague

This code downloads, analyses and plots flood days under 10 , 20, 38 and 60 cm 
SLR for NCRA, based on Hague & Talke (2024 - https://doi.org/10.1029/2023EF003993)

Flood days data files at: www.doi.org/10.6084/m9.figshare.24328903.
SLR files at: https://zenodo.org/records/6382554
"""

import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import glob
plt.rcParams["font.family"] = "Calibri"
import matplotlib
from string import ascii_lowercase
from cartopy import crs as ccrs
import cartopy.feature as cfeature

#define directory being used - change as required
temp_dir='C:\\Users\\bhague\\Documents\\NCRA\\'

##define functions to be used
def project_MSL_NASA(msl_df,lat,lon,rcp='370'):
    """
    msl_df is the NASA nc file in a df: xr.open_dataset('{}total_ssp{}_medium_confidence_values.nc'.format(temp_dir,rcp)).to_dataframe().reset_index()
    obs_df is the tide gauge record of still water level: obs_df=pd.read_csv('{}anchors_melbourne_adj.csv'.format(temp_dir),parse_dates=['UTC_DT']).set_index('UTC_DT')
    lat, lon, float, tide gauge location
    rcp = '370' for ssp 3- 7.0, '585' for ssp585 for ssp 5 - 8.5
    epoch_start, epoch_end is first and last +1 YYYY-MM-DD for aligning mean to baseline. Can be False if want to be 0
    """
    ### Find relevant data based on lat/lon
    #define difference
    msl_df['diff']=np.sqrt((msl_df['lat']-lat)**2 +(msl_df['lon']-lon)**2)
    #dropnans
    msl_df=msl_df.dropna()
    #smallest difference
    site_msl=msl_df[msl_df['diff']==msl_df['diff'].min()].copy()    
    ## select appropriate percentiles and convert to metres
    proj_df=pd.DataFrame(index=np.arange(2020,2151,10))
    #some locations have duplicate identical projections, select the first one
    proj_df['SL_LOW-ssp{}'.format(rcp)]=site_msl[site_msl['quantiles']==0.05]['sea_level_change'][0:14].values/1000
    proj_df['SL_MID-ssp{}'.format(rcp)]=site_msl[site_msl['quantiles']==0.50]['sea_level_change'][0:14].values/1000
    proj_df['SL_HIGH-ssp{}'.format(rcp)]=site_msl[site_msl['quantiles']==0.95]['sea_level_change'][0:14].values/1000
    ##interpolate SLR to annual and add baseline MSL
    #initialise df
    out_df=pd.DataFrame(index=np.arange(2005,2151,1))
    out_df=pd.merge(out_df,proj_df,left_index=True, right_index=True, how='outer')
    for col in out_df.columns:
        #linear interpolation following the NASA website
        out_df[col]=out_df[col].interpolate('linear')
    return out_df

### import IPCC AR6 MSL projections used
##SSP3-7.0
#import
msl_df_370=xr.open_dataset('{}total_ssp370_medium_confidence_values.nc'.format(temp_dir)).to_dataframe().reset_index()
#trim to Australian region
msl_df_370=msl_df_370[(msl_df_370['lat'] > -43) & (msl_df_370['lat'] < -9) & (msl_df_370['lon'] > 112) & (msl_df_370['lon'] < 155)].copy()

##SSP3-8.5
#import
msl_df_585=xr.open_dataset('{}total_ssp585_medium_confidence_values.nc'.format(temp_dir)).to_dataframe().reset_index()
#trim to Australian region
msl_df_585=msl_df_585[(msl_df_585['lat'] > -43) & (msl_df_585['lat'] < -9) & (msl_df_585['lon'] > 112) & (msl_df_585['lon'] < 155)].copy()

### import exceedances data from Hague & Talke (2024)
all_files=glob.glob('{}HT_exceedances_*-t0s0.csv'.format(temp_dir))
exceed_dict={}
for filename in all_files:
    df = pd.read_csv(filename).set_index('Year')
    scenario='{}-ssp{}'.format(filename.split('-')[1],filename.split('ssp')[-1].split('-')[0])
    exceed_dict.update({scenario:df})
exceed_df=pd.concat(exceed_dict)

### find days for each SLR increment of interest via years/SSPs/site combinations
#import anchors site info
anchors_info=pd.read_csv('https://thredds.nci.org.au/thredds/fileServer/fx31/publications/ANCHORS/pdfs/ANCHORS_latlon.csv').set_index('ANCHORS')
#initialise dataframes for minor, record and annmax.
exceed_selected_minor=pd.DataFrame()
exceed_selected_record=pd.DataFrame()
exceed_selected_annmax=pd.DataFrame()
#define SLR increments
for slr in [0.06,0.1,0.2,0.38,0.6,1.0]:
    print(slr)
    #perform for each site
    for site in anchors_info.index:
        print(site)
        #find closest projected MSL series for each site's lat/lon for each SSP
        proj_MSL_site_370=project_MSL_NASA(msl_df_370,anchors_info.loc[site].lat,anchors_info.loc[site].lon,rcp='370')
        proj_MSL_site_585=project_MSL_NASA(msl_df_585,anchors_info.loc[site].lat,anchors_info.loc[site].lon,rcp='585')
        #combine
        proj_MSL_site=pd.merge(proj_MSL_site_370,proj_MSL_site_585,left_index=True,right_index=True)
        #find the first year where SLR amount is exceeded.
        years= (proj_MSL_site > slr).idxmax()
        #define site as a string as per naming in files
        site_str=site.lower().replace(' ','-')
        for scenario in years.index:  
            print(scenario)
            #only include data if SLR amnount is reached.
            try:
                #find minor/annmax/record flooding at site in the year
                site_exceed_minor=exceed_df.loc[scenario].filter(regex='minor').filter(regex=site_str).loc[years[scenario]].reset_index()
                site_exceed_record=exceed_df.loc[scenario].filter(regex='obsmax').filter(regex=site_str).loc[years[scenario]].reset_index()
                site_exceed_annmax=exceed_df.loc[scenario].filter(regex='p99.7-').filter(regex=site_str).loc[years[scenario]].reset_index()     
                #rename index to include SLR amount, year, scenario
                year=site_exceed_minor.columns[1]
                site_exceed_minor['index'] = ['{}_{}m_{}_{}'.format(string,slr, year,scenario) for string in site_exceed_minor['index']]
                site_exceed_record['index'] = ['{}_{}m_{}_{}'.format(string,slr, year,scenario) for string in site_exceed_record['index']]
                site_exceed_annmax['index'] = ['{}_{}m_{}_{}'.format(string,slr, year,scenario) for string in site_exceed_annmax['index']]             
                #renaming columns
                site_exceed_minor=site_exceed_minor.rename(columns={year:'days'})
                site_exceed_record=site_exceed_record.rename(columns={year:'days'})
                site_exceed_annmax=site_exceed_annmax.rename(columns={year:'days'})
                #add to overall
                exceed_selected_minor=pd.concat([exceed_selected_minor,site_exceed_minor])
                exceed_selected_record=pd.concat([exceed_selected_record,site_exceed_record])
                exceed_selected_annmax=pd.concat([exceed_selected_annmax,site_exceed_annmax])
            except:
                print('SLR not reached in scenario')
### save datafiles for further analysis
#define variables for each df
names=['{}minor_exceeds.csv'.format(temp_dir),'{}record_exceeds.csv'.format(temp_dir),'{}annmax_exceeds.csv'.format(temp_dir)]
type_str=['minor-','obsmax-','p99.7-']
dfs = [exceed_selected_minor, exceed_selected_record,exceed_selected_annmax]
for i in range(3):
    df=dfs[i].copy()
    #expand out info column
    df['site']=[string.split(type_str[i])[1].split('_')[0].replace('-',' ').title() for string in df['index']]
    df['pc']=[string.split('_')[1] for string in df['index']]
    df['SLR']=[string.split('_')[2] for string in df['index']]
    df['Year']=[string.split('_')[3] for string in df['index']]
    df['Scenario']=[string.split('_')[5] for string in df['index']]
    #export
    df[['site','days','SLR','Year','Scenario','pc']].set_index('site').to_csv(names[i])

### stats
#import lat lon info
anchors_info=pd.read_csv('https://thredds.nci.org.au/thredds/fileServer/fx31/publications/ANCHORS/pdfs/ANCHORS_latlon.csv').set_index('ANCHORS')
for file in glob.glob('{}*_exceeds.csv'.format(temp_dir)):
    #import data
    minor=pd.read_csv(file).set_index('site')
    #initialise df
    summary_df=pd.DataFrame()
    #define SLR increments
    for SLR in ['0.06m', '0.2m', '0.38m', '0.6m','1.0m']:
        #define percentiles
        for pc in [0.1, 0.5, 0.9]:
            #compute site average of all scenarios
            data_df=minor[(minor['pc']==pc) & (minor['SLR']==SLR)].reset_index().groupby(by='site').mean()[['days']]
            #compute national average
            data_df.loc['National','days'] =data_df.mean()['days']
            #merge with existing
            summary_df=pd.merge(summary_df,data_df,left_index=True,right_index=True, how='outer')
            #change col name
            summary_df= summary_df.rename(columns={'days':'{} {}th percentile'.format(SLR,int(pc*100))})
    #combine with lat/lon info
    summary_df=pd.merge(anchors_info[['lat','lon']],summary_df,left_index=True, right_index=True,how='right')
    #output
    summary_df.to_csv(file.replace('.csv','_means.csv'))

###plots 
type_str_dict={'minor':'minor impact','record':'observed maximum','annmax':'observed once-a-year'}
for file in glob.glob('{}*_exceeds_means.csv'.format(temp_dir)):
    print(file)
    #import data
    minor=pd.read_csv(file).set_index('site')
    #initialise plot
    fig = plt.figure(figsize=(23,34))
    fig.suptitle('Annual exceedances of {} level under sea-level rise increments'.format(type_str_dict[file.split('\\')[-1].split('_')[0]]),fontsize=28,y=0.91)
    matplotlib.rcParams.update({'font.size': 18}) 
    for i in range(15):
        print(i)
        selected=minor[['lat','lon',minor.columns[i+2]]].copy()
        national=selected.loc['National'][minor.columns[i+2]]
        ax = fig.add_subplot(5, 3, i+1, projection=ccrs.PlateCarree())
        plt.title('({}) {}'.format(ascii_lowercase[i],minor.columns[i+2]),fontsize=20)
        reversed_color_map = plt.cm.get_cmap('viridis').reversed()
        selected['size']=100
        sc=ax.scatter(selected['lon'], selected['lat'], c=selected[minor.columns[i+2]], cmap=reversed_color_map,transform=ccrs.PlateCarree(),s=selected['size'],edgecolors='black')
        ax.add_feature(cfeature.COASTLINE)
        states_provinces = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='50m',
                facecolor='none')
        ax.add_feature(states_provinces, edgecolor='gray')
        ax.text(135,-26,'National mean: \n {} days'.format(np.round(national,1)),ha='center',va='center')
        cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
        cbar=plt.colorbar(sc,cax)
        cbar.set_label('Annual exceedances', rotation=270, labelpad=20)
        ax.set_extent([112, 155, -43, -9])
    fig.savefig(file.replace('.csv','.png'), dpi=600,bbox_inches='tight') 
    plt.close()
        
### differences
anchors_info=pd.read_csv('https://thredds.nci.org.au/thredds/fileServer/fx31/publications/ANCHORS/pdfs/ANCHORS_latlon.csv').set_index('ANCHORS')
for file in glob.glob('{}*_exceeds_means.csv'.format(temp_dir)):
    #import data
    minor=pd.read_csv(file).set_index('site')
    #initialise df
    diff_df=pd.DataFrame(index=minor.index)
    #define SLR increments
    for SLR in ['0.2m', '0.38m', '0.6m','1.0m']:
        #define percentiles
        for pc in [10, 50, 90]:
            #compute site average of all scenarios
            diff_df['{} {}th percentile'.format(SLR,pc)] = minor['{} {}th percentile'.format(SLR,pc)] - minor['0.06m {}th percentile'.format(pc)]
    #combine with lat/lon info
    diff_df=pd.merge(anchors_info[['lat','lon']],diff_df,left_index=True, right_index=True,how='right')
    #output
    diff_df.to_csv(file.replace('.csv','_diff.csv'))
#plot    
type_str_dict={'minor':'minor impact','record':'observed maximum','annmax':'observed once-a-year'}
for file in glob.glob('{}*_exceeds_means_diff.csv'.format(temp_dir)):
    print(file)
    #import data
    minor=pd.read_csv(file).set_index('site')
    #initialise plot
    fig = plt.figure(figsize=(23,29))
    fig.suptitle('Annual exceedances of {} level under sea-level rise increments: \n difference to 0.06 m '.format(type_str_dict[file.split('\\')[-1].split('_')[0]]),fontsize=28,y=0.91)
    matplotlib.rcParams.update({'font.size': 18}) 
    for i in range(12):
        print(i)
        selected=minor[['lat','lon',minor.columns[i+2]]].copy()
        national=selected.loc['National'][minor.columns[i+2]]
        ax = fig.add_subplot(4, 3, i+1, projection=ccrs.PlateCarree())
        plt.title('({}) {}'.format(ascii_lowercase[i],minor.columns[i+2]),fontsize=20)
        reversed_color_map = plt.cm.get_cmap('viridis').reversed()
        selected['size']=100
        sc=ax.scatter(selected['lon'], selected['lat'], c=selected[minor.columns[i+2]], cmap=reversed_color_map,transform=ccrs.PlateCarree(),s=selected['size'],edgecolors='black')
        ax.add_feature(cfeature.COASTLINE)
        states_provinces = cfeature.NaturalEarthFeature(
                category='cultural',
                name='admin_1_states_provinces_lines',
                scale='50m',
                facecolor='none')
        ax.add_feature(states_provinces, edgecolor='gray')
        ax.text(135,-26,'National mean: \n {} days'.format(np.round(national,1)),ha='center',va='center')
        cax = fig.add_axes([ax.get_position().x1+0.01,ax.get_position().y0,0.02,ax.get_position().height])
        cbar=plt.colorbar(sc,cax)
        cbar.set_label('Annual exceedances', rotation=270, labelpad=20)
        ax.set_extent([112, 155, -43, -9])
    fig.savefig(file.replace('.csv','.png'), dpi=600,bbox_inches='tight') 
    plt.close()
