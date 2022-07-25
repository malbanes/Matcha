if [[ $? != 0 ]] ; then
    echo "Installing Homebrew"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo "Installing Python Packages"
    brew install python3
    python3 -m pip install psycopg2
    echo "Installing Postgre Package"
    brew install postgresql
    echo "Run Postgre Package"
    brew services start postgresql
    brew services restart postgresql
    echo "Seed DB"
    su - postgres
    createuser sammy
    createdb flask_db
    psql -s flask_db -c "alter user sammy with encrypted password 'test';"
    psql -s flask_db -c "GRANT ALL PRIVILEGES ON DATABASE flask_db TO sammy;"
    python3 init_db.py
    echo "END"
    pipenv shell
    pipenv install
    python3 main.py
else
    echo "Updating Homebrew"
    brew update
    echo "Installing Python Packages"
    brew install python3
    python3 -m pip install psycopg2
    echo "Installing Postgre Package"
    brew install postgresql
    echo "Run Postgre Package"
    brew services start postgresql
    brew services restart postgresql
    echo "Seed DB"
    su - postgres
    createuser sammy
    createdb flask_db
    psql -s flask_db -c "alter user sammy with encrypted password 'test';"
    psql -s flask_db -c "GRANT ALL PRIVILEGES ON DATABASE flask_db TO sammy;"
    python3 init_db.py
    echo "END"
    pipenv shell
    pipenv install
    python3 main.py
fi

