from datetime import datetime, timedelta

import boto3
import dateutil.tz

brazil_timezone = dateutil.tz.gettz('America/Sao_Paulo')


def lambda_handler(event, context):
    client = boto3.client('ce', region_name='us-east-1')

    cost = get_cost(client)
    forecasted_cost = get_forecasted_cost(client)

    msg = (f'AWS Billing: Previsão total do mês atual é de ${forecasted_cost}. '
           f'Valor atual é de ${cost}.')

    send_email(msg)

    return {
        'statusCode': 200,
        'body': msg
    }


def get_cost(client):
    current_date, last_month_date = get_dates_cost()

    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': last_month_date,
            'End': current_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )

    return round(float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']), 2)


def get_forecasted_cost(client):
    today = datetime.now(brazil_timezone)
    next_day_of_current_month = datetime(today.year, today.month, today.day + 1)
    first_day_next_month = datetime(today.year, today.month + 1, 1)

    response = client.get_cost_forecast(
        TimePeriod={
            'Start': next_day_of_current_month.strftime('%Y-%m-%d'),
            'End': first_day_next_month.strftime('%Y-%m-%d')
        },
        Metric='UNBLENDED_COST',
        Granularity='MONTHLY'
    )

    return round(float(response['Total']['Amount']), 2)


def get_dates_cost():
    date_format = '%Y-%m-%d'

    current_date = datetime.now(brazil_timezone)
    last_month_date = current_date - timedelta(days=30)

    return current_date.strftime(date_format), last_month_date.strftime(date_format)


def send_email(message):
    ses = boto3.client('ses', region_name='us-east-1')
    sender_email = 'heycristhian@gmail.com'
    recipient_email = 'heycristhian@gmail.com'
    subject = 'AWS BILLING'
    body_html = f'<html><body><h1>{message}</h1></body></html>'

    return ses.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': body_html}
            }
        }
    )
