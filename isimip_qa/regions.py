regions_list = [
    {
        'type': 'global',
        'specifier': 'global'
    }
]

points = [
    ('potsdam', 52.395833, 13.061389),
    ('cairo', 30.056111, 31.239444),
    ('jakarta', -6.175, 106.828611)
]

for specifier, lat, lon in points:
    regions_list.append({
        'type': 'point',
        'specifier': specifier,
        'lon': lat,
        'lat': lon
    })

countrymask_path = 'ISIMIP3a/InputData/geo_conditions/countrymasks/countrymasks_fractional.nc'
countrymask_codes = [
    'AFG', 'ALB', 'DZA', 'AND', 'AGO', 'ATG', 'ARG', 'ARM', 'AUS', 'AUT',
    'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BTN',
    'BOL', 'BIH', 'BWA', 'BRA', 'BRN', 'BGR', 'BFA', 'BDI', 'KHM', 'CMR',
    'CAN', 'CPV', 'CSID', 'CYM', 'CAF', 'TCD', 'CHL', 'CHN', 'COL', 'COM',
    'COG', 'CRI', 'HRV', 'CUB', 'CYP', 'CZE', 'CIV', 'PRK', 'COD', 'DNK',
    'DJI', 'DMA', 'DOM', 'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'ETH',
    'FLK', 'FRO', 'FJI', 'FIN', 'FRA', 'GUF', 'PYF', 'ATF', 'GAB', 'GMB',
    'GEO', 'DEU', 'GHA', 'GRC', 'GRL', 'GRD', 'GLP', 'GUM', 'GTM', 'GIN',
    'GNB', 'GUY', 'HTI', 'HMD', 'HND', 'HKG', 'HUN', 'ISL', 'IND', 'IOSID',
    'IDN', 'IRN', 'IRQ', 'IRL', 'IMN', 'ISR', 'ITA', 'JAM', 'JPN',
    'JOR', 'KAZ', 'KEN', 'KIR', 'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO',
    'LBR', 'LBY', 'LTU', 'LUX', 'MDG', 'MWI', 'MYS', 'MLI', 'MLT', 'MTQ',
    'MRT', 'MUS', 'MYT', 'MEX', 'FSM', 'MDA', 'MNG', 'MNE', 'MAR', 'MOZ',
    'MMR', 'NAM', 'NPL', 'NLD', 'NCL', 'NZL', 'NIC', 'NER', 'NGA',
    'NIU', 'NOR', 'OMN', 'PSID', 'PAK', 'PLW', 'PSE', 'PAN', 'PNG', 'PRY',
    'PER', 'PHL', 'POL', 'PRT', 'PRI', 'QAT', 'KOR', 'ROU', 'RUS', 'RWA',
    'REU', 'LCA', 'SPM', 'VCT', 'WSM', 'STP', 'SAU', 'SEN', 'SRB', 'SLE',
    'SGP', 'SVK', 'SVN', 'SLB', 'SOM', 'ZAF', 'SGS', 'SSD', 'ESP', 'LKA',
    'SDN', 'SUR', 'SJM', 'SWZ', 'SWE', 'CHE', 'SYR', 'TWN', 'TJK', 'THA',
    'MKD', 'TLS', 'TGO', 'TON', 'TTO', 'TUN', 'TUR', 'TKM', 'GBR', 'UGA',
    'UKR', 'ARE', 'TZA', 'VIR', 'USA', 'URY', 'UZB', 'VUT', 'VEN', 'VNM',
    'ESH', 'YEM', 'ZMB', 'ZWE'
]

for code in countrymask_codes:
    regions_list.append({
        'type': 'mask',
        'specifier': code.lower(),
        'mask_path': countrymask_path,
        'mask_variable': f'm_{code}'
    })

georgimask_path = 'ISIMIP3a/InputData/geo_conditions/masks/georgimask.nc'
georgimask_codes = [
    'ALA', 'AMZ', 'CAM', 'CAN', 'CAS', 'CSA', 'EAF', 'EAS', 'ENA', 'EQF',
    'GRL', 'MED', 'NAS', 'NAU', 'NEE', 'NEU', 'SAF', 'SAH', 'SAS', 'SAU',
    'SEA', 'SQF', 'SSA', 'TIB', 'WAF', 'WNA',
]

for code in georgimask_codes:
    regions_list.append({
        'type': 'mask',
        'specifier': code.lower(),
        'mask_path': georgimask_path,
        'mask_variable': f'm_{code}'
    })
