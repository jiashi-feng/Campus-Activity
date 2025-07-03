import sqlite3
import hashlib
from datetime import datetime

def init_database():
    """初始化数据库和表结构"""
    conn = sqlite3.connect('campus.db')
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            real_name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            role VARCHAR(20) NOT NULL CHECK(role IN ('student', 'organizer', 'admin', 'teacher')),
            student_id VARCHAR(20),
            specialties TEXT,  -- 特长，JSON格式存储
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # 创建活动表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            organizer_id INTEGER NOT NULL,
            category VARCHAR(50),
            required_specialties TEXT,  -- 所需特长，JSON格式
            max_participants INTEGER DEFAULT 50,
            current_participants INTEGER DEFAULT 0,
            place_id INTEGER,
            start_date DATE,
            end_date DATE,
            registration_deadline DATE,
            status VARCHAR(20) DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'ongoing', 'completed')),
            requested_fund DECIMAL(10,2) DEFAULT 0,
            approved_fund DECIMAL(10,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organizer_id) REFERENCES Users(id),
            FOREIGN KEY (place_id) REFERENCES Places(id)
        )
    ''')
    
    # 创建场地表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            capacity INTEGER NOT NULL,
            location VARCHAR(200),
            equipment TEXT,  -- 设备描述
            is_available BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建参与记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Participations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'registered' CHECK(status IN ('registered', 'approved', 'rejected', 'completed', 'withdrawn')),
            progress_report TEXT,
            leave_request TEXT,
            leave_status VARCHAR(20) DEFAULT 'none' CHECK(leave_status IN ('none', 'pending', 'approved', 'rejected')),
            score DECIMAL(3,1),  -- 活动评分
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (activity_id) REFERENCES Activities(id),
            FOREIGN KEY (student_id) REFERENCES Users(id),
            UNIQUE(activity_id, student_id)
        )
    ''')
    
    # 创建资金记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Funds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            requested_amount DECIMAL(10,2) NOT NULL,
            approved_amount DECIMAL(10,2) DEFAULT 0,
            status VARCHAR(20) DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'disbursed')),
            request_reason TEXT,
            approval_reason TEXT,
            approved_by INTEGER,  -- 审批老师ID
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            FOREIGN KEY (activity_id) REFERENCES Activities(id),
            FOREIGN KEY (approved_by) REFERENCES Users(id)
        )
    ''')
    
    conn.commit()
    
    # 插入初始数据
    insert_sample_data(cursor)
    
    conn.commit()
    conn.close()
    print("数据库初始化完成!")

def hash_password(password):
    """密码哈希加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def insert_sample_data(cursor):
    """插入示例数据"""
    
    # 插入示例用户
    sample_users = [
        ('admin', hash_password('123456'), '系统管理员', 'admin@campus.edu', '13800000001', 'admin', 'ADM001', '["系统管理"]'),
        ('teacher1', hash_password('123456'), '张老师', 'teacher1@campus.edu', '13800000002', 'teacher', 'TEA001', '["教学管理"]'),
        ('organizer1', hash_password('123456'), '李组织者', 'organizer1@campus.edu', '13800000003', 'organizer', 'STU001', '["活动策划","团队协作"]'),
        ('student1', hash_password('123456'), '王学生', 'student1@campus.edu', '13800000004', 'student', 'STU002', '["编程","设计"]'),
        ('student2', hash_password('123456'), '赵同学', 'student2@campus.edu', '13800000005', 'student', 'STU003', '["音乐","表演"]'),
    ]
    
    cursor.executemany('''
        INSERT INTO Users (username, password_hash, real_name, email, phone, role, student_id, specialties)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_users)
    
    # 插入示例场地
    sample_places = [
        ('学术报告厅', 200, '教学楼A座1楼', '投影仪,音响设备,麦克风'),
        ('多媒体教室101', 60, '教学楼B座1楼', '电脑,投影仪'),
        ('体育馆', 500, '体育中心', '音响设备,灯光设备'),
        ('图书馆会议室', 30, '图书馆3楼', '投影仪,白板'),
    ]
    
    cursor.executemany('''
        INSERT INTO Places (name, capacity, location, equipment)
        VALUES (?, ?, ?, ?)
    ''', sample_places)
    
    # 插入示例活动
    sample_activities = [
        ('Python编程大赛', '面向全校学生的编程竞赛活动', 3, '技术竞赛', '["编程"]', 50, 0, 1, '2024-08-01', '2024-08-15', '2024-07-25', 'pending', 2000.00, 0),
        ('校园音乐节', '展示学生音乐才艺的文艺活动', 3, '文艺活动', '["音乐","表演"]', 100, 0, 3, '2024-08-10', '2024-08-12', '2024-08-05', 'pending', 5000.00, 0),
    ]
    
    cursor.executemany('''
        INSERT INTO Activities (title, description, organizer_id, category, required_specialties, max_participants, current_participants, place_id, start_date, end_date, registration_deadline, status, requested_fund, approved_fund)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_activities)

if __name__ == '__main__':
    init_database()