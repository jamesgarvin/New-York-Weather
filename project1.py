import csv

def build_dict_from_csv(filename, key_field_index, value_field_index):
    '''
    This funciton returns a dictionary of data read in from a given filename
    The second and third parameters speicify the index of the keys and values to build the dictionary
    These parameters can be lists of indexes - for example, you can assign multiple indexes in a row to a specific key in that row
    Or you can assign multiple keys in a single row, which is useful for searching for zipcodes in uhf.csv
    '''

    result_dict = {}
    seen = set()

    if isinstance(key_field_index, int):
        key_field_index = [key_field_index]
    if isinstance(value_field_index, int):
        value_field_index = [value_field_index]

    with open(filename, 'r', newline='') as f:
        csv_reader = csv.reader(f)

        for row in csv_reader: 

            # Skip duplicate rows
            row_tuple = tuple(row)
            if row_tuple in seen:
                continue
            seen.add(row_tuple)
            
            #builds a tuple of values 
            value_fields = tuple(
                row[value_index].strip()
                for value_index in value_field_index
                if value_index < len(row)
            )

            #skips if there are no terms in value_fields
            if not value_fields:
                continue

            # Process each key column
            for key_index in key_field_index:
                if key_index < len(row):
                    key = row[key_index].strip()
                    if key in result_dict:
                        result_dict[key] += value_fields 
                    else:
                        result_dict[key] = value_fields
    return result_dict

def search_by_date(date):
    '''
    This function returns a set of data about each reading taken on a given date in the format:
    date, uhf code, geo id, location, measurement
    '''

    #builds a dictionary with key = 'date' and values 'geo_id, location, measurement'
    dictionary = build_dict_from_csv('air_quality.csv', 2, [0,1,3])
    
    geo_id = []
    location = []
    measurement = []

    #builds lists of geo_id, location and measurment by going through all values in dictionary[specified date]
    #in steps of 3, and appending the values to the lists respectiveley in order
    for i in range(0, len(dictionary[date]), 3):
        geo_id.append(dictionary[date][i])
        location.append(dictionary[date][i+1])
        measurement.append(dictionary[date][i+2])

    
    output = []

    #builds a second dictionary to get data from uhf.csv, with key field 'geo id' and value field 'uhf'
    dictionary2 = build_dict_from_csv('uhf.csv', 2, 1)

    #for each term in the list 'geo_id' (providing there is a corresponding 'UHF code' to each 'geo id')
    #returns an output of the format:
    #date, uhf code, geo id, location, measurement
    #the indexes for the relevant location and measurement value line up with the geo_id index because of the way the 3 lists were built together
    for term in geo_id:
        if term in dictionary2:    
            index = geo_id.index(term)
            uhf = dictionary2[term]
            result = f'{date}, {uhf}, {term}, {location[index]}, {measurement[index]} mcg/m^3'
            output.append(result)
        
    return output

def search_by_uhf(UHF_code):
    #construct a dictionary between UHF codes and geo codes
    dictionary = build_dict_from_csv('uhf.csv', 1, 2)
    geo_id = []
    for term in dictionary[UHF_code]:
        geo_id.append(term)
    
    #build a second dictionary between {geo_codes: measurement, date, location}
    output = []
    dictionary2 = build_dict_from_csv('air_quality.csv', 0, [1,2,3])
    for geo in geo_id:
        index = geo_id.index(geo)
        location = []
        date = []
        measurement = []
        for i in range(0, len(dictionary2[geo]), 3):
            location.append(dictionary2[geo][i])
            date.append(dictionary2[geo][i+1])
            measurement.append(dictionary2[geo][i+2])
        
        for j in range(0, len(location)):
            result = f'{date[j]}, {UHF_code}, {geo}, {location[j]}, {measurement[j]} mcg/m^3'
            output.append(result)
    
    return output
        
def search_by_borough(borough):
    #construct a dictionary between {borough: geo_code, uhf_code}
    dictionary = build_dict_from_csv('uhf.csv', 0, [2,1])
    geo_id = []
    uhf_id = []

    for i in range(0, len(dictionary[borough]), 2):
        geo_id.append(dictionary[borough][i])
        uhf_id.append(dictionary[borough][i+1])
    
    #Construct a second dictionary between {geo_codes: location, date, measurement}
    dictionary2 = build_dict_from_csv('air_quality.csv', 0, [1,2,3])
    output = []
    for geo in geo_id:
        index = geo_id.index(geo)
        location = []
        date = []
        measurement = []
        for i in range(0, len(dictionary2[geo]),3):
            location.append(dictionary2[geo][i])
            date.append(dictionary2[geo][i+1])
            measurement.append(dictionary2[geo][i+2])
        
        for j in range(0, len(location)):
            result = f'{date[j]}, {uhf_id[index]}, {geo}, {location[j]}, {measurement[j]} mcg/m^3'
            output.append(result)
    
    return output

def search_by_zipcode(zipcode):
    #construct a dictionary between {zip codes: geo codes and UHF codes}
    dictionary = build_dict_from_csv('uhf.csv', list(range(3,17)), [2,1])
    geo_id = []
    uhf_id = []
    for i in range(0, len(dictionary[zipcode]),2):
        geo_id.append(dictionary[zipcode][i])
        uhf_id.append(dictionary[zipcode][i+1])
    

    #construct a second dictionary between {geo id: location, date, measurement}
    dictionary2 = build_dict_from_csv('air_quality.csv', 0, [1,2,3])
    output = []
    for geo in geo_id:
        index = geo_id.index(geo)
        location = []
        date = []
        measurement = []
        for i in range(0, len(dictionary2[geo]), 3):
            location.append(dictionary2[geo][i])
            date.append(dictionary2[geo][i+1])
            measurement.append(dictionary2[geo][i+2])

        for j in range(0, len(location)):
            result = f'{date[j]}, {uhf_id[index]}, {geo}, {location[j]}, {measurement[j]} mcg/m^3'
            output.append(result)
    
    return output

if __name__ == '__main__':
    import os
    from pprint import PrettyPrinter
    from pick import pick
    
    pp = PrettyPrinter(width=200)
    title = 'Search by:\n'
    options = ['Quit','Zip Code', 'UHF id', 'Borough', 'Date']
    key = True

    while key == True:
        try:
            option, index = pick(options, title, indicator='=>', default_index=1)

            match index:
                case 0:
                    key = False
                    os.system('cls')

                case 1:
                    os.system('cls')
                    zip_code = input("Enter zip code:\n")
                    pp.pprint(search_by_zipcode(zip_code))
                    input()
                
                case 2:
                    os.system('cls')
                    uhf = input("Enter UHF:\n")
                    pp.pprint(search_by_uhf(uhf))
                    input()            
                case 3:
                    os.system('cls')
                    borough = input("Enter Borough name:\n")
                    pp.pprint(search_by_borough(borough))
                    input()
                case 4:
                    os.system('cls')
                    date = input("Enter date:\n")
                    pp.pprint(search_by_date(date))
                    input()
        except KeyError:
            input('USER INPUT ERROR')

