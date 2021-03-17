# Modules from Example: https://github.com/sucitw/python-script-in-NiFi/blob/master/json_transform.py
import json
import sys
import traceback
from java.nio.charset import StandardCharsets
from org.apache.commons.io import IOUtils
from org.apache.nifi.processor.io import StreamCallback
from org.python.core.util import StringUtil

# Other Modules used
from datetime import datetime


def find_duration(start, end):
    start_day = start.split('T')[0].split('-')[2]
    end_day = end.split('T')[0].split('-')[2]
    length_in_days = int(end_day) - int(start_day)

    start_time = start.split('T')[1]
    start_hour = start_time.split(':')[0]
    start_minute = start_time.split(':')[1]

    end_time = end.split('T')[1]
    end_hour = end_time.split(':')[0]
    end_minute = end_time.split(':')[1]

    if length_in_days == 0:
        duration_in_hours = int(end_hour) - int(start_hour)
    else:
        duration_in_hours = (int(end_hour) + (length_in_days * 24)) - int(start_hour)

    duration_in_minutes = int(end_minute) - int(start_minute)

    convert_hours_to_minutes = duration_in_hours *60

    duration = duration_in_minutes + convert_hours_to_minutes

    return duration


def aws_convert_endtime_to_24_hour(end):
    end_time = end.split(' ')[0]
    am_or_pm = end.split(' ')[1]

    hour = int(end_time.split(':')[0])
    minute = end_time.split(':')[1]
    if am_or_pm == 'PM':
        hour = hour+12
    elif am_or_pm =='AM' and hour == 12:
        hour = '0'

    end_time = "{}:{}".format(hour,minute)
    return end_time


def aws_time_from_description(description):
    update_times =[]

    times = description.split('</span>')

    for i in times:
        try:
            update_times.append(i.split('class="yellowfg">')[1].strip())
        except:
            pass

    return update_times

def aws_find_end_time(update_times, start_time):

    end = update_times[-1]

    date = start_time.split(' ')[0]
    if len(end) <= 12:
        end_24 = aws_convert_endtime_to_24_hour(end)    
        end_time = "{} {} PDT-700".format(date,end_24)
    else:
        date_broken = date.split('-')
        date_broken[2] = str(int(date_broken[2]) +1)
        date = '-'.join(date_broken)
        end = " ".join(end.split(' ')[-3:])
        end_24 = aws_convert_endtime_to_24_hour(end) 
        end_time = "{} {} PDT-700".format(date,end_24)

    return end_time

def aws_find_report_time(update_times, start_time):

    report = update_times[0]

    date = start_time.split(' ')[0]
    if len(report) <= 12:
        report_24 = aws_convert_endtime_to_24_hour(report)    
        report_time = '{} {} PDT-700'.format(date, report_24)
    else:
        date_broken = date.split('-')
        date_broken[2] = str(int(date_broken[2]) +1)
        date = '-'.join(date_broken)
        report = " ".join(report.split(' ')[-3:])
        report_24 = aws_convert_endtime_to_24_hour(report) 
        report_time = '{} {} PDT-700'.format(date, report_24)

    return report_time


def parse_aws_data(cloud_source, uri, event):

    try:
        region = event['service_name'].split('(')[1].replace(')', '')
    except:
        region = 'global'

    dt = datetime.fromtimestamp(int(event['date']))
    start_time = dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    
    update_times = aws_time_from_description(event['description'])

    report_time = aws_find_report_time(update_times, start_time)
    end_time = aws_find_end_time(update_times, start_time)
    duration = 'AWS (Unable to Gather)'

    structured_output = {
        'provider' : cloud_source,
        'source_uri' : uri,
        'event_id' : event["date"],
        'region' : region,
        'service' : event["service"],
        'reported_at' : report_time,
        'start' : start_time,
        'end': end_time,
        'duration': duration,
        'severity': "AWS (No Severity)",
        'summary' : event["summary"]
    }
    return structured_output


