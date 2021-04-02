CNL Project:

Requirements:
    Python 3
    pip
    venv

Installation:
    1) clone the repository in a new folder
    2) go to the folder "cnl-gui-policy-man"
    3) create a virtual environment with the command "python -m venv env"
    4) Activate the virtual environment with the command "source ./env/bin/activate"
    5) Install all dependencies with the command "pip install -r requirements.txt"
    6) Provide the FLASK_NAME environment variable with the command "export FLASK_APP=module"
    7) Provide the FLASK_ENV environement variable with the command "export FLASK_ENV=development"
    8) Start the web server with the command "flask run"


I18N:
    To add another language use the following command with the appropriate language code:
        $ pybabel init -i messages.pot -d app/translations -l "language_code"

    To extract new messages from the source code, use the following command:
        $ pybabel extract -F babel.cfg -k _l -o messages.pot .

    To update all specific language file with new messages, use the following command:
        $ pybabel update -i messages.pot -d module/translations

    To compile new translations, use the following command:
        $ pybabel compile -f -d module/translations

Create an executable version:
    1) go to the folder "module"
    2) create the executable with the command "pyinstaller -w -F main.spec"

