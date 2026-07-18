CREATE DATABASE flaskapp;
USE flaskapp;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'parent') NOT NULL,
    status ENUM('active', 'pending') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    class_assigned VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO users(name,email,password,role,status)
VALUES(
'Admin',
'admin@gmail.com',
'scrypt:32768:8:1$2ueNxkNS32TQgxiw$d62ed5dc181ef705b32c10018593622ff5108a323b5d00e59d6d59ac79e5883f01318c23e42d6b8e23ff194d431ef004ed05643f839dfee7ce5e23ed17da863d',
'admin',
'active'
);

SELECT * FROM users;
SELECT * FROM teachers;

CREATE TABLE students(
	id int auto_increment primary key,
    name varchar(255) not null,
    dob date not null,
    gender enum('male', 'female', 'other') not null,
    class_name varchar(50) not null,
    parent_id int not null,
    
    foreign key(parent_id)
    references users(id)
    on delete cascade
);

SELECT * FROM students;

CREATE TABLE timetable (
	id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    day ENUM (
		'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday'
	) NOT NULL,
    period1 VARCHAR(100) NOT NULL,
	period2 VARCHAR(100) NOT NULL,
	period3 VARCHAR(100) NOT NULL,
	period4 VARCHAR(100) NOT NULL,
	period5 VARCHAR(100) NOT NULL,
	period6 VARCHAR(100) NOT NULL,
    
    UNIQUE(class_name, day)
);

CREATE TABLE events(
	id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    event_date DATE NOT NULL,
    target_class VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM events;

CREATE TABLE attendance(
	id int auto_increment primary key,
    student_id int not null,
    attendance_date date not null,
    status enum('present','absent') not null,
    class_name varchar(50) not null,
    marked_by int not null,
    
    foreign key (student_id)
    references students(id)
    on delete cascade,
    
    foreign key(marked_by)
    references users(id)
    on delete cascade,
    
    unique(student_id, attendance_date)
);

CREATE TABLE fee_structure(
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) UNIQUE NOT NULL,
    total_fee DECIMAL(10,2) NOT NULL,
    due_date DATE NOT NULL
);

CREATE TABLE fee_payment(
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    amount_paid DECIMAL(10,2) NOT NULL,

    payment_date DATE NOT NULL,

    payment_mode ENUM(
        'Cash',
        'UPI',
        'Card',
        'Net Banking'
    ) NOT NULL,

    status ENUM(
        'Pending',
        'Partial',
        'Paid'
    ) NOT NULL,

    FOREIGN KEY(student_id)
    REFERENCES students(id)
    ON DELETE CASCADE
);
