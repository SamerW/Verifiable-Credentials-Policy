TODO:
    Make a readme :)

I18N:
    To create the file for another language use the following command with the appropriate language code:
        $ pybabel init -i messages.pot -d app/translations -l "language_code"

    To extract new messages from the source code, use the following command:
        $ pybabel extract -F babel.cfg -k _l -o messages.pot .

    To update all specific language file with new messages, use the following command:
        $ pybabel update -i messages.pot -d module/translations

    To compile new translations, use the following command:
        $ pybabel compile -d module/translations


