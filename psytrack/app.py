from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import random
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'psytrack_secret_key_2024'

# ===================== MOCK USERS =====================
USERS = {
    'admin': {'password': 'admin123', 'role': 'Admin', 'name': 'Nguyễn Văn Admin'},
    'ceo': {'password': 'ceo123', 'role': 'CEO', 'name': 'Trần Thị CEO'},
    'hr': {'password': 'hr123', 'role': 'HR Manager', 'name': 'Lê Văn HR'},
}

# ===================== MOCK DATA =====================
DEPARTMENTS = ['Phòng IT', 'Phòng Marketing', 'Phòng Kế Toán', 'Phòng Kinh Doanh', 'Phòng Nhân Sự']
EXPRESSIONS = ['Bình thường', 'Vui vẻ', 'Căng thẳng', 'Mệt mỏi', 'Tập trung']
EXPRESSION_EN = ['normal', 'happy', 'stressed', 'tired', 'focused']
EMPLOYEES = [
    {'id': f'EMP{str(i).zfill(3)}', 'name': name, 'dept': DEPARTMENTS[i % len(DEPARTMENTS)]}
    for i, name in enumerate([
        'Nguyễn Minh Tuấn', 'Trần Thị Lan', 'Lê Văn Hùng', 'Phạm Thu Hà', 'Hoàng Đức Nam',
        'Vũ Thị Mai', 'Đặng Quốc Bảo', 'Bùi Thanh Tâm', 'Đỗ Thị Hoa', 'Ngô Văn Khoa',
        'Trịnh Minh Khải', 'Dương Thị Yến', 'Lý Văn Phong', 'Hồ Thị Ngọc', 'Phan Văn Đức',
        'Đinh Thị Hương', 'Chu Minh Quân', 'Tô Thị Bích', 'Lưu Văn Thắng', 'Mai Thị Linh',
    ], 1)
]

