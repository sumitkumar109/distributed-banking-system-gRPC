import grpc
import bank_pb2
import bank_pb2_grpc
from concurrent.futures import ThreadPoolExecutor
import json
import socket
import argparse

customer_transaction_history = {}

class BankService(bank_pb2_grpc.BankServiceServicer):
    def __init__(self, branch_id, initial_balance, port, branches_info):
        self.branch_id = branch_id
        self.replicas = branches_info
        self.replicas[branch_id] = {'balance': initial_balance, 'port': port}

    def Query(self, request, context):
        latest_balance = customer_transaction_history.get(request.customer_id, self.replicas[self.branch_id]['balance'])
        return bank_pb2.BalanceResponse(balance=latest_balance)

    def Deposit(self, request, context):
        amount = request.amount
        self.replicas[self.branch_id]['balance'] += amount
        if request.propagate:
            self.Propagate_Deposit(amount)
        customer_transaction_history[request.customer_id] = self.replicas[self.branch_id]['balance']
        return bank_pb2.EventResponse(status="Success")

    def Withdraw(self, request, context):
        amount = request.amount
        if self.replicas[self.branch_id]['balance'] >= amount:
            self.replicas[self.branch_id]['balance'] -= amount
            if request.propagate:
                self.Propagate_Withdraw(amount)
            customer_transaction_history[request.customer_id] = self.replicas[self.branch_id]['balance']
            return bank_pb2.EventResponse(status="Success")
        else:
            return bank_pb2.EventResponse(status="Failure")

    def Propagate_Deposit(self, amount):
        for branch_id in self.replicas:
            if branch_id != self.branch_id:
                self.send_deposit(branch_id, amount)

    def Propagate_Withdraw(self, amount):
        for branch_id in self.replicas:
            if branch_id != self.branch_id:
                self.send_withdraw(branch_id, amount)

    def send_deposit(self, branch_id, amount):
        port = self.replicas[branch_id]['port']
        with grpc.insecure_channel(f'localhost:{port}') as channel:
            stub = bank_pb2_grpc.BankServiceStub(channel)
            request = bank_pb2.TransactionRequest(amount=amount, propagate=False)
            stub.Deposit(request)

    def send_withdraw(self, branch_id, amount):
        port = self.replicas[branch_id]['port']
        with grpc.insecure_channel(f'localhost:{port}') as channel:
            stub = bank_pb2_grpc.BankServiceStub(channel)
            request = bank_pb2.TransactionRequest(amount=amount, propagate=False)
            stub.Withdraw(request)

def get_free_port():
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def load_branches(json_file):
    branches_info = {}
    server_objects = []

    with open(json_file, 'r') as file:
        customer_data = json.load(file)

    for entry in customer_data:
        if entry['type'] == 'branch':
            branch_id = entry['id']
            balance = entry['balance']
            port = get_free_port()

            server = grpc.server(ThreadPoolExecutor(max_workers=10))
            
            bank_pb2_grpc.add_BankServiceServicer_to_server(BankService(branch_id, balance, port, branches_info), server)
            server.add_insecure_port('[::]:' + str(port))
            server.start()

            branches_info[branch_id] = {'balance': balance, 'port': port}

            server_objects.append(server)

            print(f"Branch {branch_id} is listening on port {port}")

    with open('branch_info.json', 'w') as info_file:
        json.dump(list(branches_info.values()), info_file, indent=4)

    return server_objects

def serve():
    parser = argparse.ArgumentParser(description='Branch Server')
    parser.add_argument('json_file', help='Path to the JSON file')
    args = parser.parse_args()

    branch_servers = load_branches(args.json_file)

    for server in branch_servers:
        server.wait_for_termination()

if __name__ == '__main__':
    serve()
