# **SynergenHR** [![LGPL License](https://img.shields.io/badge/license-LGPL-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)

**SynergenHR** is a Free and Open Source HRMS (Human Resource Management System) Software designed to streamline HR processes and enhance organizational efficiency.

---

## **Installation**

SynergenHR can be installed on your system by following the steps below. Ensure you have **Python**, **Django**, and a **database** (preferably PostgreSQL) installed as prerequisites.

---

## **Prerequisites**

### **1. Python Installation**

#### **Ubuntu**
1. Open the terminal and install Python:
   ```bash
   sudo apt-get install python3
   ```
2. Verify the installation:
   ```bash
   python3 --version
   ```

#### **Windows**
1. Download Python from the [official website](https://www.python.org/downloads/windows/).
2. During installation, ensure you select **"Add Python to PATH"**.
3. Verify the installation:
   ```bash
   python --version
   ```

#### **macOS**
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Verify the installation:
   ```bash
   python3 --version
   ```

---


### **2. PostgreSQL Installation**

#### **Ubuntu**
1. **Update System Packages**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install PostgreSQL**:
   ```bash
   sudo apt install postgresql postgresql-contrib -y
   ```

3. **Start and Enable PostgreSQL**:
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

4. **Verify Installation**:
   ```bash
   psql --version
   ```

5. **Configure PostgreSQL Database and User**:
   - Switch to the `postgres` user:
     ```bash
     sudo su postgres
     psql
     ```
   - Create a new role and database:
     ```sql
     CREATE ROLE synergenhr LOGIN PASSWORD 'synergenhr';
     CREATE DATABASE synergenhr_main OWNER synergenhr;
     \q
     ```
   - Exit the `postgres` user:
     ```bash
     exit
     ```

---

#### **Windows**
1. **Download PostgreSQL**:
   - Download the installer from the [PostgreSQL Official Site](https://www.postgresql.org/download/windows/).

2. **Install PostgreSQL**:
   - Follow the setup wizard and set a password for the PostgreSQL superuser.

3. **Verify Installation**:
   ```powershell
   psql -U postgres
   ```

4. **Configure PostgreSQL Database and User**:
   - Access PostgreSQL:
     ```powershell
     psql -U postgres
     ```
   - Create a new role and database:
     ```sql
     CREATE ROLE synergenhr LOGIN PASSWORD 'synergenhr';
     CREATE DATABASE synergenhr_main OWNER synergenhr;
     \q
     ```

---

#### **macOS**
1. **Install PostgreSQL via Homebrew**:
   ```bash
   brew install postgresql
   ```

2. **Start PostgreSQL**:
   ```bash
   brew services start postgresql
   ```

3. **Verify Installation**:
   ```bash
   psql --version
   ```

4. **Configure PostgreSQL Database and User**:
   - Create a database and user:
     ```bash
     createdb synergenhr_main
     createuser synergenhr
     psql -c "ALTER USER synergenhr WITH PASSWORD 'synergenhr';"
     ```

---

## **Install SynergenHR**

Follow the steps below to install **SynergenHR** on your system. SynergenHR is compatible with **Ubuntu**, **Windows**, and **macOS**.

---

### **1. Clone the Repository**

```bash
git clone https://github.com/dinurawick/synergenHR.git
cd synergenHR
```

### **2. Set Up Python Virtual Environment**

#### **Ubuntu/macOS**
1. Install `python3-venv`:
   ```bash
   sudo apt-get install python3-venv  # Ubuntu only
   ```
2. Create and activate the virtual environment:
   ```bash
   python3 -m venv synergenvenv
   source synergenvenv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### **Windows**
1. Create and activate the virtual environment:
   ```powershell
   python -m venv synergenvenv
   .\synergenvenv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### **3. Configure Environment Variables**

1. Copy the environment file:
   ```bash
   cp .env .env.local
   ```

2. Edit the `.env.local` file and set the following values:
   ```env
   DEBUG=True
   TIME_ZONE=Asia/Kolkata
   SECRET_KEY=django-insecure-j8op9)1q8$1&@^s&p*_0%d#pr@w9qj@lo=3#@d=a(^@9@zd@%j
   ALLOWED_HOSTS=localhost,127.0.0.1,*
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=synergenhr_main
   DB_USER=synergenhr
   DB_PASSWORD=synergenhr
   DB_HOST=localhost
   DB_PORT=5432
   ```

---

### **4. Run Django Migrations**

#### **Ubuntu/macOS**
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

#### **Windows**
```powershell
python manage.py makemigrations
python manage.py migrate
```

---

### **5. Create Superuser**

#### **Ubuntu/macOS**
```bash
python3 manage.py createhorillauser --first_name admin --last_name admin --username admin --password admin --email admin@example.com --phone 1234567890
```

#### **Windows**
```powershell
python manage.py createhorillauser --first_name admin --last_name admin --username admin --password admin --email admin@example.com --phone 1234567890
```

---

### **6. Run the Project**

#### **Ubuntu/macOS**
```bash
python3 manage.py runserver
```

#### **Windows**
```powershell
python manage.py runserver
```

---

## **Docker Deployment**

For production deployment, use Docker:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or use the production configuration
docker-compose -f docker-compose.prod.yml up -d
```

---

### **Accessing SynergenHR**

Access your SynergenHR app at **http://localhost:8000**

**Default Login:**
- Username: `admin`
- Password: `admin`

⚠️ **Change the default password immediately after first login!**

---

## **Features**

- **Recruitment**
- **Onboarding**
- **Employee Management**
- **Attendance Tracking**
- **Leave Management**
- **Asset Management**
- **Payroll**
- **Performance Management System**
- **Offboarding**
- **Helpdesk**

---

## **Roadmap**

- **Calendar App** - Development Under Process
- **Project Management** - Development Under Process
- **Chat App** - Development Under Process
- **More to come...**

---

## **Languages and Tools Used**

<p align="left">
  <a href="https://getbootstrap.com" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/bootstrap/bootstrap-plain-wordmark.svg" alt="bootstrap" width="40" height="40"/>
  </a>
  <a href="https://www.chartjs.org" target="_blank" rel="noreferrer">
    <img src="https://www.chartjs.org/media/logo-title.svg" alt="chartjs" width="40" height="40"/>
  </a>
  <a href="https://www.w3schools.com/css/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" alt="css3" width="40" height="40"/>
  </a>
  <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">
    <img src="https://cdn.worldvectorlogo.com/logos/django.svg" alt="django" width="40" height="40"/>
  </a>
  <a href="https://git-scm.com/" target="_blank" rel="noreferrer">
    <img src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" alt="git" width="40" height="40"/>
  </a>
  <a href="https://www.w3.org/html/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original-wordmark.svg" alt="html5" width="40" height="40"/>
  </a>
  <a href="https://www.linux.org/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linux/linux-original.svg" alt="linux" width="40" height="40"/>
  </a>
  <a href="https://www.postgresql.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="40" height="40"/>
  </a>
  <a href="https://www.python.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/>
  </a>
</p>

---

## **Contributing**

We welcome contributions! Please feel free to submit a Pull Request.

---

## **License**

This project is licensed under the LGPL License - see the [LICENSE](LICENSE) file for details.

---

## **About**

SynergenHR is an open-source HRMS solution designed to simplify HR operations and improve organizational efficiency.

---

This README provides a comprehensive guide to installing and setting up SynergenHR on various platforms. If you encounter any issues, feel free to reach out to the SynergenHR community for support. Happy coding! 🚀
