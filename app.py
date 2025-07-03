from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import hashlib
import json
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 生产环境请使用更安全的密钥

# 数据库连接封装
def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('campus.db')
    conn.row_factory = sqlite3.Row  # 使查询结果可以像字典一样访问
    return conn

def hash_password(password):
    """密码哈希加密"""
    return hashlib.sha256(password.encode()).hexdigest()

# 登录验证装饰器
def login_required(f):
    """检查用户是否已登录"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """角色权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('请先登录', 'error')
                return redirect(url_for('login'))
            
            if session.get('role') not in roles:
                flash('权限不足', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 主路由
@app.route('/')
def index():
    """首页，根据登录状态重定向"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM Users WHERE username = ? AND password_hash = ? AND is_active = 1',
            (username, hash_password(password))
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['real_name'] = user['real_name']
            session['role'] = user['role']
            flash(f'欢迎回来，{user["real_name"]}！', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已成功退出登录', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """根据用户角色重定向到对应的主页"""
    role = session.get('role')
    if role == 'student':
        return redirect(url_for('student_dashboard'))
    elif role == 'organizer':
        return redirect(url_for('organizer_dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    else:
        flash('未知用户角色', 'error')
        return redirect(url_for('login'))

# 学生（参与者）路由
@app.route('/student')
@role_required(['student'])
def student_dashboard():
    """学生主页 - 显示可报名活动列表"""
    conn = get_db_connection()
    
    # 获取可报名的活动（已审批且未过期）
    activities = conn.execute('''
        SELECT a.*, p.name as place_name, u.real_name as organizer_name
        FROM Activities a
        LEFT JOIN Places p ON a.place_id = p.id
        LEFT JOIN Users u ON a.organizer_id = u.id
        WHERE a.status = 'approved' 
        AND a.registration_deadline >= date('now')
        AND a.current_participants < a.max_participants
        ORDER BY a.registration_deadline ASC
    ''').fetchall()
    
    # 获取我的参与记录
    my_activities = conn.execute('''
        SELECT a.*, pt.status as participation_status, pt.score
        FROM Activities a
        JOIN Participations pt ON a.id = pt.activity_id
        WHERE pt.student_id = ?
        ORDER BY pt.registered_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('student/dashboard.html', 
                         activities=activities, 
                         my_activities=my_activities)

@app.route('/student/register/<int:activity_id>', methods=['POST'])
@role_required(['student'])
def register_activity(activity_id):
    """学生报名活动"""
    conn = get_db_connection()
    
    # 检查是否已报名
    existing = conn.execute('''
        SELECT id FROM Participations 
        WHERE activity_id = ? AND student_id = ?
    ''', (activity_id, session['user_id'])).fetchone()
    
    if existing:
        flash('您已经报名了这个活动', 'warning')
    else:
        # 插入报名记录
        conn.execute('''
            INSERT INTO Participations (activity_id, student_id, status)
            VALUES (?, ?, 'registered')
        ''', (activity_id, session['user_id']))
        
        # 更新活动参与人数
        conn.execute('''
            UPDATE Activities 
            SET current_participants = current_participants + 1
            WHERE id = ?
        ''', (activity_id,))
        
        conn.commit()
        flash('报名成功！', 'success')
    
    conn.close()
    return redirect(url_for('student_dashboard'))

# 组织者路由
@app.route('/organizer')
@role_required(['organizer'])
def organizer_dashboard():
    """组织者主页"""
    conn = get_db_connection()
    
    # 获取我创建的活动
    my_activities = conn.execute('''
        SELECT a.*, p.name as place_name
        FROM Activities a
        LEFT JOIN Places p ON a.place_id = p.id
        WHERE a.organizer_id = ?
        ORDER BY a.created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('organizer/dashboard.html', my_activities=my_activities)

@app.route('/organizer/create_activity', methods=['GET', 'POST'])
@role_required(['organizer'])
def create_activity():
    """创建活动"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        max_participants = request.form['max_participants']
        place_id = request.form['place_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        registration_deadline = request.form['registration_deadline']
        requested_fund = request.form['requested_fund']
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Activities (title, description, organizer_id, category, max_participants, 
                                  place_id, start_date, end_date, registration_deadline, requested_fund)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, session['user_id'], category, max_participants, 
              place_id, start_date, end_date, registration_deadline, requested_fund))
        conn.commit()
        conn.close()
        
        flash('活动创建成功，等待审批', 'success')
        return redirect(url_for('organizer_dashboard'))
    
    # GET请求，显示创建表单
    conn = get_db_connection()
    places = conn.execute('SELECT * FROM Places WHERE is_available = 1').fetchall()
    conn.close()
    
    return render_template('organizer/create_activity.html', places=places)

