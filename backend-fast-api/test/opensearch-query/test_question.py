from main import rag
from json import dumps
import os

def create_directory(directory_path):
    """
    Create a directory if it doesn't exist.

    Parameters:
        directory_path (str): The path of the directory to be created.

    Returns:
        bool: True if the directory is created or already exists, False otherwise.
    """
    try:
        # Check if the directory already exists
        if not os.path.exists(directory_path):
            # Create the directory
            os.makedirs(directory_path)
        else:
            pass
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False

def confront(q1: str, q2: str):
    def dump(data, filename):
        open(filename, 'w', encoding='utf-8').write(dumps(data, indent=4, ensure_ascii=False))
    
    create_directory('data')
    r = rag()

    uno = r.search_doc_2of3(q1)
    due = r.search_doc_2of3(q2)

    all = uno + due

    uno_hash = r.extract_hash_from_result(uno)
    due_hash = r.extract_hash_from_result(due)

    only_in_uno = uno_hash.difference(due_hash)
    only_in_due = due_hash.difference(uno_hash)
    common = uno_hash.intersection(due_hash)

    only_in_uno = r.get_full_record_by_hashes(only_in_uno, all)
    only_in_due = r.get_full_record_by_hashes(only_in_due, all) 
    common = r.get_full_record_by_hashes(common, all)

    file_uno = 'data/test_1.json'
    file_due = 'data/test_2.json'
    file_common = 'data/common.json'

    dump(only_in_uno, file_uno)
    dump(only_in_due, file_due)
    dump(common, file_common)

    return file_uno, file_due

if __name__ == '__main__':
    print('\nQuesto script serve per automatizzare la prova di 2 domande che puntano a risolverse lo stesso problema.\n')
    print('Ad esempio per testare la stessa domanda in versione Inglese e in versione Italiana')
    print('Ma anche due domande completamente diverse, che però hanno lo stesso significato semantico,\ncon questo script puoi testare se ci sono delle incongruenze nel Vector DB.\n')

    agree = input('è importante leggere e capire lo scopo di questo script, confermi di aver compreso? ')
    if agree in ['si', 'yes', 's', 'y', 'yeap', 'yup', 'yessir', 'yesir']:
        q1 = input('Inserisci la prima domanda: ')
        q2 = input('Inserisci la seconda domanda: ')
        file_uno, file_due = confront(q1, q2)

    print(f'\n\nResult saved.')
    print(f'First Question: {q1}\n\tFile: {file_uno} contains the Added Value (extra documents)')
    print(f'Second Question: {q2}\n\tFile: {file_due} contains the Added Value (extra documents)')
    print('Find out which Question yielded the most usefull Result.')
