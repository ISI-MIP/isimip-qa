points = [
    ('potsdam', 52.395833, 13.061389),
    ('cairo', 30.056111, 31.239444),
    ('jakarta', -6.175, 106.828611)
]

countrymask_path = 'ISIMIP3a/InputData/geo_conditions/countrymasks/countrymasks_fractional.nc'
countries = [
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

regions = []

for specifier, lat, lon in points:
    regions.append({
        'type': 'point',
        'specifier': specifier,
        'lon': lat,
        'lat': lon
    })

for code in countries:
    regions.append({
        'type': 'mask',
        'specifier': code.lower(),
        'mask_path': countrymask_path,
        'mask_variable': f'm_{code}'
    })
