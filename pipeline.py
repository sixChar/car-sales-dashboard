import pandas as pd
import sqlite3


DATA_PATH="20100001-eng/20100001.csv"



def split_separate_sales_units(data):
    data_dollars = data[data['UOM'] == 'Dollars']
    data_units = data[data['UOM'] == 'Units']

    data_dollars = data_dollars.drop('UOM', axis=1)
    merge_cols = list(set(data_dollars.columns) - {'VALUE', 'SCALAR_FACTOR'})
    data_dollars = data_dollars.rename(columns={'VALUE': 'dollars', 'SCALAR_FACTOR':'dollar_scale'})
    data_dollars.dropna(inplace=True)

    data_units = data_units.drop('UOM', axis=1)
    data_units = data_units.rename(columns={'VALUE': 'units', 'SCALAR_FACTOR':'units_scale'})
    data_units.dropna(inplace=True)

    res = pd.merge(data_dollars, data_units, how='inner', left_on=merge_cols, right_on=merge_cols)

    res['units_scale'] = res['units_scale'].str.strip()

    units_in_units = (res['units_scale'] == "units").all()
    dollars_in_thousands = (res['dollar_scale'] == "thousands").all()
    assert (units_in_units and dollars_in_thousands), "This pipeline assumes all unit sales and dollar sales are measured in units and thousands respectively. If this is no longer the case it needs a refactor."

    return res


if __name__=="__main__":
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 1000)

    
    data = pd.read_csv(DATA_PATH)

    # date, location, origin of manufacture, number sold, unit of measure (dollars vs. units sold), type, scale, seasonal adjustment
    selected_cols = [
        'REF_DATE',
        'GEO',
        'Origin of manufacture',
        'VALUE',
        'UOM',
        'Vehicle type',
        'SCALAR_FACTOR',
        'Seasonal adjustment'
    ]

    data = data[selected_cols]
    # only want to focus on where there is no "seasonal adjustment"
    data = data[data['Seasonal adjustment'] == 'Unadjusted']
    data = data.drop('Seasonal adjustment', axis=1)

    data = split_separate_sales_units(data)

    data = data.rename(columns={
        "REF_DATE":"date",
        "GEO":"location",
        "Origin of manufacture":"origin",
        "Vehicle type":"vehicle_type",
    })


    location_rename = {
        "Canada":"CA",
        "Newfoundland and Labrador":"NL",
        "Prince Edward Island":"PE",
        "Nova Scotia":"NS",
        "New Brunswick":"NB",
        "Quebec":"QC",
        "Ontario":"ON",
        "Manitoba":"MB",
        "Saskatchewan":"SK",
        "Alberta":"AB",
        "British Columbia and the Territories":"BC",
    }
    data['location'] = data['location'].map(location_rename) 


    origin_rename = {
        "Total, country of manufacture": "total",
        "North America": "north_america",
        "Total, overseas": "overseas",
        "Japan": "japan",
        "Other countries": "other"
    }
    data['origin'] = data['origin'].map(origin_rename)

    type_rename = {
        "Total, new motor vehicles": "any",
        "Passenger cars": "cars",
        "Trucks": "trucks"
    }
    data['vehicle_type'] = data['vehicle_type'].map(type_rename)


    data = data[['vehicle_type', 'origin', 'location', 'date', 'dollars', 'units']]

    # Extract out car sales
    cars_start = data[['dollars', 'units']].where(data['vehicle_type'] == 'cars')
    data[['cars_dollars', 'cars_units']] = cars_start

    # Extract out truck sales
    trucks_start = data[['dollars', 'units']].where(data['vehicle_type'] == 'trucks')
    data[['trucks_dollars', 'trucks_units']] = trucks_start

    # Extract out overseas origin sales
    overseas = data[['dollars', 'units']].where(data['origin'] == 'overseas')
    data[['overseas_dollars', 'overseas_units']] = overseas

    # Extract out north america origin sales
    na = data[['dollars', 'units']].where(data['origin'] == 'north_america')
    data[['na_dollars', 'na_units']] = na

    data = data.groupby(
        ['date', 'location']
    ).max()

    del data['vehicle_type']

    conn = sqlite3.connect("sales.sqlite")

    curr = conn.cursor()

    data.to_sql("car_sales_data", conn, if_exists="replace")

    conn.close()
    
