from datetime import datetime, timedelta

import boto3
import dateutil.tz


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

    cost = round(float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']), 2)

    msg = f'AWS Billing: Previsão total do mês atual é de ${cost}'

    send_email_response = send_email(msg)

    after_print(last_month_date, current_date, send_email_response)

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


def after_print(last_month_date, current_date, send_email_response):
    print('last_month_date: ' + str(last_month_date))
    print('current_date: ' + str(current_date))
    print('send_email_response: ' + str(send_email_response))
