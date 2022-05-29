DROP TABLE IF EXISTS Recommendation, Result, Algorithm, ABTest, Interaction, Admin, DataScientist, Authentication, Customer, Articles, Names, Dataset;

-- Table that contains the dataset id's and their names
CREATE TABLE Dataset (
    dataset_id INT NOT NULL PRIMARY KEY,
    dataset_name TEXT NOT NULL
);

-- Table to keep track of which attribute is used as a 'descriptor' to represent it in different pages
CREATE TABLE Names (
    -- Reference to Dataset table
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    table_name TEXT NOT NULL,
    name TEXT NOT NULL,
    PRIMARY KEY (dataset_id, table_name)
);

-- Table to keep track of the items/articles of the datasets
CREATE TABLE Articles (
    item_number INT NOT NULL,
    val TEXT,
    attribute TEXT NOT NULL,
    type TEXT NOT NULL,
    -- Reference to Dataset table
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (dataset_id, item_number, attribute)
);

-- Table that contains the customers of a dataset
CREATE TABLE Customer (
    customer_number INT NOT NULL,
    val TEXT,
    attribute TEXT NOT NULL,
    type TEXT NOT NULL,
    -- Reference to Dataset table
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (dataset_id, customer_number, attribute)
);

-- This is the data scientist that can login in the application
CREATE TABLE DataScientist (
    username TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL
);

-- Authentication table which contains the passwords of the users
CREATE TABLE Authentication (
    -- Primary key and reference to DataScientist table
    username TEXT PRIMARY KEY REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE,
    password TEXT NOT NULL
);

-- "Admin" data scientist who is able to add datasets
CREATE TABLE Admin (
    -- Reference to DataScientist table
    username TEXT PRIMARY KEY REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table to keep track of the purchases of users for specific items.
CREATE TABLE Interaction (
    t_dat TIMESTAMP NOT NULL,
    customer_id INT NOT NULL,
    item_id INT NOT NULL,
    price FLOAT NOT NULL,
    -- Reference to dataset table to keep the database consistent
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (customer_id, item_id, t_dat, price, dataset_id)
);

-- ABTest table that contains information about the ABTest
CREATE TABLE ABTest (
    abtest_id INT NOT NULL,
    algorithm_id INT NOT NULL,
    start_point TIMESTAMP NOT NULL,
    end_point TIMESTAMP NOT NULL,
    stepsize INT NOT NULL,
    topk INT NOT NULL,
    -- Reference to DataScientist table
    creator TEXT REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE,
    -- Reference to Dataset table
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (abtest_id, algorithm_id)
);

-- Table that contains the algorithms of ABTests
CREATE TABLE Algorithm(
    abtest_id INT NOT NULL,
    algorithm_id INT NOT NULL,
    name TEXT NOT NULL,
    param_name TEXT NOT NULL,
    value TEXT NOT NULL,
    -- Foreign key to ABTest table to make sure algorithm is deleted when ABTest is deleted
    FOREIGN KEY (abtest_id, algorithm_id) REFERENCES ABTest(abtest_id, algorithm_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (abtest_id, algorithm_id, param_name)
);

-- Table to keep track of recommendations in the database (weak entity)
CREATE TABLE Recommendation (
    abtest_id INT NOT NULL,
    algorithm_id INT NOT NULL,
    -- Reference to the Dataset table
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    customer_id INT NOT NULL,
    item_number INT NOT NULL,
    start_point TIMESTAMP NOT NULL,
    end_point TIMESTAMP NOT NULL,
    -- Foreign key to ABTest table to make sure recommendation is deleted when ABTest is deleted
    FOREIGN KEY (abtest_id, algorithm_id) REFERENCES ABTest(abtest_id, algorithm_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (abtest_id, algorithm_id, customer_id, dataset_id, item_number, start_point, end_point)
);

-- Adding Admin account
INSERT INTO DataScientist(username, email, firstname, lastname) VALUES ('admin', 'admin@hotmail.com', 'admin', 'the admin');
INSERT INTO Authentication(username, password) VALUES ('admin', 'nimda');
INSERT INTO Admin(username) VALUES ('admin');