def parse_gcp_data(cloud_source, uri, event):
    gcp_regions = [
        "us-east1",
        "us-east4",
        "us-west1",
        "us-west2",
        "us-west3",
        "us-west4",
        "us-central1",
        "southamerica-east1",
        "northamerica-northeast1",
        "europe-west1",
        "europe-west2",
        "europe-west3",
        "europe-west4",
        "europe-west6",
        "europe-north1",
        "australia-southeast1",
        "asia-southeast1",
        "asia-southeast2",
        "asia-south1",
        "asia-northeast1",
        "asia-northeast2",
        "asia-northeast3",
        "asia-east1",
        "asia-east2",
        "multiple",
        'various'
    ]

    affected_regions = []

    for region in gcp_regions:
        if region in event['external_desc']:
            affected_regions.append(region)

    regions_string = ','.join(affected_regions)

    duration = find_duration(event['begin'], event['end'])
    
    structured_output = {
        'provider' : cloud_source,
        'source_uri' : uri,
        'event_id' : event["number"],
        'region' : regions_string,
        'service' : event["service_name"],
        'reported_at' : event["created"],
        'start' : event["begin"],
        'end': event["end"],
        'duration': duration,
        'severity': event["severity"],
        'summary' : event["external_desc"]
    }
    return structured_output


def parse_sap_data(cloud_source, uri, event):

    try:
        region = event['name'].split(' - ')[0]
    except:
        region = 'unknown'

    affected_services = []

    for i in event["components"]:
        if i not in affected_services:
            affected_services.append(i['name'])
    services_string = ','.join(affected_services)

    duration = find_duration(event['started_at'], event['resolved_at'])


    structured_output = {
        'provider' : cloud_source,
        'source_uri' : uri,
        'event_id' : event["id"],
        'region' : region,
        'service' : services_string,
        'reported_at' : event["created_at"],
        'start' : event["started_at"],
        'end': event["resolved_at"],
        'duration': duration,
        'severity': event["impact"],
        'summary' : event["name"]
    }
    return structured_output


def handler(parser, cloud_source, uri, event):
    output = []


    if parser == "report.cloud.statuspage.incidents.v2":
        for i in event['incidents']:
            try:
                clean_dict = parse_sap_data(cloud_source, uri, i)
                output.append(clean_dict)
            except Exception as e:
                print("Problem parsing data\n\nEvent\n\n{}\n\nError\n{}".format(i,e))
    
    elif parser == "report.cloud.gcp.incidents.v1":
        try:
            for i in event:
                clean_dict = parse_gcp_data(cloud_source, uri, i)
                output.append(clean_dict)
        except Exception as e:
            print("Problem parsing data\n\nEvent\n\n{}\n\nError\n{}".format(i,e))
    
    elif parser == "report.cloud.aws.incidents.v1":
        for i in event['archive']:
            try:
                clean_dict = parse_aws_data(cloud_source, uri, i)
                output.append(clean_dict)
            except Exception as e:
                print("Problem parsing data\n\nEvent\n\n{}\n\nError\n{}".format(i,e))
                continue

    return output


# if __name__ == "__main__":
#     with open('aws2.json', 'r') as file:
#         event = json.load(file)
    
#     handler("report.cloud.aws.incidents.v1", 'AWS', "uri", event)

class TransformCallback(StreamCallback):
    def __init__(self, flowFile):
        self.flowFile = flowFile
        pass

    def process(self, inputStream, outputStream):
        try:
            parser = self.flowFile.getAttribute("parser")
            cloud_source = self.flowFile.getAttribute("http_src_name")
            src_uri = self.flowFile.getAttribute("http_src_url")

            # Read input FlowFile content
            input_text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
            input_obj = json.loads(input_text)

            # Transform content
            output_obj = handler(parser, cloud_source, src_uri, input_obj)

            # Write output content
            #output_text = json.dumps(output_obj)
            #outputStream.write(StringUtil.toBytes(output_text))
            
            outputStream.write(bytearray(json.dumps(output_obj, indent=4).encode('utf-8'))) 

        except:
            traceback.print_exc(file=sys.stdout)
            raise


flowFile = session.get()
if flowFile != None:
    flowFile = session.write(flowFile, TransformCallback(flowFile))
    timestamp = datetime.today().strftime('%Y%m%d/%Y%m%d%H%M%S')
    source_short = flowFile.getAttribute("http_src_name").split('.')[-1]
    flowFile = session.putAttribute(flowFile, "filename", flowFile.getAttribute("targetTrans")+timestamp+'_'+source_short+'.json')

    # Finish by transferring the FlowFile to an output relationship
    session.transfer(flowFile, REL_SUCCESS)
