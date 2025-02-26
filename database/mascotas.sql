--DROP TABLE test;
--DROP TABLE adjacent_postcode;
--DROP TABLE post_code;

CREATE TABLE post_code (
    post_code INT PRIMARY KEY,
    n_cases INT DEFAULT 0,
    estimation_pets FLOAT
);

CREATE TABLE adjacent_postcode (
    post_code_origin INT,
    post_code_adjacent INT,
    PRIMARY KEY (post_code_origin, post_code_adjacent),
    FOREIGN KEY (post_code_origin) REFERENCES post_code(post_code),
    FOREIGN KEY (post_code_adjacent) REFERENCES post_code(post_code)
);

CREATE TABLE test (
    id_test SERIAL PRIMARY KEY,
    post_code INT REFERENCES post_code(post_code),
    date_done DATE NOT NULL,
    desease VARCHAR(50) NOT NULL,
    result BOOLEAN NOT NULL,  -- TRUE = positivo, FALSE = negativo
    city VARCHAR(50),
    age INT,
    sex VARCHAR(10)  
);