# 管理员路由
@app.route('/admin')
@role_required(['admin'])
def admin_dashboard():
    """管理员主页"""
    conn = get_db_connection()
    
    # 获取待审批的活动
    pending_activities = conn.execute('''
        SELECT a.*, u.real_name as organizer_name, p.name as place_name
        FROM Activities a
        JOIN Users u ON a.organizer_id = u.id
        LEFT JOIN Places p ON a.place_id = p.id
        WHERE a.status = 'pending'
        ORDER BY a.created_at ASC
    ''').fetchall()
    
    # 获取所有活动统计
    stats = conn.execute('''
        SELECT status, COUNT(*) as count
        FROM Activities
        GROUP BY status
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         pending_activities=pending_activities, 
                         stats=stats)

@app.route('/admin/approve_activity/<int:activity_id>', methods=['POST'])
@role_required(['admin'])
def approve_activity(activity_id):
    """审批活动"""
    action = request.form['action']  # 'approve' or 'reject'
    
    conn = get_db_connection()
    if action == 'approve':
        conn.execute('''
            UPDATE Activities SET status = 'approved'
            WHERE id = ?
        ''', (activity_id,))
        flash('活动审批通过', 'success')
    else:
        conn.execute('''
            UPDATE Activities SET status = 'rejected'
            WHERE id = ?
        ''', (activity_id,))
        flash('活动已拒绝', 'info')
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_dashboard'))

# 老师路由
@app.route('/teacher')
@role_required(['teacher'])
def teacher_dashboard():
    """老师主页"""
    conn = get_db_connection()
    
    # 获取需要资金审批的活动
    fund_requests = conn.execute('''
        SELECT a.*, u.real_name as organizer_name, f.requested_amount, f.id as fund_id
        FROM Activities a
        JOIN Users u ON a.organizer_id = u.id
        LEFT JOIN Funds f ON a.id = f.activity_id
        WHERE a.status = 'approved' AND a.requested_fund > 0
        AND (f.status = 'pending' OR f.status IS NULL)
        ORDER BY a.created_at ASC
    ''').fetchall()
    
    # 获取需要评分的活动
    activities_to_score = conn.execute('''
        SELECT a.*, COUNT(p.id) as participant_count
        FROM Activities a
        LEFT JOIN Participations p ON a.id = p.activity_id
        WHERE a.status = 'completed'
        GROUP BY a.id
        ORDER BY a.end_date DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('teacher/dashboard.html', 
                         fund_requests=fund_requests,
                         activities_to_score=activities_to_score)

@app.route('/teacher/approve_fund/<int:activity_id>', methods=['POST'])
@role_required(['teacher'])
def approve_fund(activity_id):
    """资金拨款审批"""
    approved_amount = request.form['approved_amount']
    
    conn = get_db_connection()
    
    # 检查是否已有资金记录
    existing_fund = conn.execute('''
        SELECT id FROM Funds WHERE activity_id = ?
    ''', (activity_id,)).fetchone()
    
    if existing_fund:
        # 更新现有记录
        conn.execute('''
            UPDATE Funds SET approved_amount = ?, status = 'approved', 
                           approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE activity_id = ?
        ''', (approved_amount, session['user_id'], activity_id))
    else:
        # 创建新记录
        conn.execute('''
            INSERT INTO Funds (activity_id, requested_amount, approved_amount, 
                             status, approved_by, approved_at)
            SELECT ?, requested_fund, ?, 'approved', ?, CURRENT_TIMESTAMP
            FROM Activities WHERE id = ?
        ''', (activity_id, approved_amount, session['user_id'], activity_id))
    
    # 更新活动的批准资金
    conn.execute('''
        UPDATE Activities SET approved_fund = ? WHERE id = ?
    ''', (approved_amount, activity_id))
    
    conn.commit()
    conn.close()
    
    flash('资金拨款审批完成', 'success')
    return redirect(url_for('teacher_dashboard'))

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)