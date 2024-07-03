# hazards-coastal
Code and plots for 'coastal and estuarine flooding' and 'coastal erosion and shoreline change' NCRA hazards

## Description
GitHub repository for ACS Coastal Hazard Team to store, track and develop code. 

## Indices considered by the hazard team:
- Mean Sea Level (Essential Climate Variable)
- Flood days
- Flood extent of 1% AEP extreme water level
- Change in frequency (multiplication factor) of storm tide levels (flooding metric) and total water levels (erosion metric).

## Products:
Global Warming Levels are unsuitable for understanding sea-level rise (SLR)-related hazards due to SLR continuing long after temperatures stabilise. 
We selected several SLR increments (SLRI) relative to the IPCC AR6 baseline of 1995 – 2014 for the National Climate Risk Assessment as follows:
- 0.06 m: Approximately 2010-2029 mean, the "present-day" period used in NCRA)
- 0.1 m: Approximate projected SLR at 2030
- 0.2 m: Approximate projected SLR at 2050
- 0.38 m: Approximate projected SLR GWL 2.0, assuming GWL 3.0 is reached in 2090.
- 0.6 m: Approximate projected SLR at GWL 3.0, assuming GWL 3.0 is reached in 2090.
- 1.0 m: Higher-end projected SLR consistent with jurisdictional planning benchmarks used in Australia (c.f., Dedekorkut-Howes et al. 2021, DOI: 10.1080/14693062.2020.1819766)
  
In terms of the colors:
- :green_circle: The data is available in its final official form
- :yellow_circle: The data creation is currently in progress and available soon
- :red_circle: The data processing has not yet started
- :white_circle: Not intended for delivery/not applicable

In terms of the methods:
- MSL: Regional sea level projection datasets are provided at yearly (2020 - 2150) under 5 SSPs (119, 126, 245, 370, 585) in NC format for Australian region (105E-165E, 5S-50S), rather than using the sea level rise increments.
* Flood days: These were calculated using results from Hague & Talke (2024) [https://doi.org/10.1029/2023EF003993]. This provides 1000 different future realisation of flood days, based on different ways of storm surges and tides coinciding. This assumes no change in future tides and storm surges, based on homogenised sea-level data and IPCC AR6 SLR projections. The original SLR projection source was reapplied to the data to re-express the results in terms of GWL, as follows:
  - Identify years in projection timeseries (for different SLR scenarios) where SLR equals the increment of interest
  - Use the flood days estimate for all scenarios to estimate an average 10th, 50th and 90th percentile estimate from.
- Flood extent: Refer: [https://github.com/AusClimateService/ncra_coastal_hazards/blob/main/Inundation_layers.html](https://htmlpreview.github.io/?https://github.com/AusClimateService/ncra_coastal_hazards/blob/main/Inundation_layers.html). The SLR increments are approximated using Year 2020 for SSP1-2.6 (0.06 m), 2030 for SSP1-2.6 (0.1 mm), 2050 for SSP2-4.5 (0.20 m), 2090 for SSP1-2.6 (0.38 m), 2090 for SSP5-8.5 (0.6 m), and 2100 for SSP5-8.5 (1 m). The underlying DEM has fundamental vertical accuracy of 0.3 m and horizontal accuracy of 0.8 m. The datafiles (geoJSON) are presented by Local Government Area.
* MF: All approaches use the formula of Hunter (2012) [https://doi.org/10.1007/s10584-011-0332-1] MF = exp(SLR/lambda), where lambda is the Gumbel scale parameter. This assumes no change in future tides and storm surges. Three different estimates of MF are obtained by fitting the Gumbel distribution to annual maxima of three different datasets:
  - quality controlled but unhomogenised tide gauge data from GESLA3 (Haigh et al. 2022) [https://doi.org/10.1002/gdj3.174]. These are files of MFSLR_GESLA3_MMALL_SLR<>.csv
  - storm-tide reanalysis of Colberg et al. (2019) [https://doi.org/10.5194/nhess-19-1067-2019]  (see column 'SWL_MFSLR_<>' in files of format MFSLR_ACSSH_MMALL_SLR<>.csv)
  - storm-tide reanalysis of Colberg et al. (2019) with addition of empirical estimate for shoreline wave setup from O'Grady et al. (2019) [https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018JC014871] (see column 'MTWL_MFSLR_<>' in files of format MFSLR_ACSSH_MMALL_SLR<>.csv)
  - For further information, please see: https://github.com/AusClimateService/ncra_coastal_hazards and the compiled markdown page https://htmlpreview.github.io/?https://github.com/AusClimateService/ncra_coastal_hazards/blob/main/Extreme_water_level_hazards.html
Both of which have an accurate description of the data and code for reference.

(Table was last updated 430pm 28/06/2024)

| Index/metric | SLRI data | SLRI 2D map |  SLRI change data |  SLRI change map |(Notes) |
|-----         | :-:      |:-:      |:-:            |:-:            |-----    |
| MSL |:green_circle:|:green_circle:|:white_circle:|:white_circle:|Data present as annual under SSP, not SLRI <br> Data is at /g/data/ia39/ncra/coastal/MSL|
| Flood days |:green_circle:|:green_circle:|:green_circle:|:green_circle:| Data is at /g/data/ia39/ncra/coastal/flood_days |
| Flood extent |:green_circle:|:green_circle:|:white_circle:|:white_circle:|geoJSON files at LGA scale information only. <br> Data is at /g/data/ia39/ncra/coastal/flood_extents|
| MF|:green_circle:|:green_circle:|:white_circle:|:white_circle:| Data is at /g/data/ia39/ncra/coastal/MF|

## Example of Climate Risk Overview information
The below plot shows that minor flooding will occur frequently in the future. Under 0.2 m SLR, we estimate a 50% chance that these sea levels will occur 38 days per year on average. Under 0.6 m SLR, these these minor flood levels will occur daily at some locations with 90% probability. Flooding will be chronic at many other locations in eastern Australia. 

![minor_exceeds_means](https://github.com/AusClimateService/hazards-coastal/assets/172552060/49609b63-fd93-4aa8-b699-5d7ea1cb385f)


## Contributing
Open to contributions. 

## Authors and acknowledgment
Hazard team:
- [ ] Julian O'Grady (CSIRO, lead)
- [ ] Ben Hague (Bureau of Meteorology, alternate lead)
