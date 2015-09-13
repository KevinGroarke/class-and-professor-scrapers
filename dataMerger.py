import json
import marisa_trie

cape_data = json.load(open('capeData'))
rmp_data = json.load(open('rmpData'))
schedule_data = json.load(open('scheduleData'))


def course_hash(course_name='', course_number='', course_subject='', professor_name=''):
    return str(hash(course_name + course_number + course_subject + professor_name))

mergedData = open('./mergedData', 'w+')

rmp_keys = [unicode(rmp_rating['professorName']) for rmp_rating in rmp_data]

rmp_trie = marisa_trie.Trie(rmp_keys)
cape_dict = {}
rmp_ratings = {}

for rmp_info in rmp_data:
    key = rmp_trie.get(unicode(rmp_info['professorName']))
    if key:
        rmp_ratings[key] = rmp_info['rmpRating']

for cape in cape_data:
    key = course_hash(cape['courseName'], cape['courseNumber'], cape['courseSubject'], cape['professorName'])
    cape_dict[key] = cape

for course in schedule_data:
    mergedData.write(course['professorName'] + '\n')
    possible_professors = rmp_trie.prefixes(course['professorName'])
    course_key = course_hash(course['courseName'], course['courseNumber'], course['courseSubject'], course['professorName'])

    course['rmpRating'] = rmp_ratings[rmp_trie[possible_professors[-1]]] if possible_professors else float()
    course['capes'] = cape_dict[course_key]['capes'] if cape_dict.get(course_key) else {}
    #course['averageCape'] = cape_dict[course_key]['averageCape'] if cape_dict.get(course_key) else {}
    mergedData.write(unicode(course['rmpRating']) + '\n')
    #mergedData.write(unicode(course['capes']) + '\n')
    #mergedData.write(unicode(course['averageCape']) + '\n')

mergedData.write(unicode(json.dumps(schedule_data, indent=4)))