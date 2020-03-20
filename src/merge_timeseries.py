from datetime import datetime, date
import numpy as np
import os
import gspread

DATE = 'date'
POSITIVE = 'positive'
RECOVERED = 'recovered'
DEATHS = 'deaths'
TESTED = 'tested'
DATE_FORMAT = '%m-%d-%Y'

CSVDIR = 'csv'

ONT_FILE = 'ont.csv'
CSSEGIS_DIR = 'cssegis-COVID-19/csse_covid_19_data/csse_covid_19_time_series'
CSSEGIS_CONFIRMED_FILE = os.path.join(CSSEGIS_DIR, 'time_series_19-covid-Confirmed.csv')
CSSEGIS_DEATHS_FILE = os.path.join(CSSEGIS_DIR, 'time_series_19-covid-Deaths.csv')
CSSEGIS_RECOVERED_FILE = os.path.join(CSSEGIS_DIR, 'time_series_19-covid-Recovered.csv')


def load_ont_timeseries(fname):
    f = open(fname, 'r')
    dat = f.readlines(f)
    
    headers = dat[0]
    timeseries = {h: [] for h in headers}

    for i in range(1, len(dat)):
        line = dat[i].strip().split(',')
        for j in range(len(line)):
            timeseries[headers[j]] = line[j]

    timeseries[DATE] = [datetime.strptime(d, '%m-%d-%Y') for d in timeseries['Date']]
    timeseries[POSITIVE] = [int(t) for t in timeseries['Confirmed Positive']]
    timeseries[RESOLVED] = [int(t) for t in timeseries['Resolved']]
    timeseries[DEATHS] = [int(t) for t in timeseries['Deaths']]
    timeseries[TESTED] = [int(t) for t in timeseries['Total number of patients approved for COVID-19 testing to date']]

    return timeseries

def load_timeseries_from_cssegis(fname):
    f = open(fname, 'r')
    dat = f.readlines()
    headers = dat[0]

    timeseries = {}
    for i in range(1, len(dat)):
        # if ', ' in dat[i]:
        #     print(dat[i])
        # if 'Korea' in dat[i]:
        #     import pdb; pdb.set_trace()
        dat[i] = dat[i].replace(', ', '_')
        line = dat[i].strip().split(',')
        region = (line[1] if len(line[0]) == 0 else '{}_{}'.format(
            line[0], line[1])).strip('"')
        nums = line[4:]
        timeseries[region] = nums 
    return timeseries
    
def load_dates_from_cssegis(fname):
    f = open(fname, 'r')
    dat = f.readlines()
    headers = dat[0].strip().split(',')
    dates = [d.split('/') for d in headers[4:]]
    dates = [datetime(int(d[2]), int(d[0]), int(d[1])) for d in dates]
    return dates

if __name__ == '__main__':
    confirmed_data = load_timeseries_from_cssegis(CSSEGIS_CONFIRMED_FILE)
    deaths_data = load_timeseries_from_cssegis(CSSEGIS_DEATHS_FILE)
    recovered_data = load_timeseries_from_cssegis(CSSEGIS_RECOVERED_FILE)
    dates = load_dates_from_cssegis(CSSEGIS_RECOVERED_FILE)

    regions = ['Italy', 'Singapore', "Korea_South", 'Ontario_Canada']
    fout = os.path.join(CSVDIR, 
            'covid_comparisons_{}.csv'.format(
                date.today().strftime('%m-%d-%Y')))
    with open(fout, 'w') as f:
        headers = ['data-type', 'Region'] + [
                d.strftime(DATE_FORMAT) for d in dates]
        f.write(','.join(headers) + '\n')
        for data, dataname in [(confirmed_data, POSITIVE), 
                                (deaths_data, DEATHS), 
                                (recovered_data, RECOVERED)]:
            for region in regions:
                region_data = [dataname, region] + data[region]
                f.write(','.join(region_data) + '\n')
    print('Wrote to {}'.format(fout))
