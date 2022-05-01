DROP TABLE IF EXISTS Recommendation, Result, Algorithm, ABTest, Interaction, Admin, DataScientist, Authentication, Customer, Dataset ;

-- Table to keep track of the items/articles of the datasets
drop table Recommendation;
CREATE TABLE Dataset (
    dataset_id INT NOT NULL,
    item_id INT NOT NULL,
    attribute TEXT NOT NULL,
    val TEXT,
    PRIMARY KEY (dataset_id, item_id, attribute)
);

-- CREATE TABLE Customer (
--     dataset_id INT NOT NULL,
--     customer_id INT NOT NULL,
--     FN BOOLEAN,
--     Active BOOLEAN,
--     club_member_status TEXT,
--     fashion_news_frequency TEXT,
--     age INT,
--     postal_code TEXT,
--     PRIMARY KEY (dataset_id, customer_id)
-- );

-- Table that contains the customers of a dataset
CREATE TABLE Customer (
    dataset_id INT NOT NULL,
    customer_id INT NOT NULL,
    attribute TEXT NOT NULL,
    val TEXT,
    PRIMARY KEY (dataset_id, customer_id, attribute)
);

-- Authentication table which contains the passwords of the users
CREATE TABLE Authentication (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
);

-- This is the data scientist that can login in the application
CREATE TABLE DataScientist (
    username TEXT PRIMARY KEY REFERENCES Authentication(username) ON UPDATE CASCADE ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL
);

-- "Admin" data scientist who is able to add datasets
CREATE TABLE Admin (
    username TEXT PRIMARY KEY REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table to keep track of the purchases of users for specific items.
CREATE TABLE Interaction (
    customer_id INT NOT NULL,
    dataset_id INT NOT NULL,
    item_id INT NOT NULL,
    attribute_dataset TEXT NOT NULL,
    attribute_customer TEXT NOT NULL,
    t_dat TIMESTAMP NOT NULL,
    price INT NOT NULL,
    -- Primary key ==> customer buys item at certain time ==> unique
    PRIMARY KEY (customer_id, item_id, t_dat),
    -- Reference to an item from a Dataset, need 3 attributes for the primary key of a dataset
    FOREIGN KEY (dataset_id, item_id, attribute_dataset) REFERENCES Dataset(dataset_id, item_id, attribute) ON UPDATE CASCADE ON DELETE CASCADE,
    -- Reference to a customer from Customers, need 2 attributes for the primary key of a customer
    FOREIGN KEY (dataset_id, customer_id, attribute_customer) REFERENCES Customer(dataset_id, customer_id, attribute) ON UPDATE CASCADE ON DELETE CASCADE
);

-- ABTest contains multiple results that are generated by the ABTest
CREATE TABLE ABTest (
    abtest_id INT NOT NULL,
    result_id INT NOT NULL,
    start_point TIMESTAMP NOT NULL,
    end_point TIMESTAMP NOT NULL,
    stepsize INT NOT NULL,
    topk INT NOT NULL,
    PRIMARY KEY (abtest_id, result_id)
);

-- Table of algorithms
-- (1, 1, topk, 20)
-- (1, 1, window_size, 30)
CREATE TABLE Algorithm(
    abtest_id INT NOT NULL,
    result_id INT NOT NULL,
    name TEXT NOT NULL,
    param_name TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (abtest_id, result_id, param_name)
);

-- Subresult of an ABTest (weak entity)
CREATE TABLE Result (
    abtest_id INT NOT NULL,
    result_id INT NOT NULL,
    dataset_id INT NOT NULL,
    item_id INT NOT NULL,
    attribute_dataset TEXT NOT NULL,
    algorithm_param TEXT NOT NULL,
    creator TEXT REFERENCES DataScientist(username) ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (abtest_id, result_id),
    -- Foreign key to ABTest
    FOREIGN KEY (abtest_id, result_id) REFERENCES ABTest(abtest_id, result_id) ON UPDATE CASCADE ON DELETE CASCADE,
    -- Foreign key to Algorithm
    FOREIGN KEY (abtest_id, result_id, algorithm_param) REFERENCES Algorithm(abtest_id, result_id, param_name) ON UPDATE CASCADE ON DELETE CASCADE,
    -- Foreign key to Dataset
    FOREIGN KEY (dataset_id, item_id, attribute_dataset) REFERENCES Dataset(dataset_id, item_id, attribute) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table to keep track of recommendations in the database (weak entity)
CREATE TABLE Recommendation (
    abtest_id INT NOT NULL,
    result_id INT NOT NULL,
    dataset_id INT NOT NULL,
    customer_id INT NOT NULL,
    item_id INT NOT NULL,
    attribute_dataset TEXT NOT NULL,
    attribute_customer TEXT NOT NULL,
    -- Params to keep the specific time period in which the topk is calculated
    start_point TIMESTAMP NOT NULL,
    end_point TIMESTAMP NOT NULL,
    -- Primary key ==> combination of abtest, result, customer and item is unique
    PRIMARY KEY (abtest_id, result_id, customer_id, dataset_id, item_id, start_point, end_point),
    -- Reference to an item/article in the Dataset table
    FOREIGN KEY (dataset_id, item_id, attribute_dataset) REFERENCES Dataset(dataset_id, item_id, attribute) ON UPDATE CASCADE ON DELETE CASCADE,
    -- Reference to a customer from Customers, need 2 attributes for the primary key of a customer
    FOREIGN KEY (dataset_id, customer_id, attribute_customer) REFERENCES Customer(dataset_id, customer_id, attribute) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Test
INSERT INTO Dataset(dataset_id, item_id, attribute, val) VALUES (1, 0, 'size', 'small'), (1, 0, 'color', 'pink') ;
-- INSERT INTO Customer(dataset_id, customer_id) VALUES (0, 10) ;
-- INSERT INTO Authentication(username, password) VALUES ('jonasdm', '123piano') ;
-- INSERT INTO DataScientist(username, email, firstname, lastname) VALUES ('jonasdm', 'jonasdm@hotmail.com', 'jonas', 'de maeyer') ;
-- INSERT INTO Interaction(customer_id, dataset_id, item_id, attribute, t_dat, price) VALUES (10, 0, 0, 'size', current_timestamp , 20) ;
-- INSERT INTO ABTest(abtest_id, result_id, start_point, end_point, stepsize, topk) VALUES (100, 0, current_timestamp , current_timestamp , 30, 30) ;
-- INSERT INTO Algorithm(abtest_id, result_id, name, param_name, value) VALUES (100, 0, 'Popularity', 'window_size', 30) ;
-- INSERT INTO Result(abtest_id, result_id, dataset_id, item_id, attribute_dataset, algorithm_param, creator) VALUES (100, 0, 0, 0, 'color', 'window_size', 'jonasdm') ;
-- INSERT INTO Recommendation(abtest_id, result_id, dataset_id, customer_id, item_id, attribute) VALUES (100, 0, 0, 10, 0, 'size') ;

-- Adding Admin account
INSERT INTO Authentication(username, password) VALUES ('admin', 'nimda');
INSERT INTO DataScientist(username, email, firstname, lastname) VALUES ('admin', 'admin@hotmail.com', 'admin', 'the admin');
