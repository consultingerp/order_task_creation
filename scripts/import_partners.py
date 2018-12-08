import csv
import oerplib
from argparse import ArgumentParser
from ast import literal_eval
from collections import namedtuple
import psycopg2
import cStringIO
import codecs


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def get_title_id(model, title_name):
    title_id = model.search([('name', 'ilike', title_name)])
    return title_id and title_id[0] or False


def get_country_id(model, country_code):
    return model.search([('code', '=', country_code)])[0]


def is_partner_imported(cr, import_ref):
    cr.execute('''
        SELECT name FROM res_partner WHERE import_ref=%s
    ''', (import_ref,))
    return cr.fetchone()


def write_import_ref(cr, import_ref, partner_id):
    cr.execute('''
        UPDATE res_partner SET import_ref=%s WHERE id=%s
    ''', (import_ref, partner_id))


def check_import_ref_exists(cr, dbname):
    try:
        cr.execute('''
            SELECT import_ref
            FROM res_partner
        ''')
    except:
        raise Exception(
            'execute query in %s before import: '
            'ALTER TABLE res_partner ADD COLUMN import_ref integer'
            % dbname)


def get_parent_partner_company(model, name):
    return model.search([
        ('name', 'ilike', name),
        ('is_company', '=', True)
    ])


def create_partner_company(model, row, company_id):
    return model.create({
        'name': row.related_company,
        'is_company': True,
        'customer': literal_eval(row.is_customer),
        'supplier': literal_eval(row.is_supplier),
        'country_id': row.country and get_country_id(country_model, row.country) or False,
        'street': row.street or False,
        'city': row.city or False,
        'zip': row.zip or False,
        'website': row.website or False,
        'company_id': company_id,
    })


def get_lastname(lastname, title):
    if lastname and title:
        return ' '.join([title, lastname])
    return lastname


def get_company(model):
    return model.search([
        ('name', 'ilike', 'Source'),
    ])[0]



if __name__ == '__main__':

    parser = ArgumentParser(
        description=("Import partners"))
    parser.add_argument('user', help='odoo user login')
    parser.add_argument('password', help='odoo user password')
    parser.add_argument('database', help='odoo database')
    parser.add_argument('host', help='IP or domain of odoo server')
    parser.add_argument('port', type=int, help='odoo server port number')
    parser.add_argument('import_file', help='an existing file path'
                                            ' from where members will be'
                                            ' imported')
    parser.add_argument('import_error_file',
                        help='an existing file path'
                             ' where failed imports'
                             ' will be written.')

    args = parser.parse_args()
    db_conn = psycopg2.connect(database=args.database)
    cr = db_conn.cursor()
    check_import_ref_exists(cr, args.database)
    oerp = oerplib.OERP(args.host, protocol='xmlrpc',
                        port=args.port, timeout=120*30)
    user = oerp.login(args.user, args.password, args.database)
    oerp.context['lang'] = 'de_DE'

    with open(args.import_file, 'rb') as f:
        length = sum(1 for r in f) - 1

    with open(args.import_file, 'rb') as f:
        reader = UnicodeReader(f, delimiter=";")
        # use first row as mapping for field names
        Row = namedtuple('Row', reader.next())

        partner_model = oerp.get('res.partner')
        title_model = oerp.get('res.partner.title')
        country_model = oerp.get('res.country')
        user_model = oerp.get('res.users')
        company_id = oerp.get('res.company').search([
            ('name', 'ilike', 'SOURCE'),
        ])[0]

        for i, row in enumerate((Row._make(r) for r in reader), start=1):
            print "Progress: %s/%s" % (i, length)
            try:
                if not is_partner_imported(cr, row.import_ref):
                    parent_company_id = get_parent_partner_company(partner_model, row.related_company)
                    parent_company_id = (
                        row.related_company and
                        parent_company_id and
                        parent_company_id[0] or
                        create_partner_company(partner_model, row, company_id) or
                        False
                    )
                    lastname = get_lastname(row.last_name, row.title)
                    new_partner_id = partner_model.create({
                        'lang': 'de_DE',
                        'country_id': row.country and get_country_id(country_model, row.country) or False,
                        'lastname': lastname or '' if row.first_name else 'no name',
                        'firstname': row.first_name or '' if row.last_name else 'no name',
                        'title': get_title_id(title_model, row.salutation),
                        'street': row.street or False,
                        'city': row.city or False,
                        'zip': row.zip or False,
                        'fax': row.fax or False,
                        'phone': row.phone or False,
                        'mobile': row.mobile or False,
                        'email': row.email or False,
                        'function': row.function or False,
                        'comment': row.comment or False,
                        'customer': literal_eval(row.is_customer),
                        'supplier': literal_eval(row.is_supplier),
                        'is_company': literal_eval(row.is_company),
                        'parent_id': parent_company_id,
                        'company_id': company_id,
                    })
                    write_import_ref(cr, row.import_ref, new_partner_id)
                    db_conn.commit()
            except Exception:
                with open(args.import_error_file, 'a') as f:
                    writer = UnicodeWriter(f, delimiter=';')
                    writer.writerow(row)
