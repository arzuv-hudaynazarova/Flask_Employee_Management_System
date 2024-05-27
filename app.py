from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from config import DATABASE_CONFIG

app = Flask(__name__)
app.secret_key = '12345'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'


def get_db_connection():
    try:
        return mysql.connector.connect(**DATABASE_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db_connection()
    if db is None:
        flash('Database connection failed')
        return redirect(url_for('login'))
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS count FROM user")
        total_employees = cursor.fetchone()['count']
        cursor.execute("SELECT SUM(insurance_payment) AS insurance_payments FROM user WHERE insurance=1")
        insurance_payments = cursor.fetchone()['insurance_payments']
        cursor.execute("SELECT SUM(salary) AS total_salaries FROM user")
        total_salaries = cursor.fetchone()['total_salaries']
        cursor.execute("SELECT id, full_name, salary, IF(insurance=1, 'Yes', 'No') AS insurance FROM user")
        employees = cursor.fetchall()
    finally:
        cursor.close()
        db.close()
    return render_template('index.html', total_employees=total_employees, total_salaries=total_salaries,
                           insurance_payments=insurance_payments, employees=employees)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        db = get_db_connection()
        if db is None:
            flash('Database connection failed')
            return redirect(url_for('create_user'))
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO user (full_name, age, salary, job, email, phone_number, date_of_employment, worked_time, insurance, insurance_payment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                request.form['full_name'], int(request.form['age']), request.form['salary'],
                request.form['job'], request.form['email'], request.form['phone_number'],
                request.form['date_of_employment'], request.form['worked_time'],
                request.form['insurance'], request.form['insurance_payment']
            ))
            db.commit()
            flash('User added successfully!')
            return redirect(url_for('home'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}")
            db.rollback()
        finally:
            cursor.close()
            db.close()
    return render_template('adduser.html')


@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db_connection()
    if db is None:
        flash('Database connection failed')
        return redirect(url_for('create_user'))
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO user (full_name, age, salary, job, email, phone_number, date_of_employment, worked_time, insurance, insurance_payment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form['full_name'], int(request.form['age']), request.form['salary'],
            request.form['job'], request.form['email'], request.form['phone_number'],
            request.form['date_of_employment'], request.form['worked_time'],
            request.form['insurance'], request.form['insurance_payment']
        ))
        db.commit()
        cursor.execute("SELECT * FROM user ORDER BY id DESC LIMIT 1")
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        flash(f"Error: {err}")
        db.rollback()
        user = None
    finally:
        cursor.close()
        db.close()
    return render_template('submitteddata.html', user=user)


@app.route('/get-data', methods=['GET', 'POST'])
def get_data():
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    if db is None:
        flash('Database connection failed')
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)
    user_data = None
    try:
        if request.method == 'POST':
            input_full_name = request.form.get('input_full_name', '')
            select_query = "SELECT * FROM user WHERE full_name LIKE %s"
            cursor.execute(select_query, (f"%{input_full_name}%",))
            user_data = cursor.fetchall()
            render_template('data.html', user=user_data)
        else:
            select_all_query = "SELECT * FROM user ORDER BY id"
            cursor.execute(select_all_query)
            user_data = cursor.fetchall()
    finally:
        cursor.close()
        db.close()

    # Check if data is empty and handle it
    if not user_data:
        flash("No data found", "info")  # Use a custom message or handling as necessary
        return render_template('get_data.html', data=[])

    return render_template('get_data.html', data=user_data)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_data(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    if db is None:
        flash('Database connection failed')
        return redirect(url_for('get_data'))

    cursor = db.cursor()
    try:
        delete_query = "DELETE FROM user WHERE id = %s"
        cursor.execute(delete_query, (id,))
        db.commit()
        flash('Data successfully deleted!')
    finally:
        cursor.close()
        db.close()
    return redirect(url_for('get_data'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    db = get_db_connection()
    if db is None:
        flash('Database connection failed', 'error')
        return redirect(url_for('get_data'))

    cursor = db.cursor(buffered=True)
    try:
        if request.method == 'POST':
            full_name = request.form['full_name']
            age = int(request.form['age'])
            salary = request.form['salary']
            job = request.form['job']
            email = request.form['email']
            phone_number = request.form['phone_number']
            date_of_employment = request.form['date_of_employment']
            worked_time = request.form['worked_time']
            insurance = request.form['insurance']
            insurance_payment = request.form['insurance_payment']

            update_query = """
            UPDATE user SET full_name=%s, age=%s, salary=%s, job=%s, email=%s, phone_number=%s, date_of_employment=%s, worked_time=%s, insurance=%s, insurance_payment=%s
            WHERE id=%s
            """
            cursor.execute(update_query, (
                full_name, age, salary, job, email, phone_number, date_of_employment, worked_time, insurance,
                insurance_payment, id))
            db.commit()
            flash('User data updated successfully.')
            return redirect(url_for('update_success', id=id))  # Corrected redirect

        # Handle GET request to pre-fill the form for updating
        cursor.execute("SELECT * FROM user WHERE id = %s", (id,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", 'error')
        db.rollback()  # Roll back the transaction on error
    finally:
        cursor.close()
        db.close()

    if user:
        return render_template('update.html', user=user)
    else:
        flash('User not found', 'error')
        return redirect(url_for('get_data'))


@app.route('/update-success/<int:id>')
def update_success(id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE id = %s", (id,))
    user_data = cursor.fetchone()
    cursor.close()
    db.close()

    if user_data:
        return render_template('update_success.html', user=user_data)
    else:
        flash('User not found', 'error')
        return redirect(url_for('get_data'))


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')