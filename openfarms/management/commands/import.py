# -*- coding: utf-8 -*-
import json, yaml
import re

from django.core.management.base import BaseCommand, CommandError

from openfarms.models import Farm, Datasource, Produce, Category
from ..categoryimport import import_category_mappers, get_category_match

def cleanhtml(raw_html):
    if not type(raw_html) is str: return raw_html
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

class Command(BaseCommand):
    help = 'Imports JSON data with schema conversion specified in YAML'

    def add_arguments(self, parser):
        parser.add_argument('jsonfiles', nargs='+', help='One or more filenames of JSON data to import')
        parser.add_argument('--yamlfile', nargs='?', help='Optional YAML file for schema mapping')

    def handle(self, *args, **options):
        if not 'yamlfile' in options:
            conf = {}
            for fld in Farm._meta.get_fields():
                conf[fld] = fld.name
        else:
            with open(options['yamlfile'], 'r') as f:
                conf = yaml.load(f)

        # hard coded hacky hacky
        filename = 'openfarms/data/generic-foods.csv'
        categories, food_map = import_category_mappers(filename)

        count = 0
        for jsonfile in options['jsonfiles']:
            with open(jsonfile, 'r') as f:
                data = json.load(f)
                datacount = len(data)
                producecount = 0

                if 'DATASOURCE' in conf:
                    source, created = Datasource.objects.get_or_create(
                        title=conf['DATASOURCE']['title']
                    )
                    source.homepage = conf['DATASOURCE']['homepage']
                    del(conf['DATASOURCE'])
                else:
                    source, created = Datasource.objects.get_or_create(
                        title=jsonfile.rstrip(".json")
                    )
                source.feed = jsonfile
                source.save()

                for i, d in enumerate(data):
                    farmtitle = d[conf['title']]
                    if len(farmtitle) < 3:
                        continue
                    farm, created = Farm.objects.get_or_create(
                        title=farmtitle
                    )
                    farm.datasource = source

                    producelist = []
                    for local in conf:
                        if local == "title": continue
                        contents = ""
                        for k in conf[local]:
                            if k in d:
                                if d[k] is None:
                                    contents = ""
                                elif type(d[k]) is str:
                                    v = cleanhtml(d[k])
                                    if contents is None:
                                        contents = ""
                                    contents = contents + v
                                else:
                                    contents = d[k]
                            else:
                                k = k.replace("_", " ")
                                contents = contents + k

                        if contents is None:
                            pass

                        elif local == "latitude" and "," in contents:
                            latlng = contents.split(",")
                            farm.latitude = latlng[0].strip()
                            farm.longitude = latlng[1].strip()

                        elif local == "image":
                            self.stdout.write(self.style.WARNING('Image fields not supported'))

                        elif local == "produce":
                            contents = []
                            for k in conf[local]:
                                if not k in d:
                                    contents.append(k)
                                elif type(d[k]) is str and len(d[k])>2:
                                    kv = d[k].replace("||",",").replace("|",",")
                                    for kval in kv.split(","):
                                        contents.append(kval)

                            for c in contents:
                                c = ''.join(line.strip() for line in c.splitlines(True))
                                c = c.strip()
                                if len(c)<3: continue

                                # Add to produce
                                produce, created = Produce.objects.get_or_create(
                                    name=c
                                )
                                produce.save()
                                # print("["+produce.name+"]")
                                producelist.append(produce)

                                matching_cat, highest_match = get_category_match(
                                    produce.name, categories, food_map
                                )

                                if len(matching_cat)<3:
                                    # First language (German)
                                    matching_cat = next(iter(next(iter(matching_cat))))
                                    cat, created = Category.objects.get_or_create(
                                        title=matching_cat.split('/')[0]
                                    )
                                    produce.category = cat
                                    # print("Category: " + cat.title)

                        else:
                            farm.__setattr__(local, contents)

                    for p in producelist:
                        farm.produce.add(p)
                    producecount = producecount + len(producelist)
                    farm.save()

                    print("%d/%d - %s" % (i+1, datacount, farm.title))
                    count += 1

        self.stdout.write(self.style.SUCCESS('Imported %d produce' % producecount))
        self.stdout.write(self.style.SUCCESS('Imported %d farms' % count))
