# -*- coding: utf-8 -*-
import json, yaml

from django.core.management.base import BaseCommand, CommandError

from openfarms.models import Farm

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
                                vals.append(d[k])
                            else:
                                k = k.replace("_", " ")
                                vals.append(k)
                        contents = "".join(vals)
                        if local == "image":
                            self.stdout.write(self.style.WARNING('Image fields not supported'))
                        else:
                            farm.__setattr__(local, contents)

                    farm.save()
                    print(farm.title)
                    count += 1

        self.stdout.write(self.style.SUCCESS('Imported %d farms' % count))
