from flask import Flask, jsonify, request
from con import set_connection
from loggerinstance import logger

app = Flask(__name__)


# CREATE TABLE roles (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     base_salary NUMERIC(10, 2) NOT NULL,
#     tax_rate NUMERIC(4, 2) NOT NULL,
#     benefits NUMERIC(10, 2) NOT NULL
# );
#
# CREATE TABLE employees (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(50) NOT NULL,
#     email VARCHAR(50) NOT NULL,
#     role_id INTEGER REFERENCES roles(id) NOT NULL
# );


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error occurred while executing {func.__name__}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return wrapper


# Endpoint to calculate the salary for an employee
@app.route('/v1/employees/salary', methods=['GET'])
@handle_exceptions
def calculate_salary():
    # Get the employee data from the request body
    # {"role_id":1}
    employee_data = request.get_json()
    cur, conn = set_connection()
    # Retrieve the salary data for the employee's role
    cur.execute('SELECT base_salary, tax_rate, benefits FROM roles WHERE id = %s', (employee_data['role_id'],))
    row = cur.fetchone()
    base_salary = row[0]
    tax_rate = row[1]
    benefits = row[2]

    # Calculate the salary and taxes for the employee
    salary = base_salary - (base_salary * tax_rate)
    taxes = base_salary * tax_rate

    # Add the employee's benefits to the salary
    salary += benefits
    # Log the salary calculation
    logger.info(f"Calculated salary of {salary} for employee with role_id {employee_data['role_id']}")

    return jsonify({'salary': salary, 'taxes': taxes}), 200


# Endpoint to add a new employee
@app.route('/v1/employees/add', methods=['POST'], endpoint='add_employee')
@handle_exceptions
def add_employee():
    # Get the employee data from the request body
    # {
    #     "name": "John Smith",
    #     "email": "john.smith@example.com",
    #     "role_id": 2
    # }

    employee_data = request.get_json()
    cur, conn = set_connection()
    # Insert the employee into the database
    cur.execute(
        'INSERT INTO employees (name, email, role_id) VALUES (%s, %s, %s)',
        (employee_data['name'], employee_data['email'], employee_data['role_id'])
    )
    conn.commit()
    # Log the successful employee creation
    logger.info(
        f"Created employee {employee_data['name']} with email {employee_data['email']} and role_id {employee_data['role_id']}")
    return jsonify({'message': 'Employee added successfully.'}), 200


@app.route('/v1/employees', methods=['GET'], endpoint='get_all_employees')
@handle_exceptions
def get_all_employees():
    cur, conn = set_connection()
    cur.execute('SELECT id, name, email, role_id FROM employees')
    rows = cur.fetchall()
    employees = []
    for row in rows:
        employee = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'role_id': row[3]
        }
        employees.append(employee)
    logger.info("Employees retrived successfully")
    return jsonify(employees), 200


@app.route('/v1/roles/add', methods=['POST'], endpoint='add_role')
@handle_exceptions
def add_role():
    # {
    #     "name": "Manager",
    #     "base_salary": 75000.00,
    #     "tax_rate": 0.30,
    #     "benefits": 10000.00
    # }

    data = request.get_json()
    name = data['name']
    base_salary = data['base_salary']
    tax_rate = data['tax_rate']
    benefits = data['benefits']

    cur, conn = set_connection()
    cur.execute('INSERT INTO roles (name, base_salary, tax_rate, benefits) VALUES (%s, %s, %s, %s)',
                (name, base_salary, tax_rate, benefits))
    conn.commit()
    logger.info(
        f"Role added successfully with name={name}, base_salary={base_salary}, tax_rate={tax_rate}, benefits={benefits}")
    return jsonify({'message': 'Role added successfully'}), 201


@app.route('/v1/roles', methods=['GET'], endpoint='get_all_roles')
@handle_exceptions
def get_all_roles():
    cur, conn = set_connection()
    cur.execute('SELECT id, name, base_salary, tax_rate, benefits FROM roles')
    rows = cur.fetchall()
    roles = []
    for row in rows:
        role = {
            'id': row[0],
            'name': row[1],
            'base_salary': float(row[2]),
            'tax_rate': float(row[3]),
            'benefits': float(row[4])
        }
        roles.append(role)
    logger.info("All roles retrieved successfully")
    return jsonify(roles), 200


if __name__ == '__main__':
    app.run(debug=True)
