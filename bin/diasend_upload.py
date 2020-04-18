"""

Dependencies:
- python-xlrd
- python-tz
"""
import datetime
import hashlib
import json
import pytz
import sys
import time
import urllib2
import xlrd


NIGHTSCOUT_URL='https://night.trixing.net'
NIGHTSCOUT_SECRET='nightscout12'


class Bolus(object):
  def __repr__(self):
    return 'Bolus(%.1f U)' % self.volume


class DiasendReader(object):

  def __init__(self, filename, timezone):
    self.timezone = timezone
    self.workbook = xlrd.open_workbook(filename)
    self.sheet_names = self.workbook.sheet_names()
    # TODO verify sheet names
    self.glucose = self.workbook.sheet_by_name(self.sheet_names[0])
    self.cgm = self.workbook.sheet_by_name(self.sheet_names[1])
    self.insulin = self.workbook.sheet_by_name(self.sheet_names[2])

  def _date_from_str(self, datestr):
      date = datetime.datetime.strptime(datestr, '%m/%d/%Y %H:%M')
      return date.replace(tzinfo=pytz.timezone(self.timezone))
    
  def _glucose_data(self, sheet, start_row):
    num_cols = sheet.ncols   # Number of columns
    r = []
    units = sheet.cell_value(start_row, 1)
    for row_idx in range(start_row + 1, sheet.nrows):    # Iterate through rows
      # 10/03/2016 18:26
      datestr = sheet.cell_value(row_idx, 0)
      date = self._date_from_str(datestr)
      value = sheet.cell_value(row_idx, 1)
      #r.append((date, value, units))
      yield (date, value, units)
      
    #return r

  def cgm_data(self):
    return self._glucose_data(self.cgm, 1)
 
  def glucose_data(self):
    return self._glucose_data(self.glucose, 4)

  def insulin_data(self, filter):
    sheet = self.insulin
    num_cols = sheet.ncols   # Number of columns
    for row_idx in range(1, sheet.nrows):    # Iterate through rows
      # 10/03/2016 18:26
      datestr = sheet.cell_value(row_idx, 0)
      date = self._date_from_str(datestr)
      note = sheet.cell_value(row_idx, 7)

      basal_rate = sheet.cell_value(row_idx, 1)
      if basal_rate and filter == 'basal':
        yield (date, basal_rate)

      bolus_type = sheet.cell_value(row_idx, 2)
      if bolus_type and filter == 'bolus':
        event = Bolus()
        event.type = bolus_type
        event.volume = sheet.cell_value(row_idx, 3)
        # For extended Bolus
        event.immediate = sheet.cell_value(row_idx, 3)
        event.extended = sheet.cell_value(row_idx, 4)
        event.duration = sheet.cell_value(row_idx, 5)
        yield (date, event)
      
      carb_value = sheet.cell_value(row_idx, 6)
      if carb_value and filter == 'carbs': 
        yield (date, carb_value)

  def bolus_data(self):
    return self.insulin_data('bolus')

  def carb_data(self):
    return self.insulin_data('carbs')

  def basal_data(self):
    return self.insulin_data('basal')


class NightscoutUploader(object):

  def __init__(self, url, secret):
    self.url = url
    self.secret = hashlib.sha1(secret).hexdigest()

  def upload(self, path, data):
    req = urllib2.Request(self.url + '/api/v1/' + path + '/')
    req.add_header('Content-Type', 'application/json')
    req.add_header('api-secret', self.secret)

    response = urllib2.urlopen(req, json.dumps(data))
    print response.read()
    return response

  def date(self, date):
    utc = date.astimezone(pytz.utc)
    local = date.replace(tzinfo=None)
    # No idea what I'm doing...
    sec = int(1000*(time.mktime(date.timetuple())-7200))
    return {'date': sec,
            'dateStr': utc.strftime('%Y-%m-%dT%H:%M:%SZ')}

  def upload_glucose(self, data, data_type):
    upload_data = []
    for date, value, units in data:
      d = self.date(date)
      d.update({
          data_type: int(value),
          'type': data_type,
          'device': 'diasend_upload',
          'notes': units,
      })
      # upload_data.append(d)
      self.upload('entries', [d]) 
      break
      
    #self.upload('entries', upload_data) 

  def upload_carbs(self, data):
    for date, value in data:
      d = self.date(date)
      d = {
          'created_at': d['dateStr'],
          'timestamp': d['dateStr'],
          'eventType': 'Meal Bolus',
          'enteredBy': 'diasend_upload',
          'carbs': value
      }
      # upload_data.append(d)
      self.upload('treatments', [d]) 
      break
    # return self.upload('treatments', upload_data) 

  def upload_bolus(self, data):
    for date, bolus in data:
      d = self.date(date)
      assert bolus.type == 'Normal'
      d = {
          'created_at': d['dateStr'],
          'timestamp': d['dateStr'],
          'eventType': 'Correction Bolus',
          'enteredBy': 'diasend_upload',
          'insulin': bolus.volume,
          'programmed': bolus.volume,
          'type': 'normal',
          'duration': 0,
      }
      # upload_data.append(d)
      self.upload('treatments', [d]) 
      break
    # return self.upload('treatments', upload_data) 

  def upload_basal(self, data):
    first = data.next()
    while True:
      (date, basal) = first
      try:
        next = data.next()
      except StopIteration:
        break
      duration = (next[0] - date).total_seconds()
      d = self.date(date)
      d = {
          'created_at': d['dateStr'],
          'timestamp': d['dateStr'],
          'eventType': 'Correction Bolus',
          'enteredBy': 'diasend_upload',
          'absolute': basal,
          'rate': basal,
          'duration': duration,
      }
      # upload_data.append(d)
      self.upload('treatments', [d]) 
      first = next
      break
    # return self.upload('treatments', upload_data) 





diasend = DiasendReader(sys.argv[1], 'Europe/Berlin')
#print '\n'.join(str(t) for t in diasend.glucose_data())
#print '\n'.join(str(t) for t in diasend.cgm_data())
# basal, bolus, carbs, notes = diasend.insulin_data()
#print '\n'.join(str(t) for t in bolus)

uploader = NightscoutUploader(NIGHTSCOUT_URL, NIGHTSCOUT_SECRET)
#print uploader.upload_glucose(diasend.glucose_data(), 'mbg')
#print uploader.upload_glucose(diasend.cgm_data(), 'sgv')
print uploader.upload_carbs(diasend.carb_data())
print uploader.upload_bolus(diasend.bolus_data())
print uploader.upload_basal(diasend.basal_data())
