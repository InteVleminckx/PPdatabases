DROP TABLE IF EXISTS ABTest, Recommendation, ALgorithm, Interaction, Dataset, Admin, DataScientist, Authentication, Customer

CREATE TABLE Customer (
    customer_id INT PRIMARY KEY ,
    FN BOOLEAN,
    Active BOOLEAN,
    club_member_status TEXT,
    fashion_news_frequency TEXT,
    age INT,
    postal_code TEXT
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

-- Table to keep track of the datasets with their items
CREATE TABLE Dataset (
    dataset_id INT NOT NULL,
    item_id INT NOT NULL,
    atribute TEXT NOT NULL,
    val TEXT,
    PRIMARY KEY(dataset_id, item_id, atribute)
);

-- Table to keep track of the purchases of users for specific items.
CREATE TABLE Interaction (
    customer_id INT NOT NULL REFERENCES Customer(customer_id) ON UPDATE CASCADE ON DELETE CASCADE ,
    ----- Reference for 1 item
    dataset_id_ref INT NOT NULL,
    item_id_ref INT NOT NULL,
    attribute_ref TEXT NOT NULL,
    -----
    t_dat TIMESTAMP NOT NULL,
    price INT NOT NULL,
    PRIMARY KEY (customer_id, item_id_ref, t_dat),
    FOREIGN KEY (dataset_id_ref, item_id_ref, attribute_ref) REFERENCES Dataset(dataset_id, item_id, atribute) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table of algorithms
CREATE TABLE Algorithm (
    name TEXT PRIMARY KEY
);

-- Table to keep track of recommendations in the database
CREATE TABLE Recommendation (
    customer_id INT NOT NULL REFERENCES Customer(customer_id) ON UPDATE CASCADE ON DELETE CASCADE ,
    ----- Reference for 1 item
    dataset_id_ref INT NOT NULL,
    item_id_ref INT NOT NULL,
    attribute_ref TEXT NOT NULL,
    -----
    algorithm_ref TEXT NOT NULL REFERENCES Algorithm(name),
    PRIMARY KEY (customer_id, dataset_id_ref, item_id_ref, algorithm_ref),
    FOREIGN KEY (dataset_id_ref, item_id_ref, attribute_ref) REFERENCES Dataset(dataset_id, item_id, atribute) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Table to keep the results of the ABTests
CREATE TABLE ABTest (
    abtest_id INT NOT NULL,
    ----- Reference for 1 recommendation
    customer_id_ref INT NOT NULL,
    dataset_id_ref INT NOT NULL,
    item_id_ref INT NOT NULL,
    algorithm_ref TEXT NOT NULL,
    -----
    FOREIGN KEY (customer_id_ref, dataset_id_ref, item_id_ref, algorithm_ref) REFERENCES Recommendation(customer_id, dataset_id_ref, item_id_ref, algorithm_ref),
    PRIMARY KEY (abtest_id, customer_id_ref, dataset_id_ref, item_id_ref, algorithm_ref)
);

INSERT INTO Algorithm(name) VALUES ('Recency') ;
INSERT INTO Algorithm(name) VALUES ('Popularity') ;
INSERT INTO Algorithm(name) VALUES ('ItemKKN') ;