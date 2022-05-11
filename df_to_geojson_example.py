import pandas as pd, requests, json

#API endpoint for city of Berkeley's 311 calls
endpoint_url = 'Https://data.cityofberkeley.info/resource/k489-uv4i.json$limit=20'

#fetch the url and load the data
response = requests.get(endpoint_url)
data = response.json()

# turn the json data into a dataframe and see how many rows and what columns we have
df = pd.DataFrame(data)

print('We have {} rows'.format(len(df)))
str(df.columns.tolist())

# convert lat-long to floats and change address from ALL CAPS to regular capitalization
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)
df['street_address'] = df['street_address'].str.title()

# we don't need all those columns - only keep useful ones
cols = ['issue_description', 'issue_type', 'latitude', 'longitude', 'street_address', 'ticket_status']
df_subset = df[cols]

# drop any rows that lack lat/long data
df_geo = df_subset.dropna(subset=['latitude', 'longitude'], axis=0, inplace=False)

print('We have {} geotagged rows'.format(len(df_geo)))
df_geo.tail()
# what is the distribution of issue types?
df_geo['issue_type'].value_counts()

def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
    # create a new python dict to contain our geojson data, using geojson format
    geojson = {'type':'FeatureCollection', 'features':[]}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type':'Feature',
                   'properties':{},
                   'geometry':{'type':'Point',
                               'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row[lon],row[lat]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]
        
        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    
    return geojson

cols = ['street_address', 'issue_description', 'issue_type', 'ticket_status']
geojson = df_to_geojson(df_geo, cols)

import IPython
IPython.display.display({'application/geo+json': geojson}, raw=True)