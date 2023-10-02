import boto3


def lambda_handler(event, context):
    client = boto3.client('ce', region_name='us-east-1')
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': '2023-01-01',
            'End': '2023-01-31'
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )

    cost = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']

    return {
        'statusCode': 200,
        'body': f'O custo do mês atual é de ${cost}'
    }