def generate_mock_data(date_str=None, dept=None, emp_id=None):
    """Generate realistic mock employee psychology data"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    records = []
    target_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    employees = EMPLOYEES
    if dept:
        employees = [e for e in EMPLOYEES if e['dept'] == dept]
    if emp_id:
        employees = [e for e in EMPLOYEES if e['id'] == emp_id]
    
    for emp in employees:
        # Morning session 7h-11h
        for hour in range(7, 12):
            for minute in [0, 30]:
                ts = target_date.replace(hour=hour, minute=minute)
                exp_idx = random.choices(range(5), weights=[35, 15, 25, 15, 10])[0]
                hr_val = random.randint(60, 110)
                stress = round(min(100, max(0, (hr_val - 65) * 2.2 + random.uniform(-10, 10))), 1)
                records.append({
                    'id': emp['id'],
                    'name': emp['name'],
                    'department': emp['dept'],
                    'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                    'heart_rate': hr_val,
                    'stress_level': stress,
                    'expression': EXPRESSIONS[exp_idx],
                    'expression_en': EXPRESSION_EN[exp_idx],
                    'health': round(random.uniform(0.6, 0.99), 2),
                    'alert': stress > 75
                })
        # Afternoon session 13h-17h
        for hour in range(13, 18):
            for minute in [0, 30]:
                ts = target_date.replace(hour=hour, minute=minute)
                exp_idx = random.choices(range(5), weights=[30, 10, 30, 20, 10])[0]
                hr_val = random.randint(62, 115)
                stress = round(min(100, max(0, (hr_val - 65) * 2.2 + random.uniform(-10, 10))), 1)
                records.append({
                    'id': emp['id'],
                    'name': emp['name'],
                    'department': emp['dept'],
                    'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                    'heart_rate': hr_val,
                    'stress_level': stress,
                    'expression': EXPRESSIONS[exp_idx],
                    'expression_en': EXPRESSION_EN[exp_idx],
                    'health': round(random.uniform(0.55, 0.98), 2),
                    'alert': stress > 75
                })
    return records

# ===================== AUTH DECORATOR =====================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ===================== ROUTES =====================
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            session['name'] = USERS[username]['name']
            return redirect(url_for('dashboard'))
        error = 'Tên đăng nhập hoặc mật khẩu không đúng!'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().strftime('%Y-%m-%d')
    data = generate_mock_data(today)
    
    # Summary stats
    total_emp = len(set(r['id'] for r in data))
    alert_emp = len(set(r['id'] for r in data if r['alert']))
    avg_stress = round(sum(r['stress_level'] for r in data) / len(data), 1) if data else 0
    avg_hr = round(sum(r['heart_rate'] for r in data) / len(data), 1) if data else 0
    
    # Expression distribution for today (latest record per employee)
    latest = {}
    for r in data:
        if r['id'] not in latest or r['timestamp'] > latest[r['id']]['timestamp']:
            latest[r['id']] = r
    
    expr_count = {}
    for r in latest.values():
        expr_count[r['expression']] = expr_count.get(r['expression'], 0) + 1
    
    # Hourly stress by hour
    hourly_stress = {}
    for r in data:
        h = int(r['timestamp'].split(' ')[1].split(':')[0])
        if h not in hourly_stress:
            hourly_stress[h] = []
        hourly_stress[h].append(r['stress_level'])
    hourly_avg = {h: round(sum(v)/len(v), 1) for h, v in hourly_stress.items()}
    
    # Dept stress
    dept_stress = {}
    for r in data:
        d = r['department']
        if d not in dept_stress:
            dept_stress[d] = []
        dept_stress[d].append(r['stress_level'])
    dept_avg = {d: round(sum(v)/len(v), 1) for d, v in dept_stress.items()}
    
    stats = {
        'total_employees': total_emp,
        'alert_employees': alert_emp,
        'avg_stress': avg_stress,
        'avg_heart_rate': avg_hr,
        'expr_distribution': expr_count,
        'hourly_stress': hourly_avg,
        'dept_stress': dept_avg,
        'today': today,
    }
    return render_template('dashboard.html', stats=stats, departments=DEPARTMENTS)

@app.route('/detail')
@login_required
def detail():
    return render_template('detail.html', departments=DEPARTMENTS, employees=EMPLOYEES)

# ===================== API ROUTES =====================
@app.route('/api/data')
@login_required
def api_data():
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    dept = request.args.get('dept', None)
    emp_id = request.args.get('emp_id', None)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    data = generate_mock_data(date_str, dept if dept != 'all' else None, emp_id if emp_id else None)
    data.sort(key=lambda x: x['timestamp'], reverse=True)
    
    total = len(data)
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'data': data[start:end]
    })

@app.route('/api/summary')
@login_required
def api_summary():
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    dept = request.args.get('dept', None)
    data = generate_mock_data(date_str, dept if dept and dept != 'all' else None)
    
    latest = {}
    for r in data:
        if r['id'] not in latest or r['timestamp'] > latest[r['id']]['timestamp']:
            latest[r['id']] = r
    
    expr_count = {}
    for r in latest.values():
        expr_count[r['expression']] = expr_count.get(r['expression'], 0) + 1
    
    hourly_stress = {}
    for r in data:
        h = int(r['timestamp'].split(' ')[1].split(':')[0])
        if h not in hourly_stress:
            hourly_stress[h] = []
        hourly_stress[h].append(r['stress_level'])
    hourly_avg = {str(h): round(sum(v)/len(v), 1) for h, v in hourly_stress.items()}
    
    dept_stress = {}
    for r in data:
        d = r['department']
        if d not in dept_stress:
            dept_stress[d] = []
        dept_stress[d].append(r['stress_level'])
    dept_avg = {d: round(sum(v)/len(v), 1) for d, v in dept_stress.items()}
    
    alert_list = [r for r in latest.values() if r['alert']]
    
    return jsonify({
        'total_employees': len(latest),
        'alert_employees': len(alert_list),
        'avg_stress': round(sum(r['stress_level'] for r in data)/len(data), 1) if data else 0,
        'avg_heart_rate': round(sum(r['heart_rate'] for r in data)/len(data), 1) if data else 0,
        'expr_distribution': expr_count,
        'hourly_stress': hourly_avg,
        'dept_stress': dept_avg,
        'alert_list': alert_list[:10],
    })

@app.route('/api/employee/<emp_id>/history')
@login_required
def api_employee_history(emp_id):
    days = int(request.args.get('days', 7))
    records = []
    for i in range(days):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        records.extend(generate_mock_data(d, emp_id=emp_id))
    records.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify({'employee_id': emp_id, 'records': records[:200]})

@app.route('/api/departments')
@login_required
def api_departments():
    return jsonify({'departments': DEPARTMENTS})

@app.route('/api/employees')
@login_required
def api_employees():
    dept = request.args.get('dept', None)
    emps = EMPLOYEES
    if dept and dept != 'all':
        emps = [e for e in EMPLOYEES if e['dept'] == dept]
    return jsonify({'employees': emps})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
