CREATE TABLE jobs (
        id INTEGER NOT NULL, 
        job_title VARCHAR(200) NOT NULL,
        job_type VARCHAR(100) NOT NULL,  
        job_category VARCHAR(100) ,
		tags VARCHAR(100),
        location VARCHAR(4000) ,
        job_description VARCHAR(4000) ,
        min_salary INTEGER, 
                max_salary INTEGER ,
        date_posted DATETIME NOT NULL,
                deadline DATETIME NOT NULL,
                employer_id INTEGER NOT NULL,
                company_id INTEGER ,
        PRIMARY KEY (id),
                FOREIGN KEY(employer_id) REFERENCES user (id)
);