import os
from datetime import datetime, timedelta

import boto3
import dateutil.tz
import math


def lambda_handler(event, context):
    client = boto3.client('ce', region_name='us-east-1')

    current_date, last_month_date = get_dates()

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': last_month_date,
            'End': current_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )

    cost = round(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])

    msg = f'AWS Billing: Previsão total do mês atual é de ${cost}'

    sns_response = send_sms(msg)
    print(sns_response)

    return {
        'statusCode': 200,
        'body': msg
    }


def get_dates():
    date_format = '%Y-%m-%d'
    brazil_timezone = dateutil.tz.gettz('America/Sao_Paulo')

    current_date = datetime.now(brazil_timezone)
    last_month_date = current_date - timedelta(days=30)

    return current_date.strftime(date_format), last_month_date.strftime(date_format)


def send_sms(message: str):
    phone_number = os.environ['PHONE_NUMBER']

    sns = boto3.client('sns')

    return sns.publish(
        PhoneNumber=phone_number,
        Message=message
    )
