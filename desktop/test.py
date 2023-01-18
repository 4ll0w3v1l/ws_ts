import web.static.scripts.db_actions as db
tmp = {'id': [1, 2, 3, 4, 5], 'creation_date': [1673895456.968237, 1673895598.868029, 1673897196.504698, 1673992634.173783, 1673995447.165871], 'status': ['Принята на рассмотрение', 'Принята на рассмотрение', 'Изменение', 'Размещена', 'Проект'], 'last_reassignment': [1673898017.214874, 1673897834.284721, 1673995721.557215, 1673995319.687163, 1674005062.015216], 'description': [None, None, 'все хуево пацаны', None, ''], 'agreed_production': [0, 0, 0, 0, 0], 'agreed_economy': [0, 0, 0, 0, 0], 'client_name': ['123', 'tuigheraoi', 'qwerttytt', '123', '123'], 'client_phone': ['+7123', '+7ytrew', '+7qttwerty', '+7123', '+7123'], 'client_email': ['123', 'uytrewq', 'ttqwerty', '123', '123'], 'short_description': ['123', 'thregfwdqs', 'qwertytrew', '123', '123'], 'current_worker': [None, None, None, None, None], 'creator': ['432', '432', '432', 'root', 'root']}
acc_ids = [1, 2]

for i in range(len(tmp['id'])):
    if tmp['id'][i] in acc_ids:
        print(tmp['id'][i])