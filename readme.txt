Required: Docker
In terminal: docker-compose up -d
Then go to:localhost:5050 with pw=1234
There: Create Server -> Name = Books and host = postgres
Create Database -> name = Books
(Run 'python3 create_integrated_database.py' and 'python3 connect.py' in Backend terminal to create schema)
(Run 'python3 main.py' for dummy data)
In localhost:4200 is frontend
