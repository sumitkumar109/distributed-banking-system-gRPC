# Distributed Banking System with gRPC

## Overview
This Distributed Banking System is a sophisticated implementation of a distributed financial infrastructure using gRPC, a high-performance, language-neutral RPC framework. The system enables multiple users to perform banking operations like deposits and withdrawals while ensuring data consistency across various branches.

### Problem Statement
The core challenge of this project was twofold:
1. **Distributed Transactions**: Implementing a distributed banking system that allows users to interact with various branches while maintaining a consistent copy of the bank account balance across all branches.
2. **Client-Centric Consistency**: Ensuring that customers consistently see the effects of their transactions across various branch processes, a concept known as "read-your-writes" consistency.

## Features
- **Multi-User Environment**: Allows several users to interact with the system concurrently, performing operations like balance queries, deposits, and withdrawals.
- **Client-Branch Interaction**: Clients communicate with their respective branches, ensuring that all branches have accurate replicas of the bank account balance.
- **Data Consistency**: Implements a robust consistency model to maintain the integrity and reliability of customer data across the distributed banking network.
- **Effective Communication**: Uses gRPC for seamless and reliable communication between clients and branches.

## Technology Stack
- **Python (3.11.4)**: Used for building server (branch) and client code, data processing, and business logic implementation.
- **gRPC (1.59.0)**: The foundational technology of the distributed system, used for defining services and generating server and client code.
- **Protocol Buffers (Proto)**: Used for defining service interfaces and data structures in a language-independent way.

## Implementation
- **Service Definition**: Services and communication channels are defined in a `.proto` file, which is then used to generate client and server code.
- **Server Implementation (Branches)**: Branches act as servers, managing banking operations and keeping a replica of the bank account balance.
- **Client Implementation (Customers)**: Customers interact with their designated branches, making transactions and ensuring data consistency through gRPC.
- **Data Consistency**: The system ensures that each customer action updates the specific branch and propagates the changes to all other branches.

## Results
- **Successful Deployment**: Enabled many clients to interact with various branches, conducting operations smoothly and efficiently.
- **Data Consistency**: Ensured consistent balance replicas between all branches and effective communication between customers and branches.

## Future Work
- **Scalability**: The system's architecture lays the groundwork for future enhancements in scalability, allowing it to handle an increasing number of branches and users.
- **Security**: Future versions can focus on integrating advanced security measures to protect customer data and transaction integrity.
- **Robust Error Handling**: Plans to improve the system's resilience against errors and exceptions, ensuring smooth operation under a wide range of scenarios.
