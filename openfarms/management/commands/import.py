# -*- coding: utf-8 -*-
import json, yaml
import re

from django.core.management.base import BaseCommand, CommandError

from openfarms.models import Farm, Datasource

def cleanhtml(raw_html):
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

                for d in data:
                    farm = Farm.objects.get_or_create(
                        title=d[conf['title']]
                    )
                    if not type(farm) is Farm:
                        farm = farm[0]
                    for local in conf:
                        vals = []
                        for k in conf[local].split(" "):
                            if k in d:
                                v = cleanhtml(d[k])
                                vals.append(v)
                            else:
                                k = k.replace("_", " ")
                                vals.append(k)
                        contents = "".join(vals)
                        if local == "image":
                            self.stdout.write(self.style.WARNING('Image fields not supported'))
                        else:
                            farm.__setattr__(local, contents)

                    farm.datasource = source
                    farm.save()
                    print(farm.title)
                    count += 1

        self.stdout.write(self.style.SUCCESS('Imported %d farms' % count))
