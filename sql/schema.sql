DROP TABLE IF EXISTS Recommendation, Result, Algorithm, ABTest, Interaction, Admin, DataScientist, Authentication, Customer, Articles, Names, Dataset;

-- Table that contains the dataset id's and their names
CREATE TABLE Dataset (
    dataset_id INT NOT NULL PRIMARY KEY,
    dataset_name TEXT NOT NULL
);

-- Table to keep track of which attribute is used as a 'descriptor' to represent it in visualisations
CREATE TABLE Names (
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
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (dataset_id, item_number, attribute)
);

-- Table that contains the customers of a dataset
CREATE TABLE Customer (
    customer_number INT NOT NULL,
    val TEXT,
    attribute TEXT NOT NULL,
    type TEXT NOT NULL,
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
    username TEXT PRIMARY KEY REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE,
    password TEXT NOT NULL
);

-- "Admin" data scientist who is able to add datasets
CREATE TABLE Admin (
    username TEXT PRIMARY KEY REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table to keep track of the purchases of users for specific items.
CREATE TABLE Interaction (
    t_dat TIMESTAMP NOT NULL,
    customer_id INT NOT NULL,
    item_id INT NOT NULL,
    price FLOAT NOT NULL,
    -- Reference to an item from a Dataset, need 3 attributes for the primary key of a dataset
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
--     attribute_customer TEXT NOT NULL,
    -- Primary key ==> customer buys item at certain time ==> unique
    PRIMARY KEY (customer_id, item_id, t_dat, price, dataset_id)
    -- Reference to a customer from Customers, need 2 attributes for the primary key of a customer
--     FOREIGN KEY (dataset_id, customer_id, attribute_customer) REFERENCES Customer(dataset_id, customer_number, attribute) ON UPDATE CASCADE ON DELETE CASCADE
);

-- ABTest contains multiple results that are generated by the ABTest
CREATE TABLE ABTest (
    abtest_id INT NOT NULL,
    algorithm_id INT NOT NULL,
    start_point TIMESTAMP NOT NULL,
    end_point TIMESTAMP NOT NULL,
    stepsize INT NOT NULL,
    topk INT NOT NULL,
    creator TEXT REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE,
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (abtest_id, algorithm_id)
);

-- Table of algorithms
-- (1, 1, topk, 20)
-- (1, 1, window_size, 30)
CREATE TABLE Algorithm(
    abtest_id INT NOT NULL,
    algorithm_id INT NOT NULL,
    name TEXT NOT NULL,
    param_name TEXT NOT NULL,
    value TEXT NOT NULL,
    -- Foreign key to ABTest
    FOREIGN KEY (abtest_id, algorithm_id) REFERENCES ABTest(abtest_id, algorithm_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (abtest_id, algorithm_id, param_name)
);

-- -- Subresult of an ABTest (weak entity)
-- CREATE TABLE Result (
--     abtest_id INT NOT NULL,
--     result_id INT NOT NULL,
--     -- Foreign key to Dataset
--     dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
-- --     algorithm_param TEXT NOT NULL,
--     PRIMARY KEY (abtest_id, result_id),
--     -- Foreign key to ABTest
--     FOREIGN KEY (abtest_id, result_id) REFERENCES ABTest(abtest_id, result_id) ON UPDATE CASCADE ON DELETE CASCADE
--     -- Foreign key to Algorithm
-- --     FOREIGN KEY (abtest_id, result_id, algorithm_param) REFERENCES Algorithm(abtest_id, result_id, param_name) ON UPDATE CASCADE ON DELETE CASCADE
-- );

-- Table to keep track of recommendations in the database (weak entity)
CREATE TABLE Recommendation (
    abtest_id INT NOT NULL,
    algorithm_id INT NOT NULL,
    -- Reference to an item/article in the Dataset table
    dataset_id INT NOT NULL REFERENCES Dataset(dataset_id) ON UPDATE CASCADE ON DELETE CASCADE,
    customer_id INT NOT NULL,
    item_number INT NOT NULL,
--     attribute_customer TEXT NOT NULL,
    -- Params to keep the specific time period in which the topk is calculated
    start_point TIMESTAMP NOT NULL,
    end_point TIMESTAMP NOT NULL,
    -- Primary key ==> combination of abtest, result, customer and item is unique
    FOREIGN KEY (abtest_id, algorithm_id) REFERENCES ABTest(abtest_id, algorithm_id) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (abtest_id, algorithm_id, customer_id, dataset_id, item_number, start_point, end_point)
    -- Reference to a customer from Customers, need 2 attributes for the primary key of a customer
--     FOREIGN KEY (dataset_id, customer_id, attribute_customer) REFERENCES Customer(dataset_id, customer_number, attribute) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Test
-- INSERT INTO Dataset(dataset_id, dataset_name) VALUES (0, 'H&M');
-- INSERT INTO Customer(dataset_id, customer_id) VALUES (0, 10) ;
-- INSERT INTO Authentication(username, password) VALUES ('jonasdm', '123piano') ;
-- INSERT INTO DataScientist(username, email, firstname, lastname) VALUES ('jonasdm', 'jonasdm@hotmail.com', 'jonas', 'de maeyer') ;
-- INSERT INTO Interaction(customer_id, dataset_id, item_id, attribute, t_dat, price) VALUES (10, 0, 0, 'size', current_timestamp , 20) ;
-- INSERT INTO ABTest(abtest_id, result_id, start_point, end_point, stepsize, topk) VALUES (100, 0, current_timestamp , current_timestamp , 30, 30) ;
-- INSERT INTO Algorithm(abtest_id, result_id, name, param_name, value) VALUES (100, 0, 'Popularity', 'window_size', 30) ;
-- INSERT INTO Result(abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param, creator) VALUES (100, 0, 0, 0, 'color', 'window_size', 'jonasdm') ;
-- INSERT INTO Recommendation(abtest_id, result_id, dataset_id, customer_id, item_id, attribute) VALUES (100, 0, 0, 10, 0, 'size') ;

-- Adding Admin account
INSERT INTO DataScientist(username, email, firstname, lastname) VALUES ('admin', 'admin@hotmail.com', 'admin', 'the admin');
INSERT INTO Authentication(username, password) VALUES ('admin', 'nimda');
INSERT INTO Admin(username) VALUES ('admin');