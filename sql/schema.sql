-- Test class
CREATE TABLE Quote (
	id SERIAL PRIMARY KEY,
	text VARCHAR(256) UNIQUE NOT NULL,
	author VARCHAR(128)
);

INSERT INTO Quote(text,author) VALUES('If people do not believe that mathematics is simple, it is only because they do not realize how complicated life is.','John Louis von Neumann');
INSERT INTO Quote(text,author) VALUES('The choice you refuse to make, is the one that will be made for you.', 'Unknown');
INSERT INTO Quote(text,author) VALUES('Computer science is no more about computers than astronomy is about telescopes.','Edsger Dijkstra');
INSERT INTO Quote(text,author) VALUES('You look at things that are and ask, why? I dream of things that never were and ask, why not?','Unknown');
INSERT INTO Quote(text,author) VALUES('Being efficient is also a form of perfection.', 'Joey');
INSERT INTO Quote(text,author) VALUES('To understand recursion you must first understand recursion..', 'Unknown');
INSERT INTO Quote(text,author) VALUES('Not everyone will understand your journey. Thats fine. Its not their journey to make sense of. Its yours.','Unknown');
INSERT INTO Quote(text,author) VALUES('One must have enough self-confidence and immunity to peer pressure to break the grip of standard paradigms.', 'Marvin Minsky');
INSERT INTO Quote(text,author) VALUES('Everyone you meet is fighting a battle you know nothing about. Be kind. Always.', 'Robin Williams');
INSERT INTO Quote(text,author) VALUES('[...] it is usual to have the polite convention that everyone thinks.', 'Alan Turing');

-- This is a customer that buys items
CREATE TABLE Customer (
    customer_id INT PRIMARY KEY,
    FN BOOLEAN,
    Active BOOLEAN,
    club_member_status TEXT,
    fashion_news_frequency TEXT,
    age INT,
    postal_code TEXT
);

-- This is the data scientist that can login in the application
CREATE TABLE DataScientist (
   ds_id INT PRIMARY KEY,
   email TEXT UNIQUE NOT NULL,
   firstname TEXT NOT NULL,
   lastname TEXT NOT NULL,
   username TEXT UNIQUE NOT NULL
);

-- "Admin" data scientist who is able to add datasets
CREATE TABLE Admin (
    ds_id INT PRIMARY KEY REFERENCES DataScientist(ds_id)
);

-- Item that can be bought by customers
CREATE TABLE Item (
    item_id TEXT NOT NULL,
    product_code INT NOT NULL,
    product_name TEXT NOT NULL,
    product_type_no INT NOT NULL,
    product_type_name TEXT NOT NULL,
    product_group_name TEXT NOT NULL,
    graphical_appearance_no INT NOT NULL,
    graphical_appearance_name TEXT NOT NULL,
    colour_group_code INT NOT NULL,
    colour_group_name TEXT NOT NULL,
    perceived_colour_value_id INT NOT NULL,
    perceived_colour_value_name TEXT NOT NULL,
    perceived_colour_master_id INT NOT NULL,
    perceived_colour_master_name TEXT NOT NULL,
    department_no INT NOT NULL,
    department_name TEXT NOT NULL,
    index_code CHAR NOT NULL,
    index_name TEXT NOT NULL,
    index_group_no INT NOT NULL,
    index_group_name TEXT NOT NULL,
    section_no INT NOT NULL,
    section_name TEXT NOT NULL,
    garment_group_no INT NOT NULL,
    garment_group_name TEXT NOT NULL,
    detail_desc TEXT NOT NULL,
    PRIMARY KEY (item_id, product_code, product_name, product_type_no, product_type_name, product_group_name, graphical_appearance_no,
                graphical_appearance_name, colour_group_code, colour_group_name, perceived_colour_value_id, perceived_colour_value_name,
                perceived_colour_master_id, perceived_colour_master_name, department_no, department_name, index_code, index_name,
                index_group_no, index_group_name, section_no, section_name, garment_group_no, garment_group_name, detail_desc)
);

-- Table to keep track of the purchases of users for specific items
CREATE TABLE Interaction (
    customer_id INT REFERENCES Customer(customer_id),
    item_id TEXT REFERENCES Item(item_id),
    t_dat TIME,
    price INT NOT NULL,
    PRIMARY KEY (customer_id, item_id)
);