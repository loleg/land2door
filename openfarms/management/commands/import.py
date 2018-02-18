# -*- coding: utf-8 -*-
import json, yaml
import re

from django.core.management.base import BaseCommand, CommandError

from openfarms.models import Farm, Datasource, Produce
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

            source = Datasource.objects.get_or_create(
                feed=jsonfile
            )
            if not type(source) is Datasource:
                source = source[0]
            else:
                source.title=jsonfile

            with open(jsonfile, 'r') as f:
                data = json.load(f)
                datacount = len(data)
                producecount = 0

                for i, d in enumerate(data):
                    farmtitle = d[conf['title']]
                    if len(farmtitle) < 3:
                        continue
                    farm = Farm.objects.get_or_create(
                        title=farmtitle
                    )
                    if not type(farm) is Farm:
                        farm = farm[0]
                    producelist = []
                    for local in conf:
                        contents = ""
                        for k in conf[local].split(" "):
                            if k in d:
                                if type(d[k]) is None:
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
                            # print("\n{}#{}#{}".format(line.strip(),'|'.join(map(lambda c: ';'.join(list(c)), matching_cat)),highest_match))
                            contents = []
                            for k in conf[local].split(" "):
                                if not k in d:
                                    contents.append(k)
                                elif type(d[k]) is str:
                                    kv = d[k].replace("||",",").replace("|",",")
                                    contents.append(kv)
                            contents = ",".join(contents)
                            for c in contents.split(","):
                                c = c.strip()
                                matching_cat, highest_match = get_category_match(c.strip(), categories, food_map)
                                if len(matching_cat)<3:
                                    # First language (German)
                                    matching_cat = next(iter(next(iter(matching_cat))))
                                    producename = matching_cat.split('/')[0]
                                    produce = Produce.objects.get_or_create(
                                        name=producename
                                    )
                                    if not type(produce) is Produce:
                                        produce = produce[0]
                                    produce.save()
                                    # print(producename)
                                    producelist.append(produce)
                        else:
                            farm.__setattr__(local, contents)

                    farm.datasource = source
                    farm.save()

                    for p in producelist:
                        farm.produce.add(p)
                    producecount = producecount + len(producelist)
                    farm.save()

                    print("%d/%d - %s" % (i, datacount, farm.title))
                    count += 1

        self.stdout.write(self.style.SUCCESS('Imported %d produce' % producecount))
        self.stdout.write(self.style.SUCCESS('Imported %d farms' % count))
