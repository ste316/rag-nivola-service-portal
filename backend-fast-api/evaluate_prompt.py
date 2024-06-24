'''
GEN DATA
    per ogni prompt da testare:
        prendere 1 documento a caso da db.json
        da 2 a 7 volte:
            creare 1 domanda dal documento, solo il primo ciclo
            porre la domanda con il prompt e i similar docs trovati
            creare 1 domanda relativa alla risposta di Claude
        dump conversation in a clear format
    cambiare documento

EVALUATE PROMPT
    prendere un batch di conversazioni
    chiedere a Claude quale conversazione è stata gestita meglio
    deve valutare piu aspetti e dare un voto 
'''
from lib_ import util
from random import choice, randint
from lib_ import aws
from prompts import *
from main import rag
from json import loads, dumps
from os import makedirs

a = aws(load_bedrock=True)
bedrock = a.bedrock

def gen_q_from_doc(answer: str = '', category: str = '') -> str:
    if answer == '':
        not_good = False
        db = util.load_json_file('db.json')

        while True:
            doc = choice(db)
            print(f'argument: {doc['category_en']}')
            if 'notes' in doc['category_en']: not_good = True
            else: not_good = False
            if not not_good: # therefore it is actually good
                break
    else:
        doc = {'text_en': answer, 'category_en': category}
    
    msg = [{
        'role': 'user',
        'content': EVALUATE_PROMPT_GEN_Q_NORMAL.format(doc=doc['text_en'], cat=doc['category_en'])
    }]
    
    try:
        res = a.call_claude_3(system_prompt=EVALUATE_PROMPT_GEN_Q_SYS, messages=msg, bedrock_runtime=bedrock)
        print(res)
        temp = loads(res)
    except Exception as e:
        print(f'error: {e}')
        return '', ''

    return temp['question'], doc['category_en']

def ask_rag(prompt_data: dict, max_msg_num: int, batch_data: dict = {}):
    '''
        dict
        k -> question-chatid-promptName
        v -> list of string (conversation)
    '''
    r = rag()
    init_q, cat = gen_q_from_doc()

    for name, p in prompt_data.items():
        first = True
        chat_id = f'evaluator-{name.replace('-', '_')}-{util.generate_random_string()}'
        eval_conv_id = f'{chat_id}-{init_q.strip()}'
        batch_data[eval_conv_id] = []
        print(f'\tTesting prompt: {name}')

        for i in range(randint(1, max_msg_num)):
            question = init_q if first else gen_q_from_doc(answer, cat)[0]
            temp = f'Q#{i}: {question}'
            batch_data[eval_conv_id].append(temp)
            # print(temp)
            answer = r.exec_rag(question.replace('\n', ' '), chat_id, p)
            first = False
            temp = f'A#{i}: {answer.replace('\n', '\n\t')}' 
            batch_data[eval_conv_id].append(temp)
            # print(temp)

    return batch_data

def main_gen_data():
    makedirs('evaluator_data', exist_ok=True)

    test_num = util.generate_random_string(5)
    repeat_test = 1 # run ask_rag X times
    max_num_msg = 10 # max number of question prompted
    batch_data = {}


    for _ in range(repeat_test):
        prompts = {
            'vero-new': SYS_CLAUDE_ASSISTANT_NIVOLA_NEW,
            'vero-old': SYS_CLAUDE_ASSISTANT_NIVOLA_OLD,
        }

        batch_data = ask_rag(prompts, max_num_msg, batch_data)

    print(dumps(batch_data, indent=4))
    filename = f'evaluator_data/generated-conv-{test_num}.json'
    print(f'Evaluator: gen_data {test_num} saved at: {filename}')
    open(filename, 'w', encoding='utf-8').write(dumps(batch_data, indent=4, ensure_ascii=False))

def eval_conversation(prompt_data: dict, test_nums: list[str]):
    '''
    {
    "What are the steps to detach a volume after it has been attached?-evaluator-vero_old-8v40VjAtGXaIBg6d3QZ7e6BzCJXyCkyumJ37Y1JLBz0I1SXaJSAReBAgs6vUSv91-vero-old": [
        "Q#0: What are the steps to detach a volume after it has been attached?",
        "A#0: Risposta: Per staccare un volume dopo che è stato attaccato, è necessario seguire questi passaggi: selezionare il volume dall'elenco, premere il pulsante per visualizzare i dettagli del volume, raggiungere il pannello di gestione del volume, aprire la cartella \"Attachments\", utilizzare il pulsante \"Detach\" sotto la voce \"Actions\" e confermare l'operazione di stacco del volume premendo il pulsante \"Proceed\". Per maggiori informazioni, consultare il documento 1f7f649db744952195e091a2229a970dde02a29726ec82c59bb884a6b5b5c92a."
    ],
    "What are the key capabilities and features offered by this log management service?-evaluator-vero_old-rOyni18Wf5rXb0UlY2KFYk0hSXSyIA5DebTUKO63EAWEIyNfgi1fdUUJnFT4tubN-vero-old": [
        "Q#0: What are the key capabilities and features offered by this log management service?",
        "A#0: Risposta: Il servizio di gestione dei log offre diverse funzionalità chiave come la possibilità di gestire i log delle applicazioni e di sistema delle istanze degli utenti tramite un'interfaccia web basata su ELK. Permette di definire ruoli e utenti con diversi livelli di accesso ai dati, di gestire e interrogare gli indici in modo controllato. Offre inoltre un cluster gestito e amministrato, con backup dei dati, monitoraggio della disponibilità dell'infrastruttura e aggiornamenti tecnologici e di sicurezza. Per maggiori dettagli, si può consultare il link 9c0b751c1167d07558dcf375c8620e1622d449b55a927d9d7a2377844afd9118."
    ]
    }
    '''
    conv_data = {}
    for id in test_nums:
        filename = f'evaluator_data/generated-conv-{id}.json'
        conv_data.update(util.load_json_file(filename))

    print(conv_data)


if __name__ == '__main__':
    prompts = {
        'vero-new': SYS_CLAUDE_ASSISTANT_NIVOLA_NEW,
        'vero-old': SYS_CLAUDE_ASSISTANT_NIVOLA_OLD,
    }
    # eval_conversation(prompts, test_nums=['zPouX', 'YKcVM'])
    main_gen_data()
