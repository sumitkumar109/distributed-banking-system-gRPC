import grpc
import bank_pb2
import bank_pb2_grpc
import json
import argparse

customer_latest_branch = {}

def query(branch_port, customer_id):
    
    if customer_id in customer_latest_branch and customer_latest_branch[customer_id] != branch_port:
        
        latest_branch_port = customer_latest_branch[customer_id]
        latest_balance = query_other_branch(latest_branch_port, customer_id)
        return latest_balance

    channel = grpc.insecure_channel(f'localhost:{branch_port}')
    stub = bank_pb2_grpc.BankServiceStub(channel)
    request = bank_pb2.CustomerRequest(customer_id=customer_id)
    response = stub.Query(request)
    return response.balance

def query_other_branch(branch_port, customer_id):
    
    channel = grpc.insecure_channel(f'localhost:{branch_port}')
    stub = bank_pb2_grpc.BankServiceStub(channel)
    request = bank_pb2.CustomerRequest(customer_id=customer_id)
    response = stub.Query(request)
    return response.balance

def deposit(amount, branch_port, customer_id):
    
    customer_latest_branch[customer_id] = branch_port
    channel = grpc.insecure_channel(f'localhost:{branch_port}')
    stub = bank_pb2_grpc.BankServiceStub(channel)
    request = bank_pb2.TransactionRequest(customer_id=customer_id, amount=amount, propagate=True)
    response = stub.Deposit(request)
    return response.status

def withdraw(amount, branch_port, customer_id):
    
    customer_latest_branch[customer_id] = branch_port
    channel = grpc.insecure_channel(f'localhost:{branch_port}')
    stub = bank_pb2_grpc.BankServiceStub(channel)
    request = bank_pb2.TransactionRequest(customer_id=customer_id, amount=amount, propagate=True)
    response = stub.Withdraw(request)
    return response.status

def get_branch_port(branches_info, branch_id):
    
    return branches_info[branch_id-1]['port']

def process_customer_requests(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    with open('branch_info.json', 'r') as info_file:
            branches_info = json.load(info_file)
    customers = [item for item in data if item['type'] == 'customer']

    results = []

    for customer in customers:
        cust_id = customer['id']

        for event in customer['events']:
            customer_result = {'id': cust_id, 'recv': []}
            result = {}
            branch_id = event['branch']
            branch_port = get_branch_port(branches_info, branch_id)

            if event['interface'] == 'query':
                balance = query(branch_port, cust_id)
                result['interface'] = 'query'
                result['branch'] = event['branch']
                result['balance'] = balance
            elif event['interface'] == 'deposit':
                money = event['money']
                status = deposit(money, branch_port, cust_id)
                result['interface'] = 'deposit'
                result['branch'] = event['branch']
                result['result'] = status
            elif event['interface'] == 'withdraw':
                money = event['money']
                status = withdraw(money, branch_port, cust_id)
                result['interface'] = 'withdraw'
                result['branch'] = event['branch']
                result['result'] = status

            customer_result['recv'].append(result)
            results.append(customer_result)

    with open('customer_events.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Customer Client')
    parser.add_argument('json_file', help='Path to the JSON file containing the process events')
    args = parser.parse_args()

    process_customer_requests(args.json_file)
