# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import localflavor.us.models
import core.models
import encrypted_fields.fields
import django_countries.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(max_length=50)),
                ('street2', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('state', localflavor.us.models.USStateField(max_length=2, choices=[(b'AL', b'Alabama'), (b'AK', b'Alaska'), (b'AS', b'American Samoa'), (b'AZ', b'Arizona'), (b'AR', b'Arkansas'), (b'AA', b'Armed Forces Americas'), (b'AE', b'Armed Forces Europe'), (b'AP', b'Armed Forces Pacific'), (b'CA', b'California'), (b'CO', b'Colorado'), (b'CT', b'Connecticut'), (b'DE', b'Delaware'), (b'DC', b'District of Columbia'), (b'FL', b'Florida'), (b'GA', b'Georgia'), (b'GU', b'Guam'), (b'HI', b'Hawaii'), (b'ID', b'Idaho'), (b'IL', b'Illinois'), (b'IN', b'Indiana'), (b'IA', b'Iowa'), (b'KS', b'Kansas'), (b'KY', b'Kentucky'), (b'LA', b'Louisiana'), (b'ME', b'Maine'), (b'MD', b'Maryland'), (b'MA', b'Massachusetts'), (b'MI', b'Michigan'), (b'MN', b'Minnesota'), (b'MS', b'Mississippi'), (b'MO', b'Missouri'), (b'MT', b'Montana'), (b'NE', b'Nebraska'), (b'NV', b'Nevada'), (b'NH', b'New Hampshire'), (b'NJ', b'New Jersey'), (b'NM', b'New Mexico'), (b'NY', b'New York'), (b'NC', b'North Carolina'), (b'ND', b'North Dakota'), (b'MP', b'Northern Mariana Islands'), (b'OH', b'Ohio'), (b'OK', b'Oklahoma'), (b'OR', b'Oregon'), (b'PA', b'Pennsylvania'), (b'PR', b'Puerto Rico'), (b'RI', b'Rhode Island'), (b'SC', b'South Carolina'), (b'SD', b'South Dakota'), (b'TN', b'Tennessee'), (b'TX', b'Texas'), (b'UT', b'Utah'), (b'VT', b'Vermont'), (b'VI', b'Virgin Islands'), (b'VA', b'Virginia'), (b'WA', b'Washington'), (b'WV', b'West Virginia'), (b'WI', b'Wisconsin'), (b'WY', b'Wyoming')])),
                ('zipcode', models.CharField(max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BatchFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('docfile', models.FileField(upload_to=core.models.request_content_file_name)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, db_index=True)),
                ('phone_number', models.CharField(default=None, max_length=15, null=True, blank=True)),
                ('tax_id', models.CharField(default=None, max_length=50, null=True, blank=True)),
                ('logo', models.ImageField(default=None, null=True, upload_to=core.models.logo_file_name, blank=True)),
                ('report_logo', models.ImageField(default=None, null=True, upload_to=core.models.report_logo_file_name, blank=True)),
                ('individual_template', models.CharField(default=None, max_length=500, null=True, blank=True)),
                ('corporate_template', models.CharField(default=None, max_length=500, null=True, blank=True)),
                ('is_corporate', models.BooleanField(default=False)),
                ('is_individual', models.BooleanField(default=True)),
                ('is_custom', models.BooleanField(default=False)),
                ('company_logo_active', models.BooleanField(default=False)),
                ('report_logo_active', models.BooleanField(default=False)),
                ('batch_upload_active', models.BooleanField(default=False)),
                ('address', models.ForeignKey(default=None, blank=True, to='core.Address', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompanyDueDiligenceTypeSelection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90)),
                ('comments', models.TextField()),
                ('level', models.IntegerField(default=1, choices=[(1, b'Essential'), (2, b'Enhanced'), (3, b'Extensive')])),
                ('company', models.ForeignKey(to='core.Company')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompanyEmployee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=15, blank=True)),
                ('position', models.CharField(max_length=50, blank=True)),
                ('is_activated', models.BooleanField(default=False)),
                ('supervisor', models.BooleanField(default=False)),
                ('company', models.ForeignKey(to='core.Company')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CompanyServiceSelection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dd_type', models.ForeignKey(to='core.CompanyDueDiligenceTypeSelection')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CorporateRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=50)),
                ('duns', models.CharField(max_length=200, blank=True)),
                ('registration', models.CharField(max_length=50, blank=True)),
                ('website', models.URLField(blank=True)),
                ('name_variant', models.CharField(max_length=50, blank=True)),
                ('parent_company_name', models.CharField(max_length=50, blank=True)),
                ('recipient', models.CharField(default=b'', max_length=50, blank=True)),
                ('street', models.CharField(max_length=200, null=True, blank=True)),
                ('dependent_locality', models.CharField(max_length=200, null=True, blank=True)),
                ('locality', models.CharField(max_length=200, null=True, blank=True)),
                ('postalcode', models.CharField(max_length=15, null=True, blank=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True, choices=[('AF', 'Afghanistan'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia, Plurinational State of'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo (the Democratic Republic of the)'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CW', 'Cura\xe7ao'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('CI', "C\xf4te d'Ivoire"), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands  [Malvinas]'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia (The)'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See  [Vatican City State]'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran (the Islamic Republic of)'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', "Korea (the Democratic People's Republic of)"), ('KR', 'Korea (the Republic of)'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', "Lao People's Democratic Republic"), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia (the former Yugoslav Republic of)'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia (the Federated States of)'), ('MD', 'Moldova (the Republic of)'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestine, State of'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RO', 'Romania'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('RE', 'R\xe9union'), ('BL', 'Saint Barth\xe9lemy'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin (French part)'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten (Dutch part)'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'), ('SS', 'South Sudan'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syrian Arab Republic'), ('TW', 'Taiwan (Province of China)'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania, United Republic of'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela, Bolivarian Republic of'), ('VN', 'Viet Nam'), ('VG', 'Virgin Islands (British)'), ('VI', 'Virgin Islands (U.S.)'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe'), ('AX', '\xc5land Islands')])),
                ('display_id', models.CharField(default=b'', max_length=50)),
                ('phone_number', models.CharField(default=b'', max_length=15, blank=True)),
                ('email', models.CharField(default=b'', max_length=50, verbose_name=b'Email', blank=True)),
                ('comments', models.TextField(blank=True)),
                ('client_attachment', models.FileField(default=None, null=True, upload_to=core.models.request_content_file_name, blank=True)),
                ('attachment', models.FileField(default=None, null=True, upload_to=core.models.request_content_file_name, blank=True)),
                ('executive_summary', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CorporateRequestServiceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('results', models.BooleanField()),
                ('comments', models.TextField()),
                ('datetime', models.DateField(blank=True)),
                ('request', models.ForeignKey(to='core.CorporateRequest')),
                ('service', models.ForeignKey(to='core.CompanyServiceSelection')),
            ],
            options={
                'db_table': 'core_corporaterequestservicestatus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CorporateRequestStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('comments', models.TextField()),
                ('corporate_request', models.ForeignKey(to='core.CorporateRequest')),
            ],
            options={
                'ordering': ['-datetime'],
                'db_table': 'core_corporaterequeststatus',
                'verbose_name': 'Corporate Request Statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_id', models.CharField(default=b'', max_length=50)),
                ('name', models.CharField(max_length=50, db_index=True)),
                ('comments', models.TextField(blank=True)),
                ('client_attachment', models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True)),
                ('attachment', models.FileField(default=None, null=True, upload_to=core.models.request_content_file_name, blank=True)),
                ('executive_summary', models.TextField(default=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomRequestFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField(blank=True)),
                ('custom_request', models.ForeignKey(to='core.CustomRequest')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomRequestServiceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('results', models.BooleanField()),
                ('comments', models.TextField()),
                ('datetime', models.DateField(blank=True)),
                ('request', models.ForeignKey(to='core.CustomRequest')),
                ('service', models.ForeignKey(to='core.CompanyServiceSelection')),
            ],
            options={
                'db_table': 'core_customrequestservicestatus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CustomRequestStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('comments', models.TextField()),
                ('request', models.ForeignKey(to='core.CustomRequest')),
            ],
            options={
                'ordering': ['-datetime'],
                'db_table': 'core_customrequestStatusstatus',
                'verbose_name': 'Custom Request Statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DueDiligenceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=90, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DueDiligenceTypeServices',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('due_diligence_type', models.ForeignKey(to='core.DueDiligenceType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DynamicRequestForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('render_form', models.BooleanField(default=True)),
                ('company', models.ForeignKey(to='core.Company')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DynamicRequestFormFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50)),
                ('sort_order', models.IntegerField(default=0)),
                ('help_text', models.CharField(max_length=150, blank=True)),
                ('field_format', models.TextField(blank=True)),
                ('required', models.BooleanField(default=False)),
                ('archive', models.BooleanField(default=False)),
                ('dynamic_request_form', models.ForeignKey(to='core.DynamicRequestForm')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LayoutGroupSections',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.CharField(unique=True, max_length=75)),
            ],
            options={
                'verbose_name': 'Layout Group Section',
                'verbose_name_plural': 'Layout Group Sections',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Reports',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('data', models.TextField()),
                ('created_date', models.DateTimeField(editable=False)),
                ('report_request_type', models.CharField(max_length=50)),
                ('report_template', models.CharField(max_length=100, null=True, blank=True)),
                ('created_by', models.ForeignKey(to='core.CompanyEmployee')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_id', models.CharField(default=b'', max_length=50)),
                ('first_name', models.CharField(max_length=50, db_index=True)),
                ('middle_name', models.CharField(db_index=True, max_length=50, blank=True)),
                ('last_name', models.CharField(db_index=True, max_length=50, blank=True)),
                ('citizenship', django_countries.fields.CountryField(blank=True, max_length=2, null=True, verbose_name=b'Citizenship', choices=[('AF', 'Afghanistan'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia, Plurinational State of'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo (the Democratic Republic of the)'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CW', 'Cura\xe7ao'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('CI', "C\xf4te d'Ivoire"), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands  [Malvinas]'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia (The)'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See  [Vatican City State]'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran (the Islamic Republic of)'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', "Korea (the Democratic People's Republic of)"), ('KR', 'Korea (the Republic of)'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', "Lao People's Democratic Republic"), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia (the former Yugoslav Republic of)'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia (the Federated States of)'), ('MD', 'Moldova (the Republic of)'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestine, State of'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RO', 'Romania'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('RE', 'R\xe9union'), ('BL', 'Saint Barth\xe9lemy'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin (French part)'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten (Dutch part)'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'), ('SS', 'South Sudan'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syrian Arab Republic'), ('TW', 'Taiwan (Province of China)'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania, United Republic of'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela, Bolivarian Republic of'), ('VN', 'Viet Nam'), ('VG', 'Virgin Islands (British)'), ('VI', 'Virgin Islands (U.S.)'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe'), ('AX', '\xc5land Islands')])),
                ('ssn', encrypted_fields.fields.EncryptedTextField(blank=True)),
                ('birthdate', models.DateField(null=True, verbose_name=b'Birthdate', blank=True)),
                ('phone_number', models.CharField(default=b'', max_length=15, blank=True)),
                ('email', models.CharField(default=b'', max_length=50, verbose_name=b'Email', blank=True)),
                ('comments', models.TextField(blank=True)),
                ('client_attachment', models.FileField(default=None, max_length=200, null=True, upload_to=core.models.request_content_file_name, blank=True)),
                ('attachment', models.FileField(default=None, null=True, upload_to=core.models.request_content_file_name, blank=True)),
                ('executive_summary', models.TextField(default=b'', blank=True)),
                ('address', models.ForeignKey(default=None, blank=True, to='core.Address', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RequestFormFieldTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'verbose_name': 'Request Form Field Type',
                'verbose_name_plural': 'Request Form Field Types',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RequestServiceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('results', models.BooleanField()),
                ('comments', models.TextField()),
                ('datetime', models.DateField(blank=True)),
                ('request', models.ForeignKey(to='core.Request')),
                ('service', models.ForeignKey(to='core.CompanyServiceSelection')),
            ],
            options={
                'db_table': 'core_requestservicestatus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RequestStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'New'), (2, b'Assigned'), (3, b'In Progress'), (4, b'Completed'), (5, b'Submitted'), (6, b'Rejected'), (7, b'Incomplete'), (8, b'New Returned'), (9, b'Deleted')])),
                ('datetime', models.DateTimeField(verbose_name=b'Date', db_index=True)),
                ('comments', models.TextField()),
                ('request', models.ForeignKey(to='core.Request')),
            ],
            options={
                'ordering': ['-datetime'],
                'db_table': 'core_requeststatus',
                'verbose_name': 'Request Statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
                ('display_order', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SpotLitStaff',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('is_activated', models.BooleanField(default=False)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='request',
            name='assignment',
            field=models.ForeignKey(default=None, blank=True, to='core.SpotLitStaff', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='completed_status',
            field=models.ForeignKey(related_name=b'+', default=None, blank=True, to='core.RequestStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='created_by',
            field=models.ForeignKey(to='core.CompanyEmployee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='in_progress_status',
            field=models.ForeignKey(related_name=b'+', default=None, blank=True, to='core.RequestStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='request_type',
            field=models.ForeignKey(to='core.CompanyDueDiligenceTypeSelection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dynamicrequestformfields',
            name='group',
            field=models.ForeignKey(to='core.LayoutGroupSections'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dynamicrequestformfields',
            name='type',
            field=models.ForeignKey(to='core.RequestFormFieldTypes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='duediligencetypeservices',
            name='service',
            field=models.ForeignKey(to='core.Service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequestfields',
            name='form_field',
            field=models.ForeignKey(to='core.DynamicRequestFormFields'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='assignment',
            field=models.ForeignKey(default=None, blank=True, to='core.SpotLitStaff', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='completed_status',
            field=models.ForeignKey(related_name=b'+', default=None, blank=True, to='core.CustomRequestStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='created_by',
            field=models.ForeignKey(to='core.CompanyEmployee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='dynamic_request_form',
            field=models.ForeignKey(to='core.DynamicRequestForm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='in_progress_status',
            field=models.ForeignKey(related_name=b'+', default=None, blank=True, to='core.CustomRequestStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='customrequest',
            name='request_type',
            field=models.ForeignKey(to='core.CompanyDueDiligenceTypeSelection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='corporaterequest',
            name='assignment',
            field=models.ForeignKey(default=None, blank=True, to='core.SpotLitStaff', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='corporaterequest',
            name='completed_status',
            field=models.ForeignKey(related_name=b'+', default=None, blank=True, to='core.CorporateRequestStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='corporaterequest',
            name='created_by',
            field=models.ForeignKey(to='core.CompanyEmployee'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='corporaterequest',
            name='in_progress_status',
            field=models.ForeignKey(related_name=b'+', default=None, blank=True, to='core.CorporateRequestStatus', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='corporaterequest',
            name='request_type',
            field=models.ForeignKey(to='core.CompanyDueDiligenceTypeSelection'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyserviceselection',
            name='service',
            field=models.ForeignKey(to='core.Service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='companyduediligencetypeselection',
            name='due_diligence_type',
            field=models.ForeignKey(to='core.DueDiligenceType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='batchfile',
            name='created_by',
            field=models.ForeignKey(to='core.CompanyEmployee'),
            preserve_default=True,
        ),
    ]
