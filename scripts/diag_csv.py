import csv
path='data/courses.csv'
with open(path, newline='', encoding='utf-8') as f:
    reader=csv.DictReader(f)
    for i,row in enumerate(reader, start=1):
        rating=row.get('rating')
        if rating is None:
            print('Row',i,'missing rating key; keys=',list(row.keys()))
            print(row)
            break
        try:
            float(rating)
        except Exception as e:
            print('Row',i,'bad rating=',rating)
            print(row)
            break
print('Done')
