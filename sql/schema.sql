DROP TABLE IF EXISTS Recommendation, Result, ABTest, Algorithm, Interaction, Dataset, Admin, DataScientist, Authentication, Customer ;

-- Table to keep track of the items/articles of the dataset
CREATE TABLE Dataset (
     dataset_id INT NOT NULL,
     item_id INT NOT NULL,
     atribute TEXT NOT NULL,
     val TEXT,
     PRIMARY KEY(dataset_id, item_id, atribute)
);

-- Table that contains the customers of a dataset
CREATE TABLE Customer (
    dataset_id INT NOT NULL,
    customer_id INT NOT NULL,
    FN BOOLEAN,
    Active BOOLEAN,
    club_member_status TEXT,
    fashion_news_frequency TEXT,
    age INT,
    postal_code TEXT,
    PRIMARY KEY (dataset_id, customer_id)
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
    dataset_id_ref INT NOT NULL,
    item_id_ref INT NOT NULL,
    attribute_ref TEXT NOT NULL,
    t_dat TIMESTAMP NOT NULL,
    price INT NOT NULL,
    -- Primary key ==> customer buys item at certain time ==> unique
    PRIMARY KEY (customer_id, item_id_ref, t_dat),
    -- Reference to an item from a Dataset, need 3 attributes for the primary key of a dataset
    FOREIGN KEY (dataset_id_ref, item_id_ref, attribute_ref) REFERENCES Dataset(dataset_id, item_id, atribute) ON UPDATE CASCADE ON DELETE CASCADE,
    -- Reference to a customer from Customers, need 2 attributes for the primary key of a customer
    FOREIGN KEY (dataset_id_ref, customer_id) REFERENCES Customer(dataset_id, customer_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table of algorithms
CREATE TABLE Algorithm (
    name TEXT PRIMARY KEY
);

-- ABTest contains multiple results that are generated by the ABTest
CREATE TABLE ABTest (
    abtest_id INT NOT NULL,
    result_id INT NOT NULL,
    PRIMARY KEY (abtest_id, result_id)
);

-- Subresult of an ABTest (weak entity)
CREATE TABLE Result (
    abtest_id_ref INT NOT NULL,
    result_id INT NOT NULL,
    PRIMARY KEY (abtest_id_ref, result_id),
    FOREIGN KEY (abtest_id_ref, result_id) REFERENCES ABTest(abtest_id, result_id) ON DELETE CASCADE ,
    algorithm_ref TEXT NOT NULL REFERENCES Algorithm(name)
);

-- Table to keep track of recommendations in the database (weak entity)
CREATE TABLE Recommendation (
    abtest_id_ref INT NOT NULL,
    result_id INT NOT NULL,
    dataset_id_ref INT NOT NULL,
    customer_id INT NOT NULL,
    item_id_ref INT NOT NULL,
    attribute_ref TEXT NOT NULL,
    -- Primary key ==> combination of abtest, result, customer and item is unique
    PRIMARY KEY (abtest_id_ref, result_id, customer_id, dataset_id_ref, item_id_ref),
    -- Reference to an item/article in the Dataset table
    FOREIGN KEY (dataset_id_ref, item_id_ref, attribute_ref) REFERENCES Dataset(dataset_id, item_id, atribute) ON UPDATE CASCADE ON DELETE CASCADE,
    -- Reference to a customer from Customers, need 2 attributes for the primary key of a customer
    FOREIGN KEY (dataset_id_ref, customer_id) REFERENCES Customer(dataset_id, customer_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Test
INSERT INTO Algorithm(name) VALUES ('Recency'), ('Popularity'), ('ItemKKN') ;
INSERT INTO Dataset(dataset_id, item_id, atribute, val) VALUES (0, 0, 'size', 'small') ;
INSERT INTO Customer(dataset_id, customer_id) VALUES (0, 10) ;
INSERT INTO Interaction(customer_id, dataset_id_ref, item_id_ref, attribute_ref, t_dat, price) VALUES (10, 0, 0, 'size', current_timestamp , 20) ;
INSERT INTO ABTest(dataset_id, customer_id) VALUES (100, 0) ;
INSERT INTO Result(dataset_id, customer_id, algorithm_ref) VALUES (100, 0, 'Recency') ;
INSERT INTO Recommendation(abtest_id_ref, result_id, dataset_id_ref, customer_id, item_id_ref, attribute_ref) VALUES (100, 0, 0, 10, 0, 'small') ;