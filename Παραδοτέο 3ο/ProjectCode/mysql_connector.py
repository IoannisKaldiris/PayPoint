import mysql.connector
from mysql.connector import Error
import json


def load_config():
    with open('appsettings.json', 'r') as file:
        data = json.load(file)
    return data


config = load_config()


def create_connection(host_name, user_name, user_password, db_name):
    port_number = config['mysql_connection']['mysql_port_number']
    try:
        connection_ = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            port=port_number
        )
        print("Connection to MySQL DB successful")
        return connection_
    except Error as e:
        print(f"The error '{e}' occurred")
        return None


def execute_query(connection_, sql_query):
    cursor = connection_.cursor()
    try:
        cursor.execute(sql_query)
        connection_.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()


def reset_connection(connection_):
    connection_.reset_session()


# Connect to the MySQL Server
connection = create_connection("localhost", "root", "", "PayPoint")

# SQL for creating the tables
queries = [
    """
    CREATE TABLE IF NOT EXISTS Users (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Email VARCHAR(255) NOT NULL,
        EmailConfirmed BOOLEAN NOT NULL,
        PasswordHash VARCHAR(255) NOT NULL,
        SecurityStamp VARCHAR(255),
        PhoneNumber VARCHAR(50),
        PhoneNumberConfirmed BOOLEAN NOT NULL,
        TwoFactorEnabled BOOLEAN NOT NULL,
        LockoutEndDateUtc DATETIME,
        LockoutEnabled BOOLEAN NOT NULL,
        AccessFailedCount INT NOT NULL,
        UserName VARCHAR(255) NOT NULL,
        Firstname VARCHAR(255),
        Surname VARCHAR(255),
        IsEnabled BOOLEAN NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS UserRoles (
        UserId INT NOT NULL,
        RoleId INT NOT NULL,
        FOREIGN KEY (UserId) REFERENCES Users(Id),
        FOREIGN KEY (RoleId) REFERENCES AspNetRoles(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS UserLogins (
        LoginProvider VARCHAR(255) NOT NULL,
        ProviderKey VARCHAR(255) NOT NULL,
        UserId INT NOT NULL,
        PRIMARY KEY (LoginProvider, ProviderKey, UserId),
        FOREIGN KEY (UserId) REFERENCES Users(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS UserClaims (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        UserId INT NOT NULL,
        ClaimType VARCHAR(255),
        ClaimValue VARCHAR(255),
        FOREIGN KEY (UserId) REFERENCES Users(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS AspNetRoles (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        RoleName VARCHAR(255) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS stakeholders (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Stakhcat VARCHAR(50),
        Name VARCHAR(255),
        Company VARCHAR(255),
        Firstname VARCHAR(255),
        Surname VARCHAR(255),
        Email VARCHAR(255),
        Tel VARCHAR(50),
        Enadis BOOLEAN NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS lndgrps (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(255),
        stakhmerch INT,
        Enadis BOOLEAN NOT NULL,
        FOREIGN KEY (stakhmerch) REFERENCES stakeholders(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS lndsettings (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(255),
        lndid INT,
        Thresholds TEXT,
        FOREIGN KEY (lndid) REFERENCES lnds(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS Contracts (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        `desc` TEXT,
        stakhmerch INT,
        stakhcit INT,
        stakhbank INT,
        lndid INT,
        Enadis BOOLEAN NOT NULL,
        FOREIGN KEY (lndid) REFERENCES lnds(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS roster (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        ScopeId INT,
        ScopeCat VARCHAR(255),
        EnableRTask BOOLEAN NOT NULL,
        DtActivate DATETIME,
        DataType VARCHAR(50),
        DataObj TEXT,
        DtPosted DATETIME,
        DtExecuted DATETIME,
        ExecStatus VARCHAR(50),
        ExecResult TEXT,
        Rtype VARCHAR(50),
        `Interval` INT, -- Using backticks for reserved keyword
        Priority INT,
        Descr TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS adtrail (
    AdtId INT AUTO_INCREMENT PRIMARY KEY,
    Id INT,
    Dtime DATETIME,
    Stakhid INT,
    Stakhcat VARCHAR(255),
    lndid INT,
    UserId INT,
    Category VARCHAR(255),
    Operation VARCHAR(255),
    Rescode INT,
    JobId INT,
    SevLevel INT,
    Descr TEXT,
    FOREIGN KEY (UserId) REFERENCES Users(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal (
    JrnId INT AUTO_INCREMENT PRIMARY KEY,
    Id INT,
    Dtime DATETIME,
    Stakhid INT,
    Stakhcat VARCHAR(255),
    lndid INT,
    UserId INT,
    Category VARCHAR(255),
    Operation VARCHAR(255),
    Rescode INT,
    JobId INT,
    AccAmt DECIMAL(10,2),
    DspAmt DECIMAL(10,2),
    AccTokens INT,
    Descr TEXT,
    FOREIGN KEY (UserId) REFERENCES Users(Id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS health (
    HlthId INT AUTO_INCREMENT PRIMARY KEY,
    Id INT,
    Dtime DATETIME,
    Stakhid INT,
    Stakhcat VARCHAR(255),
    lndid INT,
    App VARCHAR(255),
    AppModule VARCHAR(255),
    Assembly VARCHAR(255),
    Subassembly VARCHAR(255),
    Errcode VARCHAR(255),
    SevLevel INT,
    Descr TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS TransactionLog (
        TransactionId INT AUTO_INCREMENT PRIMARY KEY,
        TransactionType VARCHAR(50) DEFAULT NULL,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UserId INT DEFAULT NULL,
        TotalInsertedAmount DECIMAL(10,2) DEFAULT NULL,
        Description TEXT DEFAULT NULL,
        TotalAmount DECIMAL(10,2) DEFAULT NULL,
        DispensedAmount DECIMAL(10,2) DEFAULT NULL,
        Status VARCHAR(50) DEFAULT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS lnds (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255),
    Address VARCHAR(255),
    Zip VARCHAR(20),
    City VARCHAR(100),
    Country VARCHAR(100),
    Lat DECIMAL(9,6),
    Lon DECIMAL(9,6),
    Type VARCHAR(50),
    Enadis BOOLEAN NOT NULL,
    State VARCHAR(50),
    MRhlthId INT,
    FOREIGN KEY (MRhlthId) REFERENCES health(HlthId)
    );
    """,
    """
    CREATE TABLE simulated_inventory (
    denomination VARCHAR(10),
    count INT,
    min_threshold INT,
    float_threshold INT,
    max_threshold INT,
    full_threshold INT,
    PRIMARY KEY (denomination)
    );
    """
    # Ensure roles are unique before insertion
    """
    INSERT INTO AspNetRoles (RoleName)
    SELECT * FROM (SELECT 'Admin' AS RoleName) AS tmp
    WHERE NOT EXISTS (
        SELECT RoleName FROM AspNetRoles WHERE RoleName = 'Admin'
    ) LIMIT 1;
    """,
    """
    INSERT INTO AspNetRoles (RoleName)
    SELECT * FROM (SELECT 'NDAUser' AS RoleName) AS tmp
    WHERE NOT EXISTS (
        SELECT RoleName FROM AspNetRoles WHERE RoleName = 'NDAUser'
    ) LIMIT 1;
    """,
    """
    INSERT INTO AspNetRoles (RoleName)
    SELECT * FROM (SELECT 'Cashier' AS RoleName) AS tmp
    WHERE NOT EXISTS (
        SELECT RoleName FROM AspNetRoles WHERE RoleName = 'Cashier'
    ) LIMIT 1;
    """,

    # Creating a trigger safely
    """
    DROP TRIGGER IF EXISTS after_user_insert;
    CREATE TRIGGER after_user_insert
    AFTER INSERT ON Users
    FOR EACH ROW
    BEGIN
        DECLARE role_id INT;
        IF NEW.UserName = 'admin' THEN
            SELECT Id INTO role_id FROM AspNetRoles WHERE RoleName = 'Admin' LIMIT 1;
        ELSEIF NEW.UserName = 'ndauser1' THEN
            SELECT Id INTO role_id FROM AspNetRoles WHERE RoleName = 'NDAUser' LIMIT 1;
        ELSE
            SELECT Id INTO role_id FROM AspNetRoles WHERE RoleName = 'Cashier' LIMIT 1;
        END IF;
        INSERT INTO UserRoles (UserId, RoleId) VALUES (NEW.Id, role_id);
    END;
    """,
    # Insert users with predefined roles
    """
    INSERT INTO Users (Email, EmailConfirmed, PasswordHash, SecurityStamp, PhoneNumber, PhoneNumberConfirmed, 
                       TwoFactorEnabled, LockoutEnabled, AccessFailedCount, UserName, Firstname, Surname, IsEnabled)
    VALUES 
    ('admin@example.com', TRUE, 'hashed_password_admin', 'some_stamp', '1234567890', TRUE, FALSE, TRUE, 0, 'admin', 'Admin', 'User', TRUE),
    ('ndauser@example.com', TRUE, 'hashed_password_nda1', 'some_stamp', '1234567891', TRUE, FALSE, TRUE, 0, 'ndauser1', 'NDA', 'User1', TRUE),
    ('cashier@example.com', TRUE, 'hashed_password_cashier', 'some_stamp', '1234567892', TRUE, FALSE, TRUE, 0, 'cashier', 'Cashier', 'User', TRUE);
    """,
    """
    INSERT INTO simulated_inventory (denomination, count, min_threshold, float_threshold, max_threshold, full_threshold)
    VALUES ('1 ¢', 52, 80, 100, 730, 810),
           ('2 ¢', 52, 70, 100, 645, 715),
           ('5 ¢', 53, 50, 80, 420, 475),
           ('10 ¢', 52, 55, 60, 495, 550),
           ('20 ¢', 52, 40, 60, 315, 355),
           ('50 ¢', 52, 25, 50, 220, 245),
           ('1 €', 102, 30, 50, 270, 300),
           ('2 €', 102, 25, 50, 200, 225),
           ('5 €', 23, 5, 20, 50, 60),
           ('10 €', 13, 4, 30, 27, 30),
           ('20 €', 12, 4, 20, 40, 60),
           ('50 €', 11, 1, 12, 12, 30),
           ('100 €', 8, 0, 0, 0, 0),
           ('200 €', 1, 0, 0, 0, 0),
           ('500 €', 2, 0, 0, 0, 0);
    """
]

# Execute each query and manage connection state
for query in queries:
    if "CREATE TRIGGER" in query or "DROP TRIGGER" in query:
        reset_connection(connection)  # Reset connection before and after executing trigger related queries
    execute_query(connection, query)

connection.close()  # Close the connection when all operations are done
